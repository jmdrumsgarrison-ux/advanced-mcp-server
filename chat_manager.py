#!/usr/bin/env python3
"""
Chat Manager for Advanced MCP Server
Handles Claude chat downloading, saving, and automatic cleanup
"""

import asyncio
import json
import logging
import os
import aiofiles
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from dataclasses import dataclass, asdict

logger = logging.getLogger(__name__)

@dataclass
class ChatMetadata:
    """Chat metadata structure"""
    chat_id: str
    title: str
    created_at: str
    downloaded_at: str
    message_count: int
    file_path: str
    size_bytes: int

@dataclass 
class MaintenanceRecord:
    """Maintenance cycle record"""
    timestamp: str
    downloads_count: int
    deletions_count: int
    status: str
    duration_seconds: float
    errors: List[str] = None

class ChatManager:
    """Manages Claude chat downloading, saving, and cleanup"""
    
    def __init__(self, api_manager, chat_library_path: str = "G:\\Chat Library\\advanced-mcp-server"):
        self.api_manager = api_manager
        self.chat_library_path = Path(chat_library_path)
        self.metadata_path = self.chat_library_path / "metadata"
        
        # Ensure directories exist
        self.chat_library_path.mkdir(parents=True, exist_ok=True)
        self.metadata_path.mkdir(parents=True, exist_ok=True)
        
        self.download_log_path = self.metadata_path / "download_log.json"
        self.deletion_log_path = self.metadata_path / "deletion_log.json"
        self.maintenance_schedule_path = self.metadata_path / "maintenance_schedule.json"
        
        logger.info(f"ChatManager initialized with library path: {self.chat_library_path}")
    
    async def download_and_save_chats(self, limit: int = None, older_than_hours: int = None) -> Dict[str, Any]:
        """Download chats from Claude and save them locally"""
        try:
            start_time = datetime.now()
            logger.info("Starting chat download and save process")
            
            # Get chats from Claude API (this will replace the placeholder implementation)
            chats_data = await self._fetch_claude_chats(limit=limit, older_than_hours=older_than_hours)
            
            saved_chats = []
            total_saved = 0
            
            for chat in chats_data.get("conversations", []):
                try:
                    # Create filename with timestamp and chat ID
                    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
                    chat_id = chat.get("id", "unknown")[:8]  # First 8 chars of ID
                    filename = f"{timestamp}_chat_{chat_id}.json"
                    file_path = self.chat_library_path / filename
                    
                    # Save chat data
                    async with aiofiles.open(file_path, 'w', encoding='utf-8') as f:
                        await f.write(json.dumps(chat, indent=2, ensure_ascii=False))
                    
                    # Create metadata record
                    file_size = file_path.stat().st_size
                    metadata = ChatMetadata(
                        chat_id=chat.get("id", "unknown"),
                        title=chat.get("title", "Untitled Chat"),
                        created_at=chat.get("created_at", "unknown"),
                        downloaded_at=datetime.now().isoformat(),
                        message_count=len(chat.get("messages", [])),
                        file_path=str(file_path),
                        size_bytes=file_size
                    )
                    
                    saved_chats.append(asdict(metadata))
                    total_saved += 1
                    
                    logger.info(f"Saved chat: {filename} ({file_size} bytes)")
                    
                except Exception as e:
                    logger.error(f"Failed to save individual chat {chat.get('id', 'unknown')}: {e}")
                    continue
            
            # Update download log
            await self._update_download_log(saved_chats)
            
            duration = (datetime.now() - start_time).total_seconds()
            
            result = {
                "status": "success",
                "total_downloaded": total_saved,
                "duration_seconds": duration,
                "saved_to": str(self.chat_library_path),
                "chats": saved_chats
            }
            
            logger.info(f"Download completed: {total_saved} chats saved in {duration:.2f}s")
            return result
            
        except Exception as e:
            logger.error(f"Chat download and save failed: {e}")
            return {
                "status": "error",
                "error": str(e),
                "total_downloaded": 0
            }
    
    async def cleanup_old_chats(self, days_old: int = 1) -> Dict[str, Any]:
        """Delete chats from Claude that are older than specified days"""
        try:
            start_time = datetime.now()
            logger.info(f"Starting cleanup of chats older than {days_old} days")
            
            # Calculate cutoff date
            cutoff_date = datetime.now() - timedelta(days=days_old)
            
            # Get list of chats to delete from Claude
            chats_to_delete = await self._get_chats_for_deletion(cutoff_date)
            
            deleted_chats = []
            total_deleted = 0
            
            for chat in chats_to_delete:
                try:
                    # Delete chat from Claude via API
                    deletion_result = await self._delete_claude_chat(chat["id"])
                    
                    if deletion_result.get("success"):
                        deleted_chats.append({
                            "chat_id": chat["id"],
                            "title": chat.get("title", "Unknown"),
                            "created_at": chat.get("created_at"),
                            "deleted_at": datetime.now().isoformat()
                        })
                        total_deleted += 1
                        logger.info(f"Deleted chat from Claude: {chat['id']}")
                    
                except Exception as e:
                    logger.error(f"Failed to delete chat {chat.get('id', 'unknown')}: {e}")
                    continue
            
            # Update deletion log
            await self._update_deletion_log(deleted_chats)
            
            duration = (datetime.now() - start_time).total_seconds()
            
            result = {
                "status": "success",
                "total_deleted": total_deleted,
                "duration_seconds": duration,
                "cutoff_date": cutoff_date.isoformat(),
                "deleted_chats": deleted_chats
            }
            
            logger.info(f"Cleanup completed: {total_deleted} chats deleted in {duration:.2f}s")
            return result
            
        except Exception as e:
            logger.error(f"Chat cleanup failed: {e}")
            return {
                "status": "error",
                "error": str(e),
                "total_deleted": 0
            }
    
    async def full_maintenance_cycle(self) -> Dict[str, Any]:
        """Complete maintenance: download current chats, then delete old ones"""
        try:
            start_time = datetime.now()
            logger.info("Starting full maintenance cycle")
            
            # Step 1: Download and save current chats
            download_result = await self.download_and_save_chats()
            
            # Step 2: Delete old chats from Claude (1+ days old)
            cleanup_result = await self.cleanup_old_chats(days_old=1)
            
            duration = (datetime.now() - start_time).total_seconds()
            
            # Create maintenance record
            maintenance_record = MaintenanceRecord(
                timestamp=datetime.now().isoformat(),
                downloads_count=download_result.get("total_downloaded", 0),
                deletions_count=cleanup_result.get("total_deleted", 0),
                status="success" if download_result.get("status") == "success" and cleanup_result.get("status") == "success" else "partial_success",
                duration_seconds=duration,
                errors=[]
            )
            
            # Add any errors
            if download_result.get("status") == "error":
                maintenance_record.errors.append(f"Download error: {download_result.get('error')}")
            if cleanup_result.get("status") == "error":
                maintenance_record.errors.append(f"Cleanup error: {cleanup_result.get('error')}")
            
            # Update maintenance schedule
            await self._update_maintenance_schedule(maintenance_record)
            
            result = {
                "status": maintenance_record.status,
                "maintenance_record": asdict(maintenance_record),
                "download_result": download_result,
                "cleanup_result": cleanup_result
            }
            
            logger.info(f"Full maintenance cycle completed in {duration:.2f}s")
            return result
            
        except Exception as e:
            logger.error(f"Full maintenance cycle failed: {e}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    async def get_chat_statistics(self) -> Dict[str, Any]:
        """Get statistics about saved chats and maintenance"""
        try:
            # Count saved chat files
            chat_files = list(self.chat_library_path.glob("*.json"))
            total_files = len(chat_files)
            
            # Calculate total size
            total_size = sum(f.stat().st_size for f in chat_files)
            
            # Load logs
            download_log = await self._load_json_file(self.download_log_path)
            deletion_log = await self._load_json_file(self.deletion_log_path)
            maintenance_schedule = await self._load_json_file(self.maintenance_schedule_path)
            
            # Get recent files
            recent_files = sorted(chat_files, key=lambda f: f.stat().st_mtime, reverse=True)[:5]
            
            return {
                "total_saved_chats": total_files,
                "total_size_bytes": total_size,
                "total_size_mb": round(total_size / (1024 * 1024), 2),
                "total_downloads": download_log.get("total_downloads", 0),
                "total_deletions": deletion_log.get("total_deletions", 0),
                "last_download": download_log.get("last_download"),
                "last_cleanup": deletion_log.get("last_cleanup"),
                "maintenance_enabled": maintenance_schedule.get("schedule", {}).get("enabled", False),
                "next_maintenance": maintenance_schedule.get("schedule", {}).get("next_run"),
                "recent_files": [f.name for f in recent_files],
                "library_path": str(self.chat_library_path)
            }
            
        except Exception as e:
            logger.error(f"Failed to get chat statistics: {e}")
            return {"error": str(e)}
    
    async def list_saved_chats(self, limit: int = 20) -> Dict[str, Any]:
        """List recently saved chat files"""
        try:
            chat_files = list(self.chat_library_path.glob("*.json"))
            
            # Sort by modification time (newest first)
            sorted_files = sorted(chat_files, key=lambda f: f.stat().st_mtime, reverse=True)
            
            # Limit results
            limited_files = sorted_files[:limit]
            
            chat_list = []
            for file_path in limited_files:
                stat = file_path.stat()
                chat_list.append({
                    "filename": file_path.name,
                    "path": str(file_path),
                    "size_bytes": stat.st_size,
                    "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                    "created": datetime.fromtimestamp(stat.st_ctime).isoformat()
                })
            
            return {
                "total_found": len(chat_files),
                "returned": len(chat_list),
                "chats": chat_list
            }
            
        except Exception as e:
            logger.error(f"Failed to list saved chats: {e}")
            return {"error": str(e)}
    
    # === PRIVATE HELPER METHODS ===
    
    async def _fetch_claude_chats(self, limit: int = None, older_than_hours: int = None) -> Dict[str, Any]:
        """Fetch chats from Claude API (enhanced implementation)"""
        try:
            # Use the API manager's claude chat functionality
            # This will need to be enhanced to implement real Claude API calls
            chat_filter = {}
            if older_than_hours:
                cutoff_time = datetime.now() - timedelta(hours=older_than_hours)
                chat_filter["before"] = cutoff_time.isoformat()
            
            # Call the enhanced API method
            result = await self.api_manager.fetch_claude_conversations(
                filter=chat_filter,
                limit=limit
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to fetch Claude chats: {e}")
            # Return empty result for now
            return {
                "conversations": [],
                "total": 0,
                "note": f"API fetch failed: {e}"
            }
    
    async def _get_chats_for_deletion(self, cutoff_date: datetime) -> List[Dict[str, Any]]:
        """Get list of chats older than cutoff date from Claude"""
        try:
            # Fetch chats older than cutoff date
            result = await self.api_manager.get_claude_chats_for_deletion(cutoff_date)
            return result.get("conversations", [])
            
        except Exception as e:
            logger.error(f"Failed to get chats for deletion: {e}")
            return []
    
    async def _delete_claude_chat(self, chat_id: str) -> Dict[str, Any]:
        """Delete a specific chat from Claude"""
        try:
            result = await self.api_manager.delete_claude_chat(chat_id)
            return result
            
        except Exception as e:
            logger.error(f"Failed to delete Claude chat {chat_id}: {e}")
            return {"success": False, "error": str(e)}
    
    async def _update_download_log(self, saved_chats: List[Dict[str, Any]]):
        """Update the download log with new saves"""
        try:
            log_data = await self._load_json_file(self.download_log_path)
            
            log_data["last_download"] = datetime.now().isoformat()
            log_data["total_downloads"] = log_data.get("total_downloads", 0) + len(saved_chats)
            log_data["downloads"].extend(saved_chats)
            
            # Keep only last 100 download records
            log_data["downloads"] = log_data["downloads"][-100:]
            
            await self._save_json_file(self.download_log_path, log_data)
            
        except Exception as e:
            logger.error(f"Failed to update download log: {e}")
    
    async def _update_deletion_log(self, deleted_chats: List[Dict[str, Any]]):
        """Update the deletion log with deletions"""
        try:
            log_data = await self._load_json_file(self.deletion_log_path)
            
            log_data["last_cleanup"] = datetime.now().isoformat()
            log_data["total_deletions"] = log_data.get("total_deletions", 0) + len(deleted_chats)
            log_data["deletions"].extend(deleted_chats)
            
            # Keep only last 100 deletion records
            log_data["deletions"] = log_data["deletions"][-100:]
            
            await self._save_json_file(self.deletion_log_path, log_data)
            
        except Exception as e:
            logger.error(f"Failed to update deletion log: {e}")
    
    async def _update_maintenance_schedule(self, maintenance_record: MaintenanceRecord):
        """Update maintenance schedule and history"""
        try:
            schedule_data = await self._load_json_file(self.maintenance_schedule_path)
            
            # Update schedule
            schedule_data["schedule"]["last_run"] = maintenance_record.timestamp
            next_run = datetime.now() + timedelta(hours=schedule_data["schedule"]["interval_hours"])
            schedule_data["schedule"]["next_run"] = next_run.isoformat()
            
            # Add to history
            schedule_data["maintenance_history"].append(asdict(maintenance_record))
            
            # Keep only last 50 maintenance records
            schedule_data["maintenance_history"] = schedule_data["maintenance_history"][-50:]
            
            await self._save_json_file(self.maintenance_schedule_path, schedule_data)
            
        except Exception as e:
            logger.error(f"Failed to update maintenance schedule: {e}")
    
    async def _load_json_file(self, file_path: Path) -> Dict[str, Any]:
        """Load JSON file asynchronously"""
        try:
            if not file_path.exists():
                return {}
            
            async with aiofiles.open(file_path, 'r', encoding='utf-8') as f:
                content = await f.read()
                return json.loads(content)
                
        except Exception as e:
            logger.error(f"Failed to load JSON file {file_path}: {e}")
            return {}
    
    async def _save_json_file(self, file_path: Path, data: Dict[str, Any]):
        """Save JSON file asynchronously"""
        try:
            async with aiofiles.open(file_path, 'w', encoding='utf-8') as f:
                await f.write(json.dumps(data, indent=2, ensure_ascii=False))
                
        except Exception as e:
            logger.error(f"Failed to save JSON file {file_path}: {e}")
            raise

# === SCHEDULER INTEGRATION ===

class ChatMaintenanceScheduler:
    """Handles automatic 24-hour maintenance scheduling"""
    
    def __init__(self, chat_manager: ChatManager):
        self.chat_manager = chat_manager
        self.running = False
        self.task = None
    
    async def start_scheduler(self):
        """Start the 24-hour maintenance scheduler"""
        if self.running:
            return
        
        self.running = True
        self.task = asyncio.create_task(self._scheduler_loop())
        logger.info("Chat maintenance scheduler started")
    
    async def stop_scheduler(self):
        """Stop the maintenance scheduler"""
        self.running = False
        if self.task:
            self.task.cancel()
            try:
                await self.task
            except asyncio.CancelledError:
                pass
        logger.info("Chat maintenance scheduler stopped")
    
    async def _scheduler_loop(self):
        """Main scheduler loop - runs every hour and checks if maintenance is due"""
        try:
            while self.running:
                # Check if maintenance is due
                if await self._is_maintenance_due():
                    logger.info("24-hour maintenance cycle is due - starting automatic maintenance")
                    
                    try:
                        result = await self.chat_manager.full_maintenance_cycle()
                        if result.get("status") == "success":
                            logger.info("Automatic maintenance completed successfully")
                        else:
                            logger.warning(f"Automatic maintenance completed with issues: {result}")
                    except Exception as e:
                        logger.error(f"Automatic maintenance failed: {e}")
                
                # Wait 1 hour before next check
                await asyncio.sleep(3600)  # 1 hour
                
        except asyncio.CancelledError:
            logger.info("Scheduler loop cancelled")
        except Exception as e:
            logger.error(f"Scheduler loop error: {e}")
    
    async def _is_maintenance_due(self) -> bool:
        """Check if 24-hour maintenance is due"""
        try:
            schedule_data = await self.chat_manager._load_json_file(
                self.chat_manager.maintenance_schedule_path
            )
            
            if not schedule_data.get("schedule", {}).get("enabled", False):
                return False
            
            last_run_str = schedule_data.get("schedule", {}).get("last_run")
            if not last_run_str:
                # Never run before - do initial run
                return True
            
            last_run = datetime.fromisoformat(last_run_str.replace('Z', '+00:00'))
            interval_hours = schedule_data.get("schedule", {}).get("interval_hours", 24)
            
            # Check if enough time has passed
            time_since_last = datetime.now() - last_run.replace(tzinfo=None)
            return time_since_last.total_seconds() >= (interval_hours * 3600)
            
        except Exception as e:
            logger.error(f"Failed to check maintenance schedule: {e}")
            return False
