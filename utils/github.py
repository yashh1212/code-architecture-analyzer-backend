import re
from urllib.parse import urlparse


# -------------------------
# Regex patterns
# -------------------------

# https://github.com/owner/repo
HTTPS_PATTERN = re.compile(
    r"^https:\/\/github\.com\/[A-Za-z0-9_.-]+\/[A-Za-z0-9_.-]+(\.git)?\/?$"
)

# git@github.com:owner/repo.git
SSH_PATTERN = re.compile(
    r"^git@github\.com:[A-Za-z0-9_.-]+\/[A-Za-z0-9_.-]+(\.git)?$"
)


def is_valid_github_repo_url(url: str) -> bool:
    """
    Validate whether a string is a valid GitHub repository URL.

    Supported formats:
    - https://github.com/owner/repo
    - https://github.com/owner/repo.git
    - git@github.com:owner/repo.git
    """

    if not url or not isinstance(url, str):
        return False

    url = url.strip()

    # SSH format
    if SSH_PATTERN.match(url):
        return True

    # HTTPS format
    if HTTPS_PATTERN.match(url):
        return True

    return False
