import requests
import base64
from typing import Optional
from src.core.config import config


class GitHubClient:
    """
    A clean interface to GitHub's REST API.
    
    Every method here maps to one or more GitHub API endpoints.
    We wrap the raw API calls so the rest of our code works with
    clean Python objects rather than raw HTTP responses.
    """
    
    def __init__(self):
        self.base_url = config.GITHUB_API_BASE
        self.headers = {
            "Authorization": f"token {config.GITHUB_TOKEN}",
            "Accept": "application/vnd.github.v3+json",
            "X-GitHub-Api-Version": "2022-11-28"
        }
    
    def _get(self, endpoint: str) -> dict:
        """
        Makes a GET request to the GitHub API.
        
        The underscore prefix means this is an internal method —
        other parts of your code should use the specific methods
        below, not call _get directly.
        """
        url = f"{self.base_url}{endpoint}"
        response = requests.get(url, headers=self.headers)
        
        if response.status_code == 404:
            raise FileNotFoundError(f"GitHub resource not found: {endpoint}")
        
        if response.status_code == 403:
            raise PermissionError(f"GitHub permission denied: {endpoint}. Check your token permissions.")
        
        if not response.ok:
            raise RuntimeError(
                f"GitHub API error {response.status_code}: {response.text[:200]}"
            )
        
        return response.json()
    
    def _post(self, endpoint: str, data: dict) -> dict:
        """Makes a POST request to the GitHub API."""
        url = f"{self.base_url}{endpoint}"
        response = requests.post(url, headers=self.headers, json=data)
        
        if not response.ok:
            raise RuntimeError(
                f"GitHub API error {response.status_code}: {response.text[:200]}"
            )
        
        return response.json()
    
    def _put(self, endpoint: str, data: dict) -> dict:
        """Makes a PUT request to the GitHub API."""
        url = f"{self.base_url}{endpoint}"
        response = requests.put(url, headers=self.headers, json=data)
        
        if not response.ok:
            raise RuntimeError(
                f"GitHub API error {response.status_code}: {response.text[:200]}"
            )
        
        return response.json()
    
    def get_repo_info(self, owner: str, repo: str) -> dict:
        """
        Gets basic information about a repository.
        
        Returns: dict with keys like 'name', 'description',
        'default_branch', 'language', 'size'
        """
        return self._get(f"/repos/{owner}/{repo}")
    
    def get_file_content(self, owner: str, repo: str, 
                         path: str, branch: str = "main") -> str:
        """
        Reads the content of a single file from a GitHub repo.
        
        GitHub returns file content as base64-encoded text.
        We decode it here so callers always get plain text back.
        
        Args:
            owner: GitHub username or org (e.g., "tiangolo")
            repo: Repository name (e.g., "fastapi")
            path: File path within the repo (e.g., "src/fastapi/main.py")
            branch: Which branch to read from (defaults to "main")
        
        Returns: The file's content as a plain string
        """
        data = self._get(
            f"/repos/{owner}/{repo}/contents/{path}?ref={branch}"
        )
        
        # GitHub returns content as base64 to handle binary files safely.
        # Even for text files, we need to decode from base64 first.
        # base64.b64decode gives us bytes, then .decode('utf-8') gives us string.
        content = base64.b64decode(data["content"]).decode("utf-8")
        
        # Check file size — we don't want to process huge files
        size_kb = len(content.encode()) / 1024
        if size_kb > config.MAX_FILE_SIZE_KB:
            return f"[File too large to process: {size_kb:.1f}KB, limit is {config.MAX_FILE_SIZE_KB}KB]"
        
        return content
    
    def get_repo_structure(self, owner: str, repo: str, 
                           branch: str = "main") -> list[dict]:
        """
        Gets a list of all files in a repository.
        
        Uses GitHub's Git Trees API which returns the entire repo
        structure in one API call (much more efficient than
        recursively listing directories one by one).
        
        Returns: list of dicts, each with 'path', 'type', 'size'
        """
        # First get the branch info to find the tree SHA
        branch_data = self._get(
            f"/repos/{owner}/{repo}/branches/{branch}"
        )
        tree_sha = branch_data["commit"]["commit"]["tree"]["sha"]
        
        # Now get the full tree recursively
        tree_data = self._get(
            f"/repos/{owner}/{repo}/git/trees/{tree_sha}?recursive=1"
        )
        if tree_data.get("truncated"):
            print(f"⚠️ Warning: repo tree truncated, results incomplete for {owner}/{repo}")
            
        # Filter to only include files (not directories)
        # and exclude common non-useful files
        files = []
        excluded_patterns = [
            ".git/", "node_modules/", "__pycache__/",
            ".pyc", ".egg-info/", "dist/", "build/"
        ]
        
        for item in tree_data["tree"]:
            if item["type"] != "blob":  # blob = file, tree = directory
                continue
            
            path = item["path"]
            if any(pattern in path for pattern in excluded_patterns):
                continue
            
            files.append({
                "path": path,
                "size": item.get("size", 0),
                "type": "file"
            })
        
        return files[:config.MAX_REPO_FILES]
    
    def get_issue(self, owner: str, repo: str, 
                  issue_number: int) -> dict:
        """
        Gets a specific issue from a repository.
        
        Returns: dict with 'title', 'body', 'labels', 'state'
        """
        return self._get(
            f"/repos/{owner}/{repo}/issues/{issue_number}"
        )
    
    def create_branch(self, owner: str, repo: str,
                      branch_name: str, from_branch: str = "main") -> str:
        """
        Creates a new branch in a repository.
        
        In Git, a branch is just a pointer to a specific commit.
        Creating a branch via API means: find the commit that
        'from_branch' currently points to, then create a new
        pointer (the new branch) pointing to that same commit.
        
        Returns: the SHA of the commit the new branch points to
        """
        # Get the SHA of the latest commit on from_branch
        branch_data = self._get(
            f"/repos/{owner}/{repo}/branches/{from_branch}"
        )
        sha = branch_data["commit"]["sha"]
        
        # Create the new branch pointing to that commit
        self._post(
            f"/repos/{owner}/{repo}/git/refs",
            {
                "ref": f"refs/heads/{branch_name}",
                "sha": sha
            }
        )
        
        return sha
    
    def update_file(self, owner: str, repo: str, path: str,
                    content: str, message: str, 
                    branch: str = "main",
                    sha: Optional[str] = None) -> dict:
        """
        Creates or updates a file in a repository.
        
        GitHub's API requires:
        - The file content encoded as base64
        - A commit message
        - If updating an existing file: the SHA of the current file
          (this prevents overwriting changes made by someone else)
        
        Args:
            sha: The current file's SHA. If None, creates a new file.
                 If provided, updates the existing file.
        """
        # GitHub requires content as base64
        encoded_content = base64.b64encode(
            content.encode("utf-8")
        ).decode("utf-8")
        
        data = {
            "message": message,
            "content": encoded_content,
            "branch": branch
        }
        
        # If we're updating an existing file, we need its current SHA
        if sha:
            data["sha"] = sha
        
        return self._put(
            f"/repos/{owner}/{repo}/contents/{path}",
            data
        )
    
    def get_file_sha(self, owner: str, repo: str,
                     path: str, branch: str = "main") -> Optional[str]:
        """
        Gets the SHA of an existing file.
        
        Needed when updating files — GitHub requires the current
        SHA to prevent accidental overwrites.
        
        Returns: SHA string if file exists, None if it doesn't
        """
        try:
            data = self._get(
                f"/repos/{owner}/{repo}/contents/{path}?ref={branch}"
            )
            return data["sha"]
        except FileNotFoundError:
            return None
    
    def create_pull_request(self, owner: str, repo: str,
                             title: str, body: str,
                             head_branch: str,
                             base_branch: str = "main") -> dict:
        """
        Opens a pull request.
        
        Args:
            head_branch: The branch with your changes
            base_branch: The branch you want to merge INTO
        
        Returns: dict with 'number', 'html_url', 'title'
        """
        result = self._post(
            f"/repos/{owner}/{repo}/pulls",
            {
                "title": title,
                "body": body,
                "head": head_branch,
                "base": base_branch
            }
        )
        
        return {
            "number": result["number"],
            "url": result["html_url"],
            "title": result["title"]
        }


# Create a single shared instance
# Other modules import this instance, not the class
github = GitHubClient()