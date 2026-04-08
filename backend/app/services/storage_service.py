"""
Serviço de armazenamento seguro com criptografia em repouso.
Garante que os laudos originais do usuário sejam salvos de forma protegida.
"""
import os
import uuid
import base64
import hashlib
from dataclasses import dataclass
from pathlib import Path
from typing import Optional
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from app.config import get_settings

settings = get_settings()

class SecureStorage:
    def __init__(self):
        self.storage_root = Path(settings.storage_root)
        self.storage_root.mkdir(parents=True, exist_ok=True)
        
        # Garantir uma chave válida para o Fernet
        # Se a chave no config for uma senha comum, transformamos em chave Fernet usando KDF
        self.fernet = self._get_fernet_instance(settings.encryption_key)

    def _get_fernet_instance(self, secret: str) -> Fernet:
        """Deriva uma chave Fernet válida a partir de um segredo (string)."""
        # Usamos um salt fixo para que a chave seja determinística por ambiente
        salt = b'traduz_saude_salt_fixed' 
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(secret.encode()))
        return Fernet(key)

    def save_image(self, image_base64: str, file_hash: str) -> str:
        """
        Criptografa e salva uma imagem no disco.
        Retorna o nome do arquivo gerado.
        """
        try:
            # Remover cabeçalho se houver (data:image/png;base64,...)
            if "," in image_base64:
                image_base64 = image_base64.split(",")[1]
            
            # Dados originais em bytes
            data = base64.b64decode(image_base64)
            
            # Criptografar
            encrypted_data = self.fernet.encrypt(data)
            
            # Nome do arquivo (usamos UUID ou hash para evitar colisões e prever caminho)
            filename = f"{file_hash or uuid.uuid4()}.enc"
            filepath = self.storage_root / filename
            
            with open(filepath, "wb") as f:
                f.write(encrypted_data)
                
            return filename
        except Exception as e:
            print(f"Erro ao salvar imagem no storage: {e}")
            return ""

    def get_image(self, filename: str) -> bytes:
        """
        Lê e descriptografa uma imagem do disco.
        """
        try:
            filepath = self.storage_root / filename
            if not filepath.exists():
                return b""
                
            with open(filepath, "rb") as f:
                encrypted_data = f.read()
                
            # Descriptografar
            decrypted_data = self.fernet.decrypt(encrypted_data)
            return decrypted_data
        except Exception as e:
            print(f"Erro ao recuperar imagem do storage: {e}")
            return b""

    def delete_image(self, filename: str):
        """Remove um arquivo do storage."""
        try:
            filepath = self.storage_root / filename
            if filepath.exists():
                filepath.unlink()
        except Exception as e:
            print(f"Erro ao deletar imagem do storage: {e}")

# Instância única global
@dataclass(frozen=True)
class StoredAsset:
    storage_backend: str
    storage_key: str
    checksum_sha256: str
    byte_size: int


class StorageService:
    """Storage por referencia para o schema novo."""

    def __init__(self, root_path: Optional[str] = None):
        self.backend = settings.storage_backend
        self.root = Path(root_path or settings.storage_root)
        self.root.mkdir(parents=True, exist_ok=True)

    def save_bytes(
        self,
        *,
        document_id: str,
        asset_kind: str,
        data: bytes,
        file_name: Optional[str] = None,
        media_type: Optional[str] = None,
    ) -> StoredAsset:
        extension = self._infer_extension(file_name, media_type)
        safe_name = file_name or asset_kind
        safe_name = "".join(
            char if char.isalnum() or char in ("-", "_", ".") else "_"
            for char in safe_name
        )
        storage_key = (
            f"documents/{document_id}/{asset_kind}_{safe_name}{extension}"
            .replace("\\", "/")
        )
        target_path = self.root / storage_key
        target_path.parent.mkdir(parents=True, exist_ok=True)
        target_path.write_bytes(data)

        return StoredAsset(
            storage_backend=self.backend,
            storage_key=storage_key,
            checksum_sha256=hashlib.sha256(data).hexdigest(),
            byte_size=len(data),
        )

    def read_bytes(self, storage_key: str) -> Optional[bytes]:
        target_path = self.root / storage_key
        if not target_path.exists():
            return None
        return target_path.read_bytes()

    def read_base64(self, storage_key: str) -> Optional[str]:
        data = self.read_bytes(storage_key)
        if data is None:
            return None
        return base64.standard_b64encode(data).decode("utf-8")

    @staticmethod
    def _infer_extension(file_name: Optional[str], media_type: Optional[str]) -> str:
        if file_name and "." in file_name:
            return ""

        mapping = {
            "image/png": ".png",
            "image/jpeg": ".jpg",
            "image/webp": ".webp",
            "application/pdf": ".pdf",
            "text/plain": ".txt",
        }
        return mapping.get((media_type or "").lower(), "")


secure_storage = SecureStorage()
