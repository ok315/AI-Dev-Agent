from src.tools.github_client import github

# Test on your own Multi-Tool-Agent repo
# Replace "ok315" with your GitHub username
OWNER = "ok315"
REPO = "Multi-Tool-Agent"

print("Test 1: Get repo info")
info = github.get_repo_info(OWNER, REPO)
print(f"  Repo: {info['full_name']}")
print(f"  Default branch: {info['default_branch']}")
print(f"  Language: {info['language']}")

print("\nTest 2: Get repo structure")
files = github.get_repo_structure(OWNER, REPO, 
                                   branch=info['default_branch'])
print(f"  Found {len(files)} files")
for f in files[:5]:  # show first 5
    print(f"  {f['path']}")

print("\nTest 3: Read a specific file")
content = github.get_file_content(
    OWNER, REPO, "README.md",
    branch=info['default_branch']
)
print(f"  README first 200 chars:")
print(f"  {content[:200]}")

# print("\nTest 4: Create a branch")
# sha = github.create_branch(OWNER, REPO, "test-branch-delete-me", from_branch=info['default_branch'])
# print(f"  Created branch pointing to {sha[:7]}")

# print("\nTest 5: Update a file on that branch")
# current_sha = github.get_file_sha(OWNER, REPO, "test_file.md", branch="test-branch-delete-me")
# result = github.update_file(
#     OWNER, REPO, "test_file.md",
#     content="# Test\nCreated by github_client.py\n",
#     message="test: verify update_file works",
#     branch="test-branch-delete-me",
#     sha=current_sha  # None if file doesn't exist yet -> creates it
# )
# print(f"  Committed: {result['commit']['sha'][:7]}")

# print("\nTest 6: Open a PR")
# pr = github.create_pull_request(
#     OWNER, REPO,
#     title="Test PR — delete me",
#     body="Verifying create_pull_request works end to end.",
#     head_branch="test-branch-delete-me",
#     base_branch=info['default_branch']
# )
# print(f"  PR #{pr['number']}: {pr['url']}")
print("All tests suceeded!")