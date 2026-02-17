"""
Vector Store - RAG Service
AI-Augmented SOC

ChromaDB interface for semantic search and document storage.
Manages collections, embeddings, similarity search, and exact metadata lookup.
"""

import logging
from typing import List, Dict, Any, Optional
import chromadb
from chromadb.config import Settings

logger = logging.getLogger(__name__)


class VectorStore:
    """
    ChromaDB vector database interface.

    Manages:
    - Collection creation and management
    - Document ingestion with embeddings
    - Semantic search queries
    - Deterministic metadata-based retrieval (for MITRE IDs)
    """

    def __init__(self, embedding_engine, host: str = "chromadb", port: int = 8000):
        self.embedding_engine = embedding_engine
        self.host = host
        self.port = port
        self.client = None  # Lazy init

        logger.info(f"VectorStore configured for {host}:{port} (lazy connection)")

    # ------------------------------------------------------------------
    # Connection Management
    # ------------------------------------------------------------------

    def get_client(self):
        if self.client is None:
            try:
                self.client = chromadb.HttpClient(
                    host=self.host,
                    port=self.port,
                    settings=Settings(anonymized_telemetry=False)
                )
                self.client.heartbeat()
                logger.info(f"[OK] Connected to ChromaDB at {self.host}:{self.port}")
            except Exception as e:
                logger.warning(f"ChromaDB not ready: {e}")
                return None
        return self.client

    def is_connected(self) -> bool:
        try:
            client = self.get_client()
            if client:
                return client.heartbeat() > 0
            return False
        except Exception as e:
            logger.error(f"ChromaDB connection check failed: {e}")
            self.client = None
            return False

    # ------------------------------------------------------------------
    # Collection Management
    # ------------------------------------------------------------------

    def create_collection(
        self,
        name: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        try:
            client = self.get_client()
            if not client:
                return False

            try:
                client.get_collection(name=name)
                logger.info(f"Collection {name} already exists")
                return True
            except:
                client.create_collection(
                    name=name,
                    metadata=metadata or {"source": "rag-service"}
                )
                logger.info(f"Successfully created collection: {name}")
                return True

        except Exception as e:
            logger.error(f"Failed to create collection {name}: {e}")
            return False

    # ------------------------------------------------------------------
    # Document Ingestion
    # ------------------------------------------------------------------

    async def add_documents(
        self,
        collection_name: str,
        documents: List[str],
        metadatas: Optional[List[Dict[str, Any]]] = None,
        ids: Optional[List[str]] = None,
        embeddings: Optional[List[List[float]]] = None
    ) -> bool:
        try:
            client = self.get_client()
            if not client:
                return False

            collection = client.get_collection(collection_name)

            if ids is None:
                ids = [f"doc_{i}_{hash(doc[:50])}" for i, doc in enumerate(documents)]

            if embeddings is None:
                embeddings = self.embedding_engine.embed_batch(documents)
                if not isinstance(embeddings, list):
                    embeddings = embeddings.tolist()

            collection.add(
                documents=documents,
                embeddings=embeddings,
                metadatas=metadatas or [{} for _ in documents],
                ids=ids
            )

            logger.info(f"Added {len(documents)} documents to {collection_name}")
            return True

        except Exception as e:
            logger.error(f"Failed to add documents: {e}")
            logger.exception(e)
            return False

    # ------------------------------------------------------------------
    # Semantic Search (FREE-TEXT ONLY)
    # ------------------------------------------------------------------

    async def query(
        self,
        collection_name: str,
        query_text: str,
        top_k: int = 3,
        min_similarity: float = 0.7,
        metadata_filter: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        try:
            client = self.get_client()
            if not client:
                return []

            collection = client.get_collection(collection_name)

            query_embedding = self.embedding_engine.embed_text(query_text)

            results = collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k,
                where=metadata_filter
            )

            if not results.get("documents") or not results["documents"][0]:
                return []

            filtered_results = []

            for doc, meta, distance in zip(
                results["documents"][0],
                results["metadatas"][0],
                results["distances"][0]
            ):
                similarity = 1 - (distance / 2)
                if similarity >= min_similarity:
                    filtered_results.append({
                        "document": doc,
                        "metadata": meta,
                        "similarity_score": float(similarity)
                    })

            return filtered_results

        except Exception as e:
            logger.error(f"Query failed: {e}")
            logger.exception(e)
            return []

    # ------------------------------------------------------------------
    # [OK] EXACT METADATA LOOKUP (MITRE IDs)
    # ------------------------------------------------------------------

    def get_by_metadata(
        self,
        collection_name: str,
        metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Deterministic retrieval by metadata.
        Used for exact MITRE technique ID lookups (e.g., T1110).

        NO embeddings. NO similarity search.
        """
        client = self.get_client()
        if not client:
            raise RuntimeError("ChromaDB client not initialized")

        collection = client.get_collection(collection_name)
        return collection.get(where=metadata)

    # ------------------------------------------------------------------
    # Collection Utilities
    # ------------------------------------------------------------------

    def get_collection_stats(self, collection_name: str) -> Dict[str, Any]:
        try:
            client = self.get_client()
            if not client:
                return {"count": 0, "status": "not_connected"}

            collection = client.get_collection(collection_name)
            return {
                "name": collection_name,
                "count": collection.count(),
                "metadata": collection.metadata
            }
        except Exception as e:
            logger.error(f"Failed to get stats for {collection_name}: {e}")
            return {"count": 0, "error": str(e)}

    def delete_collection(self, collection_name: str) -> bool:
        try:
            client = self.get_client()
            if not client:
                return False

            client.delete_collection(collection_name)
            logger.info(f"Deleted collection: {collection_name}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete collection {collection_name}: {e}")
            return False

# TODO: Week 5 - Add advanced filtering
# class AdvancedVectorStore(VectorStore):
#     """Extended vector store with hybrid search"""
#
#     async def hybrid_search(
#         self,
#         collection_name: str,
#         query_text: str,
#         keyword_boost: float = 0.3
#     ) -> List[Dict[str, Any]]:
#         """Combine semantic search with keyword matching"""
#         pass