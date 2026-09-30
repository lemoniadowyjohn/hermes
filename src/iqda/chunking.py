from __future__ import annotations

import hashlib
import re

from .models import Chunk, ParsedDocument


class SectionChunker:
    def __init__(self, max_chars: int = 1200, overlap_lines: int = 2):
        if max_chars < 200:
            raise ValueError("max_chars must be >= 200")
        self.max_chars = max_chars
        self.overlap_lines = max(0, overlap_lines)

    def chunk(self, doc: ParsedDocument) -> list[Chunk]:
        sections: list[tuple[str | None, int, list[str]]] = []
        current_title: str | None = None
        current_start = 1
        current_lines: list[str] = []

        for idx, line in enumerate(doc.lines, start=1):
            if re.match(r"^#{1,6}\s+", line):
                if current_lines:
                    sections.append((current_title, current_start, current_lines))
                current_title = re.sub(r"^#{1,6}\s+", "", line).strip()
                current_start = idx
                current_lines = [line]
            else:
                current_lines.append(line)
        if current_lines:
            sections.append((current_title, current_start, current_lines))

        chunks: list[Chunk] = []
        for title, section_start, lines in sections:
            cursor = 0
            while cursor < len(lines):
                char_count = 0
                end = cursor
                while end < len(lines):
                    next_len = len(lines[end]) + 1
                    if end > cursor and char_count + next_len > self.max_chars:
                        break
                    char_count += next_len
                    end += 1
                selected = lines[cursor:end]
                start_line = section_start + cursor
                end_line = section_start + end - 1
                text = "\n".join(selected).strip()
                if text:
                    digest = hashlib.sha1(
                        f"{doc.metadata.document_id}|{start_line}|{end_line}|{text}".encode("utf-8")
                    ).hexdigest()[:10]
                    chunk_id = f"{doc.metadata.document_id}::r{doc.metadata.revision or 0}::{digest}"
                    chunks.append(
                        Chunk(
                            chunk_id=chunk_id,
                            document_id=doc.metadata.document_id,
                            text=text,
                            start_line=start_line,
                            end_line=end_line,
                            section=title,
                            metadata=doc.metadata,
                        )
                    )
                if end >= len(lines):
                    break
                cursor = max(cursor + 1, end - self.overlap_lines)
        return chunks
