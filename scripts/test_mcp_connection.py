from __future__ import annotations

import sys
from typing import Optional

from src.config import load_mcp_server_config
from src.mcp_client.stdio_client import StdIoMCPClient
from src.tools.base_mcp import MCPToolError


def main(server_name: str = "amass-mcp") -> int:
    try:
        cfg = load_mcp_server_config(server_name)
        client = StdIoMCPClient(cfg)
        tools = client.list_tools_sync()
    except MCPToolError as e:
        print(f"[ERROR] {e}")
        return 2
    except Exception as e:
        print(f"[ERROR] Unexpected failure while connecting to MCP server '{server_name}': {e}")
        return 3

    print(f"Connected to MCP server '{server_name}'. Available tools:")
    for t in tools:
        print(f"- {t.get('name')}: {t.get('description')}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else "amass-mcp"))


