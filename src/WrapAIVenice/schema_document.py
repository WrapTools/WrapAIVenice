# schema_document.py
"""
Structured document schema for storing AI prompt interactions.

Includes:
- `DocumentHeader`: Global metadata (e.g., document ID, system prompt).
- `DocumentDetail`: Individual prompt details, response, and usage.
- `DocumentManager`: Handles saving, loading, and hash-tracked serialization of prompt sessions.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, Union, Optional
import json
from pathlib import Path
import logging
import hashlib

# Logger Configuration
logger = logging.getLogger(__name__)


@dataclass
class DocumentHeader:
    # Global header fields
    document_id: str
    system_prompt: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """Convert the DocumentSumEval instance into a dictionary for JSON serialization."""
        return {
            "document_id": self.document_id,
            "system_prompt": self.system_prompt
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "DocumentHeader":
        """Create a DocumentSumEval instance from a dictionary."""
        return DocumentHeader(
            document_id=data.get("document_id", ""),
            system_prompt=data.get("system_prompt", ""))

    @staticmethod
    def from_structured_dict(data: Dict[str, Any]) -> "DocumentHeader":
        """Convert structured format (with payload/response) into a DocumentSumEval instance."""
        return DocumentHeader(
            document_id=data["payload"].get("document_id", ""),
            system_prompt=data["payload"].get("system_prompt", ""))


@dataclass
class DocumentDetail:

    # Prompt fields
    model: str = ""
    model_created: int = 0
    user_prompt: str = ""
    parameters: Dict[str, Any] = field(default_factory=dict)

    # Response fields
    think: str = ""
    results: str = ""
    usage: Dict[str, Any] = field(default_factory=dict)


    def to_dict(self) -> Dict[str, Any]:
        """Convert the DocumentSumEval instance into a dictionary for JSON serialization."""
        return {
            "model": self.model,
            "model_created": self.model_created,
            "user_prompt": self.user_prompt,
            "parameters": self.parameters,
            "think": self.think,
            "results": self.results,
            "usage": self.usage,
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "DocumentDetail":
        """Create a DocumentSumEval instance from a dictionary."""
        return DocumentDetail(
            model=data.get("model", ""),
            model_created=data.get("model_created", 0),
            user_prompt=data.get("user_prompt", ""),
            parameters=data.get("parameters", {}),
            think=data.get("think", ""),
            results=data.get("results", ""),
            usage=data.get("usage", {}),
        )

    @staticmethod
    def from_structured_dict(data: Dict[str, Any]) -> "DocumentDetail":
        """Convert structured format (with payload/response) into a DocumentSumEval instance."""
        return DocumentDetail(
            model=data["payload"].get("model", ""),
            user_prompt=data["payload"].get("user_prompt", ""),
            parameters=data["payload"].get("parameters", {}),
            think=data["response"].get("think", ""),
            results=data["response"].get("results", ""),
            usage=data["response"].get("usage", {}),
        )

class DocumentManager:
    """Manages saving and loading AI Prompts with Request and Responses."""

    APP_NAME = "DocumentProcessor"
    DATA_VERSION = "0.1.0"
    FILE_TYPE = "document"
    GENERATOR = "direct"

    def __init__(self, file_path: Union[str, Path]):
        self.file_path = Path(file_path)
        self.document_header: Optional[DocumentHeader] = None
        self.documents: Dict[str, DocumentDetail] = {}

    def create_header(self, document_id: str, system_prompt: str = ""):
        self.document_header = DocumentHeader(document_id=document_id, system_prompt=system_prompt)

    def add_document_detail(self, name: str, detail: DocumentDetail):
        self.documents[name] = detail

    def get_document_object(self, name: str) -> Optional[DocumentDetail]:
        return self.documents.get(name)

    def load_from_file(self) -> bool:
        """Loads a Document instance from a JSON file."""
        if not self.file_path.exists():
            logger.warning(f"No saved document file found at {self.file_path}.")
            return False

        try:
            with self.file_path.open("r", encoding="utf-8") as f:
                data = json.load(f)

            logger.info("🔄 Detected structured document format. Converting...")
            self.from_structured_dict(data)


            logger.info(f"✅ Loaded document data from {self.file_path}")
            return True

        except (IOError, json.JSONDecodeError, Exception) as err:
            logger.error(f"Error loading document from {self.file_path}: {err}")
            return False

    def save_to_file(self) -> bool:
        """Saves the full structured output (with hashes, header, etc.) to a JSON file."""
        if not self.document_header or not self.documents:
            logger.warning("⚠️ No document header or details to save. Skipping file write.")
            return False

        try:
            structured = self.to_structured_output()
            with self.file_path.open("w", encoding="utf-8") as json_file:
                json.dump(structured, json_file, indent=4, ensure_ascii=False)
            logger.info(f"✅ Structured document saved to {self.file_path}")
            return True

        except (IOError, TypeError, Exception) as err:
            logger.error(f"Error saving document to {self.file_path}: {err}")
            return False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "header": self.document_header.to_dict() if self.document_header else {},
            "documents": {k: v.to_dict() for k, v in self.documents.items()}
        }

    def from_dict(self, data: Dict[str, Any]):
        self.document_header = DocumentHeader.from_dict(data.get("header", {}))
        self.documents = {
            k: DocumentDetail.from_dict(v)
            for k, v in data.get("documents", {}).items()
        }

    def create_document_header(self, document_id: str, system_prompt: str = ""):
        """Initialize a Document header."""
        self.document_header = DocumentHeader(document_id=document_id, system_prompt=system_prompt)

    def update_document_detail(
            self,
            name: str,
            model: str,
            think: str,
            results: str,
            usage: Dict[str, Any],
            created: int,
            user_prompt: str,
            parameters: Dict[str, Any]
    ):
        if name not in self.documents:
            self.documents[name] = DocumentDetail()

        doc = self.documents[name]
        doc.model = model
        doc.think = think
        doc.results = results
        doc.usage = usage
        doc.model_created = created
        doc.user_prompt = user_prompt
        doc.parameters = parameters

    def get_document_detail(self, name: str) -> Dict[str, Any]:
        doc = self.documents.get(name)
        if not doc:
            return {}
        return doc.to_dict()

    def get_document_header(self) -> Dict[str, Any]:
        """Retrieve the global document header (document_id and system_prompt)."""
        if not self.document_header:
            return {}
        return {
            "document_id": self.document_header.document_id,
            "system_prompt": self.document_header.system_prompt,
        }

    def to_structured_output(self) -> dict:
        if not self.document_header:
            return {}

        payload = {
            "document_id": self.document_header.document_id,
            "system_prompt": self.document_header.system_prompt,
        }
        response = {}
        hashes = {}

        for name, detail in self.documents.items():
            payload[name] = {
                "model": detail.model,
                "user_prompt": detail.user_prompt,
                "parameters": detail.parameters,
            }
            response[name] = {
                "think": detail.think,
                "results": detail.results,
                "usage": detail.usage,
            }
            hash_input = {
                "document_id": payload["document_id"],
                "system_prompt": payload["system_prompt"],
                name: payload[name],
            }
            hashes[name] = hashlib.sha256(
                json.dumps(hash_input, sort_keys=True, separators=(",", ":")).encode()
            ).hexdigest()

        return {
            "header": {
                "app_name": self.APP_NAME,
                "data_version": self.DATA_VERSION,
                "file_type": self.FILE_TYPE,
                "generator": self.GENERATOR
            },
            "payload": payload,
            "response": response,
            "hashes": hashes
        }

    def from_structured_dict(self, data: dict):
        self.document_header = DocumentHeader.from_structured_dict(data)
        payload = data["payload"]
        response = data["response"]
        self.documents.clear()

        for key in payload:
            if key in ("document_id", "system_prompt"):
                continue
            detail = DocumentDetail(
                model=payload[key].get("model", ""),
                user_prompt=payload[key].get("user_prompt", ""),
                parameters=payload[key].get("parameters", {}),
                think=response.get(key, {}).get("think", ""),
                results=response.get(key, {}).get("results", ""),
                usage=response.get(key, {}).get("usage", {}),
            )
            self.documents[key] = detail

    def matches_hash(self, name: str, prompt_hash: str) -> bool:
        hashes = self.to_structured_output().get("hashes", {})
        return hashes.get(name) == prompt_hash

    def get_hash(self, name: str) -> Optional[str]:
        return self.to_structured_output().get("hashes", {}).get(name)

    def has_document(self, name: str) -> bool:
        return name in self.documents
