"""
MCP Server Configuration Management
Provides centralized configuration for multiple MCP servers including amass-mcp.
"""

import os
from typing import Dict, List, Optional
from dataclasses import dataclass
from mcp import StdioServerParameters


@dataclass
class MCPServerConfig:
    """Configuration for a single MCP server."""
    name: str
    server_type: str  # 'stdio', 'sse', 'http'
    command: str
    args: List[str]
    env: Optional[Dict[str, str]] = None
    description: str = ""
    enabled: bool = True


class MCPConfigManager:
    """Manages configurations for multiple MCP servers."""
    
    def __init__(self):
        self.servers: Dict[str, MCPServerConfig] = {}
        self._load_default_configs()
    
    def _load_default_configs(self):
        """Load default MCP server configurations."""
        # Amass MCP Server Configuration
        self.add_server_config(MCPServerConfig(
            name="amass-mcp",
            server_type="stdio",
            command="python",
            args=[os.path.join("mcp", "servers", "amass_mcp_server.py")],
            env={**os.environ},
            description="Amass subdomain enumeration MCP server",
            enabled=True
        ))
    
    def add_server_config(self, config: MCPServerConfig):
        """Add a new MCP server configuration."""
        self.servers[config.name] = config
    
    def get_server_config(self, name: str) -> Optional[MCPServerConfig]:
        """Get configuration for a specific server."""
        return self.servers.get(name)
    
    def get_enabled_servers(self) -> List[MCPServerConfig]:
        """Get list of enabled server configurations."""
        return [config for config in self.servers.values() if config.enabled]
    
    def create_stdio_parameters(self, server_name: str) -> Optional[StdioServerParameters]:
        """Create StdioServerParameters for a given server."""
        config = self.get_server_config(server_name)
        if not config or config.server_type != "stdio":
            return None
        
        return StdioServerParameters(
            command=config.command,
            args=config.args,
            env=config.env or {}
        )
    
    def list_servers(self) -> Dict[str, str]:
        """List all configured servers with their descriptions."""
        return {
            name: config.description 
            for name, config in self.servers.items()
        }
