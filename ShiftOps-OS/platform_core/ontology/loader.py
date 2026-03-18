import json
import os
from pathlib import Path
from typing import Dict, Optional
from platform_core.ontology.schema import IndustryPack

class OntologyLoader:
    """The 'Driver Manager' for the ShiftOps-OS Kernel."""
    
    def __init__(self, packs_dir: str = None):
        if packs_dir is None:
            # Default to 'packs' directory relative to this file
            self.packs_dir = (Path(__file__).parent / "packs").resolve()
        else:
            self.packs_dir = Path(packs_dir).resolve()
            
        print(f"DEBUG: OntologyLoader initialized with packs_dir: {self.packs_dir}")
        self.packs_dir.mkdir(parents=True, exist_ok=True)
        self.registry: Dict[str, IndustryPack] = {}

    def load_pack(self, pack_id: str) -> Optional[IndustryPack]:
        """Loads and validates an Industry Pack from disk."""
        pack_path = (self.packs_dir / f"{pack_id}.json").resolve()
        print(f"DEBUG: Attempting to load pack from: {pack_path} (exists: {pack_path.exists()})")
        
        if not pack_path.exists():
            print(f"Warning: Pack {pack_id} not found at {pack_path}")
            return None

        try:
            with open(pack_path, "r") as f:
                data = json.load(f)
                pack = IndustryPack(**data)
                self.registry[pack_id] = pack
                print(f"Successfully loaded Ontology Module: {pack_id} (v{pack.version})")
                return pack
        except Exception as e:
            print(f"Error loading pack {pack_id}: {str(e)}")
            return None

    def get_pack(self, pack_id: str) -> Optional[IndustryPack]:
        return self.registry.get(pack_id) or self.load_pack(pack_id)
