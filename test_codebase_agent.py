from src.agents.codebase_agent import get_python_files

OWNER = "ok315"
REPO = "Multi-Tool-Agent"

files = get_python_files(OWNER, REPO, branch="master")

print("\nPython files found:")
for f in files:
    print(f"  {f['path']} ({f['size']} bytes)")