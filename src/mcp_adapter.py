"""
MCP Adapter Module

This module provides a modular interface for connecting to multiple MCP servers.
It allows easy integration of different MCP services with the CrewAI agents.
"""

import asyncio
import json
import subprocess
import sys
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union
from dataclasses import dataclass
from enum import Enum

from loguru import logger


class MCPServerStatus(Enum):
    """Enumeration for MCP server status."""
    STOPPED = "stopped"
    RUNNING = "running" 
    ERROR = "error"
    UNKNOWN = "unknown"


@dataclass
class MCPServerConfig:
    """Configuration for an MCP server."""
    name: str
    command: List[str]
    working_directory: Optional[str] = None
    environment: Optional[Dict[str, str]] = None
    timeout: int = 30
    auto_restart: bool = True


@dataclass
class MCPResponse:
    """Standardized response from MCP server operations."""
    success: bool
    data: Optional[Any] = None
    error: Optional[str] = None
    server_name: Optional[str] = None


class BaseMCPClient(ABC):
    """Base class for MCP client implementations."""
    
    def __init__(self, config: MCPServerConfig):
        self.config = config
        self.status = MCPServerStatus.STOPPED
        self.process: Optional[subprocess.Popen] = None
        
    @abstractmethod
    async def connect(self) -> bool:
        """Connect to the MCP server."""
        pass
        
    @abstractmethod
    async def disconnect(self) -> bool:
        """Disconnect from the MCP server."""
        pass
        
    @abstractmethod
    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> MCPResponse:
        """Call a tool on the MCP server."""
        pass
        
    @abstractmethod
    async def list_tools(self) -> List[Dict[str, Any]]:
        """List available tools on the MCP server."""
        pass


class AmasseMCPClient(BaseMCPClient):
    """MCP client for Amass subdomain enumeration server."""
    
    async def connect(self) -> bool:
        """Connect to the Amass MCP server."""
        try:
            logger.info(f"Starting Amass MCP server: {self.config.name}")
            
            # Start the MCP server process
            self.process = subprocess.Popen(
                self.config.command,
                cwd=self.config.working_directory,
                env=self.config.environment,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Give the server time to start up
            await asyncio.sleep(2)
            
            if self.process.poll() is None:
                self.status = MCPServerStatus.RUNNING
                logger.info(f"Amass MCP server {self.config.name} started successfully")
                return True
            else:
                self.status = MCPServerStatus.ERROR
                stderr_output = self.process.stderr.read() if self.process.stderr else "Unknown error"
                logger.error(f"Amass MCP server failed to start: {stderr_output}")
                return False
                
        except Exception as e:
            self.status = MCPServerStatus.ERROR
            logger.error(f"Failed to start Amass MCP server: {str(e)}")
            return False
    
    async def disconnect(self) -> bool:
        """Disconnect from the Amass MCP server."""
        try:
            if self.process and self.process.poll() is None:
                self.process.terminate()
                try:
                    await asyncio.wait_for(
                        asyncio.create_task(self._wait_for_process()), 
                        timeout=5
                    )
                except asyncio.TimeoutError:
                    logger.warning("MCP server didn't terminate gracefully, killing...")
                    self.process.kill()
                    
            self.status = MCPServerStatus.STOPPED
            logger.info(f"Amass MCP server {self.config.name} stopped")
            return True
            
        except Exception as e:
            logger.error(f"Error stopping Amass MCP server: {str(e)}")
            return False
    
    async def _wait_for_process(self):
        """Wait for the process to terminate."""
        while self.process and self.process.poll() is None:
            await asyncio.sleep(0.1)
    
    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> MCPResponse:
        """Call a tool on the Amass MCP server."""
        if self.status != MCPServerStatus.RUNNING:
            return MCPResponse(
                success=False,
                error="MCP server is not running",
                server_name=self.config.name
            )
        
        try:
            # Prepare the MCP request
            request = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "tools/call",
                "params": {
                    "name": tool_name,
                    "arguments": arguments
                }
            }
            
            # Send request to MCP server
            request_json = json.dumps(request) + "\n"
            self.process.stdin.write(request_json)
            self.process.stdin.flush()
            
            # Read response (simplified - in production you'd want proper JSON-RPC handling)
            response_line = self.process.stdout.readline()
            if response_line:
                response = json.loads(response_line.strip())
                
                if "error" in response:
                    return MCPResponse(
                        success=False,
                        error=response["error"].get("message", "Unknown error"),
                        server_name=self.config.name
                    )
                else:
                    return MCPResponse(
                        success=True,
                        data=response.get("result"),
                        server_name=self.config.name
                    )
            else:
                return MCPResponse(
                    success=False,
                    error="No response from MCP server",
                    server_name=self.config.name
                )
                
        except Exception as e:
            logger.error(f"Error calling tool {tool_name}: {str(e)}")
            return MCPResponse(
                success=False,
                error=str(e),
                server_name=self.config.name
            )
    
    async def list_tools(self) -> List[Dict[str, Any]]:
        """List available tools on the Amass MCP server."""
        if self.status != MCPServerStatus.RUNNING:
            return []
        
        try:
            request = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "tools/list"
            }
            
            request_json = json.dumps(request) + "\n"
            self.process.stdin.write(request_json)
            self.process.stdin.flush()
            
            response_line = self.process.stdout.readline()
            if response_line:
                response = json.loads(response_line.strip())
                return response.get("result", {}).get("tools", [])
            else:
                return []
                
        except Exception as e:
            logger.error(f"Error listing tools: {str(e)}")
            return []


