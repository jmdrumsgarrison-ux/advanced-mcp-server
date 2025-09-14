#!/usr/bin/env python3
"""
Session Manager for Advanced MCP Server
Handles session lifecycle, state management, and coordination
"""

import asyncio
import json
import logging
import uuid
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Union
from enum import Enum
from dataclasses import dataclass, asdict

logger = logging.getLogger(__name__)

class SessionStatus(Enum):
    """Session status enumeration"""
    INITIALIZING = "initializing"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETING = "completing"
    COMPLETED = "completed"
    FAILED = "failed"
    TIMEOUT = "timeout"

class SessionType(Enum):
    """Session type enumeration"""
    DEFAULT = "default"
    API_WORKFLOW = "api_workflow"
    FILE_PROCESSING = "file_processing"
    BATCH_OPERATION = "batch_operation"
    DEVELOPMENT = "development"
    TESTING = "testing"
    MAINTENANCE = "maintenance"

@dataclass
class SessionConfig:
    """Session configuration data class"""
    session_type: str
    timeout_minutes: int = 60
    max_operations: int = 1000
    auto_cleanup: bool = True
    persist_state: bool = True
    log_level: str = "INFO"
    resource_limits: Dict[str, Any] = None
    custom_settings: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.resource_limits is None:
            self.resource_limits = {}
        if self.custom_settings is None:
            self.custom_settings = {}

@dataclass
class SessionMetrics:
    """Session metrics tracking"""
    operations_count: int = 0
    api_calls_count: int = 0
    files_processed: int = 0
    errors_count: int = 0
    warnings_count: int = 0
    bytes_processed: int = 0
    execution_time_seconds: float = 0.0
    memory_usage_mb: float = 0.0
    
