from mcp.server.mcpserver import MCPServer
from src.tools.sandbox import run_code_in_sandbox

mcp = MCPServer("sandbox-server")


@mcp.tool()
def run_code(files: dict, entry_point: str, timeout_seconds: int = 15) -> dict:
    """
    Runs code inside an isolated Docker container. Supports multiple
    files so a test file can import and check a separate solution file.
    
    Args:
        files: dict mapping filename -> file content, e.g.
               {"solution.py": "...", "test_solution.py": "..."}
        entry_point: which file to actually run (usually the test file)
        timeout_seconds: max time allowed before killing the process
    
    Returns: {"success": bool, "stdout": str, "stderr": str,
              "timed_out": bool, "infrastructure_error": bool}
    """
    return run_code_in_sandbox(files, entry_point, timeout_seconds)


if __name__ == "__main__":
    mcp.run()