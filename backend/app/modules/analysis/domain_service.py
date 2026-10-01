import re
from typing import Dict, Any, List


class DomainIntelligenceService:
    DOMAINS_MAP = {
        "Computer Science": [
            "algorithm", "neural network", "machine learning", "deep learning", "cloud", "software",
            "data", "transformer", "computational", "database", "security", "ai", "artificial intelligence", "gpu"
        ],
        "Medicine": [
            "patient", "clinical", "disease", "treatment", "oncology", "cardiology", "diagnosis",
            "medical", "cell", "therapy", "hospital", "biomedical", "blood", "trial"
        ],
        "Physics": [
            "quantum", "particle", "magnetic", "energy", "photon", "thermodynamics", "laser",
            "atom", "mass", "momentum", "optical", "wave"
        ],
        "Business & Economics": [
            "market", "financial", "revenue", "firm", "stock", "economic", "investment",
            "corporate", "strategy", "management", "trade"
        ],
        "Engineering": [
            "voltage", "circuit", "mechanical", "structural", "sensor", "signal", "control",
            "thermal", "device", "robot", "fabrication"
        ]
    }

    SUBDOMAINS_MAP = {
        "Machine Learning": ["learning", "neural", "classification", "training", "model", "accuracy"],
        "Cyber Security": ["security", "encryption", "vulnerability", "attack", "malware", "threat"],
        "Cloud Computing": ["cloud", "microservices", "latency", "distributed", "serverless"],
        "Computer Vision": ["image", "segmentation", "detection", "visual", "pixel", "cnn"],
        "Oncology": ["cancer", "tumor", "chemotherapy", "carcinoma", "mutation"],
        "Finance": ["portfolio", "asset", "risk", "banking", "option", "price"]
    }

    RESEARCH_TYPES = {
        "Experimental": ["experiment", "dataset", "accuracy", "baseline", "evaluation", "tested"],
        "Survey": ["survey", "overview", "taxonomy", "literature review", "state of the art"],
        "Case Study": ["case study", "empirical study", "organization", "interviews", "qualitative"],
        "Theoretical": ["theorem", "proof", "lemma", "proposition", "formalization"]
    }

    @classmethod
    def analyze_domain_and_structure(cls, cdm_data: Dict[str, Any]) -> Dict[str, Any]:
        metadata = cdm_data.get("metadata", {})
        sections = cdm_data.get("sections", [])
        
        full_text = (metadata.get("title", "") + " " + metadata.get("abstract", "") + " " +
                     " ".join([s.get("title", "") + " " + s.get("content", "") for s in sections])).lower()

        # Domain scoring
        domain_scores = {}
        for domain, keywords in cls.DOMAINS_MAP.items():
            score = sum(len(re.findall(r"\b" + kw + r"\b", full_text)) for kw in keywords)
            domain_scores[domain] = score

        primary_domain = max(domain_scores, key=domain_scores.get) if any(domain_scores.values()) else "Computer Science"
        domain_confidence = min(0.98, max(0.65, round((domain_scores.get(primary_domain, 1) + 1) / (sum(domain_scores.values()) + 5), 2)))

        # Subdomain scoring
        subdomain_scores = {}
        for sub, keywords in cls.SUBDOMAINS_MAP.items():
            score = sum(len(re.findall(r"\b" + kw + r"\b", full_text)) for kw in keywords)
            subdomain_scores[sub] = score

        subdomain = max(subdomain_scores, key=subdomain_scores.get) if any(subdomain_scores.values()) else "Machine Learning"

        # Research type
        rtype_scores = {}
        for rtype, keywords in cls.RESEARCH_TYPES.items():
            score = sum(len(re.findall(r"\b" + kw + r"\b", full_text)) for kw in keywords)
            rtype_scores[rtype] = score

        research_type = max(rtype_scores, key=rtype_scores.get) if any(rtype_scores.values()) else "Experimental"

        # Publication type
        pub_type = "Journal Paper"
        if "proceedings" in full_text or "conference" in full_text:
            pub_type = "Conference Paper"
        elif "arxiv" in full_text or "preprint" in full_text:
            pub_type = "Preprint"

        # Citation style detection
        bracket_cites = len(re.findall(r"\[\d+\]", full_text))
        author_year_cites = len(re.findall(r"\([A-Z][a-z]+,\s*\d{4}\)", full_text))
        citation_style = "IEEE" if bracket_cites >= author_year_cites else "APA"

        evidence = [
            {"factor": "Primary Keyword Matches", "detail": f"Found {domain_scores.get(primary_domain, 0)} matching domain keywords for {primary_domain}"},
            {"factor": "Section Pattern", "detail": f"Analyzed {len(sections)} sections in document"},
            {"factor": "Citation Syntax", "detail": f"Detected {bracket_cites} numerical citations and {author_year_cites} author-year citations"}
        ]

        # Structural IMRaD Analysis
        imrad_sections = ["Introduction", "Methodology", "Results", "Discussion", "Conclusion", "References"]
        present_sections = []
        missing_sections = []
        sec_titles_lower = [s.get("title", "").lower() for s in sections]

        for req in imrad_sections:
            if any(req.lower() in t for t in sec_titles_lower):
                present_sections.append(req)
            else:
                missing_sections.append(req)

        order_valid = ("Introduction" in present_sections) and (
            "References" not in present_sections or present_sections.index("References") == len(present_sections) - 1
        )

        return {
            "domain_analysis": {
                "primary_domain": primary_domain,
                "subdomain": subdomain,
                "research_type": research_type,
                "publication_type": pub_type,
                "citation_style": citation_style,
                "confidence": domain_confidence,
                "evidence": evidence
            },
            "structural_analysis": {
                "present_sections": present_sections,
                "missing_sections": missing_sections,
                "unexpected_sections": [s.get("title") for s in sections if not any(req.lower() in s.get("title", "").lower() for req in imrad_sections)],
                "order_valid": order_valid
            }
        }
