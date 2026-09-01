from src.tools.github_client import github
from src.core.config import config
from src.tools.code_chunker import chunk_python_file
from src.tools.vector_store import store_chunks
from src.tools.vector_store import collection

def get_python_files(owner: str, repo: str, branch: str) -> list[dict]:
    """
    Gets all Python files in a repo, filtered from the full file list.
    
    We reuse github.get_repo_structure() (Week 1) which already
    excludes junk like __pycache__/, node_modules/, etc. Here we
    add two more filters:
      1. Only .py files, since our chunker only understands Python
      2. Skip files over MAX_FILE_SIZE_KB — using the size info
         get_repo_structure() already gave us for free, so we
         never waste an API call downloading a file we're just
         going to discard.
    
    Returns: list of dicts like {"path": ..., "size": ..., "type": "file"}
             but only for .py files under the size limit
    """
    all_files = github.get_repo_structure(owner, repo, branch=branch)
    
    max_size_bytes = config.MAX_FILE_SIZE_KB * 1024  # size in repo data is in bytes
    
    python_files = []
    skipped_large = 0
    
    for f in all_files:
        if not f["path"].endswith(".py"):
            continue
        
        if f["size"] > max_size_bytes:
            skipped_large += 1
            print(f"  Skipping {f['path']} — {f['size'] / 1024:.1f}KB exceeds limit")
            continue
        
        python_files.append(f)
    
    print(f"Found {len(all_files)} total files, {len(python_files)} Python files kept, {skipped_large} skipped for size")
    
    return python_files


def index_repository(owner: str, repo: str) -> dict:
    """
    The main entry point for this agent. Given a repo, this:
      1. Gets repo info (to find the default branch)
      2. Gets the filtered list of Python files
      3. For each file: fetches content, chunks it, stores it
    
    Returns a summary dict so the caller knows what happened —
    useful for logging, and later for showing the user/agent
    "here's what got indexed."
    """
    repo_info = github.get_repo_info(owner, repo)
    branch = repo_info["default_branch"]
    
    python_files = get_python_files(owner, repo, branch)
    
    total_chunks = 0
    files_processed = 0
    files_failed = 0
    
    for file_info in python_files:
        path = file_info["path"]
        
        try:
            content = github.get_file_content(owner, repo, path, branch=branch)
            chunks = chunk_python_file(content, path)
            
            if chunks:
                count = store_chunks(chunks, repo_name=repo)
                total_chunks += count
                print(f"  {path}: {count} chunks stored")
            else:
                print(f"  {path}: no functions/classes found")
            
            files_processed += 1
        
        except Exception as e:
            print(f"  {path}: FAILED — {e}")
            files_failed += 1
    
    summary = {
        "repo": repo,
        "files_processed": files_processed,
        "files_failed": files_failed,
        "total_chunks_stored": total_chunks
    }
    
    print(f"\nDone. Processed {files_processed} files, {files_failed} failed, {total_chunks} total chunks stored.")
    
    return summary

def ask_codebase(question: str, repo: str, n_results: int = 3) -> list[dict]:
    """
    Queries the indexed codebase with a natural language question.
    
    This is the main interface other agents will use — they don't
    need to know about ChromaDB, embeddings, or distances. They just
    ask a question about a specific repo and get back the most
    relevant chunks of code.
    
    Args:
        question: natural language question, e.g. "where is error handling done?"
        repo: which repo to search within (since one collection can hold multiple repos)
        n_results: how many matches to return, default 3
    
    Returns: list of dicts, each with the code, file location, and how
             relevant it was — sorted best match first
    """
    results = collection.query(
        query_texts=[question],
        n_results=n_results,
        where={"repo": repo}  # only search chunks from this specific repo
    )
    
    matches = []
    for i in range(len(results["ids"][0])):
        metadata = results["metadatas"][0][i]
        matches.append({
            "name": metadata["name"],
            "type": metadata["type"],
            "file_path": metadata["file_path"],
            "start_line": metadata["start_line"],
            "end_line": metadata["end_line"],
            "code": results["documents"][0][i],
            "distance": results["distances"][0][i]
        })
    
    return matches