import uuid
from typing import Dict, Any, List


class CDMService:
    @staticmethod
    def build_initial_cdm(parsed_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Builds a canonical document model (CDM) from parsed raw data.
        """
        title = parsed_data.get("title") or "Untitled Research Document"
        abstract = parsed_data.get("abstract") or ""
        keywords = parsed_data.get("keywords") or []
        authors = parsed_data.get("authors") or [{"name": "Lead Researcher", "affiliation": "Institution", "email": ""}]

        raw_sections = parsed_data.get("sections") or []
        formatted_sections = []

        for idx, sec in enumerate(raw_sections, start=1):
            sec_id = sec.get("id") or f"sec_{idx}"
            formatted_sections.append({
                "id": sec_id,
                "title": sec.get("title", f"Section {idx}"),
                "level": sec.get("level", 1),
                "content": sec.get("content", ""),
                "order": idx,
                "subsections": sec.get("subsections", [])
            })

        # Heuristic reference extraction
        references = []
        full_text = parsed_data.get("raw_text", "")
        ref_matches = CDMService._extract_heuristic_references(full_text)
        for r_idx, ref_text in enumerate(ref_matches, start=1):
            references.append({
                "id": f"ref_{r_idx}",
                "key": f"[{r_idx}]",
                "text": ref_text,
                "authors": ["Author et al."],
                "title": f"Reference {r_idx}",
                "year": "2024",
                "venue": "Academic Journal",
                "doi": ""
            })

        cdm = {
            "metadata": {
                "title": title,
                "abstract": abstract,
                "keywords": keywords,
                "authors": authors
            },
            "sections": formatted_sections,
            "figures": [],
            "tables": [],
            "references": references,
            "citations": [],
            "appendices": []
        }
        return cdm

    @staticmethod
    def _extract_heuristic_references(text: str) -> List[str]:
        references = []
        if "References" in text or "REFERENCES" in text:
            split_parts = text.split("References") if "References" in text else text.split("REFERENCES")
            ref_block = split_parts[-1]
            lines = [line.strip() for line in ref_block.split("\n") if line.strip()]
            for line in lines[:20]:
                if len(line) > 15:
                    references.append(line)
        return references
