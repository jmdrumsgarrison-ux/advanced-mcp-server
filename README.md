# Advanced MCP Server

🚀 **A comprehensive Model Context Protocol (MCP) server providing session management, external API integrations, and local file operations.**

## 🎯 Overview

The Advanced MCP Server is a powerful automation platform that extends Claude Desktop with:

- **Session Management**: Intelligent session lifecycle management with multiple session types
- **API Integrations**: Seamless connections to Claude, OpenAI, HuggingFace, GitHub, Google Cloud, and more
- **File Operations**: Safe local file system operations with backup and rollback capabilities
- **Rules Engine**: Customizable automation rules and workflows
- **Security**: Comprehensive credential management and encryption

## 📋 Prerequisites

- **Python 3.8+** installed and available in PATH
- **pip** package manager
- **Claude Desktop** (for MCP integration)
- **Git** (for Git operations functionality)

## 🛠️ Installation

### Step 1: Clone or Download

```bash
# If using Git
git clone <repository-url>
cd advanced-mcp-server

# Or download and extract the project files to a directory
```

### Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 3: Configure Environment Variables

1. Copy the environment template:
   ```bash
   copy .env.example .env
   ```

2. Edit `.env` file with your actual API keys:
   ```bash
   # Example .env configuration
   ANTHROPIC_API_KEY=your_anthropic_api_key_here
   OPENAI_API_KEY=your_openai_api_key_here
   HUGGINGFACE_TOKEN=your_huggingface_token_here
   GITHUB_TOKEN=your_github_token_here
   ```

### Step 4: Configure Claude Desktop

Add the following to your Claude Desktop configuration file:

**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "advanced-mcp-server": {
      "command": "python",
      "args": ["path/to/your/advanced-mcp-server/main.py"]
    }
  }
}
```

Replace `path/to/your/advanced-mcp-server/main.py` with the actual path to your installation.

### Step 5: Test Installation

```bash
# Test the server
python main.py

# Or run health check
python -c "from main import AdvancedMCPServer; import asyncio; server = AdvancedMCPServer(); print('✅ Server initialized successfully')"
```

## 🔧 Configuration

### Server Configuration

Edit `config.json` to customize server behavior:

```json
{
  "server": {
    "name": "advanced-mcp-server",
    "log_level": "INFO"
  },
  "session_management": {
    "max_active_sessions": 10,
    "session_timeout_minutes": 60
  },
  "file_operations": {
    "backup_enabled": true,
    "max_file_size_mb": 50
  }
}
```

### API Keys Setup

#### Anthropic Claude
1. Visit [Anthropic Console](https://console.anthropic.com/)
2. Generate an API key
3. Add to `.env`: `ANTHROPIC_API_KEY=your_key_here`

#### OpenAI
1. Visit [OpenAI Platform](https://platform.openai.com/api-keys)
2. Create a new API key
3. Add to `.env`: `OPENAI_API_KEY=your_key_here`

#### HuggingFace
1. Visit [HuggingFace Settings](https://huggingface.co/settings/tokens)
2. Create a new token
3. Add to `.env`: `HUGGINGFACE_TOKEN=your_token_here`

#### GitHub
1. Go to GitHub Settings > Developer settings > Personal access tokens
2. Generate a new token with appropriate scopes
3. Add to `.env`: `GITHUB_TOKEN=your_token_here`

#### Google Cloud APIs
1. Create a service account in Google Cloud Console
2. Download the JSON credentials file
3. Add to `.env`: `GOOGLE_APPLICATION_CREDENTIALS=path/to/credentials.json`

## 🚀 Usage

### Session Management

```python
# Start a new session
await start_session({
    "session_type": "api_workflow",
    "config": {"timeout": 3600}
})

# Get session status
await get_session_status({"session_id": "session_123"})
```

### API Integrations

```python
# Claude API call
await claude_api_call({
    "endpoint": "/messages",
    "data": {"message": "Hello, Claude!"}
})

# OpenAI API call
await openai_api_call({
    "endpoint": "chat/completions",
    "data": {"model": "gpt-4", "messages": [...]}
})

# Create HuggingFace Space
await huggingface_create_space({
    "space_name": "my-awesome-app",
    "space_type": "gradio"
})
```

### File Operations

```python
# Write file with backup
await write_file_local({
    "file_path": "./data/output.txt",
    "content": "Hello, World!"
})

