Amass MCP setup (manual)

This project expects a local Model Context Protocol server for Amass to be available, as described in the amass-mcp documentation.

Reference: amass-mcp in mcp-for-security

- Repository: https://github.com/cyproxio/mcp-for-security/tree/main/amass-mcp

Guidelines and constraints

- Keep the MCP service here under `mcp/` only.
- Do not automate installation or startup. Follow the upstream instructions exactly.
- No adapters or extensions beyond the documented setup.

Configuration

Provide your local server command in `mcp/mcp_servers.yaml`. Example (adjust to your environment):

```yaml
servers:
  - name: amass-mcp
    command: node
    args:
      - path/to/amass-mcp/server.js
    env: {}
```

Windows users: if the path contains spaces, prefer using absolute paths and ensure the `args` entries are split per argument.

Testing the MCP connection (from repo root)

1. Ensure the amass MCP server is available according to the upstream docs.
2. Set `mcp/mcp_servers.yaml` accordingly.
3. Run:

```bash
python -m scripts.test_mcp_connection amass-mcp
```

You should see the available tools printed if the connection succeeds.


