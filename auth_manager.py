#!/usr/bin/env python3
"""
Authentication Manager for Advanced MCP Server
Handles secure credential storage, validation, and authentication management
"""

import asyncio
import base64
import json
import logging
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import keyring
import getpass
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

logger = logging.getLogger(__name__)

class AuthManager:
    """Manages authentication credentials and security"""
    
    def __init__(self):
        self.initialized = False
        self.credentials_cache = {}
        self.encryption_key = None
        self.master_password = None
        
        # Credential storage methods
        self.storage_methods = {
            "environment": self._env_storage,
            "keyring": self._keyring_storage,
            "encrypted_file": self._encrypted_file_storage,
            "memory": self._memory_storage
        }
        
        # Default storage method
        self.default_storage_method = "environment"
        
        # Supported services and their expected credential formats
        self.supported_services = {
            "anthropic": {
                "required_fields": ["api_key"],
                "env_vars": ["ANTHROPIC_API_KEY"],
                "validation_pattern": r"^sk-ant-[a-zA-Z0-9_-]{40,}$"
            },
            "openai": {
                "required_fields": ["api_key"],
                "env_vars": ["OPENAI_API_KEY"],
                "validation_pattern": r"^sk-[a-zA-Z0-9]{40,}$"
            },
            "huggingface": {
                "required_fields": ["token"],
                "env_vars": ["HUGGINGFACE_TOKEN", "HF_TOKEN"],
                "validation_pattern": r"^hf_[a-zA-Z0-9]{30,}$"
            },
            "github": {
                "required_fields": ["token"],
                "env_vars": ["GITHUB_TOKEN", "GITHUB_ACCESS_TOKEN"],
                "validation_pattern": r"^gh[ps]_[a-zA-Z0-9]{30,}$"
            },
            "together": {
                "required_fields": ["api_key"],
                "env_vars": ["TOGETHER_API_KEY"],
                "validation_pattern": r"^[a-zA-Z0-9]{40,}$"
            },
            "grok": {
                "required_fields": ["api_key"],
                "env_vars": ["GROK_API_KEY", "XAI_API_KEY"],
                "validation_pattern": r"^xai-[a-zA-Z0-9]{40,}$"
            },
            "google": {
                "required_fields": ["credentials_file"],
                "env_vars": ["GOOGLE_APPLICATION_CREDENTIALS"],
                "validation_pattern": None  # File path validation
            }
        }
        
        # Security settings
        self.max_failed_attempts = 3
        self.lockout_duration_minutes = 15
        self.credential_expiry_days = 90
        self.require_encryption = False
        
        # Tracking
        self.failed_attempts = {}
        self.credential_access_log = []
        self.last_validation_check = None
        
        # Encrypted storage file
        self.encrypted_storage_file = "credentials.enc"
        
        logger.info("AuthManager initialized")
    
    async def initialize(self):
        """Initialize the authentication manager"""
        try:
            # Check for existing master password or create one
            await self._setup_encryption()
            
            # Load existing credentials
            await self._load_stored_credentials()
            
            # Validate all stored credentials
            await self._validate_all_credentials()
            
            self.initialized = True
            logger.info("AuthManager initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize AuthManager: {e}")
            raise
    
    async def _setup_encryption(self):
        """Setup encryption for secure credential storage"""
        try:
            # Try to get master password from keyring first
            try:
                self.master_password = keyring.get_password("advanced_mcp_server", "master_password")
            except:
                self.master_password = None
            
            # If no master password found, create one
            if not self.master_password:
                logger.info("No master password found, generating new one")
                # In production, you'd want to prompt user for password
                # For now, we'll use a default that can be overridden
                self.master_password = os.getenv("MCP_MASTER_PASSWORD", "default_master_password_change_me")
                
                # Store in keyring if available
                try:
                    keyring.set_password("advanced_mcp_server", "master_password", self.master_password)
                    logger.info("Master password stored in system keyring")
                except:
                    logger.warning("Could not store master password in keyring, using environment variable")
            
            # Generate encryption key from master password
            password_bytes = self.master_password.encode()
            salt = b"advanced_mcp_server_salt"  # In production, use random salt
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=100000,
            )
            key = base64.urlsafe_b64encode(kdf.derive(password_bytes))
            self.encryption_key = Fernet(key)
            
            logger.info("Encryption setup completed")
            
        except Exception as e:
            logger.error(f"Failed to setup encryption: {e}")
            # Continue without encryption if it fails
            self.encryption_key = None
    
    async def _load_stored_credentials(self):
        """Load credentials from various storage methods"""
        try:
            # Load from environment variables
            await self._load_from_environment()
            
            # Load from encrypted file if it exists
            if os.path.exists(self.encrypted_storage_file):
                await self._load_from_encrypted_file()
            
            # Load from keyring
            await self._load_from_keyring()
            
            logger.info(f"Loaded credentials for {len(self.credentials_cache)} services")
            
        except Exception as e:
            logger.error(f"Failed to load stored credentials: {e}")
    
    async def _load_from_environment(self):
        """Load credentials from environment variables"""
        for service, config in self.supported_services.items():
            for env_var in config["env_vars"]:
                value = os.getenv(env_var)
                if value:
                    if service not in self.credentials_cache:
                        self.credentials_cache[service] = {}
                    
                    if service == "google":
                        self.credentials_cache[service]["credentials_file"] = value
                    else:
                        if "api_key" in config["required_fields"]:
                            self.credentials_cache[service]["api_key"] = value
                        elif "token" in config["required_fields"]:
                            self.credentials_cache[service]["token"] = value
                    
                    self.credentials_cache[service]["source"] = "environment"
                    self.credentials_cache[service]["loaded_at"] = datetime.now().isoformat()
                    break
    
    async def _load_from_keyring(self):
        """Load credentials from system keyring"""
        try:
            for service in self.supported_services.keys():
                stored_value = keyring.get_password("advanced_mcp_server", service)
                if stored_value:
                    if service not in self.credentials_cache:
                        self.credentials_cache[service] = {}
                    
                    # Parse stored JSON
                    try:
                        credential_data = json.loads(stored_value)
                        self.credentials_cache[service].update(credential_data)
                        self.credentials_cache[service]["source"] = "keyring"
                        self.credentials_cache[service]["loaded_at"] = datetime.now().isoformat()
                    except json.JSONDecodeError:
                        # Legacy single value storage
                        if service == "google":
                            self.credentials_cache[service]["credentials_file"] = stored_value
                        else:
                            config = self.supported_services[service]
                            if "api_key" in config["required_fields"]:
                                self.credentials_cache[service]["api_key"] = stored_value
                            elif "token" in config["required_fields"]:
                                self.credentials_cache[service]["token"] = stored_value
                        
                        self.credentials_cache[service]["source"] = "keyring"
                        self.credentials_cache[service]["loaded_at"] = datetime.now().isoformat()
        
        except Exception as e:
            logger.warning(f"Could not load from keyring: {e}")
    
    async def _load_from_encrypted_file(self):
        """Load credentials from encrypted file"""
        try:
            if not self.encryption_key:
                logger.warning("No encryption key available, skipping encrypted file")
                return
            
            with open(self.encrypted_storage_file, 'rb') as f:
                encrypted_data = f.read()
            
            decrypted_data = self.encryption_key.decrypt(encrypted_data)
            credential_data = json.loads(decrypted_data.decode())
            
            for service, data in credential_data.items():
                if service not in self.credentials_cache:
                    self.credentials_cache[service] = {}
                
                self.credentials_cache[service].update(data)
                self.credentials_cache[service]["source"] = "encrypted_file"
                self.credentials_cache[service]["loaded_at"] = datetime.now().isoformat()
            
            logger.info("Loaded credentials from encrypted file")
            
        except Exception as e:
            logger.error(f"Failed to load from encrypted file: {e}")
    
    async def _validate_all_credentials(self):
        """Validate all stored credentials"""
        validation_results = {}
        
        for service, credentials in self.credentials_cache.items():
            try:
                is_valid = await self._validate_credential_format(service, credentials)
                validation_results[service] = {
                    "valid": is_valid,
                    "checked_at": datetime.now().isoformat()
                }
                
                if not is_valid:
                    logger.warning(f"Invalid credentials detected for service: {service}")
                
            except Exception as e:
                logger.error(f"Failed to validate credentials for {service}: {e}")
                validation_results[service] = {
                    "valid": False,
                    "error": str(e),
                    "checked_at": datetime.now().isoformat()
                }
        
        self.last_validation_check = datetime.now()
        return validation_results
    
    async def _validate_credential_format(self, service: str, credentials: Dict[str, Any]) -> bool:
        """Validate credential format for a specific service"""
        if service not in self.supported_services:
            return False
        
        config = self.supported_services[service]
        
        # Check required fields
        for field in config["required_fields"]:
            if field not in credentials:
                return False
            
            value = credentials[field]
            if not value:
                return False
            
            # Special validation for Google credentials (file path)
            if service == "google" and field == "credentials_file":
                return os.path.exists(value) and value.endswith(('.json', '.p12'))
            
            # Pattern validation for other services
            if config["validation_pattern"]:
                import re
                if not re.match(config["validation_pattern"], value):
                    return False
        
        return True
    
    async def manage_credentials(self, action: str, service: str, credentials: Dict[str, Any] = None) -> Dict[str, Any]:
        """Manage API credentials securely"""
        if not self.initialized:
            raise RuntimeError("AuthManager not initialized")
        
        # Check for lockout
        if self._is_locked_out(service):
            raise PermissionError(f"Service {service} is locked out due to failed attempts")
        
        try:
            if action == "set":
                return await self._set_credentials(service, credentials)
            
            elif action == "get":
                return await self._get_credentials(service)
            
            elif action == "delete":
                return await self._delete_credentials(service)
            
            elif action == "list":
                return await self._list_services()
            
            elif action == "validate":
                return await self._validate_credentials(service)
            
            elif action == "test":
                return await self._test_credentials(service)
            
            else:
                raise ValueError(f"Unknown action: {action}")
        
        except Exception as e:
            self._record_failed_attempt(service)
            logger.error(f"Credential management failed for {service}: {e}")
            raise
    
    async def _set_credentials(self, service: str, credentials: Dict[str, Any]) -> Dict[str, Any]:
        """Set credentials for a service"""
        if service not in self.supported_services:
            raise ValueError(f"Unsupported service: {service}")
        
        if not credentials:
            raise ValueError("Credentials cannot be empty")
        
        # Validate credential format
        if not await self._validate_credential_format(service, credentials):
            raise ValueError(f"Invalid credential format for service: {service}")
        
        # Add metadata
        credential_data = credentials.copy()
        credential_data.update({
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "source": "manual",
            "service": service
        })
        
        # Store in cache
        self.credentials_cache[service] = credential_data
        
        # Store persistently based on configuration
        storage_method = credentials.get("storage_method", self.default_storage_method)
        storage_handler = self.storage_methods.get(storage_method, self._env_storage)
        
        try:
            await storage_handler("set", service, credential_data)
            
            # Log the action
            self._log_credential_access("set", service, success=True)
            
            logger.info(f"Credentials set for service: {service}")
            
            return {
                "service": service,
                "action": "set",
                "status": "success",
                "storage_method": storage_method,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to store credentials for {service}: {e}")
            raise
    
    async def _get_credentials(self, service: str) -> Dict[str, Any]:
        """Get credentials for a service"""
        if service not in self.supported_services:
            raise ValueError(f"Unsupported service: {service}")
        
        if service not in self.credentials_cache:
            raise ValueError(f"No credentials found for service: {service}")
        
        # Check if credentials are expired
        credential_data = self.credentials_cache[service]
        created_at = datetime.fromisoformat(credential_data.get("created_at", datetime.now().isoformat()))
        
        if datetime.now() - created_at > timedelta(days=self.credential_expiry_days):
            logger.warning(f"Credentials for {service} are expired")
        
        # Remove sensitive metadata for response
        response_data = {k: v for k, v in credential_data.items() 
                        if k not in ["source", "created_at", "updated_at"]}
        
        # Log the access
        self._log_credential_access("get", service, success=True)
        
        return {
            "service": service,
            "credentials": response_data,
            "loaded_from": credential_data.get("source", "unknown"),
            "last_validated": self.last_validation_check.isoformat() if self.last_validation_check else None
        }
    
    async def _delete_credentials(self, service: str) -> Dict[str, Any]:
        """Delete credentials for a service"""
        if service not in self.credentials_cache:
            raise ValueError(f"No credentials found for service: {service}")
        
        # Remove from cache
        credential_data = self.credentials_cache.pop(service)
        
        # Remove from persistent storage
        storage_method = credential_data.get("source", self.default_storage_method)
        storage_handler = self.storage_methods.get(storage_method, self._env_storage)
        
        try:
            await storage_handler("delete", service, None)
            
            # Log the action
            self._log_credential_access("delete", service, success=True)
            
            logger.info(f"Credentials deleted for service: {service}")
            
            return {
                "service": service,
                "action": "delete",
                "status": "success",
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            # Re-add to cache if deletion failed
            self.credentials_cache[service] = credential_data
            logger.error(f"Failed to delete credentials for {service}: {e}")
            raise
    
    async def _list_services(self) -> Dict[str, Any]:
        """List all services and their credential status"""
        services_status = {}
        
        for service in self.supported_services.keys():
            has_credentials = service in self.credentials_cache
            status_info = {
                "has_credentials": has_credentials,
                "supported": True
            }
            
            if has_credentials:
                credential_data = self.credentials_cache[service]
                status_info.update({
                    "source": credential_data.get("source", "unknown"),
                    "created_at": credential_data.get("created_at"),
                    "updated_at": credential_data.get("updated_at"),
                    "required_fields": self.supported_services[service]["required_fields"]
                })
                
                # Check if expired
                if credential_data.get("created_at"):
                    created_at = datetime.fromisoformat(credential_data["created_at"])
                    is_expired = datetime.now() - created_at > timedelta(days=self.credential_expiry_days)
                    status_info["expired"] = is_expired
            
            services_status[service] = status_info
        
        return {
            "total_services": len(self.supported_services),
            "configured_services": len(self.credentials_cache),
            "services": services_status,
            "last_validation_check": self.last_validation_check.isoformat() if self.last_validation_check else None
        }
    
    async def _validate_credentials(self, service: str) -> Dict[str, Any]:
        """Validate credentials for a service"""
        if service not in self.credentials_cache:
            raise ValueError(f"No credentials found for service: {service}")
        
        credential_data = self.credentials_cache[service]
        is_valid = await self._validate_credential_format(service, credential_data)
        
        return {
            "service": service,
            "valid": is_valid,
            "checked_at": datetime.now().isoformat(),
            "required_fields": self.supported_services[service]["required_fields"]
        }
    
    async def _test_credentials(self, service: str) -> Dict[str, Any]:
        """Test credentials by making a simple API call"""
        if service not in self.credentials_cache:
            raise ValueError(f"No credentials found for service: {service}")
        
        # Note: This would require importing the API manager
        # For now, we'll just do format validation
        validation_result = await self._validate_credentials(service)
        
        # In a full implementation, this would make actual test API calls
        test_result = {
            "service": service,
            "format_valid": validation_result["valid"],
            "api_test": "not_implemented",  # Would be "success" or "failed" with actual testing
            "tested_at": datetime.now().isoformat()
        }
        
        return test_result
    
    # Storage method implementations
    
    async def _env_storage(self, action: str, service: str, credential_data: Dict[str, Any] = None):
        """Environment variable storage handler"""
        if action == "set":
            # Note: Can't actually set environment variables for the current process
            logger.warning(f"Cannot set environment variable for {service} - manual setup required")
        elif action == "delete":
            logger.warning(f"Cannot delete environment variable for {service} - manual cleanup required")
    
    async def _keyring_storage(self, action: str, service: str, credential_data: Dict[str, Any] = None):
        """System keyring storage handler"""
        try:
            if action == "set":
                # Store as JSON
                json_data = json.dumps({k: v for k, v in credential_data.items() 
                                      if k not in ["source", "service"]})
                keyring.set_password("advanced_mcp_server", service, json_data)
            
            elif action == "delete":
                keyring.delete_password("advanced_mcp_server", service)
        
        except Exception as e:
            logger.error(f"Keyring operation failed for {service}: {e}")
            raise
    
    async def _encrypted_file_storage(self, action: str, service: str, credential_data: Dict[str, Any] = None):
        """Encrypted file storage handler"""
        if not self.encryption_key:
            raise RuntimeError("Encryption not available")
        
        try:
            # Load existing data
            existing_data = {}
            if os.path.exists(self.encrypted_storage_file):
                with open(self.encrypted_storage_file, 'rb') as f:
                    encrypted_data = f.read()
                decrypted_data = self.encryption_key.decrypt(encrypted_data)
                existing_data = json.loads(decrypted_data.decode())
            
            # Modify data
            if action == "set":
                existing_data[service] = {k: v for k, v in credential_data.items() 
                                        if k not in ["source", "service"]}
            elif action == "delete":
                existing_data.pop(service, None)
            
            # Save data
            json_data = json.dumps(existing_data, indent=2)
            encrypted_data = self.encryption_key.encrypt(json_data.encode())
            
            with open(self.encrypted_storage_file, 'wb') as f:
                f.write(encrypted_data)
        
        except Exception as e:
            logger.error(f"Encrypted file operation failed for {service}: {e}")
            raise
    
    async def _memory_storage(self, action: str, service: str, credential_data: Dict[str, Any] = None):
        """Memory-only storage handler (no persistence)"""
        # Already handled by credentials_cache
        pass
    
    def _is_locked_out(self, service: str) -> bool:
        """Check if a service is locked out due to failed attempts"""
        if service not in self.failed_attempts:
            return False
        
        attempts_data = self.failed_attempts[service]
        if attempts_data["count"] < self.max_failed_attempts:
            return False
        
        lockout_end = attempts_data["last_attempt"] + timedelta(minutes=self.lockout_duration_minutes)
        return datetime.now() < lockout_end
    
    def _record_failed_attempt(self, service: str):
        """Record a failed authentication attempt"""
        if service not in self.failed_attempts:
            self.failed_attempts[service] = {"count": 0, "last_attempt": None}
        
        self.failed_attempts[service]["count"] += 1
        self.failed_attempts[service]["last_attempt"] = datetime.now()
        
        logger.warning(f"Failed attempt #{self.failed_attempts[service]['count']} for service {service}")
    
    def _log_credential_access(self, action: str, service: str, success: bool):
        """Log credential access for audit purposes"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "action": action,
            "service": service,
            "success": success,
            "source_ip": "localhost"  # In a network context, you'd get real IP
        }
        
        self.credential_access_log.append(log_entry)
        
        # Keep only last 1000 entries
        if len(self.credential_access_log) > 1000:
            self.credential_access_log = self.credential_access_log[-1000:]
    
    async def get_access_log(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent credential access log"""
        return self.credential_access_log[-limit:]
    
    async def clear_failed_attempts(self, service: str = None) -> Dict[str, Any]:
        """Clear failed attempts for a service or all services"""
        if service:
            if service in self.failed_attempts:
                del self.failed_attempts[service]
                logger.info(f"Cleared failed attempts for service: {service}")
                return {"service": service, "status": "cleared"}
            else:
                return {"service": service, "status": "no_attempts_found"}
        else:
            cleared_count = len(self.failed_attempts)
            self.failed_attempts.clear()
            logger.info(f"Cleared failed attempts for {cleared_count} services")
            return {"services_cleared": cleared_count, "status": "all_cleared"}
    
    async def export_credentials(self, export_format: str = "json", include_values: bool = False) -> Dict[str, Any]:
        """Export credential configuration (optionally with values)"""
        export_data = {}
        
        for service, credential_data in self.credentials_cache.items():
            service_data = {
                "service": service,
                "configured": True,
                "source": credential_data.get("source", "unknown"),
                "created_at": credential_data.get("created_at"),
                "updated_at": credential_data.get("updated_at"),
                "required_fields": self.supported_services[service]["required_fields"]
            }
            
            if include_values:
                # Only include values if explicitly requested (security risk)
                for field in self.supported_services[service]["required_fields"]:
                    if field in credential_data:
                        service_data[field] = credential_data[field]
            
            export_data[service] = service_data
        
        return {
            "export_format": export_format,
            "exported_at": datetime.now().isoformat(),
            "include_values": include_values,
            "total_services": len(export_data),
            "services": export_data
        }
    
    async def health_check(self) -> Dict[str, Any]:
        """Check health of the authentication manager"""
        try:
            # Check storage methods availability
            storage_health = {}
            for method_name, handler in self.storage_methods.items():
                try:
                    # Simple test (this would be more sophisticated in practice)
                    storage_health[method_name] = "available"
                except:
                    storage_health[method_name] = "unavailable"
            
            # Count locked out services
            locked_services = sum(1 for service in self.supported_services.keys() 
                                if self._is_locked_out(service))
            
            # Recent access attempts
            recent_accesses = len([log for log in self.credential_access_log 
                                 if datetime.fromisoformat(log["timestamp"]) > datetime.now() - timedelta(hours=1)])
            
            return {
                "status": "healthy" if self.initialized else "not_initialized",
                "encryption_available": self.encryption_key is not None,
                "configured_services": len(self.credentials_cache),
                "total_supported_services": len(self.supported_services),
                "locked_out_services": locked_services,
                "storage_methods": storage_health,
                "recent_access_attempts": recent_accesses,
                "last_validation_check": self.last_validation_check.isoformat() if self.last_validation_check else None,
                "security_settings": {
                    "max_failed_attempts": self.max_failed_attempts,
                    "lockout_duration_minutes": self.lockout_duration_minutes,
                    "credential_expiry_days": self.credential_expiry_days,
                    "require_encryption": self.require_encryption
                }
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
    
    async def rotate_master_password(self, new_password: str) -> Dict[str, Any]:
        """Rotate the master password (re-encrypt all data)"""
        try:
            old_password = self.master_password
            
            # Re-encrypt all stored credentials with new password
            # This is a simplified implementation
            self.master_password = new_password
            await self._setup_encryption()
            
            # Re-save all credentials with new encryption
            for service, credential_data in self.credentials_cache.items():
                if credential_data.get("source") == "encrypted_file":
                    await self._encrypted_file_storage("set", service, credential_data)
            
            # Update keyring
            try:
                keyring.set_password("advanced_mcp_server", "master_password", new_password)
            except:
                logger.warning("Could not update master password in keyring")
            
            logger.info("Master password rotated successfully")
            
            return {
                "status": "success",
                "rotated_at": datetime.now().isoformat(),
                "affected_services": len([s for s, d in self.credentials_cache.items() 
                                        if d.get("source") == "encrypted_file"])
            }
            
        except Exception as e:
            # Restore old password on failure
            self.master_password = old_password
            await self._setup_encryption()
            logger.error(f"Failed to rotate master password: {e}")
            raise
    
    async def cleanup_expired_credentials(self) -> Dict[str, Any]:
        """Remove expired credentials"""
        expired_services = []
        cutoff_date = datetime.now() - timedelta(days=self.credential_expiry_days)
        
        for service, credential_data in list(self.credentials_cache.items()):
            created_at_str = credential_data.get("created_at")
            if created_at_str:
                created_at = datetime.fromisoformat(created_at_str)
                if created_at < cutoff_date:
                    try:
                        await self._delete_credentials(service)
                        expired_services.append(service)
                        logger.info(f"Removed expired credentials for service: {service}")
                    except Exception as e:
                        logger.error(f"Failed to remove expired credentials for {service}: {e}")
        
        return {
            "cleaned_services": expired_services,
            "count": len(expired_services),
            "cutoff_date": cutoff_date.isoformat()
        }
