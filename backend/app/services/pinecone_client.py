import json
from typing import Dict, List, Optional, Tuple, Any

# -----------------------------------------------------------------------------
# Pinecone Python SDK v3+ (>=2024-xx) no longer exposes a top-level `init` or
# global helpers.  Instead, you create a `Pinecone` client instance and work
# with that.  Importing the class is therefore required **before** any calls
# to list / create / open indexes.
# -----------------------------------------------------------------------------

from pinecone import Pinecone, ServerlessSpec

from langchain_text_splitters import RecursiveCharacterTextSplitter
# from dotenv import load_dotenv  # redundant, config handles env vars

# load_dotenv()  # redundant

from ..config import get_settings
from .llm_client import LLMClient

# -----------------------------------------------------------------------------
# Create a *singleton* Pinecone client so that subsequent calls reuse the
# underlying HTTP session / connection-pool.  We keep the object at module
# level because this file is imported once per interpreter process.
# -----------------------------------------------------------------------------

_pc = Pinecone(api_key=get_settings().pinecone_api_key)

# Optional: if you are still using pod-based indexes or want to specify an
# environment explicitly you can pass `environment=...` when instantiating the
# client.  The serverless flow no longer requires this because the API key is
# already scoped to a project/region.


class PineconeClient:
    """Client for Pinecone vector database."""

    @staticmethod
    def get_index():
        """Get Pinecone index."""
        index_name = get_settings().pinecone_index
        # ------------------------------------------------------------------
        # The new SDK returns a rich object from list_indexes().  We can use
        # the `.names` convenience property for a flat list of names.
        # ------------------------------------------------------------------
        if index_name not in _pc.list_indexes().names:
            # Default to an AWS us-east-1 serverless spec if none supplied.
            # You can control this via env vars PINECONE_CLOUD / REGION later.
            _pc.create_index(
                name=index_name,
                dimension=1536,  # OpenAI embedding dimension
                metric="cosine",
                spec=ServerlessSpec(cloud="aws", region="us-east-1"),
            )
        return _pc.Index(index_name)

    @staticmethod
    async def chunk_text(text: str) -> List[str]:
        """Chunk text into smaller pieces."""
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=100,
            length_function=len,
        )
        return text_splitter.split_text(text)

    @staticmethod
    async def upsert_chunks(
        chunks: List[str], metadata: Dict[str, Any], namespace: str
    ) -> List[str]:
        """Upsert chunks to Pinecone."""
        # Generate embeddings
        embeddings = await LLMClient.generate_embeddings(chunks)

        # Prepare vectors for upsert
        vectors = []
        ids = []
        for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
            chunk_id = f"{metadata['id']}_{i}"
            ids.append(chunk_id)
            vectors.append(
                {
                    "id": chunk_id,
                    "values": embedding,
                    "metadata": {
                        **metadata,
                        "chunk_index": i,
                        "text": chunk,
                    },
                }
            )

        # Upsert to Pinecone
        index = PineconeClient.get_index()
        index.upsert(vectors=vectors, namespace=namespace)

        return ids

    @staticmethod
    async def search(
        query: str, namespace: str, top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """Search for similar vectors."""
        # Generate query embedding
        query_embedding = await LLMClient.generate_embeddings([query])

        # Search in Pinecone
        index = PineconeClient.get_index()
        results = index.query(
            vector=query_embedding[0],
            top_k=top_k,
            namespace=namespace,
            include_metadata=True,
        )

        # Format results
        formatted_results = []
        for match in results["matches"]:
            formatted_results.append(
                {
                    "id": match["id"],
                    "score": match["score"],
                    "metadata": match["metadata"],
                }
            )

        return formatted_results

    @staticmethod
    async def delete_by_ids(ids: List[str], namespace: str) -> None:
        """Delete vectors by IDs."""
        index = PineconeClient.get_index()
        index.delete(ids=ids, namespace=namespace)

    @staticmethod
    async def delete_by_metadata_filter(filter_dict: Dict[str, Any], namespace: str) -> None:
        """Delete vectors by metadata filter."""
        index = PineconeClient.get_index()
        index.delete(filter=filter_dict, namespace=namespace) 