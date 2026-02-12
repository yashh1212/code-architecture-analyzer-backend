# import os
# import git
# from .file_filter import is_valid_file

# BASE_REPO_DIR = "repos"

# def clone_repo(repo_url: str, repo_id: str) -> str:
#     """
#     Clones a GitHub repository locally and returns the local path
#     """
#     os.makedirs(BASE_REPO_DIR, exist_ok=True)
#     repo_path = os.path.join(BASE_REPO_DIR, repo_id)

#     if not os.path.exists(repo_path):
#         git.Repo.clone_from(repo_url, repo_path)

#     return repo_path


# def load_repo_from_github(repo_url: str, repo_id: str):
#     """
#     Clone repo → read valid files → return content
#     """
#     repo_path = clone_repo(repo_url, repo_id)
#     files = []

#     for root, _, filenames in os.walk(repo_path):
#         for name in filenames:
#             full_path = os.path.join(root, name)
#             if is_valid_file(full_path):
#                 try:
#                     with open(full_path, "r", encoding="utf-8", errors="ignore") as f:
#                         files.append({
#                             "path": full_path.replace(repo_path, ""),
#                             "content": f.read()
#                         })
#                 except Exception:
#                     continue

#     return files

import os
import shutil
import zipfile
import git

BASE_REPO_DIR = "repos"


def clone_github_repo(repo_url: str, repo_id: str) -> str:
    repo_path = os.path.join(BASE_REPO_DIR, repo_id)
    os.makedirs(repo_path, exist_ok=True)

    git.Repo.clone_from(repo_url, repo_path)
    return repo_path


# def extract_zip_repo(zip_path: str, repo_id: str) -> str:

#     """Safely extract a zip file into a repo directory and normalize layout.

#     - Prevents ZipSlip (no absolute paths or '..' entries).
#     - Extracts into a temporary dir first.
#     - If the archive contains a single top-level directory (common for GitHub zips),
#       its contents are moved up into the repo root so `repo_path` contains the repo files
#       directly (no extra nesting).
#     """
#     import tempfile
#     from pathlib import PurePosixPath

#     repo_path = os.path.join(BASE_REPO_DIR, repo_id)

#     # Ensure a clean target directory
#     if os.path.exists(repo_path):
#         shutil.rmtree(repo_path)
#     os.makedirs(repo_path, exist_ok=True)

#     # Extract to a temp directory first to validate and normalize
#     tmp_dir = tempfile.mkdtemp()
#     try:
#         with zipfile.ZipFile(zip_path, "r") as z:
#             # Validate entries to avoid path traversal
#             for member in z.infolist():
#                 member_name = member.filename
#                 # Skip directories
#                 if not member_name:
#                     continue
#                 parts = PurePosixPath(member_name).parts
#                 if any(p == ".." for p in parts) or member_name.startswith("/"):
#                     raise Exception("Unsafe zip entry detected")

#             z.extractall(tmp_dir)

#         # Normalize: if a single top-level folder exists, use it as source; else use tmp_dir
#         entries = [e for e in os.listdir(tmp_dir) if not e.startswith(".")]
#         if len(entries) == 1 and os.path.isdir(os.path.join(tmp_dir, entries[0])):
#             src = os.path.join(tmp_dir, entries[0])
#         else:
#             src = tmp_dir

#         # Move contents from src into repo_path
#         for name in os.listdir(src):
#             s = os.path.join(src, name)
#             d = os.path.join(repo_path, name)
#             shutil.move(s, d)

#     finally:
#         # Clean temp directory
#         if os.path.exists(tmp_dir):
#             shutil.rmtree(tmp_dir)

#     return repo_path
def extract_zip_repo(zip_path: str, repo_id: str) -> str:
    repo_path = os.path.join("repos", repo_id)
    os.makedirs(repo_path, exist_ok=True)

    with zipfile.ZipFile(zip_path, "r") as zip_ref:
        for member in zip_ref.namelist():
            target_path = os.path.abspath(os.path.join(repo_path, member))
            if not target_path.startswith(os.path.abspath(repo_path)):
                raise Exception("Unsafe zip entry detected")

        zip_ref.extractall(repo_path)

    return repo_path
