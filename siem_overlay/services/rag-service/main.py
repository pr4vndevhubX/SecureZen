"""
RAG Service - FastAPI Application
AI-Augmented SOC

FIXED: Exact MITRE ID lookup now uses ChromaDB's get() method
"""

import logging
import os
import re
from contextlib import asynccontextmanager
from typing import List, Dict, Any, Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from vector_store import VectorStore
from embeddings import EmbeddingEngine
from knowledge_base import KnowledgeBaseManager

# -------------------------------------------------------------------
# Logging
# -------------------------------------------------------------------

logging.basicConfig(
    level="INFO",
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# -------------------------------------------------------------------
# Globals
# -------------------------------------------------------------------

vector_store: VectorStore = None
embedding_engine: EmbeddingEngine = None
kb_manager: KnowledgeBaseManager = None

# MITRE ID Pattern: T1110 or T1110.003
MITRE_ID_REGEX = re.compile(r"^T\d{4}(\.\d{3})?$", re.IGNORECASE)

# -------------------------------------------------------------------
# App Lifecycle
# -------------------------------------------------------------------

@asynccontextmanager
async def lifespan(app: FastAPI):
    global vector_store, embedding_engine, kb_manager

    logger.info("=" * 60)
    logger.info("Starting RAG Service (PRODUCTION)")
    logger.info("=" * 60)

    # Initialize embedding engine
    embedding_engine = EmbeddingEngine()
    logger.info("[YES] Embedding engine loaded")

    # Connect to ChromaDB
    chromadb_host = os.getenv("RAG_CHROMADB_HOST", "chromadb")
    chromadb_port = int(os.getenv("RAG_CHROMADB_PORT", "8000"))

    vector_store = VectorStore(
        embedding_engine,
        host=chromadb_host,
        port=chromadb_port
    )
    logger.info(f"[YES] Connected to ChromaDB at {chromadb_host}:{chromadb_port}")

    # Initialize knowledge base manager
    kb_manager = KnowledgeBaseManager(vector_store)
    logger.info("[YES] Knowledge base manager ready")

    logger.info("=" * 60)
    logger.info("RAG Service initialization complete")
    logger.info("=" * 60)
    
    yield
    
    logger.info("Shutting down RAG Service")


app = FastAPI(
    title="RAG Service - AI SOC",
    description="Retrieval-Augmented Generation for security knowledge with hybrid MITRE search",
    version="2.0.0",
    lifespan=lifespan
)

# -------------------------------------------------------------------
# Models
# -------------------------------------------------------------------

class RetrievalRequest(BaseModel):
    query: str = Field(..., min_length=1, description="Search query (MITRE ID or free text)")
    collection: str = Field("mitre_attack", description="Knowledge base collection")
    top_k: int = Field(5, ge=1, le=20, description="Number of results to return")
    min_similarity: float = Field(0.3, ge=0.0, le=1.0, description="Minimum similarity threshold")


class RetrievalResult(BaseModel):
    document: str
    metadata: Dict[str, Any]
    similarity_score: float


class RetrievalResponse(BaseModel):
    query: str
    results: List[RetrievalResult]
    total_results: int
    retrieval_mode: str = Field(description="exact or semantic")


class IngestDocument(BaseModel):
    text: str
    metadata: Optional[Dict[str, Any]] = None
    id: Optional[str] = None


class IngestRequest(BaseModel):
    collection: str
    documents: List[IngestDocument]

# -------------------------------------------------------------------
# Health
# -------------------------------------------------------------------

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "rag-service",
        "version": "2.0.0",
        "chromadb_connected": vector_store.is_connected() if vector_store else False,
        "features": ["hybrid_retrieval", "mitre_official", "sub_techniques"]
    }

# -------------------------------------------------------------------
# [OK] HYBRID RETRIEVAL ENDPOINT (FIXED)
# -------------------------------------------------------------------

