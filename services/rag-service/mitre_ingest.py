"""
MITRE ATT&CK Knowledge Base Ingestion Script
AI-Augmented SOC

Downloads MITRE ATT&CK Enterprise framework and ingests into ChromaDB.
Run this script to populate the RAG knowledge base.

FEATURES:
- Official STIX 2.1 parser
- Sub-technique support (T1110.003)
- Version tracking
- Batch ingestion with progress
- Connection validation
"""

import requests
import json
import logging
import sys
from pathlib import Path

import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# -------------------------------------------------------------------
# Configuration
# -------------------------------------------------------------------

MITRE_URL = "https://raw.githubusercontent.com/mitre/cti/master/enterprise-attack/enterprise-attack.json"
CHROMADB_HOST = "localhost"
CHROMADB_PORT = 8200

# -------------------------------------------------------------------
# MITRE ATT&CK Parser
# -------------------------------------------------------------------

class MitreParser:
    """Official MITRE ATT&CK STIX 2.1 parser"""
    
    @staticmethod
    def parse_techniques(mitre_data: dict) -> list:
        """
        Parse techniques from official MITRE ATT&CK JSON.
        
        Args:
            mitre_data: Raw MITRE ATT&CK JSON
            
        Returns:
            List of parsed technique dictionaries
        """
        techniques = []
        mitre_version = mitre_data.get("spec_version", "unknown")
        
        logger.info(f"Parsing MITRE ATT&CK version: {mitre_version}")
        logger.info(f"Total objects in dataset: {len(mitre_data.get('objects', []))}")
        
        for obj in mitre_data.get('objects', []):
            # Only process attack patterns (techniques)
            if obj.get('type') != 'attack-pattern':
                continue
            
            try:
                # Extract MITRE ATT&CK reference
                external_refs = obj.get('external_references', [])
                mitre_ref = next(
                    (r for r in external_refs if r.get('source_name') == 'mitre-attack'),
                    None
                )
                
                if not mitre_ref:
                    continue
                
                # Get technique ID (T1110 or T1110.003)
                technique_id = mitre_ref.get('external_id', '').strip().upper()
                if not technique_id:
                    continue
                
                # Extract tactics (kill chain phases)
                kill_chain = obj.get('kill_chain_phases', [])
                tactics = [
                    phase.get('phase_name', '').replace('-', '_')
                    for phase in kill_chain
                ]
                
                # Extract platforms
                platforms = obj.get('x_mitre_platforms', [])
                
                # Check if sub-technique
                is_subtechnique = obj.get('x_mitre_is_subtechnique', False)
                
                # Build searchable text
                text = f"""Technique: {technique_id} - {obj.get('name', 'Unknown')}
Tactics: {', '.join(tactics)}
Description: {obj.get('description', '')}
Platforms: {', '.join(platforms)}
""".strip()
                
                # Build metadata
                metadata = {
                    'technique_id': technique_id,
                    'name': obj.get('name', 'Unknown'),
                    'tactic': tactics[0] if tactics else 'unknown',
                    'tactics': json.dumps(tactics),
                    'platforms': json.dumps(platforms),
                    'is_subtechnique': is_subtechnique,
                    'mitre_version': mitre_version,
                    'type': 'mitre_technique'
                }
                
                techniques.append({
                    'id': technique_id,
                    'text': text,
                    'metadata': metadata
                })
                
            except Exception as e:
                logger.warning(f"Failed to parse technique: {e}")
                continue
        
        # Log statistics
        main_techniques = [t for t in techniques if not t['metadata']['is_subtechnique']]
        sub_techniques = [t for t in techniques if t['metadata']['is_subtechnique']]
        
        logger.info(f"Successfully parsed {len(techniques)} techniques:")
        logger.info(f"  - Main techniques: {len(main_techniques)}")
        logger.info(f"  - Sub-techniques: {len(sub_techniques)}")
        
        return techniques

# -------------------------------------------------------------------
# Download Functions
# -------------------------------------------------------------------

def download_mitre_attack() -> dict:
    """
    Download MITRE ATT&CK Enterprise framework from GitHub.
    
    Returns:
        Parsed JSON data
    """
    logger.info("=" * 60)
    logger.info("Downloading MITRE ATT&CK Enterprise Framework")
    logger.info("=" * 60)
    logger.info(f"Source: {MITRE_URL}")
    
    try:
        response = requests.get(MITRE_URL, timeout=60)
        response.raise_for_status()
        
        data = response.json()
        
        logger.info(f"✓ Downloaded successfully")
        logger.info(f"  - Total objects: {len(data.get('objects', []))}")
        logger.info(f"  - Spec version: {data.get('spec_version', 'unknown')}")
        
        return data
        
    except requests.exceptions.RequestException as e:
        logger.error(f"❌ Failed to download MITRE ATT&CK: {e}")
        return None
    except json.JSONDecodeError as e:
        logger.error(f"❌ Invalid JSON response: {e}")
        return None

