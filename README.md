# Reconnaissance Agent

A specialized CrewAI agent for performing comprehensive subdomain reconnaissance using the Amass MCP server integration.

## Features

- **Passive Subdomain Enumeration**: Stealthy reconnaissance without direct target interaction
- **Active Subdomain Enumeration**: Comprehensive discovery with DNS probing and brute force
- **Subdomain Intelligence**: Gather additional information about discovered subdomains
- **Modular MCP Integration**: Extensible architecture for multiple MCP servers
- **CrewAI Framework**: Advanced AI agent capabilities for intelligent reconnaissance

## Architecture

```
reconnaissance-agent/
├── mcp/                        # MCP server integrations
│   ├── __init__.py
│   └── amass_mcp_server.py    # Amass MCP server implementation
├── src/                        # Source code
│   ├── __init__.py
│   ├── mcp_adapter.py         # Modular MCP adapter
│   └── reconnaissance_agent.py # Main CrewAI agent
├── main.py                     # CLI entry point
├── test_mcp_connection.py     # MCP connection tester
└── requirements.txt           # Dependencies
```

## Prerequisites

### 1. Install Amass

Follow the installation guide for Amass:
- **GitHub**: https://github.com/owasp-amass/amass
- **Installation**: https://github.com/owasp-amass/amass/blob/master/doc/install.md

### 2. Setup Amass MCP Server

Follow the official documentation:
- **Documentation**: https://github.com/cyproxio/mcp-for-security/tree/main/amass-mcp

**Important**: The MCP service setup should be done manually according to the documentation. This project does NOT automate the installation or running of MCP servers.

## Installation

1. Clone this repository:
```bash
git clone <your-repo-url>
cd reconnaissance-agent
```

2. Install Python dependencies:
```bash
pip install -r requirements.txt
```

3. Create logs directory:
```bash
mkdir logs
```

## Usage

### Command Line Interface

Basic passive reconnaissance:
```bash
python main.py example.com
```

Comprehensive reconnaissance (passive + active):
```bash
python main.py example.com --comprehensive
```

With verbose logging:
```bash
python main.py example.com --verbose
```

Save report to file:
```bash
python main.py example.com --output report.txt
```

### Test MCP Connection

Before running reconnaissance, test your MCP server setup:

```bash
# Run full test suite
python test_mcp_connection.py

# Interactive testing
python test_mcp_connection.py --interactive

# Quick connectivity check
# Option 3 in interactive mode
```

### Programmatic Usage

```python
import asyncio
from src.reconnaissance_agent import run_reconnaissance

# Basic usage
async def main():
    result = await run_reconnaissance("example.com")
    print(result)

asyncio.run(main())
```

### Advanced Usage

```python
from src.reconnaissance_agent import ReconnaissanceAgent
from src.mcp_adapter import MCPManager, create_amass_config

async def advanced_reconnaissance():
    # Setup custom MCP manager
    mcp_manager = MCPManager()
    
    # Register custom Amass configuration
    amass_config = create_amass_config(
        name="amass-mcp",
        working_directory="./mcp",
        config_file="/path/to/amass/config.yaml"
    )
    mcp_manager.register_server(amass_config)
    
    # Create agent with custom manager
    agent = ReconnaissanceAgent(mcp_manager)
    
    # Start MCP servers
    await agent.start_mcp_servers()
    
    try:
        # Run reconnaissance
        result = agent.execute_reconnaissance("example.com", comprehensive=True)
        print(result)
    finally:
        # Cleanup
        await agent.stop_mcp_servers()
```

## MCP Server Management

### Manual Management

If you prefer to manage MCP servers manually:

```bash
python main.py example.com --no-auto-manage
```

### Status Checking

Check MCP server status:

```python
from src.reconnaissance_agent import ReconnaissanceAgent

agent = ReconnaissanceAgent()
status = await agent.get_server_status()
print(status)
```

## Configuration

### Amass Configuration

You can provide custom Amass configuration files:

```python
amass_config = create_amass_config(
    name="amass-mcp",
    config_file="/path/to/amass_config.yaml"
)
```

### Environment Variables

Set environment variables for MCP server configuration:

```bash
export AMASS_CONFIG=/path/to/config.yaml
```

## Extending with Additional MCP Servers

The architecture is designed to be modular. To add new MCP servers:

1. **Create MCP Server Implementation**:
```python
# mcp/your_tool_mcp_server.py
# Implement your MCP server following the pattern in amass_mcp_server.py
```

2. **Create Client Adapter**:
```python
# In src/mcp_adapter.py
class YourToolMCPClient(BaseMCPClient):
    # Implement the abstract methods
    pass
```

3. **Register with Manager**:
```python
config = MCPServerConfig(
    name="your-tool-mcp",
    command=["python", "-m", "mcp.your_tool_mcp_server"]
)
mcp_manager.register_server(config, YourToolMCPClient)
```

## Troubleshooting

### Common Issues

1. **MCP Server Won't Start**:
   - Check Amass installation: `amass version`
   - Verify MCP server setup according to documentation
   - Run connection test: `python test_mcp_connection.py`

2. **Permission Errors**:
   - Ensure proper file permissions in the `mcp/` directory
   - Check that Amass binary is in PATH

3. **Timeout Errors**:
   - Increase timeout values in tool calls
   - Check network connectivity for passive enumeration

4. **No Results**:
   - Verify target domain is valid
   - Check if domain has subdomains
   - Try with a known domain like `example.com` for testing

### Debug Mode

Enable debug logging:
```bash
python main.py example.com --verbose
```

Check log files:
```bash
tail -f logs/reconnaissance.log
```

## Security Considerations

1. **Target Authorization**: Only perform reconnaissance on domains you own or have explicit permission to test
2. **Rate Limiting**: Be mindful of request rates to avoid overwhelming target infrastructure
3. **Passive First**: Always start with passive techniques before active enumeration
4. **Legal Compliance**: Ensure compliance with local laws and regulations

## Contributing

1. Fork the repository
2. Create a feature branch
3. Implement your changes
4. Add tests for new functionality
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- [OWASP Amass](https://github.com/owasp-amass/amass) - The subdomain enumeration tool
- [CrewAI](https://github.com/joaomdmoura/crewAI) - The AI agent framework
- [MCP for Security](https://github.com/cyproxio/mcp-for-security) - MCP server implementations

## Support

For issues and questions:
1. Check the troubleshooting section
2. Run the MCP connection test
3. Review the logs for error details
4. Open an issue with detailed error information
