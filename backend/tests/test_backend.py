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

        # 9. AI Assistant test
        ai_res = await ac.post(f"/api/v1/ai/assistant/{doc_id}", json={
            "action": "improve_wording",
            "selected_text": "We formulate network architecture search as a Markov decision process."
        }, headers=headers)
        assert ai_res.status_code == 200

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