@app.post("/retrieve", response_model=RetrievalResponse)
async def retrieve_context(request: RetrievalRequest):
    """
    Hybrid retrieval with intelligent routing:
    
    1. EXACT MODE (MITRE IDs):
       - Input: T1110, T1110.003
       - Returns: Exact ID match via ChromaDB get()
       - Score: 1.0 (perfect match)
    
    2. SEMANTIC MODE (Free text):
       - Input: "PowerShell lateral movement", "SSH brute force"
       - Returns: Top-k similar techniques via embeddings
       - Score: Cosine similarity (0.0 - 1.0)
    """
    
    try:
        query = request.query.strip()
        
        logger.info(
            f"Retrieval request: query='{query}', "
            f"collection={request.collection}, top_k={request.top_k}"
        )
        
        # ================================================================
        # CASE 1: EXACT MITRE ID LOOKUP (FIXED)
        # ================================================================
        mitre_match = MITRE_ID_REGEX.match(query.upper())
        
        if mitre_match and request.collection == "mitre_attack":
            technique_id = mitre_match.group(0).upper()
            
            logger.info(f"? EXACT MODE: Looking up MITRE ID '{technique_id}'")
            
            try:
                # Direct ChromaDB lookup by ID
                collection = vector_store.client.get_collection(name="mitre_attack")
                
                result = collection.get(
                    ids=[technique_id],
                    include=["documents", "metadatas"]
                )
                
                results = []
                
                # Check if we got a match
                if result and result['ids'] and len(result['ids']) > 0:
                    for doc, meta in zip(result['documents'], result['metadatas']):
                        results.append(
                            RetrievalResult(
                                document=doc,
                                metadata=meta,
                                similarity_score=1.0  # Perfect match
                            )
                        )
                    
                    logger.info(f"[YES] Found exact match for {technique_id}")
                    return RetrievalResponse(
                        query=query,
                        results=results,
                        total_results=len(results),
                        retrieval_mode="exact"
                    )
                else:
                    logger.warning(f"No exact match found for {technique_id}, falling back to semantic search")
                    
            except Exception as e:
                logger.error(f"Exact lookup failed: {e}, falling back to semantic search")
        
        # ================================================================
        # CASE 2: SEMANTIC SEARCH
        # ================================================================
        logger.info(f"[BRAIN] SEMANTIC MODE: Embedding query and searching...")
        
        semantic_results = await vector_store.query(
            collection_name=request.collection,
            query_text=query,
            top_k=request.top_k,
            min_similarity=request.min_similarity
        )
        
        results = [
            RetrievalResult(
                document=r["document"],
                metadata=r["metadata"],
                similarity_score=r["similarity_score"]
            )
            for r in semantic_results
        ]
        
        logger.info(f"[YES] Semantic search returned {len(results)} results")
        
        return RetrievalResponse(
            query=query,
            results=results,
            total_results=len(results),
            retrieval_mode="semantic"
        )
    
    except Exception as e:
        logger.error(f"[ERR] Retrieval failed: {e}")
        logger.exception(e)
        raise HTTPException(
            status_code=500,
            detail=f"Retrieval error: {str(e)}"
        )

# -------------------------------------------------------------------
# Ingestion
# -------------------------------------------------------------------