# Batch file operations
await batch_file_operations({
    "operations": [
        {"action": "write", "path": "file1.txt", "content": "Content 1"},
        {"action": "write", "path": "file2.txt", "content": "Content 2"}
    ]
})
```

### Git Operations

```python
# Commit and push changes
await git_commit_and_push({
    "repo_path": "./my-project",
    "commit_message": "Update files via MCP server",
    "branch": "main"
})

# Create GitHub repository
await github_create_repo({
    "repo_name": "my-new-repo",
    "description": "Created via MCP server",
    "private": false
})
```

## 🛡️ Security Features

- **Credential Encryption**: API keys encrypted with master password
- **Path Traversal Protection**: Prevents access to system directories
- **File Extension Validation**: Only allowed file types can be processed
- **Audit Logging**: All operations logged for security review
- **Rate Limiting**: Prevents API abuse
- **Failed Attempt Tracking**: Automatic lockout on suspicious activity

## 📊 Monitoring and Health Checks

```python
# Get comprehensive server status
await get_server_status({})

# Health check response includes:
{
  "server": "healthy",
  "components": {
    "api_manager": "healthy",
    "rules_engine": "healthy",
    "session_manager": "healthy",
    "file_operations": "healthy",
    "auth_manager": "healthy"
  },
  "active_sessions": 3,
  "api_connections": "all_connected"
}
```

## 🔄 Session Types

- **default**: Basic session for general operations
- **api_workflow**: Optimized for API orchestration
- **file_processing**: Enhanced for file operations
- **batch_operation**: Designed for bulk operations
- **development**: Development and testing environment
- **testing**: Isolated testing environment
- **maintenance**: System maintenance operations

## 🛠️ Troubleshooting

### Common Issues

#### Import Errors
```bash
# Install missing dependencies
pip install -r requirements.txt

# Check Python version
python --version  # Should be 3.8+
```

#### API Connection Issues
```bash
# Test API credentials
python -c "import os; print('ANTHROPIC_API_KEY' in os.environ)"

# Check network connectivity
ping api.anthropic.com
```

#### File Permission Errors
```bash
# Check file permissions
ls -la ./backups/
ls -la ./sessions/

# Create directories if missing
mkdir backups sessions
```

#### Claude Desktop Integration Issues
1. Verify `claude_desktop_config.json` path is correct
2. Check that Python path in config is absolute
3. Restart Claude Desktop after configuration changes
4. Check Claude Desktop logs for error messages

### Logging and Debugging

Enable debug logging in `.env`:
```bash
MCP_LOG_LEVEL=DEBUG
MCP_DEBUG=true
```

Check log files:
- `advanced_mcp.log` - Main server log
- `./sessions/` - Session-specific logs
- `./backups/` - File operation backups

## 📝 API Reference

### Available Tools

| Tool | Description | Parameters |
|------|-------------|------------|
| `start_session` | Start new session | `session_type`, `config` |
| `get_session_status` | Get session info | `session_id` |
| `execute_rule` | Execute automation rule | `rule_name`, `parameters` |
| `claude_api_call` | Call Claude API | `endpoint`, `method`, `data` |
| `openai_api_call` | Call OpenAI API | `endpoint`, `data` |
| `huggingface_create_space` | Create HF Space | `space_name`, `space_type`, `config` |
| `git_commit_and_push` | Git operations | `repo_path`, `commit_message`, `branch` |
| `github_create_repo` | Create GitHub repo | `repo_name`, `description`, `private` |
| `google_sheets_operation` | Google Sheets ops | `sheet_id`, `operation`, `data` |
| `write_file_local` | Write local file | `file_path`, `content`, `encoding` |
| `read_file_local` | Read local file | `file_path`, `encoding` |
| `batch_file_operations` | Batch file ops | `operations` |
| `manage_credentials` | Credential management | `action`, `service`, `credentials` |
| `get_server_status` | Server health check | None |

### Available Resources

| Resource | Description | URI |
|----------|-------------|-----|
| Server Configuration | Current server config | `advanced-mcp://config` |
| Server Logs | Recent log entries | `advanced-mcp://logs` |
| Active Sessions | Session information | `advanced-mcp://sessions` |

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For issues and questions:

1. Check the troubleshooting section above
2. Review the logs in `advanced_mcp.log`
3. Create an issue with detailed error information
4. Include your configuration (with API keys redacted)

## 🔄 Version History

- **v1.0.0** - Initial release with full feature set
  - Session management
  - API integrations (Claude, OpenAI, HuggingFace, GitHub, Google)
  - File operations with backup/restore
  - Rules engine
  - Security and authentication
  - Health monitoring

---

**🎉 Enjoy using the Advanced MCP Server! 🎉**
