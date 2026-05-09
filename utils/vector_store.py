"""
utils/vector_store.py — ChromaDB ingestion and retrieval for QueryWise.
"""

import chromadb
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction

EMBEDDING_MODEL = "all-MiniLM-L6-v2"


def build_collection(table_info: list[str], collection_name: str):
    """
    (Re)build a ChromaDB in-memory collection from the provided schema strings.
    Returns the collection object.
    """
    embedding_fn = SentenceTransformerEmbeddingFunction(model_name=EMBEDDING_MODEL)
    client = chromadb.EphemeralClient()

    try:
        client.delete_collection(name=collection_name)
    except Exception:
        pass

    collection = client.get_or_create_collection(
        name=collection_name,
        embedding_function=embedding_fn,
    )

    ids = [f"id{i + 1}" for i in range(len(table_info))]
    collection.add(ids=ids, documents=table_info)
    return collection


def query_collection(collection, user_query: str, n_results: int = 4) -> str:
    """
    Query the collection for the most relevant schema chunks.
    Returns them joined as a single context string.
    """
    result = collection.query(query_texts=[user_query], n_results=min(n_results, collection.count()))
    return "\n\n".join(result["documents"][0])