@app.post("/ingest")
async def ingest_documents(request: IngestRequest):
    """Generic document ingestion endpoint"""
    try:
        logger.info(f"Ingesting {len(request.documents)} documents into {request.collection}")
        
        # Create collection if needed
        vector_store.create_collection(request.collection)
        
        texts = [doc.text for doc in request.documents]
        metadatas = [doc.metadata or {} for doc in request.documents]
        ids = [doc.id for doc in request.documents if doc.id]
        
        success = await vector_store.add_documents(
            collection_name=request.collection,
            documents=texts,
            metadatas=metadatas,
            ids=ids if ids else None
        )
        
        if not success:
            raise HTTPException(status_code=500, detail="Document ingestion failed")
        
        return {
            "status": "success",
            "documents_added": len(request.documents),
            "collection": request.collection
        }
    
    except Exception as e:
        logger.error(f"Ingestion error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# -------------------------------------------------------------------
# Collections Management
# -------------------------------------------------------------------

@app.get("/collections")
async def list_collections():
    """List all available knowledge base collections"""
    collections_list = [
        "mitre_attack",
        "cve_database",
        "incident_history",
        "security_runbooks"
    ]
    
    output = []
    
    for name in collections_list:
        stats = vector_store.get_collection_stats(name)
        output.append({
            "name": name,
            "document_count": stats.get("count", 0),
            "metadata": stats.get("metadata", {}),
            "status": "active" if stats.get("count", 0) > 0 else "empty"
        })
    
    return {
        "collections": output,
        "total_collections": len([c for c in output if c["status"] == "active"])
    }

@app.delete("/collections/{collection_name}")
async def delete_collection(collection_name: str):
    """Delete a knowledge base collection"""
    try:
        vector_store.delete_collection(collection_name)
        return {
            "status": "success",
            "message": f"Collection '{collection_name}' deleted"
        }
    except Exception as e:
        logger.error(f"Failed to delete collection {collection_name}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# -------------------------------------------------------------------
# MITRE ATT&CK Ingestion (Official)
# -------------------------------------------------------------------

@app.post("/ingest/mitre")
async def ingest_mitre_attack():
    """
    Ingest official MITRE ATT&CK Enterprise framework.
    
    Downloads latest data from GitHub and ingests:
    - Main techniques (T1110)
    - Sub-techniques (T1110.003)
    - Tactics, platforms, data sources
    - Version metadata
    
    Returns:
        Ingestion statistics and status
    """
    logger.info("[INPUT] MITRE ATT&CK ingestion requested")
    
    result = await kb_manager.ingest_mitre_attack(
        data_path="data/enterprise-attack.json"
    )
    
    if result["status"] == "error":
        raise HTTPException(status_code=500, detail=result["message"])
    
    return result

@app.post("/refresh/mitre")
async def refresh_mitre_attack():
    """
    Refresh MITRE ATT&CK database by downloading latest version.
    
    This will:
    1. Download latest enterprise-attack.json from GitHub
    2. Delete existing mitre_attack collection
    3. Re-ingest all techniques
    
    Returns:
        Refresh statistics
    """
    logger.info("? MITRE ATT&CK refresh requested")
    
    try:
        # Delete old collection
        try:
            vector_store.delete_collection("mitre_attack")
            logger.info("[YES] Deleted old MITRE collection")
        except:
            pass
        
        # Re-ingest with fresh download
        result = await kb_manager.ingest_mitre_attack(data_path=None)
        
        if result["status"] == "error":
            raise HTTPException(status_code=500, detail=result["message"])
        
        return {
            **result,
            "refreshed": True,
            "message": "MITRE ATT&CK database refreshed successfully"
        }
    
    except Exception as e:
        logger.error(f"Refresh failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# -------------------------------------------------------------------
# Statistics & Monitoring
# -------------------------------------------------------------------

@app.get("/stats/mitre")
async def get_mitre_stats():
    """Get MITRE ATT&CK collection statistics"""
    stats = vector_store.get_collection_stats("mitre_attack")
    
    return {
        "collection": "mitre_attack",
        "total_techniques": stats.get("count", 0),
        "metadata": stats.get("metadata", {}),
        "status": "ready" if stats.get("count", 0) > 0 else "empty"
    }

# -------------------------------------------------------------------
# Root
# -------------------------------------------------------------------

@app.get("/")
async def root():
    """Service information endpoint"""
    return {
        "service": "rag-service",
        "status": "production",
        "version": "2.0.0",
        "features": {
            "hybrid_retrieval": True,
            "mitre_official": True,
            "sub_techniques": True,
            "version_tracking": True,
            "exact_id_lookup": True
        },
        "endpoints": {
            "retrieval": "/retrieve",
            "ingest_mitre": "/ingest/mitre",
            "refresh_mitre": "/refresh/mitre",
            "collections": "/collections",
            "stats": "/stats/mitre",
            "health": "/health"
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8001,
        reload=True,
        log_level="info"
    )