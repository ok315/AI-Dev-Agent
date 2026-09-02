from src.tools.sandbox import run_code_in_sandbox

# Test: two files, one imports the other
files = {
    "solution.py": "def add(a, b):\n    return a + b\n",
    "test_solution.py": "from solution import add\nassert add(2, 3) == 5\nprint('Test passed!')\n"
}

result = run_code_in_sandbox(files, entry_point="test_solution.py")
print(result)