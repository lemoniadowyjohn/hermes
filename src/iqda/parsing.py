from __future__ import annotations

import json
import re
from pathlib import Path
from pypdf import PdfReader

from .models import DocumentMetadata, ParsedDocument


FIELD_MAP = {
    "document id": "document_id",
    "component id": "component_id",
    "revision": "revision",
    "status": "status",
    "effective date": "effective_date",
    "document type": "document_type",
    "supersedes": "supersedes",
}


class DocumentParser:
    supported_extensions = {".md", ".txt", ".json", ".pdf"}

    def parse(self, path: str | Path) -> ParsedDocument:
        path = Path(path)
        if path.suffix.lower() not in self.supported_extensions:
            raise ValueError(f"Unsupported file type: {path.suffix}")
        if path.suffix.lower() == ".pdf":
            text = self._parse_pdf(path)
        elif path.suffix.lower() == ".json":
            text = self._parse_json(path)
        else:
            text = path.read_text(encoding="utf-8")
        lines = text.splitlines()
        metadata = self._extract_metadata(lines, path)
        return ParsedDocument(metadata=metadata, text=text, lines=lines)

    def parse_directory(self, directory: str | Path) -> list[ParsedDocument]:
        directory = Path(directory)
        docs = []
        for path in sorted(directory.rglob("*")):
            if path.is_file() and path.suffix.lower() in self.supported_extensions:
                docs.append(self.parse(path))
        return docs

    @staticmethod
    def _parse_pdf(path: Path) -> str:
        reader = PdfReader(str(path))
        return "\n".join((page.extract_text() or "") for page in reader.pages)

    @staticmethod
    def _parse_json(path: Path) -> str:
        obj = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(obj, dict) and "text" in obj:
            prefix = "\n".join(f"{k}: {v}" for k, v in obj.items() if k != "text")
            return prefix + "\n\n" + str(obj["text"])
        return json.dumps(obj, ensure_ascii=False, indent=2)

    def _extract_metadata(self, lines: list[str], path: Path) -> DocumentMetadata:
        raw: dict[str, object] = {"source_path": str(path)}
        for line in lines[:30]:
            m = re.match(r"^\s*([A-Za-z ]+):\s*(.*?)\s*$", line)
            if not m:
                continue
            key = FIELD_MAP.get(m.group(1).strip().lower())
            if not key:
                continue
            value: object = m.group(2).strip()
            if key == "revision":
                num = re.search(r"\d+", str(value))
                value = int(num.group()) if num else None
            raw[key] = value
        if "document_id" not in raw:
            raw["document_id"] = path.stem
        return DocumentMetadata.model_validate(raw)
