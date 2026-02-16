"""
Knowledge Base Manager - FIXED VERSION
Correctly extracts ALL MITRE techniques including T1110
"""

import logging
import json
from typing import List, Dict, Any, Optional
from pathlib import Path
import requests

logger = logging.getLogger(__name__)


class MitreKnowledgeBase:
    """Official MITRE ATT&CK parser - FIXED"""
    
    def __init__(self, json_path: str):
        self.json_path = json_path
        logger.info(f"MitreKnowledgeBase initialized with {json_path}")
    
    def load_techniques(self) -> List[Dict[str, Any]]:
        """Load MITRE ATT&CK techniques - FIXED to extract ALL techniques"""
        logger.info(f"Loading MITRE ATT&CK data from {self.json_path}")
        
        try:
            with open(self.json_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except FileNotFoundError:
            logger.error(f"MITRE ATT&CK file not found: {self.json_path}")
            return []
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON: {e}")
            return []
        
        techniques = []
        mitre_version = data.get("spec_version", "unknown")
        
        logger.info(f"Processing MITRE objects (version: {mitre_version})")
        
        for obj in data.get("objects", []):
            # Only process attack patterns
            if obj.get("type") != "attack-pattern":
                continue
            
            # Skip revoked/deprecated
            if obj.get("revoked") or obj.get("x_mitre_deprecated"):
                continue
            
            try:
                # Extract external references
                external_refs = obj.get("external_references", [])
                if not external_refs:
                    continue
                
                # Find MITRE ATT&CK reference
                technique_id = None
                technique_url = None
                
                for ref in external_refs:
                    if ref.get("source_name") == "mitre-attack":
                        technique_id = ref.get("external_id", "").strip()
                        technique_url = ref.get("url", "")
                        break
                
                if not technique_id:
                    continue
                
                # Extract tactics
                kill_chain = obj.get("kill_chain_phases", [])
                tactics = []
                for phase in kill_chain:
                    if phase.get("kill_chain_name") == "mitre-attack":
                        tactic = phase.get("phase_name", "").replace("-", "_")
                        if tactic:
                            tactics.append(tactic)
                
                # Extract platforms
                platforms = obj.get("x_mitre_platforms", [])
                
                # Check if sub-technique
                is_subtechnique = obj.get("x_mitre_is_subtechnique", False)
                
                # Build technique object
                technique = {
                    "technique_id": technique_id,
                    "name": obj.get("name", "Unknown"),
                    "description": obj.get("description", ""),
                    "tactics": tactics,
                    "platforms": platforms,
                    "is_subtechnique": is_subtechnique,
                    "mitre_version": mitre_version,
                    "url": technique_url
                }
                
                techniques.append(technique)
                
            except Exception as e:
                logger.warning(f"Failed to parse technique: {e}")
                continue
        
        logger.info(f"✓ Parsed {len(techniques)} MITRE techniques")
        
        main = [t for t in techniques if not t["is_subtechnique"]]
        subs = [t for t in techniques if t["is_subtechnique"]]
        logger.info(f"  - Main: {len(main)}, Sub-techniques: {len(subs)}")
        
        return techniques


class KnowledgeBaseManager:
    """Manages security knowledge base ingestion"""

    def __init__(self, vector_store):
        self.vector_store = vector_store
        logger.info("KnowledgeBaseManager initialized")

    async def ingest_mitre_attack(self, data_path: Optional[str] = None) -> Dict[str, Any]:
        """Ingest MITRE ATT&CK framework"""
        logger.info("=" * 60)
        logger.info("MITRE ATT&CK Ingestion - FIXED VERSION")
        logger.info("=" * 60)

        try:
            # Download if needed
            if not data_path:
                logger.info("Downloading latest MITRE ATT&CK...")
                data_path = await self._download_mitre_attack()
            
            if not Path(data_path).exists():
                raise FileNotFoundError(f"File not found: {data_path}")

            # Parse techniques
            kb = MitreKnowledgeBase(data_path)
            techniques = kb.load_techniques()
            
            if not techniques:
                raise ValueError("No techniques extracted!")

            logger.info(f"Loaded {len(techniques)} techniques")

            # Create collection
            self.vector_store.create_collection(
                name='mitre_attack',
                metadata={
                    'source': 'mitre-attack-official',
                    'version': techniques[0]['mitre_version'],
                    'type': 'enterprise'
                }
            )

            # Prepare documents
            documents = []
            metadatas = []
            ids = []

            for t in techniques:
                # Create searchable document
                doc = self._format_technique_document(t)
                
                # Metadata
                metadata = {
                    'technique_id': t['technique_id'],
                    'name': t['name'],
                    'tactic': t['tactics'][0] if t['tactics'] else 'unknown',
                    'tactics': json.dumps(t['tactics']),
                    'platforms': json.dumps(t['platforms']),
                    'is_subtechnique': t['is_subtechnique'],
                    'type': 'mitre_technique',
                    'mitre_version': t['mitre_version']
                }
                
                documents.append(doc)
                metadatas.append(metadata)
                ids.append(t['technique_id'])

            # Batch ingest
            batch_size = 50
            total = 0

            logger.info(f"Ingesting in batches of {batch_size}...")

            for i in range(0, len(documents), batch_size):
                batch_docs = documents[i:i+batch_size]
                batch_metas = metadatas[i:i+batch_size]
                batch_ids = ids[i:i+batch_size]

                await self.vector_store.add_documents(
                    collection_name='mitre_attack',
                    documents=batch_docs,
                    metadatas=batch_metas,
                    ids=batch_ids
                )

                total += len(batch_docs)
                
                if (i // batch_size + 1) % 10 == 0:
                    logger.info(f"Progress: {total}/{len(documents)}")

            logger.info("=" * 60)
            logger.info(f"✅ SUCCESS: {total} techniques ingested")
            logger.info("=" * 60)

            return {
                "status": "success",
                "techniques_ingested": total,
                "main_techniques": len([t for t in techniques if not t['is_subtechnique']]),
                "sub_techniques": len([t for t in techniques if t['is_subtechnique']]),
                "version": techniques[0]['mitre_version'],
                "message": f"Successfully ingested {total} MITRE ATT&CK techniques"
            }

        except Exception as e:
            logger.error(f"Ingestion failed: {e}")
            logger.exception(e)
            return {
                "status": "error",
                "techniques_ingested": 0,
                "message": str(e)
            }

    def _format_technique_document(self, technique: Dict[str, Any]) -> str:
        """Format technique as searchable document"""
        parts = [
            f"Technique {technique['technique_id']} - {technique['name']}",
            "",
            f"Tactics: {', '.join(technique['tactics'])}",
            f"Platforms: {', '.join(technique['platforms'])}",
        ]
        
        if technique['is_subtechnique']:
            parent = technique['technique_id'].split('.')[0]
            parts.append(f"Sub-technique of: {parent}")
        
        parts.extend(["", technique['description']])
        
        return "\n".join(parts)

    async def _download_mitre_attack(self) -> str:
        """Download latest MITRE ATT&CK"""
        url = "https://raw.githubusercontent.com/mitre/cti/master/enterprise-attack/enterprise-attack.json"
        output_path = Path("/tmp/enterprise-attack.json")

        try:
            logger.info(f"Downloading from {url}")
            response = requests.get(url, timeout=60)
            response.raise_for_status()

            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(response.json(), f, indent=2)

            logger.info(f"✓ Downloaded to {output_path}")
            return str(output_path)

        except Exception as e:
            logger.error(f"Download failed: {e}")
            raise

    async def update_knowledge_base(self, collection: str) -> Dict[str, Any]:
        """Update knowledge base"""
        logger.info(f"Updating: {collection}")
        return {"status": "not_implemented"}