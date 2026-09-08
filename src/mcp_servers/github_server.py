from mcp.server.mcpserver import MCPServer
from src.tools.github_client import github

mcp = MCPServer("github-server")

@mcp.tool()
def get_file_content(owner: str, repo: str, path: str, branch: str = "main") -> str:
    """Reads the content of a file from a GitHub repo."""
    return github.get_file_content(owner, repo, path, branch=branch)

@mcp.tool()
def get_repo_structure(owner: str, repo: str, branch: str = "main") -> list[dict]:
    """Gets a list of all files in a repository."""
    return github.get_repo_structure(owner, repo, branch=branch)

@mcp.tool()
def get_repo_info(owner: str, repo: str) -> dict:
    """Gets basic information about a repository."""
    return github.get_repo_info(owner, repo)

@mcp.tool()
def create_branch(owner: str, repo: str, branch_name: str, from_branch: str = "main") -> str:
    """Creates a new branch in a repository."""
    return github.create_branch(owner, repo, branch_name, from_branch=from_branch)

@mcp.tool()
def update_file(owner: str, repo: str, path: str, content: str, message: str,
                 branch: str = "main", sha: str = None) -> dict:
    """Creates or updates a file in a repository."""
    return github.update_file(owner, repo, path, content, message, branch=branch, sha=sha)

@mcp.tool()
def get_file_sha(owner: str, repo: str, path: str, branch: str = "main") -> str:
    """Gets the SHA of an existing file, needed for updates."""
    return github.get_file_sha(owner, repo, path, branch=branch)

@mcp.tool()
def create_pull_request(owner: str, repo: str, title: str, body: str,
                         head_branch: str, base_branch: str = "main") -> dict:
    """Opens a pull request."""
    return github.create_pull_request(owner, repo, title, body, head_branch, base_branch=base_branch)

if __name__ == "__main__":
    mcp.run()