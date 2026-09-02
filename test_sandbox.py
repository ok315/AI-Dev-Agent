from src.tools.sandbox import run_code_in_sandbox

# Test 1: normal code that should succeed
result = run_code_in_sandbox("print('Hello from inside the sandbox')")
print("Test 1 — normal code:")
print(result)

# Test 2: code that crashes, to verify we correctly capture failure
result = run_code_in_sandbox("print(1 / 0)")
print("\nTest 2 — code that crashes:")
print(result)

# Test 3: infinite loop, to verify the timeout actually works
result = run_code_in_sandbox("while True: pass", timeout_seconds=5)
print("\nTest 3 — infinite loop (should time out after ~5 seconds):")
print(result)