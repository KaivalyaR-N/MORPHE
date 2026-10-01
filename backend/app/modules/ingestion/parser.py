import os
import re
import fitz  # PyMuPDF
import docx
from typing import Dict, Any, List


class DocumentParser:
    """
    Parses PDF, DOCX, TXT, MD, and LaTeX files into a standard raw structure suitable for CDM generation.
    """

    @classmethod
    def parse_file(cls, file_path: str, file_type: str) -> Dict[str, Any]:
        ext = file_type.lower().lstrip(".")
        if ext == "pdf":
            return cls._parse_pdf(file_path)
        elif ext in ["docx", "doc"]:
            return cls._parse_docx(file_path)
        elif ext in ["txt", "text"]:
            return cls._parse_txt(file_path)
        elif ext in ["md", "markdown"]:
            return cls._parse_markdown(file_path)
        elif ext in ["tex", "latex"]:
            return cls._parse_latex(file_path)
        else:
            return cls._parse_txt(file_path)

    @classmethod
    def _parse_pdf(cls, file_path: str) -> Dict[str, Any]:
        doc = fitz.open(file_path)
        full_text_blocks = []
        pages_text = []

        for page in doc:
            p_text = page.get_text("text")
            pages_text.append(p_text)
            full_text_blocks.append(p_text)

        full_text = "\n\n".join(full_text_blocks)
        doc.close()

        lines = [line.strip() for line in full_text.split("\n") if line.strip()]
        title = lines[0] if lines else "Untitled Document"
        
        # Simple metadata extract
        abstract = ""
        abstract_match = re.search(r"(?i)abstract[:\s]*(.*?)(?=\n\s*\n|introduction|1\.|keywords)", full_text, re.DOTALL)
        if abstract_match:
            abstract = abstract_match.group(1).strip()

        keywords = []
        kw_match = re.search(r"(?i)keywords[:\s]*(.*?)(?=\n\s*\n|1\.|introduction)", full_text, re.DOTALL)
        if kw_match:
            raw_kws = kw_match.group(1).strip()
            keywords = [k.strip() for k in re.split(r"[,;•]", raw_kws) if k.strip()]

        sections = cls._structure_raw_text(full_text)

        return {
            "title": title,
            "abstract": abstract,
            "keywords": keywords,
            "authors": [{"name": "Extracted Author", "affiliation": "", "email": ""}],
            "raw_text": full_text,
            "sections": sections
        }

    @classmethod
    def _parse_docx(cls, file_path: str) -> Dict[str, Any]:
        doc = docx.Document(file_path)
        full_text = "\n".join([p.text for p in doc.paragraphs if p.text.strip()])
        
        title = "Untitled Document"
        for p in doc.paragraphs:
            if p.text.strip():
                title = p.text.strip()
                break

        abstract = ""
        keywords = []
        
        abstract_match = re.search(r"(?i)abstract[:\s]*(.*?)(?=\n\s*\n|introduction|1\.|keywords)", full_text, re.DOTALL)
        if abstract_match:
            abstract = abstract_match.group(1).strip()

        kw_match = re.search(r"(?i)keywords[:\s]*(.*?)(?=\n\s*\n|1\.|introduction)", full_text, re.DOTALL)
        if kw_match:
            raw_kws = kw_match.group(1).strip()
            keywords = [k.strip() for k in re.split(r"[,;•]", raw_kws) if k.strip()]

        sections = cls._structure_raw_text(full_text)

        return {
            "title": title,
            "abstract": abstract,
            "keywords": keywords,
            "authors": [{"name": "Extracted Author", "affiliation": "", "email": ""}],
            "raw_text": full_text,
            "sections": sections
        }

    @classmethod
    def _parse_txt(cls, file_path: str) -> Dict[str, Any]:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            full_text = f.read()

        lines = [line.strip() for line in full_text.split("\n") if line.strip()]
        title = lines[0] if lines else "Untitled Document"

        sections = cls._structure_raw_text(full_text)
        return {
            "title": title,
            "abstract": "",
            "keywords": [],
            "authors": [],
            "raw_text": full_text,
            "sections": sections
        }

    @classmethod
    def _parse_markdown(cls, file_path: str) -> Dict[str, Any]:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            full_text = f.read()

        title = "Untitled Document"
        title_match = re.search(r"^#\s+(.*)$", full_text, re.MULTILINE)
        if title_match:
            title = title_match.group(1).strip()

        sections = []
        section_splits = re.split(r"\n(?=#{1,3}\s+)", full_text)
        
        sec_id = 1
        for block in section_splits:
            if not block.strip():
                continue
            header_match = re.match(r"^(#{1,3})\s+(.*)$", block, re.MULTILINE)
            if header_match:
                level = len(header_match.group(1))
                sec_title = header_match.group(2).strip()
                content = block[header_match.end():].strip()
            else:
                level = 1
                sec_title = f"Section {sec_id}"
                content = block.strip()

            sections.append({
                "id": f"sec_{sec_id}",
                "title": sec_title,
                "level": level,
                "content": content,
                "order": sec_id,
                "subsections": []
            })
            sec_id += 1

        return {
            "title": title,
            "abstract": "",
            "keywords": [],
            "authors": [],
            "raw_text": full_text,
            "sections": sections
        }

    @classmethod
    def _parse_latex(cls, file_path: str) -> Dict[str, Any]:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            full_text = f.read()

        title_match = re.search(r"\\title\{([^}]+)\}", full_text)
        title = title_match.group(1).strip() if title_match else "Untitled LaTeX Document"

        abstract_match = re.search(r"\\begin\{abstract\}(.*?)\\end\{abstract\}", full_text, re.DOTALL)
        abstract = abstract_match.group(1).strip() if abstract_match else ""

        # Extract sections
        sec_matches = re.findall(r"\\(section|subsection|subsubsection)\{([^}]+)\}", full_text)
        sections = []
        sec_id = 1
        for level_name, sec_title in sec_matches:
            lvl = 1 if level_name == "section" else 2 if level_name == "subsection" else 3
            sections.append({
                "id": f"sec_{sec_id}",
                "title": sec_title,
                "level": lvl,
                "content": f"Content for {sec_title}",
                "order": sec_id,
                "subsections": []
            })
            sec_id += 1

        return {
            "title": title,
            "abstract": abstract,
            "keywords": [],
            "authors": [],
            "raw_text": full_text,
            "sections": sections
        }

    @classmethod
    def _structure_raw_text(cls, full_text: str) -> List[Dict[str, Any]]:
        headings_pattern = r"\n(?=[0-9IVX]+\.\s+|[A-Z][A-Za-z\s]{3,40}\n)"
        blocks = re.split(headings_pattern, full_text)

        sections = []
        sec_id = 1
        for block in blocks:
            clean_block = block.strip()
            if not clean_block:
                continue

            lines = clean_block.split("\n")
            sec_title = lines[0].strip()
            sec_content = "\n".join(lines[1:]).strip() if len(lines) > 1 else clean_block

            sections.append({
                "id": f"sec_{sec_id}",
                "title": sec_title[:100],
                "level": 1,
                "content": sec_content,
                "order": sec_id,
                "subsections": []
            })
            sec_id += 1

        if not sections:
            sections = [{
                "id": "sec_1",
                "title": "Main Content",
                "level": 1,
                "content": full_text,
                "order": 1,
                "subsections": []
            }]

        return sections
