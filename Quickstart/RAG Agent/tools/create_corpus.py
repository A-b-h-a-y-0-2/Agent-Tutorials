import re
from ..config import (
    DEFAULT_EMBEDDING_MODEL
)
from vertexai import rag
from google.adk.tools.tool_context import ToolContext
from utils import check_corpus_exists
def create_corpus(corpus_name:str, tool_context: ToolContext)-> dict:
    """
    Create a new corpus with the specified name and based on Vertex AI RAG capabilities.

    Args:
        corpus_name (str): name of the new corpus
        tool_context (ToolContext): the tool context required by the session and for state management
        
    Returns:
        Dict: A dictionary providing the status of the corpus creation.
    """
    if check_corpus_exists(corpus_name, tool_context):
        return {
            "status": "Error",
            "message": f"Corpus '{corpus_name}' already exists."
            ,"corpus-created": False,
            "corpus-name": corpus_name,
        }
    try:
        display_name = re.sub(r"[^a-zA-Z0-9_-]","_", corpus_name)
        embedding_model_config = rag.RagEmbeddingModelConfig(
            vertex_prediction_endpoint = rag.VertexPredictionEndpoint(
                publisher= DEFAULT_EMBEDDING_MODEL
            )
        )
        
        rag_corpus = rag.create_corpus(
            display_name = display_name,
            backend_config = rag.RagVectorDbConfig(
                rag_embedding_model_config=embedding_model_config
            ),
        )
        
        tool_context.state["corpus_exists_{corpus_name}"] = True
        
        tool_context.state["current_corpus"] = corpus_name
        
        return {
            "status": "Success",
            "message": f"Corpus {corpus_name} successfully created.",
            "corpus-created": True,
            "display_name": display_name,
            "corpus-name": corpus_name,  
        }
    except Exception as e: 
        return {
            "status": "Error",
            "message": f"Failed to create corpus '{corpus_name}': {str(e)}",
            "corpus-created": False,
            "corpus-name": corpus_name,
        }