
# import os
# import uuid
# import zipfile
# from fastapi import APIRouter,UploadFile, File, Form, HTTPException
# from  Ingestion.repo_loader import clone_github_repo, extract_zip_repo
# from utils.github import is_valid_github_repo_url
# from pathlib import Path
# from utils.build_repo_tree_arch import build_file_tree
# from utils.analyze_repo_arch import analyze_repo_architecture
# from utils.dependency import analyze_repo_dependencies
# from services.repo_processor import     


# TMP_DIR = "/tmp"
# router=APIRouter()

# REPOS_BASE_PATH = Path("repos")




# @router.post("/upload")
# async def upload_repo(
#     repo_url: str | None = Form(None),
#     zip_file: UploadFile | None = File(None),
# ):
#     # -------------------------
#     # Validation
#     # -------------------------
#     if not repo_url and not zip_file:
#         raise HTTPException(
#             status_code=400,
#             detail="Provide either repo_url or zip_file",
#         )

#     if repo_url and zip_file:
#         raise HTTPException(
#             status_code=400,
#             detail="Provide only one: repo_url OR zip_file",
#         )

#     repo_id = str(uuid.uuid4())

#     try:
#         # -------------------------
#         # GitHub Repo Handling
#         # -------------------------
#         if repo_url:
#             if not is_valid_github_repo_url(repo_url):
#                 raise HTTPException(
#                     status_code=400,
#                     detail=(
#                         "Invalid GitHub repository URL. "
#                         "Expected formats:\n"
#                         "- https://github.com/owner/repo\n"
#                         "- git@github.com:owner/repo.git"
#                     ),
#                 )

#             repo_path = clone_github_repo(repo_url, repo_id)

#         # -------------------------
#         # ZIP Upload Handling
#         # -------------------------
#         else:
#             if not zip_file.filename.endswith(".zip"):
#                 raise HTTPException(
#                     status_code=400,
#                     detail="Only .zip files are supported",
#                 )

#             os.makedirs(TMP_DIR, exist_ok=True)
#             temp_zip_path = os.path.join(TMP_DIR, f"{repo_id}.zip")

#             # 1️⃣ Save ZIP to /tmp
#             with open(temp_zip_path, "wb") as f:
#                 f.write(await zip_file.read())

#             # 2️⃣ Validate ZIP (prevents zip bombs & corruption)
#             if not zipfile.is_zipfile(temp_zip_path):
#                 raise HTTPException(
#                     status_code=400,
#                     detail="Uploaded file is not a valid zip archive",
#                 )

#             # 3️⃣ Extract safely
#             repo_path = extract_zip_repo(temp_zip_path, repo_id)

#             # 4️⃣ Cleanup temp zip
#             os.remove(temp_zip_path)

#     except zipfile.BadZipFile:
#         raise HTTPException(
#             status_code=400,
#             detail="Invalid or corrupted zip file",
#         )

#     except HTTPException:
#         raise

#     except Exception as e:
#         raise HTTPException(
#             status_code=500,
#             detail=f"Failed to load repository: {str(e)}",
#         )
#     process_repository(repo_id)
#     return {
#         "repo_id": repo_id,
#         "repo_path": repo_path,
#         "status": "repo_loaded",
#     }

# @router.get("/structure/{repo_id}")
# def get_repo_structure(repo_id: str):
#     repo_path = REPOS_BASE_PATH / repo_id

#     if not repo_path.exists() or not repo_path.is_dir():
#         raise HTTPException(status_code=404, detail="Repository not found")

#     return build_file_tree(repo_path)

# @router.get("/architecture/{repo_id}")
# def get_architecture_overview(repo_id: str):
#     repo_path = REPOS_BASE_PATH / repo_id

#     if not repo_path.exists() or not repo_path.is_dir():
#         raise HTTPException(status_code=404, detail="Repository not found")

#     return analyze_repo_architecture(repo_path)

