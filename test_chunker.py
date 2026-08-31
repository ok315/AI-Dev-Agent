from src.tools.code_chunker import chunk_python_file

# A small sample with imports, functions, and a class —
# mirrors the auth example we discussed
sample_code = '''
import jwt
from datetime import datetime, timedelta
from typing import Optional

SECRET = "test-secret"

def hash_password(password: str) -> str:
    """Hashes a plaintext password."""
    import bcrypt
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def authenticate_user(username: str, password: str) -> Optional[dict]:
    """Checks credentials and returns the user if valid."""
    user = {"username": username}
    return user

class TokenValidator:
    """Validates incoming JWTs on protected routes."""
    
    def __init__(self, secret: str):
        self.secret = secret
    
    def validate(self, token: str) -> dict:
        """Decodes and verifies a JWT."""
        return jwt.decode(token, self.secret, algorithms=["HS256"])
'''

chunks = chunk_python_file(sample_code, "src/auth/handlers.py")

print(f"Found {len(chunks)} chunks\n")

for chunk in chunks:
    print(f"Name: {chunk['name']}")
    print(f"Type: {chunk['type']}")
    print(f"Lines: {chunk['start_line']}-{chunk['end_line']}")
    print(f"Imports: {chunk['imports']}")
    print(f"Code:\n{chunk['code']}")
    print("-" * 60)