import re
from typing import List, Optional

from google.adk.tools.tool_context import ToolContext
from vertexai import rag

from utils import get_corpus_resource_name, check_corpus_exists
from ..config import (
    DEFAULT_CHUNK_SIZE,
    DEFAULT_CHUNK_OVERLAP,
    DEFAULT_EMBEDDING_REQUEST_PER_MIN)

def add_data(corpus_name:str,paths:List[str] ,tool_context:ToolContext) -> dict:
    """
    Add new data sources to the rag corpus specified by the corpus_name.
    Args:
        corpus_name (str): The name of the corpus to which data will be added.
        path (List[str]): List of paths to the data files to be added.
        tool_context (ToolContext): The tool context required by the session and for state management.
    Returns:
        A dictionary providing the status of the data addition.
    """
    if not check_corpus_exists(corpus_name, tool_context):
        return {
            "status": "Error",
            "message": f"Corpus '{corpus_name}' does not exist.",
            "data-added": False,
            "corpus-name": corpus_name,
        }
    
    if  not paths or not all(isinstance(path,str) for path in paths):
        return {
            "status": "Error",
            "message": "Invalid or empty paths provided.",
            "data-added": False,
            "corpus-name": corpus_name,
        }
    validated_paths =[]
    invalid_paths = []
    conversions = []
    
    for path in paths:
        if not path or not isinstance(path, str):
            invalid_paths.append(path)
            continue
        
        docs_match = re.match(
            r"https:\/\/docs\.google\.com\/(?:document|spreadsheets|presentation)\/d\/([a-zA-Z0-9_-]+)(?:\/|$)",
            path,
        )
        if docs_match:
            file_id = docs_match.group(1)
            drive_url = f"https://drive.google.com/file/d/{file_id}/view"
            validated_paths.append(drive_url)
            conversions.append(f"{path} → {drive_url}")
            continue
        
        drive_match = re.match(
            r"https:\/\/drive\.google\.com\/(?:file\/d\/|open\?id=)([a-zA-Z0-9_-]+)(?:\/|$)",
            path,
        )
        if drive_match:
            file_id = drive_match.group(1)
            drive_url = f"https://drive.google.com/file/d/{file_id}/view"
            validated_paths.append(drive_url)
            if drive_url != path:
                conversions.append(f"{path} → {drive_url}")
            continue

        if path.startswith("gs://"):
            validated_paths.append(path)
            continue

        invalid_paths.append(f"{path} (Invalid format)")

    if not validated_paths:
        return {
            "status": "error",
            "message": "No valid paths provided. Please provide Google Drive URLs or GCS paths.",
            "corpus_name": corpus_name,
            "invalid_paths": invalid_paths,
        }
        
