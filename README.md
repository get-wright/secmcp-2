# Reconnaissance Agent with Amass MCP Server

A CrewAI-based reconnaissance agent that performs passive and active subdomain enumeration using the Amass MCP (Model Control Protocol) server. This implementation follows a modular design to support multiple MCP servers for expandability.

## Features

- **Passive Subdomain Enumeration**: Uses public sources without direct queries to target
- **Active Subdomain Enumeration**: Direct DNS queries and resolution with optional brute force
- **Domain Intelligence Gathering**: WHOIS data and organizational information
- **Modular MCP Architecture**: Easy integration of additional MCP servers
- **Comprehensive Testing**: Built-in connection and functionality tests

## Architecture

```
├── mcp/                          # MCP server integration module
│   ├── __init__.py
│   ├── config.py                 # MCP server configuration management
│   ├── adapter.py                # MCP connection utilities
│   └── servers/
│       └── amass_mcp_server.py   # Amass MCP server implementation
├── reconnaissance_agent.py       # Main CrewAI agent implementation
├── test_mcp_connection.py        # MCP connection testing script
├── example_usage.py              # Usage examples
├── requirements.txt              # Python dependencies
└── README.md                     # This file
```

## Prerequisites

1. **Python 3.8+**
2. **Amass**: Install from [OWASP Amass](https://github.com/owasp-amass/amass)
3. **Dependencies**: Install via pip (see installation section)

## Installation

1. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Install Amass** (if not already installed):
   ```bash
   # On Ubuntu/Debian
   sudo apt update
   sudo apt install amass
   
   # On macOS with Homebrew
   brew install amass
   
   # Or download from releases
   # https://github.com/owasp-amass/amass/releases
   ```

3. **Test the installation**:
   ```bash
   python test_mcp_connection.py
   ```

## Quick Start

### Basic Usage

```python
from reconnaissance_agent import ReconnaissanceAgent

# Create the agent
recon_agent = ReconnaissanceAgent()

# Run passive enumeration
result = recon_agent.run_reconnaissance(
    domain="example.com",
    tasks=['passive'],
    passive_timeout=300
)

print(result)
```

### Comprehensive Reconnaissance

```python
# Run all reconnaissance tasks
result = recon_agent.run_reconnaissance(
    domain="example.com",
    tasks=['passive', 'active', 'intel'],
    passive_timeout=300,
    active_timeout=600,
    brute_force=False,
    whois=True
)
```

### Custom Configuration

```python
# Use custom Amass configuration and wordlist
result = recon_agent.run_reconnaissance(
    domain="example.com",
    tasks=['passive', 'active'],
    config_file="/path/to/amass/config.ini",
    wordlist="/path/to/wordlist.txt",
    brute_force=True
)
```

## Available Tools

The Amass MCP server provides the following tools:

1. **amass_passive_enum**: Passive subdomain enumeration
   - Uses public sources (search engines, certificate transparency, DNS databases)
   - No direct queries to target domain
   - Configurable timeout and wordlist

2. **amass_active_enum**: Active subdomain enumeration
   - Direct DNS queries and resolution
   - Optional brute force enumeration
   - Configurable timeout and wordlist

3. **amass_intel**: Domain intelligence gathering
   - WHOIS information
   - Organizational data
   - Related domains and IP ranges

## Configuration

### MCP Server Configuration

The system uses a modular configuration approach defined in `mcp/config.py`:

```python
from mcp.config import MCPConfigManager, MCPServerConfig

# Add a new MCP server
config_manager = MCPConfigManager()
config_manager.add_server_config(MCPServerConfig(
    name="custom-server",
    server_type="stdio",
    command="python",
    args=["path/to/custom_server.py"],
    description="Custom MCP server",
    enabled=True
))
```

### Amass Configuration

You can provide custom Amass configuration files:

```ini
# amass_config.ini
[scope]
domains = example.com

[data_sources]
minimum_ttl = 1440

[resolvers]
resolver = 8.8.8.8
resolver = 1.1.1.1
```

## Testing

### Test MCP Connection

```bash
python test_mcp_connection.py
```

This script tests:
- Server configuration loading
- StdioServerParameters creation
- MCP server connection
- Tool availability
- Modular design functionality

### Example Usage

```bash
python example_usage.py
```

Provides examples for different reconnaissance scenarios.

## Security Considerations

1. **Legal Compliance**: Ensure you have permission to test target domains
2. **Rate Limiting**: Configure appropriate timeouts to avoid overwhelming targets
3. **Detection Awareness**: Active enumeration may be detected by monitoring systems
4. **Data Handling**: Secure storage and handling of reconnaissance data

## Extending with Additional MCP Servers

The modular design allows easy integration of additional MCP servers:

1. **Create server configuration**:
   ```python
   new_server_config = MCPServerConfig(
       name="new-tool-mcp",
       server_type="stdio",
       command="python",
       args=["mcp/servers/new_tool_server.py"],
       description="New reconnaissance tool",
       enabled=True
   )
   ```

2. **Add to configuration manager**:
   ```python
   config_manager.add_server_config(new_server_config)
   ```

3. **Update agent to use multiple servers**:
   ```python
   result = recon_agent.run_reconnaissance(
       domain="example.com",
       tasks=['passive', 'active', 'custom']
   )
   ```

## Troubleshooting

### Common Issues

1. **"Amass command not found"**:
   - Ensure Amass is installed and in PATH
   - Check Amass installation: `amass version`

2. **MCP connection fails**:
   - Verify Python dependencies are installed
   - Check server script permissions
   - Review log output for specific errors

3. **Tool execution timeout**:
   - Increase timeout values
   - Check network connectivity
   - Verify target domain accessibility

### Debugging

Enable verbose logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Run reconnaissance with detailed logging
recon_agent = ReconnaissanceAgent()
result = recon_agent.run_reconnaissance(domain="example.com")
```

## License

This project follows the same license as the underlying tools and dependencies. Please ensure compliance with all applicable licenses when using this software.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Submit a pull request

## Disclaimer

This tool is intended for authorized security testing and research purposes only. Users are responsible for ensuring compliance with all applicable laws and regulations. The authors are not responsible for any misuse of this software.
