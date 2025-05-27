from vertexai import rag

def list_corposa()-> dict:
    """
    List all available corpora in the Vertex AI RAG system.
    
    Args:
        None
    
    Returns:
        dict: A dictionary containing the status of corpora with each corpus containing:
            - corpus_name: The name of the corpus
            - display_name: The human readable name of the corpus
            - create_time: Time of creation of the corpus
            - update_time: Time of last update of the corpus    
    """
    try:
        corpora = rag.list_corpora()
        
        corpus_info = []
        for corpus in corpora:
            corpus_info.append({
                "corpus_name": corpus.name,
                "display_name": corpus.display_name,
                "create_time": corpus.create_time if hasattr(corpus, "create_time") else "",
                "update_time": corpus.update_time if hasattr(corpus, "update_time") else "",
            })    
        return {
            "status": "Success",
            "message": "List of corpora retrieved successfully.",
            "num-of-corpus": len(corpus_info),
            "corpora": corpus_info,
        }
    except Exception as e:
        return {
            "status": "Error",
            "message": f"Failed to list corpora: {str(e)}",
            "num-of-corpus": 0,
            "corpora": [],
        }