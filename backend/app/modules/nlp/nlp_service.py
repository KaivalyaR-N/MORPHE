import re
from collections import Counter
from typing import Dict, Any, List


class NLPService:
    @staticmethod
    def analyze_cdm(cdm_data: Dict[str, Any]) -> Dict[str, Any]:
        metadata = cdm_data.get("metadata", {})
        sections = cdm_data.get("sections", [])
        
        full_text_parts = [
            metadata.get("title", ""),
            metadata.get("abstract", "")
        ]
        for sec in sections:
            full_text_parts.append(sec.get("title", ""))
            full_text_parts.append(sec.get("content", ""))

        full_text = " ".join(full_text_parts)

        # 1. Keywords extraction using frequency & heuristics
        words = re.findall(r"\b[A-Za-z]{4,}\b", full_text.lower())
        stopwords = {
            "this", "that", "with", "from", "have", "were", "which", "their", "there", "these",
            "using", "used", "study", "paper", "results", "analysis", "data", "method", "system",
            "show", "shows", "based", "table", "figure", "section", "about", "above", "after"
        }
        filtered_words = [w for w in words if w not in stopwords]
        freq_counter = Counter(filtered_words)
        
        keywords = [{"word": word, "score": round(count / (len(filtered_words) or 1) * 10, 2)}
                    for word, count in freq_counter.most_common(12)]

        # 2. Named Entities (heuristics for capitalized terms, method names, institutions)
        entities = []
        capitalized = re.findall(r"\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b", full_text)
        cap_counts = Counter([e for e in capitalized if len(e) > 3])
        for ent, count in cap_counts.most_common(8):
            category = "CONCEPT"
            if any(term in ent.lower() for term in ["university", "lab", "institute", "dept", "org"]):
                category = "ORGANIZATION"
            elif any(term in ent.lower() for term in ["algorithm", "model", "bert", "gpt", "cnn", "transformer", "network", "system"]):
                category = "METHODOLOGY"
            entities.append({"text": ent, "category": category, "frequency": count})

        # 3. Research Terminology
        research_terms = []
        academic_vocabulary = [
            "methodology", "empirical", "framework", "hypothesis", "qualitative", "quantitative",
            "validation", "performance", "benchmark", "dataset", "ablation", "taxonomy", "optimization"
        ]
        for term in academic_vocabulary:
            matches = len(re.findall(r"\b" + term + r"\b", full_text, re.IGNORECASE))
            if matches > 0:
                research_terms.append({"term": term, "occurrences": matches})

        # 4. Citation patterns
        bracket_cites = len(re.findall(r"\[\d+\]", full_text))
        author_year_cites = len(re.findall(r"\([A-Z][a-z]+(?:\s+et\s+al\.)?,\s*\d{4}\)", full_text))
        citation_patterns = {
            "bracket_count": bracket_cites,
            "author_year_count": author_year_cites,
            "predominant_style": "IEEE (Numeric)" if bracket_cites >= author_year_cites else "APA (Author-Year)"
        }

        # 5. Summary generation
        abstract = metadata.get("abstract", "")
        if abstract and len(abstract.strip()) > 30:
            summary = abstract
        else:
            summary = full_text[:400] + "..." if len(full_text) > 400 else full_text

        return {
            "keywords": keywords,
            "entities": entities,
            "terminology": research_terms,
            "citation_patterns": citation_patterns,
            "summary": summary
        }
