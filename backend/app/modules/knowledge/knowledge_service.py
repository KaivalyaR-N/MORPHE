from typing import List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload

SEED_PUBLISHERS = [
    {
        "code": "IEEE",
        "name": "Institute of Electrical and Electronics Engineers",
        "description": "Leading publisher in electrical engineering, computer science, and electronics.",
        "journals": [
            {
                "code": "IEEE_TIT",
                "name": "IEEE Transactions on Information Theory",
                "citation_style": "IEEE",
                "required_sections": ["Abstract", "Introduction", "System Model", "Theoretical Analysis", "Simulation Results", "Conclusion", "References"],
                "max_words": 10000,
                "abstract_max_words": 250
            },
            {
                "code": "IEEE_TSE",
                "name": "IEEE Transactions on Software Engineering",
                "citation_style": "IEEE",
                "required_sections": ["Abstract", "Introduction", "Related Work", "Methodology", "Empirical Evaluation", "Threats to Validity", "Conclusion", "References"],
                "max_words": 12000,
                "abstract_max_words": 250
            }
        ]
    },
    {
        "code": "ELSEVIER",
        "name": "Elsevier",
        "description": "Major publisher of scientific, technical, and medical academic research.",
        "journals": [
            {
                "code": "ELS_PR",
                "name": "Pattern Recognition",
                "citation_style": "APA",
                "required_sections": ["Abstract", "Introduction", "Proposed Method", "Experiments", "Discussion", "Conclusion", "References"],
                "max_words": 8000,
                "abstract_max_words": 200
            }
        ]
    },
    {
        "code": "ACM",
        "name": "Association for Computing Machinery",
        "description": "World's largest educational and scientific computing society.",
        "journals": [
            {
                "code": "ACM_TOIS",
                "name": "ACM Transactions on Information Systems",
                "citation_style": "ACM",
                "required_sections": ["Abstract", "Introduction", "Background", "Methodology", "Experiments", "Conclusion", "References"],
                "max_words": 10000,
                "abstract_max_words": 250
            }
        ]
    },
    {
        "code": "SPRINGER",
        "name": "Springer Nature",
        "description": "Global publisher providing high quality research to science, technology, medicine, humanities, and social sciences.",
        "journals": [
            {
                "code": "SPR_SNCS",
                "name": "SN Computer Science",
                "citation_style": "Vancouver",
                "required_sections": ["Abstract", "Introduction", "Literature Review", "Proposed Framework", "Results", "Conclusion", "References"],
                "max_words": 9000,
                "abstract_max_words": 250
            }
        ]
    },
    {
        "code": "NATURE",
        "name": "Nature Publishing Group",
        "description": "Publisher of Nature and Nature research journals across multidisciplinary science.",
        "journals": [
            {
                "code": "NAT_MAIN",
                "name": "Nature",
                "citation_style": "Nature",
                "required_sections": ["Summary", "Main Text", "Methods", "Data Availability", "References"],
                "max_words": 4500,
                "abstract_max_words": 150
            }
        ]
    }
]

SEED_CITATION_STYLES = [
    {
        "code": "IEEE",
        "name": "IEEE Numeric Style",
        "description": "Uses bracketed numbers in text e.g. [1] corresponding to a numbered bibliography list at the end.",
        "formatting_rules": {"in_text": "[{num}]", "author_format": "A. B. Author", "title_quotes": True}
    },
    {
        "code": "APA",
        "name": "APA 7th Edition",
        "description": "Uses author-year citations in text e.g. (Smith, 2020) with an alphabetical reference list.",
        "formatting_rules": {"in_text": "({author}, {year})", "author_format": "Author, A. B.", "title_quotes": False}
    },
    {
        "code": "ACM",
        "name": "ACM Reference Format",
        "description": "Uses numbered citations in square brackets with full names and publication venues.",
        "formatting_rules": {"in_text": "[{num}]", "author_format": "Firstname Lastname", "title_quotes": False}
    },
    {
        "code": "CHICAGO",
        "name": "Chicago Manual of Style",
        "description": "Supports both Notes-Bibliography and Author-Date citation styles.",
        "formatting_rules": {"in_text": "({author} {year})", "author_format": "Lastname, Firstname", "title_quotes": True}
    }
]


class KnowledgeService:
    @staticmethod
    def get_all_publishers() -> List[Dict[str, Any]]:
        return SEED_PUBLISHERS

    @staticmethod
    def get_publisher_by_code(code: str) -> Dict[str, Any]:
        for p in SEED_PUBLISHERS:
            if p["code"].upper() == code.upper():
                return p
        return SEED_PUBLISHERS[0]

    @staticmethod
    def get_citation_styles() -> List[Dict[str, Any]]:
        return SEED_CITATION_STYLES

    @classmethod
    async def seed_knowledge_base(cls, db: AsyncSession):
        from app.models.models import Publisher, Journal, CitationStyle

        pub_count = await db.scalar(select(func.count(Publisher.id)))
        if not pub_count:
            for p_seed in SEED_PUBLISHERS:
                pub = Publisher(
                    name=p_seed["name"],
                    code=p_seed["code"],
                    description=p_seed["description"]
                )
                db.add(pub)
                await db.flush()

                for j_seed in p_seed.get("journals", []):
                    j = Journal(
                        publisher_id=pub.id,
                        name=j_seed["name"],
                        code=j_seed["code"],
                        citation_style=j_seed["citation_style"],
                        required_sections=j_seed["required_sections"],
                        max_words=j_seed.get("max_words"),
                        abstract_max_words=j_seed.get("abstract_max_words")
                    )
                    db.add(j)

        cite_count = await db.scalar(select(func.count(CitationStyle.id)))
        if not cite_count:
            for c_seed in SEED_CITATION_STYLES:
                cs = CitationStyle(
                    name=c_seed["name"],
                    code=c_seed["code"],
                    description=c_seed["description"],
                    formatting_rules=c_seed.get("formatting_rules", {})
                )
                db.add(cs)

        await db.commit()

    @classmethod
    async def get_publishers_from_db(cls, db: AsyncSession) -> List[Dict[str, Any]]:
        from app.models.models import Publisher
        result = await db.execute(select(Publisher).options(selectinload(Publisher.journals)))
        pubs = result.scalars().all()
        if not pubs:
            return SEED_PUBLISHERS
        
        out = []
        for p in pubs:
            out.append({
                "code": p.code,
                "name": p.name,
                "description": p.description,
                "journals": [
                    {
                        "code": j.code,
                        "name": j.name,
                        "citation_style": j.citation_style,
                        "required_sections": j.required_sections,
                        "max_words": j.max_words,
                        "abstract_max_words": j.abstract_max_words
                    }
                    for j in p.journals
                ]
            })
        return out