# @router.get("/dependencies/{repo_id}")
# def get_dependencies(repo_id: str):
#     repo_path = REPOS_BASE_PATH / repo_id

#     if not repo_path.exists() or not repo_path.is_dir():
#         raise HTTPException(status_code=404, detail="Repository not found")

#     return analyze_repo_dependencies(repo_path)
import os
import uuid
import zipfile
from pathlib import Path

from fastapi import APIRouter, UploadFile, File, Form, HTTPException, BackgroundTasks

from Ingestion.repo_loader import clone_github_repo, extract_zip_repo
from utils.github import is_valid_github_repo_url
from utils.build_repo_tree_arch import build_file_tree
from utils.analyze_repo_arch import analyze_repo_architecture
from utils.dependency import analyze_repo_dependencies
from services.repo_processor import process_repository


TMP_DIR = "/tmp"
REPOS_BASE_PATH = Path("repos")

router = APIRouter()


# ----------------------------------------------------
# UPLOAD ROUTE
# ----------------------------------------------------
@router.post("/upload")
async def upload_repo(
    background_tasks: BackgroundTasks,
    repo_url: str | None = Form(None),
    zip_file: UploadFile | None = File(None),
):

    if not repo_url and not zip_file:
        raise HTTPException(
            status_code=400,
            detail="Provide either repo_url or zip_file",
        )

    if repo_url and zip_file:
        raise HTTPException(
            status_code=400,
            detail="Provide only one: repo_url OR zip_file",
        )

    repo_id = str(uuid.uuid4())

    try:
        if repo_url:
            if not is_valid_github_repo_url(repo_url):
                raise HTTPException(
                    status_code=400,
                    detail="Invalid GitHub repository URL.",
                )

            repo_path = clone_github_repo(repo_url, repo_id)

        else:
            if not zip_file.filename.endswith(".zip"):
                raise HTTPException(
                    status_code=400,
                    detail="Only .zip files are supported",
                )

            os.makedirs(TMP_DIR, exist_ok=True)
            temp_zip_path = os.path.join(TMP_DIR, f"{repo_id}.zip")

            with open(temp_zip_path, "wb") as f:
                f.write(await zip_file.read())

            if not zipfile.is_zipfile(temp_zip_path):
                raise HTTPException(
                    status_code=400,
                    detail="Uploaded file is not a valid zip archive",
                )

            repo_path = extract_zip_repo(temp_zip_path, repo_id)
            os.remove(temp_zip_path)

    except zipfile.BadZipFile:
        raise HTTPException(status_code=400, detail="Invalid zip file")

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to load repository: {str(e)}",
        )

    # 🔥 PROCESS IN BACKGROUND (non-blocking)
    background_tasks.add_task(process_repository, repo_id)

    return {
        "repo_id": repo_id,
        "repo_path": str(repo_path),
        "status": "repo_uploaded_processing_started"
    }


# ----------------------------------------------------
# FILE STRUCTURE
# ----------------------------------------------------
@router.get("/structure/{repo_id}")
def get_repo_structure(repo_id: str):

    repo_path = REPOS_BASE_PATH / repo_id

    if not repo_path.exists():
        raise HTTPException(status_code=404, detail="Repository not found")

    return build_file_tree(repo_path)


# ----------------------------------------------------
# ARCHITECTURE OVERVIEW
# ----------------------------------------------------
@router.get("/architecture/{repo_id}")
def get_architecture_overview(repo_id: str):

    repo_path = REPOS_BASE_PATH / repo_id

    if not repo_path.exists():
        raise HTTPException(status_code=404, detail="Repository not found")

    return analyze_repo_architecture(repo_path)


# ----------------------------------------------------
# DEPENDENCIES
# ----------------------------------------------------
@router.get("/dependencies/{repo_id}")
def get_dependencies(repo_id: str):

    repo_path = REPOS_BASE_PATH / repo_id

    if not repo_path.exists():
        raise HTTPException(status_code=404, detail="Repository not found")

    return analyze_repo_dependencies(repo_path)
