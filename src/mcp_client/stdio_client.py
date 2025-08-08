from __future__ import annotations

import anyio
from typing import Any, Dict, List, Optional, Tuple

from mcp import StdioServerParameters
from mcp.client.stdio import stdio_client
from mcp.client.session import ClientSession

from src.tools.base_mcp import MCPServerConfig, MCPToolError


class StdIoMCPClient:
    """
    Minimal MCP stdio client wrapper around the official Python MCP SDK.

    Provides convenience helpers to list tools and call a tool with arguments.
    """

    def __init__(self, server_config: MCPServerConfig):
        self.server_config = server_config

    async def _asession(self) -> Tuple[ClientSession, Any]:
        params = StdioServerParameters(
            command=self.server_config.command,
            args=self.server_config.args,
            env=self.server_config.env or {},
        )

        transport_cm = stdio_client(params)
        read = write = None
        transport = await transport_cm.__aenter__()
        if isinstance(transport, tuple) and len(transport) == 2:
            read, write = transport
        else:
            # Fallback if SDK changes; fail clearly
            await transport_cm.__aexit__(None, None, None)
            raise MCPToolError("Unexpected transport returned by MCP stdio_client().")

        session = ClientSession(read, write)
        await session.__aenter__()
        # Ensure handshake/initialization is performed before use
        await session.initialize()
        return session, transport_cm

    async def list_tools(self) -> List[Dict[str, Any]]:
        session: Optional[ClientSession] = None
        transport_cm: Optional[anyio.abc.AsyncResource] = None
        try:
            session, transport_cm = await self._asession()
            tools_response = await session.list_tools()
            # Normalize to list of dicts for easier consumption
            tools: List[Dict[str, Any]] = []
            for tool in tools_response.tools:
                tools.append({
                    "name": tool.name,
                    "description": tool.description,
                    "inputSchema": getattr(tool, "input_schema", None),
                })
            return tools
        finally:
            if session is not None:
                await session.__aexit__(None, None, None)
            if transport_cm is not None:
                await transport_cm.__aexit__(None, None, None)

    async def call_tool(self, name: str, arguments: Dict[str, Any]) -> Any:
        session: Optional[ClientSession] = None
        transport_cm: Optional[anyio.abc.AsyncResource] = None
        try:
            session, transport_cm = await self._asession()
            result = await session.call_tool(name, arguments)
            # Some MCP servers return structured content; standardize to dict
            return getattr(result, "content", result)
        finally:
            if session is not None:
                await session.__aexit__(None, None, None)
            if transport_cm is not None:
                await transport_cm.__aexit__(None, None, None)

    def list_tools_sync(self) -> List[Dict[str, Any]]:
        return anyio.run(self.list_tools)

    def call_tool_sync(self, name: str, arguments: Dict[str, Any]) -> Any:
        return anyio.run(lambda: self.call_tool(name, arguments))


