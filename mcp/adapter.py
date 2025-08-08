"""
MCP Adapter Utilities
Provides utilities for connecting to and managing multiple MCP servers.
"""

from typing import List, Optional, Dict, Any
from crewai_tools import MCPServerAdapter
from mcp import StdioServerParameters
import logging

from .config import MCPConfigManager, MCPServerConfig

logger = logging.getLogger(__name__)


class MCPManager:
    """Manages multiple MCP server connections."""
    
    def __init__(self, config_manager: Optional[MCPConfigManager] = None):
        self.config_manager = config_manager or MCPConfigManager()
        self.adapters: Dict[str, MCPServerAdapter] = {}
        self._all_tools = []
    
    def get_server_parameters(self, server_names: Optional[List[str]] = None) -> List[StdioServerParameters]:
        """Get StdioServerParameters for specified servers or all enabled servers."""
        if server_names is None:
            # Get all enabled servers
            configs = self.config_manager.get_enabled_servers()
        else:
            # Get specific servers
            configs = []
            for name in server_names:
                config = self.config_manager.get_server_config(name)
                if config and config.enabled:
                    configs.append(config)
                else:
                    logger.warning(f"Server '{name}' not found or disabled")
        
        # Filter for stdio servers only and create parameters
        stdio_params = []
        for config in configs:
            if config.server_type == "stdio":
                params = self.config_manager.create_stdio_parameters(config.name)
                if params:
                    stdio_params.append(params)
        
        return stdio_params
    
    def create_managed_adapter(self, server_names: Optional[List[str]] = None) -> MCPServerAdapter:
        """Create a managed MCPServerAdapter for the specified servers."""
        server_params = self.get_server_parameters(server_names)
        
        if not server_params:
            raise ValueError("No valid server parameters found")
        
        # If only one server, pass the single parameter
        if len(server_params) == 1:
            return MCPServerAdapter(server_params[0])
        else:
            # For multiple servers, pass the list
            return MCPServerAdapter(server_params)
    
    def list_available_servers(self) -> Dict[str, str]:
        """List all available servers with their descriptions."""
        return self.config_manager.list_servers()
    
    def add_server_config(self, config: MCPServerConfig):
        """Add a new server configuration."""
        self.config_manager.add_server_config(config)


class ReconnaissanceMCPTools:
    """Wrapper class for reconnaissance-specific MCP tools."""
    
    def __init__(self, mcp_manager: MCPManager):
        self.mcp_manager = mcp_manager
        self.adapter = None
        self.tools = []
    
    def __enter__(self):
        """Enter context manager to start MCP connections."""
        try:
            # Create adapter for amass-mcp server specifically
            self.adapter = self.mcp_manager.create_managed_adapter(["amass-mcp"])
            self.adapter.__enter__()
            self.tools = self.adapter.tools
            logger.info(f"Connected to MCP servers. Available tools: {[tool.name for tool in self.tools]}")
            return self.tools
        except Exception as e:
            logger.error(f"Failed to connect to MCP servers: {e}")
            raise
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit context manager to clean up MCP connections."""
        if self.adapter:
            try:
                self.adapter.__exit__(exc_type, exc_val, exc_tb)
                logger.info("Disconnected from MCP servers")
            except Exception as e:
                logger.error(f"Error disconnecting from MCP servers: {e}")
    
    def get_amass_tools(self) -> List[Any]:
        """Get tools specifically for Amass operations."""
        if not self.tools:
            return []
        
        # Filter tools that are related to Amass
        amass_tools = [tool for tool in self.tools if 'amass' in tool.name.lower()]
        return amass_tools
