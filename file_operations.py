#!/usr/bin/env python3
"""
File Operations Manager for Advanced MCP Server
Handles local file system operations with safety, batching, and backup capabilities
"""

import asyncio
import aiofiles
import json
import logging
import os
import shutil
import hashlib
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Union, Tuple
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class OperationType(Enum):
    """File operation types"""
    READ = "read"
    WRITE = "write"
    APPEND = "append"
    DELETE = "delete"
    COPY = "copy"
    MOVE = "move"
    MKDIR = "mkdir"
    RMDIR = "rmdir"
    EXISTS = "exists"
    STAT = "stat"
    LIST = "list"
    BACKUP = "backup"
    RESTORE = "restore"

class OperationStatus(Enum):
    """Operation status"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"
    ROLLED_BACK = "rolled_back"

@dataclass
class FileOperation:
    """File operation definition"""
    operation_id: str
    operation_type: OperationType
    source_path: str
    target_path: Optional[str] = None
    content: Optional[str] = None
    encoding: str = "utf-8"
    create_backup: bool = True
    overwrite: bool = False
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

@dataclass
class OperationResult:
    """File operation result"""
    operation_id: str
    operation_type: OperationType
    status: OperationStatus
    source_path: str
    target_path: Optional[str] = None
    backup_path: Optional[str] = None
    bytes_processed: int = 0
    checksum: Optional[str] = None
    error_message: Optional[str] = None
    execution_time_seconds: float = 0.0
    timestamp: str = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()

class FileOperations:
    """Manages file operations with safety features and batch processing"""
    
    def __init__(self):
        self.initialized = False
        self.operation_history = []
        self.backup_directory = "backups"
        self.temp_directory = "temp"
        
        # Configuration
        self.max_file_size_mb = 100
        self.max_batch_size = 1000
        self.create_backups = True
        self.verify_checksums = True
        self.safe_mode = True  # Prevents dangerous operations
        
        # Allowed file extensions for security
        self.allowed_extensions = {
            '.txt', '.json', '.csv', '.xml', '.yaml', '.yml', '.md', '.log',
            '.py', '.js', '.html', '.css', '.sql', '.ini', '.cfg', '.conf',
            '.bat', '.sh', '.ps1', '.psm1', '.psd1'
        }
        
        # Blocked directories for security
        self.blocked_directories = {
            'C:\\Windows', 'C:\\Program Files', 'C:\\Program Files (x86)',
            '/etc', '/bin', '/sbin', '/usr/bin', '/usr/sbin', '/root'
        }
        
        # Statistics
        self.total_operations = 0
        self.successful_operations = 0
        self.failed_operations = 0
        self.bytes_processed = 0
        
        logger.info("FileOperations initialized")
    
    async def initialize(self):
        """Initialize the file operations manager"""
        try:
            # Create required directories
            os.makedirs(self.backup_directory, exist_ok=True)
            os.makedirs(self.temp_directory, exist_ok=True)
            
            # Verify permissions
            await self._verify_permissions()
            
            self.initialized = True
            logger.info("FileOperations initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize FileOperations: {e}")
            raise
    
    async def _verify_permissions(self):
        """Verify we have necessary permissions"""
        try:
            # Test write permissions in backup directory
            test_file = os.path.join(self.backup_directory, "test_permissions.tmp")
            async with aiofiles.open(test_file, 'w') as f:
                await f.write("test")
            os.remove(test_file)
            
            # Test write permissions in temp directory
            test_file = os.path.join(self.temp_directory, "test_permissions.tmp")
            async with aiofiles.open(test_file, 'w') as f:
                await f.write("test")
            os.remove(test_file)
            
            logger.info("File operation permissions verified")
            
        except Exception as e:
            logger.error(f"Permission verification failed: {e}")
            raise
    
    def _validate_path(self, file_path: str) -> Tuple[bool, str]:
        """Validate file path for security"""
        try:
            # Convert to absolute path
            abs_path = os.path.abspath(file_path)
            
            # Check for path traversal
            if '..' in file_path:
                return False, "Path traversal detected"
            
            # Check blocked directories
            for blocked_dir in self.blocked_directories:
                if abs_path.startswith(blocked_dir):
                    return False, f"Access to {blocked_dir} is blocked"
            
            # Check file extension if in safe mode
            if self.safe_mode:
                file_ext = Path(file_path).suffix.lower()
                if file_ext and file_ext not in self.allowed_extensions:
                    return False, f"File extension {file_ext} not allowed"
            
            return True, ""
            
        except Exception as e:
            return False, f"Path validation error: {e}"
    
    def _generate_backup_path(self, file_path: str) -> str:
        """Generate backup path for a file"""
        file_path_obj = Path(file_path)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        backup_name = f"{file_path_obj.stem}_{timestamp}{file_path_obj.suffix}"
        return os.path.join(self.backup_directory, backup_name)
    
    async def _calculate_checksum(self, file_path: str) -> str:
        """Calculate SHA-256 checksum of a file"""
        try:
            hash_sha256 = hashlib.sha256()
            async with aiofiles.open(file_path, 'rb') as f:
                while chunk := await f.read(8192):
                    hash_sha256.update(chunk)
            return hash_sha256.hexdigest()
        except Exception as e:
            logger.error(f"Failed to calculate checksum for {file_path}: {e}")
            return ""
    
    async def _create_backup(self, file_path: str) -> str:
        """Create backup of a file"""
        if not os.path.exists(file_path):
            return ""
        
        try:
            backup_path = self._generate_backup_path(file_path)
            shutil.copy2(file_path, backup_path)
            logger.info(f"Created backup: {file_path} -> {backup_path}")
            return backup_path
        except Exception as e:
            logger.error(f"Failed to create backup for {file_path}: {e}")
            raise
    
    async def write_file(self, file_path: str, content: str, encoding: str = "utf-8") -> Dict[str, Any]:
        """Write content to a file"""
        operation_id = f"write_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
        start_time = datetime.now()
        
        try:
            # Validate path
            is_valid, error_msg = self._validate_path(file_path)
            if not is_valid:
                raise ValueError(error_msg)
            
            # Check file size
            content_bytes = content.encode(encoding)
            size_mb = len(content_bytes) / (1024 * 1024)
            if size_mb > self.max_file_size_mb:
                raise ValueError(f"Content size ({size_mb:.2f}MB) exceeds limit ({self.max_file_size_mb}MB)")
            
            backup_path = ""
            
            # Create backup if file exists and backups are enabled
            if self.create_backups and os.path.exists(file_path):
                backup_path = await self._create_backup(file_path)
            
            # Ensure parent directory exists
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            # Write file
            async with aiofiles.open(file_path, 'w', encoding=encoding) as f:
                await f.write(content)
            
            # Calculate checksum if verification is enabled
            checksum = ""
            if self.verify_checksums:
                checksum = await self._calculate_checksum(file_path)
            
            # Create result
            execution_time = (datetime.now() - start_time).total_seconds()
            result = OperationResult(
                operation_id=operation_id,
                operation_type=OperationType.WRITE,
                status=OperationStatus.COMPLETED,
                source_path=file_path,
                backup_path=backup_path,
                bytes_processed=len(content_bytes),
                checksum=checksum,
                execution_time_seconds=execution_time
            )
            
            # Update statistics
            self.total_operations += 1
            self.successful_operations += 1
            self.bytes_processed += len(content_bytes)
            
            # Add to history
            self.operation_history.append(result)
            
            logger.info(f"File written successfully: {file_path} ({len(content_bytes)} bytes)")
            
            return {
                "operation_id": operation_id,
                "status": "completed",
                "file_path": file_path,
                "bytes_written": len(content_bytes),
                "backup_path": backup_path,
                "checksum": checksum,
                "execution_time": execution_time
            }
            
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            result = OperationResult(
                operation_id=operation_id,
                operation_type=OperationType.WRITE,
                status=OperationStatus.FAILED,
                source_path=file_path,
                error_message=str(e),
                execution_time_seconds=execution_time
            )
            
            self.total_operations += 1
            self.failed_operations += 1
            self.operation_history.append(result)
            
            logger.error(f"Failed to write file {file_path}: {e}")
            raise
    
    async def read_file(self, file_path: str, encoding: str = "utf-8") -> str:
        """Read content from a file"""
        operation_id = f"read_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
        start_time = datetime.now()
        
        try:
            # Validate path
            is_valid, error_msg = self._validate_path(file_path)
            if not is_valid:
                raise ValueError(error_msg)
            
            # Check if file exists
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"File not found: {file_path}")
            
            # Check file size
            file_size = os.path.getsize(file_path)
            size_mb = file_size / (1024 * 1024)
            if size_mb > self.max_file_size_mb:
                raise ValueError(f"File size ({size_mb:.2f}MB) exceeds limit ({self.max_file_size_mb}MB)")
            
            # Read file
            async with aiofiles.open(file_path, 'r', encoding=encoding) as f:
                content = await f.read()
            
            # Calculate checksum if verification is enabled
            checksum = ""
            if self.verify_checksums:
                checksum = await self._calculate_checksum(file_path)
            
            # Create result
            execution_time = (datetime.now() - start_time).total_seconds()
            result = OperationResult(
                operation_id=operation_id,
                operation_type=OperationType.READ,
                status=OperationStatus.COMPLETED,
                source_path=file_path,
                bytes_processed=file_size,
                checksum=checksum,
                execution_time_seconds=execution_time
            )
            
            # Update statistics
            self.total_operations += 1
            self.successful_operations += 1
            self.bytes_processed += file_size
            
            # Add to history
            self.operation_history.append(result)
            
            logger.info(f"File read successfully: {file_path} ({file_size} bytes)")
            
            return content
            
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            result = OperationResult(
                operation_id=operation_id,
                operation_type=OperationType.READ,
                status=OperationStatus.FAILED,
                source_path=file_path,
                error_message=str(e),
                execution_time_seconds=execution_time
            )
            
            self.total_operations += 1
            self.failed_operations += 1
            self.operation_history.append(result)
            
            logger.error(f"Failed to read file {file_path}: {e}")
            raise
    
    async def append_file(self, file_path: str, content: str, encoding: str = "utf-8") -> Dict[str, Any]:
        """Append content to a file"""
        operation_id = f"append_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
        start_time = datetime.now()
        
        try:
            # Validate path
            is_valid, error_msg = self._validate_path(file_path)
            if not is_valid:
                raise ValueError(error_msg)
            
            content_bytes = content.encode(encoding)
            backup_path = ""
            
            # Create backup if file exists and backups are enabled
            if self.create_backups and os.path.exists(file_path):
                backup_path = await self._create_backup(file_path)
            
            # Ensure parent directory exists
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            # Append to file
            async with aiofiles.open(file_path, 'a', encoding=encoding) as f:
                await f.write(content)
            
            # Calculate checksum if verification is enabled
            checksum = ""
            if self.verify_checksums:
                checksum = await self._calculate_checksum(file_path)
            
            # Create result
            execution_time = (datetime.now() - start_time).total_seconds()
            result = OperationResult(
                operation_id=operation_id,
                operation_type=OperationType.APPEND,
                status=OperationStatus.COMPLETED,
                source_path=file_path,
                backup_path=backup_path,
                bytes_processed=len(content_bytes),
                checksum=checksum,
                execution_time_seconds=execution_time
            )
            
            # Update statistics
            self.total_operations += 1
            self.successful_operations += 1
            self.bytes_processed += len(content_bytes)
            
            # Add to history
            self.operation_history.append(result)
            
            logger.info(f"Content appended successfully: {file_path} ({len(content_bytes)} bytes)")
            
            return {
                "operation_id": operation_id,
                "status": "completed",
                "file_path": file_path,
                "bytes_appended": len(content_bytes),
                "backup_path": backup_path,
                "checksum": checksum,
                "execution_time": execution_time
            }
            
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            result = OperationResult(
                operation_id=operation_id,
                operation_type=OperationType.APPEND,
                status=OperationStatus.FAILED,
                source_path=file_path,
                error_message=str(e),
                execution_time_seconds=execution_time
            )
            
            self.total_operations += 1
            self.failed_operations += 1
            self.operation_history.append(result)
            
            logger.error(f"Failed to append to file {file_path}: {e}")
            raise
    
    async def delete_file(self, file_path: str) -> Dict[str, Any]:
        """Delete a file"""
        operation_id = f"delete_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
        start_time = datetime.now()
        
        try:
            # Validate path
            is_valid, error_msg = self._validate_path(file_path)
            if not is_valid:
                raise ValueError(error_msg)
            
            # Check if file exists
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"File not found: {file_path}")
            
            file_size = os.path.getsize(file_path)
            backup_path = ""
            
            # Create backup before deletion if backups are enabled
            if self.create_backups:
                backup_path = await self._create_backup(file_path)
            
            # Delete file
            os.remove(file_path)
            
            # Create result
            execution_time = (datetime.now() - start_time).total_seconds()
            result = OperationResult(
                operation_id=operation_id,
                operation_type=OperationType.DELETE,
                status=OperationStatus.COMPLETED,
                source_path=file_path,
                backup_path=backup_path,
                bytes_processed=file_size,
                execution_time_seconds=execution_time
            )
            
            # Update statistics
            self.total_operations += 1
            self.successful_operations += 1
            self.bytes_processed += file_size
            
            # Add to history
            self.operation_history.append(result)
            
            logger.info(f"File deleted successfully: {file_path} (backup: {backup_path})")
            
            return {
                "operation_id": operation_id,
                "status": "completed",
                "file_path": file_path,
                "backup_path": backup_path,
                "execution_time": execution_time
            }
            
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            result = OperationResult(
                operation_id=operation_id,
                operation_type=OperationType.DELETE,
                status=OperationStatus.FAILED,
                source_path=file_path,
                error_message=str(e),
                execution_time_seconds=execution_time
            )
            
            self.total_operations += 1
            self.failed_operations += 1
            self.operation_history.append(result)
            
            logger.error(f"Failed to delete file {file_path}: {e}")
            raise
    
    async def copy_file(self, source_path: str, target_path: str) -> Dict[str, Any]:
        """Copy a file"""
        operation_id = f"copy_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
        start_time = datetime.now()
        
        try:
            # Validate paths
            is_valid, error_msg = self._validate_path(source_path)
            if not is_valid:
                raise ValueError(f"Source path invalid: {error_msg}")
            
            is_valid, error_msg = self._validate_path(target_path)
            if not is_valid:
                raise ValueError(f"Target path invalid: {error_msg}")
            
            # Check if source exists
            if not os.path.exists(source_path):
                raise FileNotFoundError(f"Source file not found: {source_path}")
            
            file_size = os.path.getsize(source_path)
            backup_path = ""
            
            # Create backup if target exists and backups are enabled
            if self.create_backups and os.path.exists(target_path):
                backup_path = await self._create_backup(target_path)
            
            # Ensure target directory exists
            os.makedirs(os.path.dirname(target_path), exist_ok=True)
            
            # Copy file
            shutil.copy2(source_path, target_path)
            
            # Calculate checksum if verification is enabled
            checksum = ""
            if self.verify_checksums:
                checksum = await self._calculate_checksum(target_path)
            
            # Create result
            execution_time = (datetime.now() - start_time).total_seconds()
            result = OperationResult(
                operation_id=operation_id,
                operation_type=OperationType.COPY,
                status=OperationStatus.COMPLETED,
                source_path=source_path,
                target_path=target_path,
                backup_path=backup_path,
                bytes_processed=file_size,
                checksum=checksum,
                execution_time_seconds=execution_time
            )
            
            # Update statistics
            self.total_operations += 1
            self.successful_operations += 1
            self.bytes_processed += file_size
            
            # Add to history
            self.operation_history.append(result)
            
            logger.info(f"File copied successfully: {source_path} -> {target_path}")
            
            return {
                "operation_id": operation_id,
                "status": "completed",
                "source_path": source_path,
                "target_path": target_path,
                "backup_path": backup_path,
                "bytes_copied": file_size,
                "checksum": checksum,
                "execution_time": execution_time
            }
            
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            result = OperationResult(
                operation_id=operation_id,
                operation_type=OperationType.COPY,
                status=OperationStatus.FAILED,
                source_path=source_path,
                target_path=target_path,
                error_message=str(e),
                execution_time_seconds=execution_time
            )
            
            self.total_operations += 1
            self.failed_operations += 1
            self.operation_history.append(result)
            
            logger.error(f"Failed to copy file {source_path} to {target_path}: {e}")
            raise
    
    async def batch_operations(self, operations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Perform batch operations on multiple files"""
        batch_id = f"batch_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
        start_time = datetime.now()
        
        if len(operations) > self.max_batch_size:
            raise ValueError(f"Batch size ({len(operations)}) exceeds limit ({self.max_batch_size})")
        
        results = []
        successful_count = 0
        failed_count = 0
        total_bytes = 0
        
        logger.info(f"Starting batch operation {batch_id} with {len(operations)} operations")
        
        try:
            for i, op in enumerate(operations):
                operation_type = op.get("operation")
                file_path = op.get("file_path")
                
                try:
                    if operation_type == "read":
                        content = await self.read_file(file_path, op.get("encoding", "utf-8"))
                        results.append({
                            "operation": operation_type,
                            "file_path": file_path,
                            "status": "completed",
                            "content": content[:100] + "..." if len(content) > 100 else content  # Truncate for batch response
                        })
                        successful_count += 1
                        total_bytes += len(content.encode())
                    
                    elif operation_type == "write":
                        result = await self.write_file(
                            file_path, 
                            op.get("content", ""), 
                            op.get("encoding", "utf-8")
                        )
                        results.append({
                            "operation": operation_type,
                            "file_path": file_path,
                            "status": "completed",
                            "bytes_written": result["bytes_written"]
                        })
                        successful_count += 1
                        total_bytes += result["bytes_written"]
                    
                    elif operation_type == "delete":
                        result = await self.delete_file(file_path)
                        results.append({
                            "operation": operation_type,
                            "file_path": file_path,
                            "status": "completed",
                            "backup_path": result["backup_path"]
                        })
                        successful_count += 1
                    
                    elif operation_type == "copy":
                        target_path = op.get("target_path")
                        if not target_path:
                            raise ValueError("Target path required for copy operation")
                        
                        result = await self.copy_file(file_path, target_path)
                        results.append({
                            "operation": operation_type,
                            "source_path": file_path,
                            "target_path": target_path,
                            "status": "completed",
                            "bytes_copied": result["bytes_copied"]
                        })
                        successful_count += 1
                        total_bytes += result["bytes_copied"]
                    
                    else:
                        raise ValueError(f"Unknown operation type: {operation_type}")
                
                except Exception as e:
                    logger.error(f"Batch operation {i+1} failed: {e}")
                    results.append({
                        "operation": operation_type,
                        "file_path": file_path,
                        "status": "failed",
                        "error": str(e)
                    })
                    failed_count += 1
            
            execution_time = (datetime.now() - start_time).total_seconds()
            
            logger.info(f"Batch operation {batch_id} completed: {successful_count} successful, {failed_count} failed")
            
            return {
                "batch_id": batch_id,
                "total_operations": len(operations),
                "successful_operations": successful_count,
                "failed_operations": failed_count,
                "total_bytes_processed": total_bytes,
                "execution_time_seconds": execution_time,
                "results": results
            }
            
        except Exception as e:
            logger.error(f"Batch operation {batch_id} failed: {e}")
            raise
    
    async def list_directory(self, directory_path: str, recursive: bool = False) -> Dict[str, Any]:
        """List files and directories"""
        operation_id = f"list_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
        
        try:
            # Validate path
            is_valid, error_msg = self._validate_path(directory_path)
            if not is_valid:
                raise ValueError(error_msg)
            
            if not os.path.exists(directory_path):
                raise FileNotFoundError(f"Directory not found: {directory_path}")
            
            if not os.path.isdir(directory_path):
                raise ValueError(f"Path is not a directory: {directory_path}")
            
            files = []
            directories = []
            
            if recursive:
                for root, dirs, filenames in os.walk(directory_path):
                    for dirname in dirs:
                        dir_path = os.path.join(root, dirname)
                        directories.append({
                            "name": dirname,
                            "path": dir_path,
                            "relative_path": os.path.relpath(dir_path, directory_path)
                        })
                    
                    for filename in filenames:
                        file_path = os.path.join(root, filename)
                        file_stat = os.stat(file_path)
                        files.append({
                            "name": filename,
                            "path": file_path,
                            "relative_path": os.path.relpath(file_path, directory_path),
                            "size": file_stat.st_size,
                            "modified": datetime.fromtimestamp(file_stat.st_mtime).isoformat()
                        })
            else:
                for item in os.listdir(directory_path):
                    item_path = os.path.join(directory_path, item)
                    if os.path.isdir(item_path):
                        directories.append({
                            "name": item,
                            "path": item_path,
                            "relative_path": item
                        })
                    else:
                        file_stat = os.stat(item_path)
                        files.append({
                            "name": item,
                            "path": item_path,
                            "relative_path": item,
                            "size": file_stat.st_size,
                            "modified": datetime.fromtimestamp(file_stat.st_mtime).isoformat()
                        })
            
            return {
                "operation_id": operation_id,
                "directory": directory_path,
                "recursive": recursive,
                "file_count": len(files),
                "directory_count": len(directories),
                "files": files,
                "directories": directories
            }
            
        except Exception as e:
            logger.error(f"Failed to list directory {directory_path}: {e}")
            raise
    
    async def get_file_info(self, file_path: str) -> Dict[str, Any]:
        """Get file information and metadata"""
        try:
            # Validate path
            is_valid, error_msg = self._validate_path(file_path)
            if not is_valid:
                raise ValueError(error_msg)
            
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"File not found: {file_path}")
            
            stat = os.stat(file_path)
            
            info = {
                "path": file_path,
                "name": os.path.basename(file_path),
                "extension": Path(file_path).suffix,
                "size": stat.st_size,
                "size_mb": stat.st_size / (1024 * 1024),
                "is_file": os.path.isfile(file_path),
                "is_directory": os.path.isdir(file_path),
                "created": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                "accessed": datetime.fromtimestamp(stat.st_atime).isoformat(),
                "permissions": oct(stat.st_mode)[-3:]
            }
            
            # Add checksum for files if verification is enabled
            if self.verify_checksums and os.path.isfile(file_path):
                info["checksum"] = await self._calculate_checksum(file_path)
            
            return info
            
        except Exception as e:
            logger.error(f"Failed to get file info for {file_path}: {e}")
            raise
    
    async def restore_backup(self, backup_path: str, target_path: str) -> Dict[str, Any]:
        """Restore a file from backup"""
        operation_id = f"restore_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
        start_time = datetime.now()
        
        try:
            # Validate paths
            if not os.path.exists(backup_path):
                raise FileNotFoundError(f"Backup file not found: {backup_path}")
            
            is_valid, error_msg = self._validate_path(target_path)
            if not is_valid:
                raise ValueError(f"Target path invalid: {error_msg}")
            
            file_size = os.path.getsize(backup_path)
            current_backup = ""
            
            # Create backup of current file if it exists
            if os.path.exists(target_path):
                current_backup = await self._create_backup(target_path)
            
            # Restore from backup
            shutil.copy2(backup_path, target_path)
            
            execution_time = (datetime.now() - start_time).total_seconds()
            
            logger.info(f"File restored from backup: {backup_path} -> {target_path}")
            
            return {
                "operation_id": operation_id,
                "status": "completed",
                "backup_path": backup_path,
                "target_path": target_path,
                "current_file_backup": current_backup,
                "bytes_restored": file_size,
                "execution_time": execution_time
            }
            
        except Exception as e:
            logger.error(f"Failed to restore from backup {backup_path}: {e}")
            raise
    
    async def health_check(self) -> Dict[str, Any]:
        """Check health of the file operations manager"""
        try:
            # Check directory permissions
            backup_writable = os.access(self.backup_directory, os.W_OK)
            temp_writable = os.access(self.temp_directory, os.W_OK)
            
            # Get backup directory size
            backup_size = 0
            backup_files = 0
            if os.path.exists(self.backup_directory):
                for root, dirs, files in os.walk(self.backup_directory):
                    backup_files += len(files)
                    for file in files:
                        backup_size += os.path.getsize(os.path.join(root, file))
            
            return {
                "status": "healthy" if self.initialized else "not_initialized",
                "directories": {
                    "backup_directory": self.backup_directory,
                    "temp_directory": self.temp_directory,
                    "backup_writable": backup_writable,
                    "temp_writable": temp_writable
                },
                "statistics": {
                    "total_operations": self.total_operations,
                    "successful_operations": self.successful_operations,
                    "failed_operations": self.failed_operations,
                    "success_rate": (self.successful_operations / max(1, self.total_operations)) * 100,
                    "total_bytes_processed": self.bytes_processed,
                    "total_bytes_processed_mb": self.bytes_processed / (1024 * 1024)
                },
                "backups": {
                    "backup_files": backup_files,
                    "backup_size_bytes": backup_size,
                    "backup_size_mb": backup_size / (1024 * 1024)
                },
                "configuration": {
                    "max_file_size_mb": self.max_file_size_mb,
                    "max_batch_size": self.max_batch_size,
                    "create_backups": self.create_backups,
                    "verify_checksums": self.verify_checksums,
                    "safe_mode": self.safe_mode,
                    "allowed_extensions": len(self.allowed_extensions),
                    "blocked_directories": len(self.blocked_directories)
                },
                "recent_operations": len([op for op in self.operation_history if 
                    datetime.fromisoformat(op.timestamp) > datetime.now() - timedelta(hours=1)])
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
    
    async def cleanup_old_backups(self, days_old: int = 30) -> Dict[str, Any]:
        """Clean up old backup files"""
        try:
            cutoff_date = datetime.now() - timedelta(days=days_old)
            deleted_files = 0
            freed_bytes = 0
            
            for root, dirs, files in os.walk(self.backup_directory):
                for file in files:
                    file_path = os.path.join(root, file)
                    file_mtime = datetime.fromtimestamp(os.path.getmtime(file_path))
                    
                    if file_mtime < cutoff_date:
                        file_size = os.path.getsize(file_path)
                        os.remove(file_path)
                        deleted_files += 1
                        freed_bytes += file_size
                        logger.info(f"Deleted old backup: {file_path}")
            
            return {
                "deleted_files": deleted_files,
                "freed_bytes": freed_bytes,
                "freed_mb": freed_bytes / (1024 * 1024),
                "cutoff_date": cutoff_date.isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to cleanup old backups: {e}")
            raise
    
    async def get_operation_history(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent operation history"""
        history_items = self.operation_history[-limit:]
        return [
            {
                "operation_id": item.operation_id,
                "operation_type": item.operation_type.value,
                "status": item.status.value,
                "source_path": item.source_path,
                "target_path": item.target_path,
                "bytes_processed": item.bytes_processed,
                "execution_time_seconds": item.execution_time_seconds,
                "timestamp": item.timestamp,
                "error_message": item.error_message
            }
            for item in history_items
        ]
