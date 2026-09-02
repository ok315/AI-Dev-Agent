import subprocess
import tempfile
import os


def run_code_in_sandbox(code: str, timeout_seconds: int = 15) -> dict:
    """
    Runs a string of Python code inside an isolated Docker container
    and returns what happened.
    
    Safety measures applied:
      - No network access (--network none)
      - Memory capped at 256MB (--memory 256m)
      - CPU capped at half a core (--cpus 0.5)
      - Killed automatically if it runs longer than timeout_seconds
      - Container is auto-removed after running (--rm), so nothing lingers
    
    Args:
        code: the Python source code to execute, as a string
        timeout_seconds: max time allowed before we kill it
    
    Returns:
        {
            "success": True/False — did it run without crashing,
            "stdout": whatever the code printed,
            "stderr": any error output,
            "timed_out": True if we had to kill it for running too long
        }
    """
    # Create a temporary folder on YOUR machine (not in the container yet)
    # to hold the code file we're about to run.
    with tempfile.TemporaryDirectory() as temp_dir:
        code_path = os.path.join(temp_dir, "solution.py")
        
        with open(code_path, "w") as f:
            f.write(code)
        
        # This builds the actual `docker run` command as a list of
        # arguments — same as typing it in a terminal, but as a list
        # so subprocess can run it directly without shell parsing issues.
        docker_command = [
            "docker", "run",
            "--rm",                          # auto-delete container when done
            "--network", "none",             # no internet access at all
            "--memory", "256m",              # hard memory cap
            "--cpus", "0.5",                 # hard CPU cap
            "-v", f"{temp_dir}:/sandbox",     # mount our temp folder INTO the container at /sandbox
            "-w", "/sandbox",                # set working directory inside container to /sandbox
            "python:3.11-slim",              # the image to use
            "python", "solution.py"          # the command to run INSIDE the container
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