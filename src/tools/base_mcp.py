from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional


@dataclass
class MCPServerConfig:
    """
    Generic configuration for an MCP stdio server.

    command: executable to launch (e.g., "node" or "python")
    args: arguments to the executable to start the MCP server
    env: optional environment variables for the subprocess
    name: logical name used for identification/logging
    """

    command: str
    args: List[str]
    env: Optional[Dict[str, str]] = None
    name: str = "mcp-server"


class MCPToolError(RuntimeError):
    pass


