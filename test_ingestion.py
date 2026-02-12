from Ingestion.repo_loader import load_repo_from_github

repo_url = "https://github.com/yashh1212/heart_disease_prediction"
repo_id = "heart_disease_repo"

files = load_repo_from_github(repo_url, repo_id)

print(f"Loaded {len(files)} files")
print(files[0]["path"])
