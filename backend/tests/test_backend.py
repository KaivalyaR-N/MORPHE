import pytest
import pytest_asyncio
import os
import asyncio
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.core.database import engine, Base


@pytest_asyncio.fixture(scope="module", autouse=True)
async def setup_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield


@pytest.mark.asyncio
async def test_auth_and_full_flow():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        # 1. Register User
        reg_res = await ac.post("/api/v1/auth/register", json={
            "email": "test@morphe.org",
            "password": "Password123!",
            "full_name": "Dr. Test Researcher",
            "role": "RESEARCHER"
        })
        assert reg_res.status_code == 200
        reg_data = reg_res.json()
        assert reg_data["success"] is True
        token = reg_data["data"]["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # 2. Login User
        login_res = await ac.post("/api/v1/auth/login", json={
            "email": "test@morphe.org",
            "password": "Password123!"
        })
        assert login_res.status_code == 200

        # 3. Create Project
        proj_res = await ac.post("/api/v1/projects", json={
            "name": "Neural Architecture Search Paper",
            "description": "Deep learning research document for IEEE publishing"
        }, headers=headers)
        assert proj_res.status_code == 200
        project_id = proj_res.json()["data"]["id"]

        # 4. Upload Document
        sample_paper = """Title: Efficient Neural Architecture Search via Reinforcement Learning

Abstract: Neural architecture search (NAS) has automated the design of deep neural networks. In this paper, we present an efficient NAS methodology utilizing reinforcement learning and ablation benchmarks. Our algorithm reduces search time by 40%.

Introduction
Deep neural networks have achieved state of the art results in computer vision and natural language processing. However, designing custom architectures remains a manual task.

Methodology
We formulate network architecture search as a Markov decision process. The agent samples network topologies evaluated on a validation dataset.

Results
Our experimental evaluation on CIFAR-10 demonstrates 96.4% accuracy with 3.2M parameters.

Conclusion
We introduced an efficient NAS framework with substantial speedups.

References
[1] Smith et al., "Deep Learning Architectures," Journal of AI, 2023.
[2] Johnson et al., "Reinforcement Learning for NAS," IEEE Transactions, 2022.
"""
        files = {"file": ("paper.txt", sample_paper.encode("utf-8"), "text/plain")}
        data = {"project_id": project_id}
        up_res = await ac.post("/api/v1/documents/upload", files=files, data=data, headers=headers)
        assert up_res.status_code == 200
        up_data = up_res.json()["data"]
        doc_id = up_data["id"]
        assert up_data["status"] == "COMPLETED"

        # 5. Get CDM
        cdm_res = await ac.get(f"/api/v1/cdm/{doc_id}", headers=headers)
        assert cdm_res.status_code == 200
        cdm_version = cdm_res.json()["data"]
        assert cdm_version["version_number"] == 1
        cdm_data = cdm_version["cdm_data"]
        assert cdm_data["metadata"]["title"] != ""

        # 6. Get NLP & Domain Analysis
        an_res = await ac.get(f"/api/v1/analysis/{doc_id}", headers=headers)
        assert an_res.status_code == 200
        an_data = an_res.json()["data"]
        assert "nlp_analysis" in an_data
        assert "domain_analysis" in an_data
        assert an_data["domain_analysis"]["primary_domain"] == "Computer Science"

        # 7. Get Validation
        val_res = await ac.get(f"/api/v1/validation/{doc_id}?publisher_code=IEEE", headers=headers)
        assert val_res.status_code == 200
        val_data = val_res.json()["data"]
        assert "validation" in val_data

        # 8. Update CDM (CDM Editor action)
        cdm_data["metadata"]["title"] = "Updated Efficient Neural Architecture Search Paper"
        update_res = await ac.post(f"/api/v1/cdm/{doc_id}/update", json={
            "cdm_data": cdm_data,
            "commit_message": "Refined title and expanded abstract"
        }, headers=headers)
        assert update_res.status_code == 200
        assert update_res.json()["data"]["version_number"] == 2

        # Rollback CDM test
        rb_res = await ac.post(f"/api/v1/cdm/{doc_id}/rollback/1", headers=headers)
        assert rb_res.status_code == 200
        assert rb_res.json()["data"]["version_number"] == 3
        assert "Rollback to Version 1" in rb_res.json()["data"]["commit_message"]

        # 9. AI Assistant test & conversation persistence
        ai_res = await ac.post(f"/api/v1/ai/assistant/{doc_id}", json={
            "action": "improve_wording",
            "selected_text": "We formulate network architecture search as a Markov decision process."
        }, headers=headers)
        assert ai_res.status_code == 200

        # Retrieve conversation history
        conv_res = await ac.get(f"/api/v1/ai/conversation/{doc_id}", headers=headers)
        assert conv_res.status_code == 200
        msgs = conv_res.json()["data"]["messages"]
        assert len(msgs) >= 2
        assert msgs[0]["role"] == "user"
        assert msgs[1]["role"] == "assistant"

        # 10. Generate Export Artifact (PDF)
        gen_res = await ac.post(f"/api/v1/generation/generate/{doc_id}", json={
            "format": "PDF",
            "publisher_code": "IEEE"
        }, headers=headers)
        assert gen_res.status_code == 200
        art_data = gen_res.json()["data"]
        export_id = art_data["id"]

        # 11. Download Export Artifact
        dl_res = await ac.get(f"/api/v1/exports/{export_id}/download", headers=headers)
        assert dl_res.status_code == 200
        assert len(dl_res.content) > 0

        # 12. Get Analytics
        analytics_res = await ac.get("/api/v1/analytics", headers=headers)
        assert analytics_res.status_code == 200
        assert analytics_res.json()["data"]["total_projects"] >= 1

        # 13. Test LaTeX generation with publisher class (ACM)
        latex_gen = await ac.post(f"/api/v1/generation/generate/{doc_id}", json={
            "format": "LATEX",
            "publisher_code": "ACM"
        }, headers=headers)
        assert latex_gen.status_code == 200
        assert latex_gen.json()["data"]["format"] == "LATEX"

        # 14. Test LaTeX Document upload & parsing
        sample_tex = r"""\documentclass{article}
\title{Quantum Circuit Optimization}
\author{Alice Smith \and Bob Jones}
\begin{abstract}
We demonstrate a scalable quantum circuit synthesis framework with verified depth bounds.
\end{abstract}
\section{Introduction}
Quantum computing promises exponential acceleration.
\section{Methodology}
We formulate pulse synthesis via optimal control.
\begin{thebibliography}{1}
\bibitem{q1} Nielsen and Chuang, Quantum Computation, 2010.
\end{thebibliography}
\end{document}"""
        tex_files = {"file": ("paper.tex", sample_tex.encode("utf-8"), "application/x-tex")}
        tex_data = {"project_id": project_id}
        tex_up = await ac.post("/api/v1/documents/upload", files=tex_files, data=tex_data, headers=headers)
        assert tex_up.status_code == 200
        tex_doc_id = tex_up.json()["data"]["id"]

        # Verify CDM extracted actual content rather than dummy strings
        tex_cdm = await ac.get(f"/api/v1/cdm/{tex_doc_id}", headers=headers)
        assert tex_cdm.status_code == 200
        sec1 = tex_cdm.json()["data"]["cdm_data"]["sections"][0]
        assert "Quantum computing" in sec1["content"]

        # 15. Knowledge base seeded publishers and styles
        pub_res = await ac.get("/api/v1/knowledge/publishers", headers=headers)
        assert pub_res.status_code == 200
        pubs = pub_res.json()["data"]
        assert len(pubs) >= 5
        pub_codes = [p["code"] for p in pubs]
        assert "IEEE" in pub_codes
        assert "ACM" in pub_codes

        styles_res = await ac.get("/api/v1/knowledge/styles", headers=headers)
        assert styles_res.status_code == 200
        styles = styles_res.json()["data"]
        assert len(styles) >= 4

        # 16. Citation Cross-referencing Validation test
        val_res = await ac.get(f"/api/v1/validation/{tex_doc_id}", headers=headers)
        assert val_res.status_code == 200
        val_data = val_res.json()["data"]["validation"]
        assert "citation_issues" in val_data
        assert "structural_issues" in val_data
        assert isinstance(val_data["citation_issues"], list)
        # 17. Download original uploaded file
        orig_dl = await ac.get(f"/api/v1/documents/{doc_id}/download-original", headers=headers)
        assert orig_dl.status_code == 200
        assert b"Efficient Neural Architecture Search" in orig_dl.content
        # 18. Update User Profile & Preferences (Settings)
        profile_res = await ac.put("/api/v1/auth/profile", json={
            "full_name": "Dr. Test Senior Researcher",
            "preferences": {
                "affiliation": "MIT CSAIL",
                "ai_model": "gemini-1.5-pro",
                "default_publisher": "IEEE"
            }
        }, headers=headers)
        assert profile_res.status_code == 200
        p_data = profile_res.json()["data"]
        assert p_data["full_name"] == "Dr. Test Senior Researcher"
        assert p_data["preferences"]["ai_model"] == "gemini-1.5-pro"

        # Verify /auth/me returns updated preferences
        me_res = await ac.get("/api/v1/auth/me", headers=headers)
        assert me_res.status_code == 200
        assert me_res.json()["data"]["preferences"]["affiliation"] == "MIT CSAIL"


