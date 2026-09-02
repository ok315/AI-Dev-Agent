import subprocess
import tempfile
import os


def run_code_in_sandbox(files: dict, entry_point: str, timeout_seconds: int = 15) -> dict:
    """
    Runs code inside an isolated Docker container. Supports multiple
    files so a test file can import and check a separate solution file.
    
    Args:
        files: dict mapping filename -> file content, e.g.
               {"solution.py": "...", "test_solution.py": "..."}
        entry_point: which file to actually RUN (usually the test file,
                     since it will import the solution file itself)
        timeout_seconds: max time allowed before we kill it
    
    Returns: same result shape as before —
        {"success": bool, "stdout": str, "stderr": str, "timed_out": bool}
    """
    with tempfile.TemporaryDirectory() as temp_dir:
        # Write ALL files into the same temp folder, so they can
        # import each other when the container runs.
        for filename, content in files.items():
            file_path = os.path.join(temp_dir, filename)
            with open(file_path, "w") as f:
                f.write(content)
        
        docker_command = [
            "docker", "run",
            "--rm",
            "--network", "none",
            "--memory", "256m",
            "--cpus", "0.5",
            "-v", f"{temp_dir}:/sandbox",
            "-w", "/sandbox",
            "python:3.11-slim",
            "python", entry_point   # run whichever file we're told to
        ]
        
        try:
            result = subprocess.run(
                docker_command,
                capture_output=True,
                text=True,
                timeout=timeout_seconds
            )
            
            return {
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "timed_out": False
            }
        
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "stdout": "",
                "stderr": f"Execution timed out after {timeout_seconds} seconds",
                "timed_out": True
            }