# -------------------------------------------------------------------
# ChromaDB Ingestion
# -------------------------------------------------------------------

def ingest_to_chromadb(techniques: list) -> bool:
    """
    Ingest techniques into ChromaDB with embeddings.
    
    Args:
        techniques: List of parsed techniques
        
    Returns:
        Success status
    """
    logger.info("=" * 60)
    logger.info("Ingesting into ChromaDB")
    logger.info("=" * 60)
    logger.info(f"Target: {CHROMADB_HOST}:{CHROMADB_PORT}")
    
    try:
        # Connect to ChromaDB
        logger.info("Connecting to ChromaDB...")
        client = chromadb.HttpClient(
            host=CHROMADB_HOST,
            port=CHROMADB_PORT,
            settings=Settings(anonymized_telemetry=False)
        )
        
        # Test connection
        heartbeat = client.heartbeat()
        logger.info(f"✓ ChromaDB connection successful (heartbeat: {heartbeat})")
        
        # Load embedding model
        logger.info("Loading embedding model (all-MiniLM-L6-v2)...")
        embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        logger.info("✓ Embedding model loaded")
        
        # Create collection
        collection_name = "mitre_attack"
        
        # Delete old collection if exists
        try:
            client.delete_collection(name=collection_name)
            logger.info(f"✓ Deleted old '{collection_name}' collection")
        except:
            pass
        
        # Create fresh collection
        collection = client.create_collection(
            name=collection_name,
            metadata={"source": "mitre-attack-official"}
        )
        logger.info(f"✓ Created collection: {collection_name}")
        
        # Batch ingest
        batch_size = 50
        total_ingested = 0
        
        logger.info(f"Starting ingestion ({batch_size} per batch)...")
        logger.info("-" * 60)
        
        for i in range(0, len(techniques), batch_size):
            batch = techniques[i:i+batch_size]
            
            # Prepare batch data
            documents = [t['text'] for t in batch]
            ids = [t['id'] for t in batch]
            metadatas = [t['metadata'] for t in batch]
            
            # Generate embeddings
            embeddings = embedding_model.encode(documents).tolist()
            
            # Add to collection
            collection.add(
                documents=documents,
                embeddings=embeddings,
                ids=ids,
                metadatas=metadatas
            )
            
            total_ingested += len(batch)
            
            # Progress update every 10 batches
            if (i // batch_size + 1) % 10 == 0:
                logger.info(f"Progress: {total_ingested}/{len(techniques)} techniques")
        
        logger.info("-" * 60)
        logger.info(f"✓ Ingestion complete: {total_ingested} techniques")
        
        # Verify ingestion
        count = collection.count()
        logger.info(f"✓ Verification: {count} documents in collection")
        
        # Test semantic search
        logger.info("=" * 60)
        logger.info("Testing Semantic Search")
        logger.info("=" * 60)
        
        test_queries = [
            "SSH brute force attack",
            "PowerShell lateral movement",
            "credential dumping"
        ]
        
        for query in test_queries:
            logger.info(f"Query: '{query}'")
            
            query_embedding = embedding_model.encode([query]).tolist()
            
            results = collection.query(
                query_embeddings=query_embedding,
                n_results=3
            )
            
            for j, (doc, metadata) in enumerate(zip(
                results['documents'][0],
                results['metadatas'][0]
            ), 1):
                logger.info(f"  {j}. {metadata['technique_id']}: {metadata['name']}")
            
            logger.info("")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Ingestion failed: {e}")
        logger.exception(e)
        return False

# -------------------------------------------------------------------
# Main Workflow
# -------------------------------------------------------------------

def main():
    """Main ingestion workflow"""
    logger.info("=" * 60)
    logger.info("MITRE ATT&CK Knowledge Base Ingestion")
    logger.info("Official STIX 2.1 Parser")
    logger.info("=" * 60)
    
    # Step 1: Download MITRE ATT&CK
    mitre_data = download_mitre_attack()
    if not mitre_data:
        logger.error("❌ Failed to download MITRE ATT&CK data")
        sys.exit(1)
    
    # Step 2: Parse techniques
    parser = MitreParser()
    techniques = parser.parse_techniques(mitre_data)
    
    if not techniques:
        logger.error("❌ No techniques extracted")
        sys.exit(1)
    
    # Step 3: Ingest to ChromaDB
    success = ingest_to_chromadb(techniques)
    
    if success:
        logger.info("=" * 60)
        logger.info("✅ MITRE ATT&CK INGESTION SUCCESSFUL")
        logger.info("=" * 60)
        logger.info(f"Total techniques: {len(techniques)}")
        logger.info(f"Collection: mitre_attack")
        logger.info(f"Status: Ready for RAG queries")
        logger.info("=" * 60)
    else:
        logger.error("=" * 60)
        logger.error("❌ MITRE ATT&CK INGESTION FAILED")
        logger.error("=" * 60)
        sys.exit(1)


if __name__ == "__main__":
    main()