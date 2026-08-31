import chromadb
from chromadb.utils import embedding_functions
from typing import List, Dict

# Initialize once, at module load time — not inside a function.
# This means every part of your code that imports `vector_store`
# shares the same DB connection and same embedding model, instead
# of reloading the model from disk every time you call a function.

# persist_directory means data is saved to disk, not just kept
# in memory — so your index survives between separate script runs.
client = chromadb.PersistentClient(path="./chroma_db")

# This tells ChromaDB to use sentence-transformers locally to
# convert text into vectors, instead of calling an external API.
embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="all-MiniLM-L6-v2"
)

# get_or_create_collection: if "codebase" collection already exists
# (from a previous run), reuse it. Otherwise, create it fresh.
collection = client.get_or_create_collection(
    name="codebase",
    embedding_function=embedding_fn
)


def store_chunks(chunks: List[Dict], repo_name: str) -> int:
    """
    Takes chunks from code_chunker.py and stores them in ChromaDB.
    
    Args:
        chunks: list of chunk dicts from chunk_python_file()
        repo_name: which repo these chunks belong to — needed because
                   later you might index multiple repos into the same
                   collection, and you'll want to filter by repo
    
    Returns:
        number of chunks stored
    """
    if not chunks:
        return 0
    
    documents = []
    metadatas = []
    ids = []
    
    for chunk in chunks:
        documents.append(chunk["code"])
        
        metadatas.append({
            "name": chunk["name"],
            "type": chunk["type"],
            "file_path": chunk["file_path"],
            "start_line": chunk["start_line"],
            "end_line": chunk["end_line"],
            "imports": "; ".join(chunk["imports"]),
            "repo": repo_name
        })
        
        # Unique ID: repo + file + name, so the same function name
        # in different files (or different repos) doesn't collide
        ids.append(f"{repo_name}::{chunk['file_path']}::{chunk['name']}")
    
    collection.add(
        documents=documents,
        metadatas=metadatas,
        ids=ids
    )
    
    return len(documents)