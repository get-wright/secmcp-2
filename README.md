# CrewAI Subdomain Enumeration Agent

A powerful CrewAI agent that performs comprehensive subdomain enumeration using MCP (Model Context Protocol) servers with Amass integration. This modular system supports multiple MCP servers and provides both passive and active subdomain discovery capabilities.

## Features

- 🤖 **CrewAI Integration**: Intelligent agent-based subdomain enumeration
- 🔌 **Modular MCP Support**: Supports multiple MCP servers for load balancing and redundancy
- 🔍 **Comprehensive Enumeration**: Both passive and active subdomain discovery methods
- 🛠️ **Amass Integration**: Leverages the powerful Amass tool through MCP servers
- ⚙️ **Configurable**: YAML-based configuration for easy setup and customization
- 📊 **Detailed Reporting**: Comprehensive results with analysis and recommendations
- 🎯 **Interactive Mode**: Command-line interface for real-time enumeration

## Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   CrewAI Agent  │◄──►│   MCP Client     │◄──►│  MCP Servers    │
│                 │    │                  │    │                 │
│ - Task Planning │    │ - Server Mgmt    │    │ - Amass Server 1│
│ - Result Analysis│    │ - Load Balancing │    │ - Amass Server 2│
│ - Reporting     │    │ - Error Handling │    │ - Future Servers│
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

## Installation

### Prerequisites

