"""
File Manager for handling file uploads, storage, and retrieval
"""

import os
import shutil
import uuid
from pathlib import Path
from typing import Optional, Dict, Any
import logging
from datetime import datetime

try:
    from fastapi import UploadFile
    import aiofiles
except ImportError:
    UploadFile = None
    aiofiles = None

logger = logging.getLogger(__name__)

class FileManager:
    """Manager for file operations in the CP Generator"""
    
    def __init__(self, base_path: str = "."):
        self.base_path = Path(base_path)
        self.upload_dir = self.base_path / "uploads"
        self.output_dir = self.base_path / "outputs"
        self.temp_dir = self.base_path / "temp"
        
        # Create directories
        self._create_directories()
        
        # File type mappings
        self.allowed_extensions = {
            'templates': ['.pdf', '.docx', '.doc', '.txt'],
            'recaps': ['.pdf', '.docx', '.doc', '.txt'],
            'outputs': ['.docx', '.pdf', '.html', '.txt']
        }
        
        # Max file sizes (in bytes)
        self.max_file_sizes = {
            'templates': 50 * 1024 * 1024,  # 50MB
            'recaps': 20 * 1024 * 1024,     # 20MB
        }
    
    def _create_directories(self):
        """Create necessary directories"""
        directories = [
            self.upload_dir / "templates",
            self.upload_dir / "recaps", 
            self.output_dir,
            self.temp_dir
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
            logger.info(f"Created directory: {directory}")
    
    async def save_upload(self, file: UploadFile, file_type: str) -> Path:
        """Save an uploaded file"""
        if not UploadFile or not aiofiles:
            raise ImportError("Required libraries not available")
        
        try:
            # Validate file
            self._validate_file(file, file_type)
            
            # Generate unique filename
            filename = self._generate_filename(file.filename)
            file_path = self.upload_dir / file_type / filename
            
            # Save file
            async with aiofiles.open(file_path, 'wb') as f:
                content = await file.read()
                await f.write(content)
            
            logger.info(f"File saved: {file_path}")
            return file_path
            
        except Exception as e:
            logger.error(f"Error saving file {file.filename}: {str(e)}")
            raise
    
    async def save_generated_cp(self, cp_data: Dict[str, Any], output_format: str) -> Path:
        """Save a generated charter party"""
        try:
            # Generate filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"charter_party_{timestamp}.{output_format}"
            file_path = self.output_dir / filename
            
            if output_format.lower() == "docx" and "document" in cp_data:
                # Save DOCX document
                cp_data["document"].save(str(file_path))
            elif output_format.lower() == "html":
                # Save HTML content
                async with aiofiles.open(file_path, 'w', encoding='utf-8') as f:
                    await f.write(cp_data.get("content", ""))
            else:
                # Save as text
                async with aiofiles.open(file_path, 'w', encoding='utf-8') as f:
                    await f.write(cp_data.get("content", ""))
            
            logger.info(f"Generated CP saved: {file_path}")
            return file_path
            
        except Exception as e:
            logger.error(f"Error saving generated CP: {str(e)}")
            raise
    
    def _validate_file(self, file: UploadFile, file_type: str):
        """Validate uploaded file"""
        if not file.filename:
            raise ValueError("No filename provided")
        
        # Check file extension
        file_ext = Path(file.filename).suffix.lower()
        allowed_exts = self.allowed_extensions.get(file_type, [])
        
        if file_ext not in allowed_exts:
            raise ValueError(f"Invalid file extension {file_ext}. Allowed: {allowed_exts}")
        
        # Check file size
        if hasattr(file, 'size') and file.size:
            max_size = self.max_file_sizes.get(file_type, float('inf'))
            if file.size > max_size:
                raise ValueError(f"File too large. Max size: {max_size / (1024*1024):.1f}MB")
    
    def _generate_filename(self, original_filename: str) -> str:
        """Generate unique filename"""
        file_ext = Path(original_filename).suffix
        unique_id = str(uuid.uuid4())[:8]
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Sanitize original filename
        safe_name = "".join(c for c in Path(original_filename).stem if c.isalnum() or c in "._-")[:20]
        
        return f"{safe_name}_{timestamp}_{unique_id}{file_ext}"
    
    def get_file_info(self, file_path: Path) -> Dict[str, Any]:
        """Get information about a file"""
        try:
            stat = file_path.stat()
            return {
                "path": str(file_path),
                "name": file_path.name,
                "size": stat.st_size,
                "created": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                "extension": file_path.suffix.lower(),
                "exists": file_path.exists()
            }
        except Exception as e:
            logger.error(f"Error getting file info for {file_path}: {str(e)}")
            return {"path": str(file_path), "exists": False, "error": str(e)}
    
    def list_files(self, directory: str, pattern: str = "*") -> List[Dict[str, Any]]:
        """List files in a directory"""
        try:
            dir_path = self.base_path / directory
            if not dir_path.exists():
                return []
            
            files = []
            for file_path in dir_path.glob(pattern):
                if file_path.is_file():
                    files.append(self.get_file_info(file_path))
            
            return sorted(files, key=lambda x: x.get("modified", ""), reverse=True)
            
        except Exception as e:
            logger.error(f"Error listing files in {directory}: {str(e)}")
            return []
    
    def delete_file(self, file_path: Path) -> bool:
        """Delete a file"""
        try:
            if file_path.exists():
                file_path.unlink()
                logger.info(f"File deleted: {file_path}")
                return True
            return False
        except Exception as e:
            logger.error(f"Error deleting file {file_path}: {str(e)}")
            return False
    
    def cleanup_temp_files(self, max_age_hours: int = 24):
        """Clean up temporary files older than specified hours"""
        try:
            current_time = datetime.now()
            cleaned_count = 0
            
            for file_path in self.temp_dir.glob("*"):
                if file_path.is_file():
                    file_age = datetime.fromtimestamp(file_path.stat().st_mtime)
                    age_hours = (current_time - file_age).total_seconds() / 3600
                    
                    if age_hours > max_age_hours:
                        if self.delete_file(file_path):
                            cleaned_count += 1
            
            logger.info(f"Cleaned up {cleaned_count} temporary files")
            return cleaned_count
            
        except Exception as e:
            logger.error(f"Error cleaning up temp files: {str(e)}")
            return 0
    
    def get_storage_stats(self) -> Dict[str, Any]:
        """Get storage statistics"""
        try:
            stats = {
                "upload_dir": self._get_directory_size(self.upload_dir),
                "output_dir": self._get_directory_size(self.output_dir),
                "temp_dir": self._get_directory_size(self.temp_dir),
                "total_files": 0,
                "total_size": 0
            }
            
            for dir_stat in stats.values():
                if isinstance(dir_stat, dict):
                    stats["total_files"] += dir_stat.get("file_count", 0)
                    stats["total_size"] += dir_stat.get("size_bytes", 0)
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting storage stats: {str(e)}")
            return {"error": str(e)}
    
    def _get_directory_size(self, directory: Path) -> Dict[str, Any]:
        """Get size and file count for a directory"""
        try:
            if not directory.exists():
                return {"size_bytes": 0, "size_mb": 0, "file_count": 0}
            
            total_size = 0
            file_count = 0
            
            for file_path in directory.rglob("*"):
                if file_path.is_file():
                    total_size += file_path.stat().st_size
                    file_count += 1
            
            return {
                "size_bytes": total_size,
                "size_mb": round(total_size / (1024 * 1024), 2),
                "file_count": file_count
            }
            
        except Exception as e:
            logger.error(f"Error getting directory size for {directory}: {str(e)}")
            return {"error": str(e)}
    
    def backup_file(self, file_path: Path, backup_dir: Optional[Path] = None) -> Optional[Path]:
        """Create a backup of a file"""
        try:
            if not file_path.exists():
                return None
            
            if backup_dir is None:
                backup_dir = self.base_path / "backups"
            
            backup_dir.mkdir(parents=True, exist_ok=True)
            
            # Generate backup filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"{file_path.stem}_{timestamp}{file_path.suffix}"
            backup_path = backup_dir / backup_name
            
            shutil.copy2(file_path, backup_path)
            logger.info(f"File backed up: {file_path} -> {backup_path}")
            
            return backup_path
            
        except Exception as e:
            logger.error(f"Error backing up file {file_path}: {str(e)}")
            return None
