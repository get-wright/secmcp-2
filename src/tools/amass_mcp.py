from __future__ import annotations

from typing import Any, Dict, Optional

from crewai_tools import BaseTool

from src.config import load_mcp_server_config
from src.mcp_client.stdio_client import StdIoMCPClient
from src.tools.base_mcp import MCPToolError


class AmassMCPTool(BaseTool):
    """
    CrewAI Tool that connects to an amass MCP server over stdio and performs
    passive or active subdomain enumeration.

    Input:
      - domain: target domain
      - enumeration_type: "passive" (default) or "active"
    """

    name: str = "Amass MCP Subdomain Enumerator"
    description: str = (
        "Perform subdomain enumeration via amass MCP server."
    )

    mcp_server_name: str = "amass-mcp"

    def __init__(self, mcp_server_name: str = "amass-mcp"):
        super().__init__()
        self.mcp_server_name = mcp_server_name

    def _select_tool_name(self, tools: list[dict], enumeration_type: str) -> Optional[str]:
        et = enumeration_type.lower().strip()
        candidates = []
        for t in tools:
            name = (t.get("name") or "").lower()
            if et == "passive" and "passive" in name:
                candidates.append(t.get("name"))
            if et == "active" and "active" in name:
                candidates.append(t.get("name"))
        # Prefer exact matches if multiple
        for c in candidates:
            if f"{et}" in c.lower():
                return c
        return candidates[0] if candidates else None

    def _run(self, domain: str, enumeration_type: str = "passive") -> str:
        if not domain or not isinstance(domain, str):
            raise MCPToolError("Parameter 'domain' must be a non-empty string.")

        cfg = load_mcp_server_config(self.mcp_server_name)
        client = StdIoMCPClient(cfg)

        tools = client.list_tools_sync()
        tool_name = self._select_tool_name(tools, enumeration_type)

        if not tool_name:
            raise MCPToolError(
                f"No suitable MCP tool found for enumeration_type='{enumeration_type}'. "
                f"Available tools: {[t.get('name') for t in tools]}"
            )

        result = client.call_tool_sync(tool_name, {"domain": domain})

        # Normalize result to string for CrewAI
        if isinstance(result, (dict, list)):
            return str(result)
        return result if isinstance(result, str) else str(result)


