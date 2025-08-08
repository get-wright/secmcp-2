from __future__ import annotations

from typing import List, Optional
import os
import yaml

from src.tools.base_mcp import MCPServerConfig, MCPToolError


DEFAULT_MCP_SERVERS_FILE = os.path.join("mcp", "mcp_servers.yaml")


def _load_yaml(path: str) -> dict:
    if not os.path.exists(path):
        raise MCPToolError(
            f"MCP servers config file not found at '{path}'. Please create it as per the README."
        )
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def load_mcp_server_config(name: str, path: str = DEFAULT_MCP_SERVERS_FILE) -> MCPServerConfig:
    data = _load_yaml(path)
    servers: List[dict] = data.get("servers", [])
    for s in servers:
        if s.get("name") == name:
            command = s.get("command")
            args = s.get("args") or []
            env = s.get("env") or None
            if not command or not isinstance(args, list):
                raise MCPToolError(
                    f"Invalid MCP server entry for '{name}'. 'command' and list 'args' are required."
                )
            return MCPServerConfig(command=command, args=args, env=env, name=name)
    raise MCPToolError(f"MCP server configuration for '{name}' not found in {path}.")