class Session:
    """Individual session instance"""
    
    def __init__(self, session_id: str, session_type: str, config: SessionConfig):
        self.session_id = session_id
        self.session_type = session_type
        self.config = config
        self.status = SessionStatus.INITIALIZING
        self.metrics = SessionMetrics()
        
        self.created_at = datetime.now()
        self.started_at = None
        self.completed_at = None
        self.last_activity = datetime.now()
        
        self.state_data = {}
        self.operation_history = []
        self.error_log = []
        
        # Resource tracking
        self.allocated_resources = set()
        self.open_connections = []
        self.temp_files = []
        
        logger.info(f"Session {session_id} created with type {session_type}")
    
    def update_activity(self):
        """Update last activity timestamp"""
        self.last_activity = datetime.now()
    
    def add_operation(self, operation_type: str, operation_data: Dict[str, Any] = None):
        """Add operation to history"""
        operation = {
            "timestamp": datetime.now().isoformat(),
            "type": operation_type,
            "data": operation_data or {},
            "operation_id": len(self.operation_history) + 1
        }
        self.operation_history.append(operation)
        self.metrics.operations_count += 1
        self.update_activity()
    
    def add_error(self, error_type: str, error_message: str, error_data: Dict[str, Any] = None):
        """Add error to log"""
        error = {
            "timestamp": datetime.now().isoformat(),
            "type": error_type,
            "message": error_message,
            "data": error_data or {},
            "error_id": len(self.error_log) + 1
        }
        self.error_log.append(error)
        self.metrics.errors_count += 1
        self.update_activity()
    
    def is_expired(self) -> bool:
        """Check if session has expired"""
        if self.status in [SessionStatus.COMPLETED, SessionStatus.FAILED]:
            return False
        
        timeout_delta = timedelta(minutes=self.config.timeout_minutes)
        return datetime.now() - self.last_activity > timeout_delta
    
    def get_runtime_duration(self) -> float:
        """Get runtime duration in seconds"""
        if self.started_at is None:
            return 0.0
        
        end_time = self.completed_at or datetime.now()
        return (end_time - self.started_at).total_seconds()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert session to dictionary"""
        return {
            "session_id": self.session_id,
            "session_type": self.session_type,
            "status": self.status.value,
            "config": asdict(self.config),
            "metrics": asdict(self.metrics),
            "created_at": self.created_at.isoformat(),
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "last_activity": self.last_activity.isoformat(),
            "runtime_duration": self.get_runtime_duration(),
            "is_expired": self.is_expired(),
            "operation_count": len(self.operation_history),
            "error_count": len(self.error_log),
            "allocated_resources": list(self.allocated_resources),
            "state_keys": list(self.state_data.keys())
        }

class SessionManager:
    """Manages session lifecycle and coordination"""
    
    def __init__(self):
        self.initialized = False
        self.sessions: Dict[str, Session] = {}
        self.session_templates = {}
        
        # Configuration
        self.max_concurrent_sessions = 100
        self.default_timeout_minutes = 60
        self.cleanup_interval_minutes = 10
        self.persistence_enabled = True
        
        # Background tasks
        self.cleanup_task = None
        self.monitoring_task = None
        
        # Statistics
        self.total_sessions_created = 0
        self.total_sessions_completed = 0
        self.total_sessions_failed = 0
        
        # Load session templates
        self._load_session_templates()
        
        logger.info("SessionManager initialized")
    
    async def initialize(self):
        """Initialize the session manager"""
        try:
            # Load persisted sessions if enabled
            if self.persistence_enabled:
                await self._load_persisted_sessions()
            
            # Start background tasks
            self.cleanup_task = asyncio.create_task(self._cleanup_expired_sessions())
            self.monitoring_task = asyncio.create_task(self._monitor_sessions())
            
            self.initialized = True
            logger.info("SessionManager initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize SessionManager: {e}")
            raise
    
    def _load_session_templates(self):
        """Load predefined session templates"""
        
        self.session_templates = {
            "default": SessionConfig(
                session_type="default",
                timeout_minutes=60,
                max_operations=1000,
                auto_cleanup=True,
                persist_state=True
            ),
            
            "api_workflow": SessionConfig(
                session_type="api_workflow",
                timeout_minutes=120,
                max_operations=5000,
                auto_cleanup=True,
                persist_state=True,
                resource_limits={"max_concurrent_api_calls": 10}
            ),
            
            "file_processing": SessionConfig(
                session_type="file_processing",
                timeout_minutes=180,
                max_operations=10000,
                auto_cleanup=True,
                persist_state=True,
                resource_limits={"max_file_size_mb": 100, "max_files": 1000}
            ),
            
            "batch_operation": SessionConfig(
                session_type="batch_operation",
                timeout_minutes=300,
                max_operations=50000,
                auto_cleanup=True,
                persist_state=True,
                resource_limits={"batch_size": 100, "max_concurrent_batches": 5}
            ),
            
            "development": SessionConfig(
                session_type="development",
                timeout_minutes=240,
                max_operations=2000,
                auto_cleanup=False,  # Keep for debugging
                persist_state=True,
                log_level="DEBUG"
            ),
            
            "testing": SessionConfig(
                session_type="testing",
                timeout_minutes=30,
                max_operations=500,
                auto_cleanup=True,
                persist_state=False,
                log_level="DEBUG"
            ),
            
            "maintenance": SessionConfig(
                session_type="maintenance",
                timeout_minutes=600,
                max_operations=100,
                auto_cleanup=False,
                persist_state=True,
                custom_settings={"allow_system_operations": True}
            )
        }
        
        logger.info(f"Loaded {len(self.session_templates)} session templates")
    
    async def start_session(self, session_type: str, config: Dict[str, Any] = None) -> str:
        """Start a new session"""
        if not self.initialized:
            raise RuntimeError("SessionManager not initialized")
        
        # Check session limits
        if len(self.sessions) >= self.max_concurrent_sessions:
            raise RuntimeError(f"Maximum concurrent sessions ({self.max_concurrent_sessions}) reached")
        
        # Generate session ID
        session_id = str(uuid.uuid4())
        
        try:
            # Get session configuration
            session_config = await self._get_session_config(session_type, config)
            
            # Create session
            session = Session(session_id, session_type, session_config)
            session.status = SessionStatus.INITIALIZING
            
            # Add to sessions
            self.sessions[session_id] = session
            self.total_sessions_created += 1
            
            # Initialize session
            await self._initialize_session(session)
            
            # Start session
            session.status = SessionStatus.ACTIVE
            session.started_at = datetime.now()
            session.add_operation("session_start", {"session_type": session_type})
            
            logger.info(f"Session {session_id} started successfully")
            
            return session_id
            
        except Exception as e:
            # Cleanup on failure
            if session_id in self.sessions:
                del self.sessions[session_id]
            
            logger.error(f"Failed to start session: {e}")
            raise
    
    async def _get_session_config(self, session_type: str, config_override: Dict[str, Any] = None) -> SessionConfig:
        """Get session configuration from template with overrides"""
        
        # Get base configuration from template
        if session_type in self.session_templates:
            base_config = self.session_templates[session_type]
        else:
            logger.warning(f"Unknown session type '{session_type}', using default")
            base_config = self.session_templates["default"]
        
        # Create copy of base config
        config_dict = asdict(base_config)
        
        # Apply overrides
        if config_override:
            for key, value in config_override.items():
                if key in config_dict:
                    config_dict[key] = value
                elif key in ["resource_limits", "custom_settings"]:
                    config_dict[key].update(value)
        
        return SessionConfig(**config_dict)
    
    async def _initialize_session(self, session: Session):
        """Initialize a session with resources and setup"""
        try:
            # Allocate basic resources
            session.allocated_resources.add("memory")
            session.allocated_resources.add("logging")
            
            # Setup based on session type
            if session.session_type == "api_workflow":
                session.allocated_resources.add("api_pool")
                session.state_data["api_clients"] = {}
            
            elif session.session_type == "file_processing":
                session.allocated_resources.add("file_handlers")
                session.state_data["file_queue"] = []
                session.state_data["processed_files"] = []
            
            elif session.session_type == "batch_operation":
                session.allocated_resources.add("batch_processor")
                session.state_data["batch_queue"] = []
                session.state_data["batch_results"] = []
            
            # Setup logging if configured
            if session.config.log_level:
                session.allocated_resources.add(f"logger_{session.session_id}")
            
            logger.info(f"Session {session.session_id} initialized with resources: {session.allocated_resources}")
            
        except Exception as e:
            logger.error(f"Failed to initialize session {session.session_id}: {e}")
            raise
    
    async def get_session_status(self, session_id: str = None) -> Dict[str, Any]:
        """Get status of a specific session or all sessions"""
        if session_id:
            if session_id not in self.sessions:
                raise ValueError(f"Session {session_id} not found")
            
            session = self.sessions[session_id]
            return session.to_dict()
        
        else:
            # Return summary of all sessions
            status_summary = {
                "total_sessions": len(self.sessions),
                "active_sessions": sum(1 for s in self.sessions.values() if s.status == SessionStatus.ACTIVE),
                "completed_sessions": sum(1 for s in self.sessions.values() if s.status == SessionStatus.COMPLETED),
                "failed_sessions": sum(1 for s in self.sessions.values() if s.status == SessionStatus.FAILED),
                "session_details": {sid: session.to_dict() for sid, session in self.sessions.items()}
            }
            
            return status_summary
    
    async def get_active_sessions_count(self) -> int:
        """Get count of active sessions"""
        return sum(1 for session in self.sessions.values() 
                  if session.status in [SessionStatus.ACTIVE, SessionStatus.INITIALIZING])
    
    async def get_all_sessions(self) -> List[Dict[str, Any]]:
        """Get information about all sessions"""
        return [session.to_dict() for session in self.sessions.values()]
    
    async def pause_session(self, session_id: str) -> Dict[str, Any]:
        """Pause a session"""
        if session_id not in self.sessions:
            raise ValueError(f"Session {session_id} not found")
        
        session = self.sessions[session_id]
        
        if session.status != SessionStatus.ACTIVE:
            raise ValueError(f"Session {session_id} is not active (status: {session.status.value})")
        
        session.status = SessionStatus.PAUSED
        session.add_operation("session_pause")
        
        logger.info(f"Session {session_id} paused")
        
        return {"session_id": session_id, "status": "paused", "timestamp": datetime.now().isoformat()}
    
    async def resume_session(self, session_id: str) -> Dict[str, Any]:
        """Resume a paused session"""
        if session_id not in self.sessions:
            raise ValueError(f"Session {session_id} not found")
        
        session = self.sessions[session_id]
        
        if session.status != SessionStatus.PAUSED:
            raise ValueError(f"Session {session_id} is not paused (status: {session.status.value})")
        
        session.status = SessionStatus.ACTIVE
        session.add_operation("session_resume")
        
        logger.info(f"Session {session_id} resumed")
        
        return {"session_id": session_id, "status": "active", "timestamp": datetime.now().isoformat()}
    
    async def complete_session(self, session_id: str, completion_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """Complete a session"""
        if session_id not in self.sessions:
            raise ValueError(f"Session {session_id} not found")
        
        session = self.sessions[session_id]
        
        try:
            session.status = SessionStatus.COMPLETING
            session.add_operation("session_complete", completion_data)
            
            # Cleanup session resources
            await self._cleanup_session(session)
            
            # Mark as completed
            session.status = SessionStatus.COMPLETED
            session.completed_at = datetime.now()
            session.metrics.execution_time_seconds = session.get_runtime_duration()
            
            self.total_sessions_completed += 1
            
            # Persist session if configured
            if session.config.persist_state:
                await self._persist_session(session)
            
            # Auto-cleanup if configured
            if session.config.auto_cleanup:
                await asyncio.sleep(1)  # Small delay before cleanup
                await self._remove_session(session_id)
            
            logger.info(f"Session {session_id} completed successfully")
            
            return {
                "session_id": session_id,
                "status": "completed",
                "duration_seconds": session.metrics.execution_time_seconds,
                "operations_count": session.metrics.operations_count,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            session.status = SessionStatus.FAILED
            session.add_error("completion_error", str(e))
            self.total_sessions_failed += 1
            
            logger.error(f"Failed to complete session {session_id}: {e}")
            raise
    
    async def _cleanup_session(self, session: Session):
        """Cleanup session resources"""
        try:
            # Close connections
            for connection in session.open_connections:
                try:
                    if hasattr(connection, 'close'):
                        await connection.close()
                except:
                    pass
            session.open_connections.clear()
            
            # Clean up temporary files
            import os
            for temp_file in session.temp_files:
                try:
                    if os.path.exists(temp_file):
                        os.remove(temp_file)
                except:
                    pass
            session.temp_files.clear()
            
            # Release allocated resources
            session.allocated_resources.clear()
            
            logger.info(f"Cleaned up resources for session {session.session_id}")
            
        except Exception as e:
            logger.error(f"Failed to cleanup session {session.session_id}: {e}")
    
    async def _remove_session(self, session_id: str):
        """Remove session from active sessions"""
        if session_id in self.sessions:
            del self.sessions[session_id]
            logger.info(f"Removed session {session_id} from active sessions")
    
    async def _cleanup_expired_sessions(self):
        """Background task to cleanup expired sessions"""
        while True:
            try:
                await asyncio.sleep(self.cleanup_interval_minutes * 60)  # Convert to seconds
                
                expired_sessions = []
                for session_id, session in self.sessions.items():
                    if session.is_expired():
                        expired_sessions.append(session_id)
                
                for session_id in expired_sessions:
                    try:
                        session = self.sessions[session_id]
                        session.status = SessionStatus.TIMEOUT
                        session.add_error("timeout", "Session expired due to inactivity")
                        
                        await self._cleanup_session(session)
                        await self._remove_session(session_id)
                        
                        logger.info(f"Cleaned up expired session {session_id}")
                        
                    except Exception as e:
                        logger.error(f"Failed to cleanup expired session {session_id}: {e}")
                
            except Exception as e:
                logger.error(f"Error in cleanup task: {e}")
    
    async def _monitor_sessions(self):
        """Background task to monitor session health"""
        while True:
            try:
                await asyncio.sleep(60)  # Monitor every minute
                
                # Update metrics
                for session in self.sessions.values():
                    if session.status == SessionStatus.ACTIVE:
                        # Update runtime metrics
                        session.metrics.execution_time_seconds = session.get_runtime_duration()
                        
                        # Check resource limits
                        if session.metrics.operations_count >= session.config.max_operations:
                            logger.warning(f"Session {session.session_id} approaching operation limit")
                
            except Exception as e:
                logger.error(f"Error in monitoring task: {e}")
    
    async def _persist_session(self, session: Session):
        """Persist session state to storage"""
        try:
            # Create sessions directory if it doesn't exist
            import os
            os.makedirs("sessions", exist_ok=True)
            
            # Save session data
            session_file = f"sessions/session_{session.session_id}.json"
            with open(session_file, 'w', encoding='utf-8') as f:
                json.dump(session.to_dict(), f, indent=2, ensure_ascii=False)
            
            logger.info(f"Persisted session {session.session_id} to {session_file}")
            
        except Exception as e:
            logger.error(f"Failed to persist session {session.session_id}: {e}")
    
    async def _load_persisted_sessions(self):
        """Load persisted sessions from storage"""
        try:
            import os
            sessions_dir = "sessions"
            
            if not os.path.exists(sessions_dir):
                return
            
            for filename in os.listdir(sessions_dir):
                if filename.startswith("session_") and filename.endswith(".json"):
                    try:
                        session_file = os.path.join(sessions_dir, filename)
                        with open(session_file, 'r', encoding='utf-8') as f:
                            session_data = json.load(f)
                        
                        # Only load active sessions
                        if session_data.get("status") in ["active", "paused"]:
                            logger.info(f"Loading persisted session from {filename}")
                            # Note: Full session restoration would require more complex logic
                    
                    except Exception as e:
                        logger.error(f"Failed to load session from {filename}: {e}")
            
        except Exception as e:
            logger.error(f"Failed to load persisted sessions: {e}")
    
    async def health_check(self) -> Dict[str, Any]:
        """Check health of the session manager"""
        active_count = await self.get_active_sessions_count()
        
        return {
            "status": "healthy" if self.initialized else "not_initialized",
            "total_sessions": len(self.sessions),
            "active_sessions": active_count,
            "session_limit": self.max_concurrent_sessions,
            "utilization_percent": (active_count / self.max_concurrent_sessions) * 100,
            "total_created": self.total_sessions_created,
            "total_completed": self.total_sessions_completed,
            "total_failed": self.total_sessions_failed,
            "cleanup_task_running": self.cleanup_task and not self.cleanup_task.done(),
            "monitoring_task_running": self.monitoring_task and not self.monitoring_task.done(),
            "available_templates": list(self.session_templates.keys())
        }
    
    async def get_session_statistics(self) -> Dict[str, Any]:
        """Get detailed session statistics"""
        sessions_by_type = {}
        sessions_by_status = {}
        
        for session in self.sessions.values():
            # Count by type
            sessions_by_type[session.session_type] = sessions_by_type.get(session.session_type, 0) + 1
            
            # Count by status
            status_str = session.status.value
            sessions_by_status[status_str] = sessions_by_status.get(status_str, 0) + 1
        
        return {
            "total_sessions": len(self.sessions),
            "sessions_by_type": sessions_by_type,
            "sessions_by_status": sessions_by_status,
            "total_operations": sum(s.metrics.operations_count for s in self.sessions.values()),
            "total_errors": sum(s.metrics.errors_count for s in self.sessions.values()),
            "average_runtime": sum(s.get_runtime_duration() for s in self.sessions.values()) / len(self.sessions) if self.sessions else 0,
            "lifetime_stats": {
                "total_created": self.total_sessions_created,
                "total_completed": self.total_sessions_completed,
                "total_failed": self.total_sessions_failed,
                "success_rate": (self.total_sessions_completed / max(1, self.total_sessions_created)) * 100
            }
        }
    
    async def shutdown(self):
        """Shutdown the session manager"""
        logger.info("Shutting down SessionManager...")
        
        # Cancel background tasks
        if self.cleanup_task:
            self.cleanup_task.cancel()
        if self.monitoring_task:
            self.monitoring_task.cancel()
        
        # Complete all active sessions
        active_sessions = [sid for sid, session in self.sessions.items() 
                          if session.status == SessionStatus.ACTIVE]
        
        for session_id in active_sessions:
            try:
                await self.complete_session(session_id, {"reason": "shutdown"})
            except Exception as e:
                logger.error(f"Failed to complete session {session_id} during shutdown: {e}")
        
        logger.info("SessionManager shutdown complete")
