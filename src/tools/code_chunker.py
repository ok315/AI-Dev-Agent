import ast
from typing import List, Dict


def extract_imports(tree: ast.Module) -> List[str]:
    """
    Walks the top level of the file's AST and collects every
    import statement as a plain string.
    
    We only look at tree.body (top-level nodes), not ast.walk(),
    because imports inside functions (rare, but possible) belong
    to that function's own context, not the whole file.
    
    ast.unparse() converts an AST node back into source code —
    it's the reverse of ast.parse(). Available in Python 3.9+.
    """
    imports = []
    for node in tree.body:
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            imports.append(ast.unparse(node))
    return imports


def chunk_python_file(source_code: str, file_path: str) -> List[Dict]:
    """
    Parses a Python file and returns one chunk per top-level
    function or class definition.
    
    Each chunk contains:
      - the exact source code of that function/class (this is
        the only part that gets embedded later)
      - metadata: name, type, file path, line numbers, and the
        file's imports (not embedded, just carried along)
    
    Args:
        source_code: the full text content of a .py file
        file_path: where this file lives in the repo, e.g. "src/auth/handlers.py"
                   (needed so retrieval results can point back to a real location)
    
    Returns:
        list of chunk dicts, or [] if the file has a syntax error
        or contains no functions/classes
    """
    try:
        tree = ast.parse(source_code)
    except SyntaxError:
        # Some files might not parse — e.g. Python 2 code, or
        # files with intentional syntax errors during testing.
        # We skip them rather than crashing the whole pipeline.
        return []
    
    imports = extract_imports(tree)
    
    # Split source into lines once, so we can slice by line number
    # for every chunk without re-splitting each time.
    source_lines = source_code.splitlines()
    
    chunks = []
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            start = node.lineno - 1        # AST line numbers are 1-indexed, lists are 0-indexed
            end = node.end_lineno          # end_lineno is already the correct exclusive-safe boundary
            
            code = "\n".join(source_lines[start:end])
            
            chunks.append({
                "name": node.name,
                "type": "class" if isinstance(node, ast.ClassDef) else "function",
                "code": code,
                "file_path": file_path,
                "start_line": node.lineno,
                "end_line": node.end_lineno,
                "imports": imports
            })
    
    return chunks