class MCPManager:
    """Manager for multiple MCP server connections."""
    
    def __init__(self):
        self.clients: Dict[str, BaseMCPClient] = {}
        self.configs: Dict[str, MCPServerConfig] = {}
    
    def register_server(self, config: MCPServerConfig, client_class: type = AmasseMCPClient):
        """Register a new MCP server configuration."""
        if config.name in self.configs:
            logger.warning(f"Server {config.name} already registered, updating...")
        
        self.configs[config.name] = config
        self.clients[config.name] = client_class(config)
        logger.info(f"Registered MCP server: {config.name}")
    
    async def connect_server(self, server_name: str) -> bool:
        """Connect to a specific MCP server."""
        if server_name not in self.clients:
            logger.error(f"Server {server_name} not registered")
            return False
        
        return await self.clients[server_name].connect()
    
    async def disconnect_server(self, server_name: str) -> bool:
        """Disconnect from a specific MCP server."""
        if server_name not in self.clients:
            logger.error(f"Server {server_name} not registered")
            return False
        
        return await self.clients[server_name].disconnect()
    
    async def connect_all(self) -> Dict[str, bool]:
        """Connect to all registered MCP servers."""
        results = {}
        for server_name in self.clients:
            results[server_name] = await self.connect_server(server_name)
        return results
    
    async def disconnect_all(self) -> Dict[str, bool]:
        """Disconnect from all MCP servers."""
        results = {}
        for server_name in self.clients:
            results[server_name] = await self.disconnect_server(server_name)
        return results
    
    async def call_tool(self, server_name: str, tool_name: str, arguments: Dict[str, Any]) -> MCPResponse:
        """Call a tool on a specific MCP server."""
        if server_name not in self.clients:
            return MCPResponse(
                success=False,
                error=f"Server {server_name} not registered"
            )
        
        return await self.clients[server_name].call_tool(tool_name, arguments)
    
    async def list_tools(self, server_name: str) -> List[Dict[str, Any]]:
        """List tools for a specific MCP server."""
        if server_name not in self.clients:
            return []
        
        return await self.clients[server_name].list_tools()
    
    def get_server_status(self, server_name: str) -> MCPServerStatus:
        """Get the status of a specific MCP server."""
        if server_name not in self.clients:
            return MCPServerStatus.UNKNOWN
        
        return self.clients[server_name].status
    
    def get_all_statuses(self) -> Dict[str, MCPServerStatus]:
        """Get status of all registered MCP servers."""
        return {
            name: client.status 
            for name, client in self.clients.items()
        }


# Convenience function to create Amass MCP configuration
def create_amass_config(
    name: str = "amass-mcp",
    amass_binary_path: str = "amass",
    config_file: Optional[str] = None,
    working_directory: Optional[str] = None
) -> MCPServerConfig:
    """Create an Amass MCP server configuration."""
    
    # Build the command to run the Amass MCP server
    # This assumes the mcp server script is in the mcp directory
    command = [sys.executable, "-m", "mcp.amass_mcp_server"]
    
    environment = {}
    if config_file:
        environment["AMASS_CONFIG"] = config_file
    
    return MCPServerConfig(
        name=name,
        command=command,
        working_directory=working_directory,
        environment=environment,
        timeout=30,
        auto_restart=True
    )
