import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    GROQ_API_KEY: str = os.environ.get("GROQ_API_KEY", "")
    GITHUB_TOKEN: str = os.environ.get("GITHUB_TOKEN", "")
    
    # GitHub API base URL — all GitHub API calls go through this
    GITHUB_API_BASE: str = "https://api.github.com"
    
    # The model we'll use for all LLM calls
    LLM_MODEL: str = "llama-3.3-70b-versatile"
    
    # Safety limits
    MAX_DEBUG_ITERATIONS: int = 3    # max times the debug loop can retry
    MAX_FILE_SIZE_KB: int = 100      # don't read files larger than this
    MAX_REPO_FILES: int = 50         # don't process repos with more files

config = Config()