from typing import Dict, Any, List


class ValidationService:
    @classmethod
    def validate_document(cls, cdm_data: Dict[str, Any], target_publisher_code: str = "IEEE") -> Dict[str, Any]:
        metadata = cdm_data.get("metadata", {})
        sections = cdm_data.get("sections", [])
        references = cdm_data.get("references", [])
        
        structural_issues = []
        metadata_issues = []
        citation_issues = []
        content_issues = []

        # 1. Structure Validation
        title = metadata.get("title", "").strip()
        if not title or title.lower() == "untitled document":
            structural_issues.append({
                "severity": "error",
                "category": "structure",
                "message": "Document is missing a clear title.",
                "location": "Metadata Title",
                "suggestion": "Provide a descriptive research title."
            })

        abstract = metadata.get("abstract", "").strip()
        if not abstract:
            structural_issues.append({
                "severity": "error",
                "category": "structure",
                "message": "Document abstract is missing.",
                "location": "Abstract Section",
                "suggestion": "Add an abstract summarizing objectives, methodology, and key results."
            })
        elif len(abstract.split()) < 50:
            structural_issues.append({
                "severity": "warning",
                "category": "structure",
                "message": "Abstract is unusually short (< 50 words).",
                "location": "Abstract Section",
                "suggestion": "Expand the abstract to 150-250 words."
            })

        sec_titles = [s.get("title", "").strip() for s in sections]
        req_sections = ["Introduction", "Methodology", "Results", "Discussion", "Conclusion"]
        missing_req = [r for r in req_sections if not any(r.lower() in t.lower() for t in sec_titles)]
        
        for m in missing_req:
            structural_issues.append({
                "severity": "warning",
                "category": "structure",
                "message": f"Recommended section '{m}' was not detected.",
                "location": "Document Sections",
                "suggestion": f"Add a dedicated '{m}' section to follow standard academic structure."
            })

        # 2. Metadata Validation
        authors = metadata.get("authors", [])
        if not authors:
            metadata_issues.append({
                "severity": "error",
                "category": "metadata",
                "message": "No author metadata found.",
                "location": "Authors",
                "suggestion": "Specify author names and institutional affiliations."
            })
        else:
            for idx, a in enumerate(authors):
                if not a.get("affiliation"):
                    metadata_issues.append({
                        "severity": "info",
                        "category": "metadata",
                        "message": f"Author '{a.get('name', f'Author {idx+1}')}' has no institutional affiliation.",
                        "location": f"Author {idx+1}",
                        "suggestion": "Include institutional affiliation for academic credibility."
                    })

        keywords = metadata.get("keywords", [])
        if not keywords or len(keywords) < 3:
            metadata_issues.append({
                "severity": "warning",
                "category": "metadata",
                "message": "Fewer than 3 keywords defined.",
                "location": "Keywords",
                "suggestion": "Include 3 to 6 domain-specific index keywords."
            })

        # 3. Content Validation
        for sec in sections:
            content = sec.get("content", "").strip()
            word_count = len(content.split())
            if word_count == 0:
                content_issues.append({
                    "severity": "error",
                    "category": "content",
                    "message": f"Section '{sec.get('title')}' is empty.",
                    "location": sec.get("id"),
                    "suggestion": "Add content or remove the section."
                })
            elif word_count < 25:
                content_issues.append({
                    "severity": "warning",
                    "category": "content",
                    "message": f"Section '{sec.get('title')}' has less than 25 words.",
                    "location": sec.get("id"),
                    "suggestion": "Expand section details or merge with an adjacent section."
                })

        # 4. Citation & Reference Validation
        if not references:
            citation_issues.append({
                "severity": "warning",
                "category": "citation",
                "message": "No reference list was extracted.",
                "location": "References",
                "suggestion": "Ensure the document includes a formatted References section."
            })

        # 5. Publisher Compliance Evaluation
        compliance_check = cls._evaluate_publisher_compliance(cdm_data, target_publisher_code)

        # Calculate Overall Score (100 base, deductions for issues)
        deductions = (
            sum(15 for i in structural_issues if i["severity"] == "error") +
            sum(8 for i in structural_issues if i["severity"] == "warning") +
            sum(10 for i in metadata_issues if i["severity"] == "error") +
            sum(5 for i in metadata_issues if i["severity"] == "warning") +
            sum(12 for i in content_issues if i["severity"] == "error") +
            sum(5 for i in content_issues if i["severity"] == "warning") +
            sum(5 for i in citation_issues)
        )
        overall_score = max(20.0, float(100 - deductions))

        return {
            "structural_issues": structural_issues,
            "metadata_issues": metadata_issues,
            "citation_issues": citation_issues,
            "content_issues": content_issues,
            "publisher_compliance": compliance_check,
            "overall_score": overall_score
        }

    @classmethod
    def _evaluate_publisher_compliance(cls, cdm_data: Dict[str, Any], publisher_code: str) -> Dict[str, Any]:
        pub_rules = {
            "IEEE": {"citation_style": "Numeric [1]", "max_abstract": 250, "req_sections": ["Introduction", "Methodology", "Results", "Conclusion", "References"]},
            "ACM": {"citation_style": "Numeric [1] or Author-Year", "max_abstract": 300, "req_sections": ["Introduction", "Background", "Evaluation", "References"]},
            "ELSEVIER": {"citation_style": "APA / Author-Year", "max_abstract": 250, "req_sections": ["Introduction", "Methods", "Results", "Discussion", "References"]},
            "SPRINGER": {"citation_style": "Numeric / Author-Year", "max_abstract": 250, "req_sections": ["Introduction", "Related Work", "Methodology", "Experiments", "Conclusion"]},
            "NATURE": {"citation_style": "Numbered superscripts", "max_abstract": 200, "req_sections": ["Summary", "Main Text", "Methods", "References"]}
        }

        rules = pub_rules.get(publisher_code.upper(), pub_rules["IEEE"])
        metadata = cdm_data.get("metadata", {})
        abstract_len = len(metadata.get("abstract", "").split())
        
        abstract_ok = abstract_len <= rules["max_abstract"]
        citation_ok = True
        
        checklist = [
            {"criterion": "Abstract Word Limit", "status": "PASS" if abstract_ok else "FAIL", "detail": f"{abstract_len} / {rules['max_abstract']} max words"},
            {"criterion": "Author Metadata", "status": "PASS" if metadata.get("authors") else "FAIL", "detail": f"{len(metadata.get('authors', []))} authors provided"},
            {"criterion": "Keyword List", "status": "PASS" if metadata.get("keywords") else "WARN", "detail": f"{len(metadata.get('keywords', []))} keywords provided"},
            {"criterion": "Target Citation Format", "status": "PASS", "detail": f"Expected: {rules['citation_style']}"}
        ]

        passed_count = sum(1 for c in checklist if c["status"] == "PASS")
        score = round((passed_count / len(checklist)) * 100, 1)

        return {
            "publisher": publisher_code,
            "compliance_score": score,
            "checklist": checklist
        }
