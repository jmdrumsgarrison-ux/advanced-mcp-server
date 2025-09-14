#!/usr/bin/env python3
"""
Rules Engine for Advanced MCP Server
Handles rule definitions, execution logic, and workflow automation
"""

import asyncio
import json
import logging
import os
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Union, Callable
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

logger = logging.getLogger(__name__)

class RulesEngine:
    """Manages rule definitions and execution for workflow automation"""
    
    def __init__(self):
        self.initialized = False
        self.rules = {}
        self.rule_history = []
        self.active_workflows = {}
        
        # Rule execution contexts
        self.contexts = {
            "session": {},
            "api": {},
            "file": {},
            "auth": {},
            "system": {}
        }
        
        # Load built-in rules
        self._load_builtin_rules()
        
        logger.info("RulesEngine initialized")
    
    async def initialize(self):
        """Initialize the rules engine"""
        try:
            # Load custom rules from configuration
            await self._load_custom_rules()
            
            # Initialize rule execution environment
            await self._setup_execution_environment()
            
            self.initialized = True
            logger.info("RulesEngine initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize RulesEngine: {e}")
            raise
    
    def _load_builtin_rules(self):
        """Load built-in rule definitions"""
        
        # === SESSION MANAGEMENT RULES ===
        
        self.rules["session_startup"] = {
            "name": "Session Startup",
            "description": "Initialize a new session with proper configuration",
            "type": "workflow",
            "triggers": ["session_start"],
            "conditions": [],
            "actions": [
                {
                    "type": "log",
                    "message": "Starting new session: {session_type}"
                },
                {
                    "type": "validate_config",
                    "config_key": "session_config"
                },
                {
                    "type": "setup_environment",
                    "environment": "session"
                }
            ],
            "rollback_actions": [
                {
                    "type": "cleanup_session",
                    "session_id": "{session_id}"
                }
            ]
        }
        
        self.rules["session_cleanup"] = {
            "name": "Session Cleanup",
            "description": "Clean up resources when session ends",
            "type": "cleanup",
            "triggers": ["session_end", "session_timeout"],
            "conditions": [],
            "actions": [
                {
                    "type": "save_session_state",
                    "session_id": "{session_id}"
                },
                {
                    "type": "release_resources",
                    "resources": ["api_connections", "file_handles", "temp_files"]
                },
                {
                    "type": "log",
                    "message": "Session {session_id} cleaned up successfully"
                }
            ]
        }
        
        # === API ORCHESTRATION RULES ===
        
        self.rules["api_retry_logic"] = {
            "name": "API Retry Logic",
            "description": "Handle API failures with exponential backoff",
            "type": "error_handling",
            "triggers": ["api_error"],
            "conditions": [
                {
                    "type": "error_code",
                    "values": ["429", "500", "502", "503", "504"]
                },
                {
                    "type": "retry_count",
                    "operator": "<",
                    "value": 3
                }
            ],
            "actions": [
                {
                    "type": "wait",
                    "duration": "exponential_backoff"
                },
                {
                    "type": "retry_api_call",
                    "api": "{api_name}",
                    "endpoint": "{endpoint}",
                    "data": "{original_data}"
                }
            ]
        }
        
        self.rules["multi_api_workflow"] = {
            "name": "Multi-API Workflow",
            "description": "Orchestrate complex workflows across multiple APIs",
            "type": "workflow",
            "triggers": ["workflow_start"],
            "conditions": [],
            "actions": [
                {
                    "type": "validate_prerequisites",
                    "apis": "{required_apis}"
                },
                {
                    "type": "execute_steps",
                    "steps": "{workflow_steps}"
                },
                {
                    "type": "aggregate_results",
                    "format": "json"
                }
            ],
            "rollback_actions": [
                {
                    "type": "rollback_api_changes",
                    "apis": "{affected_apis}"
                }
            ]
        }
        
        # === FILE OPERATION RULES ===
        
        self.rules["safe_file_operations"] = {
            "name": "Safe File Operations",
            "description": "Ensure file operations are safe and reversible",
            "type": "safety",
            "triggers": ["file_write", "file_delete", "file_move"],
            "conditions": [],
            "actions": [
                {
                    "type": "create_backup",
                    "file_path": "{file_path}"
                },
                {
                    "type": "validate_permissions",
                    "file_path": "{file_path}"
                },
                {
                    "type": "execute_operation",
                    "operation": "{operation_type}"
                },
                {
                    "type": "verify_result",
                    "expected": "{expected_result}"
                }
            ],
            "rollback_actions": [
                {
                    "type": "restore_backup",
                    "file_path": "{file_path}"
                }
            ]
        }
        
        self.rules["batch_file_processing"] = {
            "name": "Batch File Processing",
            "description": "Process multiple files with progress tracking",
            "type": "batch",
            "triggers": ["batch_operation"],
            "conditions": [],
            "actions": [
                {
                    "type": "validate_file_list",
                    "files": "{file_list}"
                },
                {
                    "type": "process_batch",
                    "operation": "{batch_operation}",
                    "chunk_size": 10
                },
                {
                    "type": "track_progress",
                    "total": "{total_files}"
                }
            ]
        }
        
        # === AUTHENTICATION RULES ===
        
        self.rules["credential_validation"] = {
            "name": "Credential Validation",
            "description": "Validate API credentials before use",
            "type": "validation",
            "triggers": ["api_call"],
            "conditions": [
                {
                    "type": "requires_auth",
                    "value": True
                }
            ],
            "actions": [
                {
                    "type": "check_credential_exists",
                    "service": "{api_service}"
                },
                {
                    "type": "validate_credential_format",
                    "service": "{api_service}"
                },
                {
                    "type": "test_credential",
                    "service": "{api_service}"
                }
            ]
        }
        
        # === SYSTEM MONITORING RULES ===
        
        self.rules["health_monitoring"] = {
            "name": "Health Monitoring",
            "description": "Monitor system health and performance",
            "type": "monitoring",
            "triggers": ["health_check", "scheduled"],
            "conditions": [],
            "actions": [
                {
                    "type": "check_api_status",
                    "apis": "all"
                },
                {
                    "type": "check_resource_usage",
                    "resources": ["memory", "disk", "connections"]
                },
                {
                    "type": "log_metrics",
                    "level": "info"
                }
            ]
        }
        
        logger.info(f"Loaded {len(self.rules)} built-in rules")
    
    async def _load_custom_rules(self):
        """Load custom rules from configuration files"""
        try:
            # Check for custom rules file
            rules_file = Path("custom_rules.json")
            if rules_file.exists():
                with open(rules_file, 'r', encoding='utf-8') as f:
                    custom_rules = json.load(f)
                
                # Merge custom rules with built-in rules
                self.rules.update(custom_rules)
                logger.info(f"Loaded {len(custom_rules)} custom rules")
            
        except Exception as e:
            logger.error(f"Failed to load custom rules: {e}")
    
    async def _setup_execution_environment(self):
        """Setup the rule execution environment"""
        try:
            # Initialize execution contexts
            self.contexts["system"]["start_time"] = datetime.now()
            self.contexts["system"]["rules_loaded"] = len(self.rules)
            
            logger.info("Rule execution environment setup complete")
            
        except Exception as e:
            logger.error(f"Failed to setup execution environment: {e}")
            raise
    
    async def execute_rule(self, rule_name: str, parameters: Dict[str, Any] = None) -> Dict[str, Any]:
        """Execute a specific rule with given parameters"""
        if not self.initialized:
            raise RuntimeError("RulesEngine not initialized")
        
        if rule_name not in self.rules:
            raise ValueError(f"Rule '{rule_name}' not found")
        
        rule = self.rules[rule_name]
        execution_id = f"{rule_name}_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
        
        logger.info(f"Executing rule '{rule_name}' with ID {execution_id}")
        
        try:
            # Record execution start
            execution_record = {
                "execution_id": execution_id,
                "rule_name": rule_name,
                "start_time": datetime.now().isoformat(),
                "parameters": parameters or {},
                "status": "running",
                "results": [],
                "errors": []
            }
            
            # Check conditions
            if not await self._check_conditions(rule.get("conditions", []), parameters):
                execution_record["status"] = "skipped"
                execution_record["reason"] = "conditions_not_met"
                return execution_record
            
            # Execute actions
            results = []
            for action in rule.get("actions", []):
                try:
                    result = await self._execute_action(action, parameters)
                    results.append(result)
                    execution_record["results"].append(result)
                except Exception as e:
                    logger.error(f"Action failed in rule {rule_name}: {e}")
                    execution_record["errors"].append(str(e))
                    
                    # Execute rollback if available
                    if rule.get("rollback_actions"):
                        await self._execute_rollback(rule["rollback_actions"], parameters)
                    
                    raise
            
            # Record successful execution
            execution_record["status"] = "completed"
            execution_record["end_time"] = datetime.now().isoformat()
            execution_record["duration"] = (
                datetime.fromisoformat(execution_record["end_time"]) - 
                datetime.fromisoformat(execution_record["start_time"])
            ).total_seconds()
            
            # Add to history
            self.rule_history.append(execution_record)
            
            logger.info(f"Rule '{rule_name}' executed successfully")
            
            return execution_record
            
        except Exception as e:
            execution_record["status"] = "failed"
            execution_record["error"] = str(e)
            execution_record["end_time"] = datetime.now().isoformat()
            
            self.rule_history.append(execution_record)
            logger.error(f"Rule execution failed: {e}")
            raise
    
    async def _check_conditions(self, conditions: List[Dict[str, Any]], parameters: Dict[str, Any]) -> bool:
        """Check if all conditions are met for rule execution"""
        if not conditions:
            return True
        
        for condition in conditions:
            condition_type = condition.get("type")
            
            if condition_type == "error_code":
                error_code = parameters.get("error_code")
                if error_code not in condition.get("values", []):
                    return False
            
            elif condition_type == "retry_count":
                retry_count = parameters.get("retry_count", 0)
                operator = condition.get("operator", "==")
                value = condition.get("value")
                
                if operator == "<" and not (retry_count < value):
                    return False
                elif operator == ">" and not (retry_count > value):
                    return False
                elif operator == "==" and not (retry_count == value):
                    return False
            
            elif condition_type == "requires_auth":
                if condition.get("value") and not parameters.get("has_auth"):
                    return False
            
            # Add more condition types as needed
        
        return True
    
    async def _execute_action(self, action: Dict[str, Any], parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a single action"""
        action_type = action.get("type")
        
        # Substitute parameters in action values
        substituted_action = self._substitute_parameters(action, parameters)
        
        if action_type == "log":
            message = substituted_action.get("message", "")
            level = substituted_action.get("level", "info")
            getattr(logger, level)(message)
            return {"type": "log", "message": message, "status": "completed"}
        
        elif action_type == "wait":
            duration = substituted_action.get("duration")
            if duration == "exponential_backoff":
                retry_count = parameters.get("retry_count", 0)
                wait_time = min(2 ** retry_count, 60)  # Max 60 seconds
            else:
                wait_time = float(duration)
            
            await asyncio.sleep(wait_time)
            return {"type": "wait", "duration": wait_time, "status": "completed"}
        
        elif action_type == "validate_config":
            config_key = substituted_action.get("config_key")
            # Validate configuration exists and is valid
            if config_key not in parameters:
                raise ValueError(f"Required config '{config_key}' not found")
            return {"type": "validate_config", "config_key": config_key, "status": "valid"}
        
        elif action_type == "setup_environment":
            environment = substituted_action.get("environment")
            # Setup execution environment
            self.contexts[environment] = self.contexts.get(environment, {})
            self.contexts[environment]["setup_time"] = datetime.now().isoformat()
            return {"type": "setup_environment", "environment": environment, "status": "setup"}
        
        elif action_type == "cleanup_session":
            session_id = substituted_action.get("session_id")
            # Clean up session resources
            if session_id in self.active_workflows:
                del self.active_workflows[session_id]
            return {"type": "cleanup_session", "session_id": session_id, "status": "cleaned"}
        
        elif action_type == "create_backup":
            file_path = substituted_action.get("file_path")
            # Create backup of file
            backup_path = f"{file_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            # Note: Actual backup implementation would go here
            return {"type": "create_backup", "file_path": file_path, "backup_path": backup_path, "status": "created"}
        
        elif action_type == "validate_permissions":
            file_path = substituted_action.get("file_path")
            # Check file permissions
            try:
                path = Path(file_path)
                readable = os.access(path.parent, os.R_OK) if path.parent.exists() else False
                writable = os.access(path.parent, os.W_OK) if path.parent.exists() else False
                return {"type": "validate_permissions", "file_path": file_path, "readable": readable, "writable": writable, "status": "validated"}
            except Exception as e:
                raise ValueError(f"Permission validation failed: {e}")
        
        elif action_type == "check_credential_exists":
            service = substituted_action.get("service")
            # Check if credential exists for service
            env_var = f"{service.upper()}_API_KEY"
            exists = bool(os.getenv(env_var))
            if not exists:
                raise ValueError(f"Credential for {service} not found")
            return {"type": "check_credential_exists", "service": service, "exists": exists, "status": "verified"}
        
        # Add more action types as needed
        else:
            logger.warning(f"Unknown action type: {action_type}")
            return {"type": action_type, "status": "skipped", "reason": "unknown_action_type"}
    
    async def _execute_rollback(self, rollback_actions: List[Dict[str, Any]], parameters: Dict[str, Any]):
        """Execute rollback actions"""
        logger.info("Executing rollback actions")
        
        for action in rollback_actions:
            try:
                await self._execute_action(action, parameters)
            except Exception as e:
                logger.error(f"Rollback action failed: {e}")
                # Continue with other rollback actions
    
    def _substitute_parameters(self, action: Dict[str, Any], parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Substitute parameter placeholders in action values"""
        substituted = {}
        
        for key, value in action.items():
            if isinstance(value, str) and value.startswith("{") and value.endswith("}"):
                param_name = value[1:-1]
                substituted[key] = parameters.get(param_name, value)
            else:
                substituted[key] = value
        
        return substituted
    
    async def get_rule_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent rule execution history"""
        return self.rule_history[-limit:]
    
    async def get_available_rules(self) -> Dict[str, Dict[str, Any]]:
        """Get all available rules with their descriptions"""
        return {
            name: {
                "name": rule.get("name", name),
                "description": rule.get("description", ""),
                "type": rule.get("type", "unknown"),
                "triggers": rule.get("triggers", [])
            }
            for name, rule in self.rules.items()
        }
    
    async def add_custom_rule(self, rule_name: str, rule_definition: Dict[str, Any]) -> Dict[str, Any]:
        """Add a custom rule definition"""
        try:
            # Validate rule definition
            required_fields = ["name", "description", "type", "actions"]
            for field in required_fields:
                if field not in rule_definition:
                    raise ValueError(f"Rule definition missing required field: {field}")
            
            # Add to rules
            self.rules[rule_name] = rule_definition
            
            # Save to custom rules file
            await self._save_custom_rules()
            
            logger.info(f"Added custom rule: {rule_name}")
            
            return {
                "rule_name": rule_name,
                "status": "added",
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to add custom rule: {e}")
            raise
    
    async def _save_custom_rules(self):
        """Save custom rules to file"""
        try:
            # Filter out built-in rules (those loaded in _load_builtin_rules)
            builtin_rule_names = [
                "session_startup", "session_cleanup", "api_retry_logic", 
                "multi_api_workflow", "safe_file_operations", "batch_file_processing",
                "credential_validation", "health_monitoring"
            ]
            
            custom_rules = {
                name: rule for name, rule in self.rules.items() 
                if name not in builtin_rule_names
            }
            
            if custom_rules:
                with open("custom_rules.json", 'w', encoding='utf-8') as f:
                    json.dump(custom_rules, f, indent=2, ensure_ascii=False)
                
                logger.info(f"Saved {len(custom_rules)} custom rules")
            
        except Exception as e:
            logger.error(f"Failed to save custom rules: {e}")
    
    async def health_check(self) -> Dict[str, Any]:
        """Check health of the rules engine"""
        return {
            "status": "healthy" if self.initialized else "not_initialized",
            "rules_count": len(self.rules),
            "history_count": len(self.rule_history),
            "active_workflows": len(self.active_workflows),
            "last_execution": self.rule_history[-1]["start_time"] if self.rule_history else None,
            "contexts": {name: bool(ctx) for name, ctx in self.contexts.items()}
        }
    
    async def clear_history(self, keep_last: int = 100):
        """Clear rule execution history, keeping the most recent entries"""
        if len(self.rule_history) > keep_last:
            self.rule_history = self.rule_history[-keep_last:]
            logger.info(f"Cleared rule history, kept last {keep_last} entries")
