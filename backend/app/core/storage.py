import os
import hashlib
import uuid
import shutil
from typing import Tuple
from app.core.config import settings


class StorageService:
    def __init__(self, base_dir: str = settings.STORAGE_DIR, exports_dir: str = settings.EXPORTS_DIR):
        self.base_dir = base_dir
        self.exports_dir = exports_dir
        os.makedirs(self.base_dir, exist_ok=True)
        os.makedirs(self.exports_dir, exist_ok=True)

    def save_uploaded_file(self, file_content: bytes, original_filename: str) -> Tuple[str, str, int, str]:
        ext = os.path.splitext(original_filename)[1].lower()
        sha256_hash = hashlib.sha256(file_content).hexdigest()
        file_id = f"{uuid.uuid4()}{ext}"
        target_path = os.path.join(self.base_dir, file_id)
        
        with open(target_path, "wb") as f:
            f.write(file_content)
            
        file_size = len(file_content)
        return target_path, sha256_hash, file_size, ext

    def get_file_content(self, file_path: str) -> bytes:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        with open(file_path, "rb") as f:
            return f.read()

    def save_export_artifact(self, content: bytes, file_extension: str, prefix: str = "export") -> Tuple[str, int]:
        artifact_id = f"{prefix}_{uuid.uuid4()}{file_extension}"
        target_path = os.path.join(self.exports_dir, artifact_id)
        with open(target_path, "wb") as f:
            f.write(content)
        return target_path, len(content)


storage_service = StorageService()
