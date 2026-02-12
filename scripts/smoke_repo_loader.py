import os
import zipfile
import tempfile
from Ingestion.repo_loader import extract_zip_repo


def make_zip_with_topdir(zippath: str, topdir: str, files: dict):
    with zipfile.ZipFile(zippath, "w") as z:
        for name, content in files.items():
            z.writestr(f"{topdir}/{name}", content)


def make_zip_with_root_files(zippath: str, files: dict):
    with zipfile.ZipFile(zippath, "w") as z:
        for name, content in files.items():
            z.writestr(name, content)


tmp = tempfile.TemporaryDirectory()
try:
    z1 = os.path.join(tmp.name, "topdir.zip")
    files = {"a.txt": "hello", "subdir/b.txt": "world"}
    make_zip_with_topdir(z1, "myrepo-master", files)
    repo1 = extract_zip_repo(z1, "smoke1")
    assert os.path.isfile(os.path.join(repo1, "a.txt"))
    assert os.path.isfile(os.path.join(repo1, "subdir", "b.txt"))

    z2 = os.path.join(tmp.name, "root.zip")
    files2 = {"x.txt": "123", "dir/y.txt": "456"}
    make_zip_with_root_files(z2, files2)
    repo2 = extract_zip_repo(z2, "smoke2")
    assert os.path.isfile(os.path.join(repo2, "x.txt"))
    assert os.path.isfile(os.path.join(repo2, "dir", "y.txt"))

    print("Smoke tests passed")
finally:
    tmp.cleanup()