1. **Python 3.8+**
2. **Amass**: Install from [https://github.com/OWASP/Amass](https://github.com/OWASP/Amass)

### Install Dependencies

```bash
# Clone the repository
git clone https://github.com/example/crewai-subdomain-enumeration.git
cd crewai-subdomain-enumeration

# Install Python dependencies
pip install -r requirements.txt

# Or install with setup.py
pip install -e .
```

### Install Amass

#### Linux/macOS
```bash
# Using Go
go install -v github.com/OWASP/Amass/v3/...@master

# Using package managers
# Ubuntu/Debian
sudo apt install amass

# macOS
brew install amass
```

#### Windows
Download from [Amass Releases](https://github.com/OWASP/Amass/releases)

## Configuration

The system uses YAML configuration files to manage MCP servers:

```yaml
# config/mcp_servers.yaml
mcp_servers:
  - name: "amass-mcp-primary"
    url: "http://localhost:8001"
    type: "amass"
    enabled: true
    description: "Primary Amass MCP server"
  
  - name: "amass-mcp-secondary"
    url: "http://localhost:8002"
    type: "amass"
    enabled: false
    description: "Secondary Amass MCP server for load balancing"

default_config:
  timeout: 30
  max_retries: 3
  retry_delay: 1
```

## Usage

### Command Line Interface

#### Basic Usage
```bash
# Passive enumeration
python main.py example.com --method passive

# Active enumeration
python main.py example.com --method active

# Combined enumeration (default)
python main.py example.com --method combined
```

#### Advanced Options
```bash
# Use specific servers
python main.py example.com --servers amass-mcp-primary

# Custom passive sources
python main.py example.com --method passive --passive-sources crtsh,hackertarget

# Active enumeration with brute force
python main.py example.com --method active --active-brute --wordlist wordlist.txt

# Set timeout
python main.py example.com --timeout 60

# Save results to file
python main.py example.com --output results.txt

# Verbose logging
python main.py example.com --verbose
```

#### Server Management
```bash
# Check server status
python main.py --status

# Show help
python main.py --help
```

### Interactive Mode

```bash
# Start interactive mode
python main.py

# Available commands:
Enumeration> enum example.com
Enumeration> enum example.com passive
Enumeration> status
Enumeration> servers
Enumeration> help
Enumeration> quit
```

### Python API

```python
from src.subdomain_agent import create_subdomain_agent
import asyncio

async def main():
    # Create the agent
    agent = create_subdomain_agent()
    
    # Start MCP servers
    await agent.start_mcp_servers()
    
    # Perform enumeration
    result = agent.execute_enumeration(
        domain="example.com",
        method="combined"
    )
    
    print(result)
    
    # Cleanup
    await agent.stop_mcp_servers()

# Run the enumeration
asyncio.run(main())
```

### Advanced Configuration

#### Custom Passive Enumeration
```python
passive_config = {
    "sources": ["crtsh", "hackertarget", "virustotal"],
    "timeout": 30
}

result = agent.execute_enumeration(
    domain="example.com",
    method="passive",
    passive_config=passive_config
)
```

#### Custom Active Enumeration
```python
active_config = {
    "brute": True,
    "wordlist": "/path/to/wordlist.txt",
    "timeout": 60,
    "resolvers": "/path/to/resolvers.txt"
}

result = agent.execute_enumeration(
    domain="example.com",
    method="active",
    active_config=active_config
)
```

## MCP Server Management

### Starting Servers

The MCP servers run as separate processes and communicate via the MCP protocol:

```python
from src.mcp_client import MCPClient

# Initialize client
client = MCPClient("config/mcp_servers.yaml")

# Start all enabled servers
await client.start_all_servers()

# Start specific server
await client.start_server("amass-mcp-primary")

# Check server status
status = client.get_server_status()
print(status)
```

### Direct MCP Calls

```python
# Call enumeration directly
result = await client.enumerate_subdomains_passive("example.com")

# Use specific servers
result = await client.enumerate_subdomains_active(
    "example.com", 
    servers=["amass-mcp-primary"]
)

# Combined enumeration
result = await client.enumerate_subdomains_combined(
    "example.com",
    passive_config={"sources": ["crtsh"]},
    active_config={"brute": True}
)
```

## Output Format

The agent provides detailed results including:

```
Subdomain Enumeration Results for example.com:
Method: combined
Total subdomains found: 42
Successful servers: amass-mcp-primary
Failed servers: None

Discovered Subdomains:
  1. admin.example.com
  2. api.example.com
  3. app.example.com
  4. blog.example.com
  5. dev.example.com
  ...

Analysis:
- Found 5 potentially interesting subdomains (admin, dev, staging, test, internal)
- Naming pattern suggests organized subdomain structure
- Recommend further investigation of admin and dev subdomains

Recommendations:
1. Perform web application assessment on discovered subdomains
2. Check for common vulnerabilities on admin interfaces
3. Investigate development/staging environments for information disclosure
```

## Extending the System

### Adding New MCP Servers

1. Create a new MCP server implementation
2. Add server configuration to `config/mcp_servers.yaml`
3. The system will automatically discover and use the new server

### Custom Enumeration Methods

The modular design allows for easy extension with new enumeration techniques:

```python
# Add to mcp_client.py
async def enumerate_subdomains_custom(self, domain: str, method: str):
    """Custom enumeration method"""
    # Implementation here
    pass
```

## Troubleshooting

### Common Issues

1. **Amass not found**: Ensure Amass is installed and in PATH
2. **MCP servers not starting**: Check server configurations and dependencies
3. **No results**: Verify network connectivity and domain validity

### Debug Mode

```bash
# Enable verbose logging
python main.py example.com --verbose

# Check logs
tail -f subdomain_enumeration.log
```

### Server Status

```bash
# Check which servers are running
python main.py --status
```

## Security Considerations

- **Rate Limiting**: The tool respects rate limits and implements delays
- **Passive First**: Prefer passive enumeration to avoid detection
- **Legal Compliance**: Only enumerate domains you own or have permission to test
- **Resource Usage**: Monitor system resources when running multiple servers

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- [OWASP Amass](https://github.com/OWASP/Amass) for the core enumeration engine
- [CrewAI](https://github.com/joaomdmoura/crewAI) for the agent framework
- [MCP](https://modelcontextprotocol.io/) for the server protocol
- The cybersecurity community for continuous improvements

## Changelog

### v1.0.0
- Initial release with CrewAI integration
- MCP server support for Amass
- Modular architecture for multiple servers
- Command-line and interactive interfaces
- Comprehensive configuration system
