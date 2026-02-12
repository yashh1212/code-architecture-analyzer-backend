import os
import tempfile
import zipfile
from Ingestion.repo_loader import extract_zip_repo


def make_zip_with_topdir(zippath: str, topdir: str, files: dict):
    with zipfile.ZipFile(zippath, "w") as z:
        for name, content in files.items():
            z.writestr(f"{topdir}/{name}", content)


def make_zip_with_root_files(zippath: str, files: dict):
    with zipfile.ZipFile(zippath, "w") as z:
        for name, content in files.items():
            z.writestr(name, content)


def test_extract_zip_with_topdir(tmp_path):
    zpath = tmp_path / "topdir.zip"
    files = {"a.txt": "hello", "subdir/b.txt": "world"}

    make_zip_with_topdir(str(zpath), "myrepo-master", files)

    repo_id = "test1"
    repo_path = extract_zip_repo(str(zpath), repo_id)

    assert os.path.exists(repo_path)
    assert os.path.isfile(os.path.join(repo_path, "a.txt"))
    assert os.path.isfile(os.path.join(repo_path, "subdir", "b.txt"))


def test_extract_zip_with_root_files(tmp_path):
    zpath = tmp_path / "root.zip"
    files = {"x.txt": "123", "dir/y.txt": "456"}

    make_zip_with_root_files(str(zpath), files)

    repo_id = "test2"
    repo_path = extract_zip_repo(str(zpath), repo_id)

    assert os.path.exists(repo_path)
    assert os.path.isfile(os.path.join(repo_path, "x.txt"))
    assert os.path.isfile(os.path.join(repo_path, "dir", "y.txt"))
