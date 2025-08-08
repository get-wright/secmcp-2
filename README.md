Reconnaissance Agent (CrewAI) with MCP (Amass)

What this provides

- A single CrewAI agent named "Reconnaissance Agent" capable of passive and active subdomain enumeration via an MCP server for Amass.
- Modular MCP stdio client and configuration to enable adding other MCP servers easily.
- A test script to validate MCP connectivity and list available tools.

Key directories

- `src/agents/`: CrewAI agent factory.
- `src/tools/`: CrewAI tools, including `AmassMCPTool`.
- `src/mcp_client/`: Minimal MCP stdio client wrapper.
- `mcp/`: MCP server documentation and local configuration (no automation).
- `scripts/`: Utilities such as test connection script.

Setup

1) Install Python dependencies

```bash
pip install -r requirements.txt
```

2) Configure the MCP server command

Edit `mcp/mcp_servers.yaml` according to the upstream amass-mcp documentation:

- amass-mcp: https://github.com/cyproxio/mcp-for-security/tree/main/amass-mcp

3) Test MCP connection

```bash
python -m scripts.test_mcp_connection amass-mcp
```

Using the agent

Instantiate the agent in your application:

```python
from src.agents.recon_agent import create_reconnaissance_agent

agent = create_reconnaissance_agent()

# Example tool invocation via CrewAI task prompt variables
# Provide `{domain}` and `{enumeration_type}` ("passive" or "active") in your task inputs.
```

References

- CrewAI docs: https://docs.crewai.com/
- Amass MCP: https://github.com/cyproxio/mcp-for-security/tree/main/amass-mcp


