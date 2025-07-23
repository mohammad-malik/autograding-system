import json
from typing import Dict, List, Optional, Tuple, Any

import pinecone
from langchain_text_splitters import RecursiveCharacterTextSplitter
from dotenv import load_dotenv

load_dotenv()

from ..config import get_settings
from .llm_client import LLMClient

# Initialize Pinecone
pinecone.init(
    api_key=get_settings().pinecone_api_key,
    environment=get_settings().pinecone_environment,
)


class PineconeClient:
    """Client for Pinecone vector database."""

    @staticmethod
    def get_index():
        """Get Pinecone index."""
        index_name = get_settings().pinecone_index
        if index_name not in pinecone.list_indexes():
            pinecone.create_index(
                name=index_name,
                dimension=1536,  # OpenAI embedding dimension
                metric="cosine",
            )
        return pinecone.Index(index_name)

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