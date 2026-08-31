from src.tools.code_chunker import chunk_python_file
from src.tools.vector_store import store_chunks, collection

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

# Step 1: chunk it (same as before)
chunks = chunk_python_file(sample_code, "src/auth/handlers.py")
print(f"Chunked into {len(chunks)} pieces")

# Step 2: store in ChromaDB
count = store_chunks(chunks, repo_name="test-repo")
print(f"Stored {count} chunks in ChromaDB\n")

# Step 3: query with a natural language question
query = "find the function that handles user authentication"
results = collection.query(
    query_texts=[query],
    n_results=2
)

print(f"Query: '{query}'")
print(f"Top {len(results['ids'][0])} results:\n")

for i in range(len(results["ids"][0])):
    print(f"Match {i+1}: {results['metadatas'][0][i]['name']}")
    print(f"  File: {results['metadatas'][0][i]['file_path']}")
    print(f"  Lines: {results['metadatas'][0][i]['start_line']}-{results['metadatas'][0][i]['end_line']}")
    print(f"  Distance: {results['distances'][0][i]:.4f}")  # lower = more similar
    print()