"""
MCP Client for connecting to multiple MCP servers
Provides a unified interface for subdomain enumeration
"""

import json
import asyncio
import yaml
import logging
from typing import Dict, List, Any, Optional
from pathlib import Path
import subprocess
import time

logger = logging.getLogger(__name__)

class MCPServerConfig:
    """Configuration for an individual MCP server"""
    
    def __init__(self, name: str, url: str, server_type: str, enabled: bool = True, **kwargs):
        self.name = name
        self.url = url
        self.server_type = server_type
        self.enabled = enabled
        self.config = kwargs
        self.process = None
        self.client = None

class MCPClient:
    """Client for managing multiple MCP servers"""
    
    def __init__(self, config_path: str = "config/mcp_servers.yaml"):
        self.config_path = Path(config_path)
        self.servers: Dict[str, MCPServerConfig] = {}
        self.default_config = {}
        self.load_config()
    
    def load_config(self):
        """Load MCP server configurations from YAML file"""
        try:
            with open(self.config_path, 'r') as f:
                config = yaml.safe_load(f)
            
            self.default_config = config.get('default_config', {})
            
            for server_config in config.get('mcp_servers', []):
                server = MCPServerConfig(**server_config)
                self.servers[server.name] = server
                
            logger.info(f"Loaded {len(self.servers)} MCP server configurations")
            
        except FileNotFoundError:
            logger.warning(f"Config file {self.config_path} not found, using default configuration")
            self._create_default_config()
        except Exception as e:
            logger.error(f"Error loading config: {e}")
            raise
    
    def _create_default_config(self):
        """Create default configuration if no config file exists"""
        default_server = MCPServerConfig(
            name="amass-mcp-default",
            url="http://localhost:8001",
            server_type="amass",
            enabled=True
        )
        self.servers[default_server.name] = default_server
    
    async def start_server(self, server_name: str) -> bool:
        """Start an MCP server process"""
        if server_name not in self.servers:
            logger.error(f"Server {server_name} not found in configuration")
            return False
        
        server = self.servers[server_name]
        
        if not server.enabled:
            logger.info(f"Server {server_name} is disabled")
            return False
        
        try:
            # Start the MCP server process
            if server.server_type == "amass":
                cmd = ["python", "mcp/amass_mcp_server.py"]
            else:
                logger.error(f"Unknown server type: {server.server_type}")
                return False
            
            server.process = await asyncio.create_subprocess_exec(
                *cmd,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            # Wait a moment for the server to start
            await asyncio.sleep(1)
            
            if server.process.returncode is None:
                logger.info(f"Started MCP server {server_name}")
                return True
            else:
                logger.error(f"Failed to start MCP server {server_name}")
                return False
            
        except Exception as e:
            logger.error(f"Error starting server {server_name}: {e}")
            return False
    
    async def stop_server(self, server_name: str):
        """Stop an MCP server process"""
        if server_name not in self.servers:
            return
        
        server = self.servers[server_name]
        
        if server.process:
            try:
                server.process.terminate()
                await asyncio.wait_for(server.process.wait(), timeout=5.0)
                logger.info(f"Stopped MCP server {server_name}")
            except asyncio.TimeoutError:
                server.process.kill()
                await server.process.wait()
                logger.warning(f"Force killed MCP server {server_name}")
            except Exception as e:
                logger.error(f"Error stopping server {server_name}: {e}")
    
    async def call_tool(self, server_name: str, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Call a tool on a specific MCP server"""
        if server_name not in self.servers:
            return {"error": f"Server {server_name} not found"}
        
        server = self.servers[server_name]
        
        if not server.enabled:
            return {"error": f"Server {server_name} is disabled"}
        
        try:
            # Create the tool call request
            request = {
                "method": "tools/call",
                "params": {
                    "name": tool_name,
                    "arguments": arguments
                }
            }
            
            # Send request to server
            if server.process and server.process.stdin:
                request_json = json.dumps(request) + "\\n"
                server.process.stdin.write(request_json.encode())
                await server.process.stdin.drain()
                
                # Read response
                response_line = await server.process.stdout.readline()
                if response_line:
                    response = json.loads(response_line.decode().strip())
                    return response
                else:
                    return {"error": "No response from server"}
            else:
                return {"error": "Server not running or not accessible"}
                
        except Exception as e:
            logger.error(f"Error calling tool {tool_name} on server {server_name}: {e}")
            return {"error": str(e)}
    
    async def enumerate_subdomains_passive(self, domain: str, servers: Optional[List[str]] = None) -> Dict[str, Any]:
        """Perform passive subdomain enumeration across specified servers"""
        if servers is None:
            servers = [name for name, server in self.servers.items() if server.enabled]
        
        results = {}
        
        for server_name in servers:
            try:
                result = await self.call_tool(
                    server_name,
                    "passive_subdomain_enum",
                    {"domain": domain}
                )
                results[server_name] = result
            except Exception as e:
                results[server_name] = {"error": str(e)}
        
        return self._consolidate_results(results, domain, "passive")
    
    async def enumerate_subdomains_active(self, domain: str, servers: Optional[List[str]] = None, config: Optional[Dict] = None) -> Dict[str, Any]:
        """Perform active subdomain enumeration across specified servers"""
        if servers is None:
            servers = [name for name, server in self.servers.items() if server.enabled]
        
        if config is None:
            config = {}
        
        results = {}
        
        for server_name in servers:
            try:
                arguments = {"domain": domain, **config}
                result = await self.call_tool(
                    server_name,
                    "active_subdomain_enum",
                    arguments
                )
                results[server_name] = result
            except Exception as e:
                results[server_name] = {"error": str(e)}
        
        return self._consolidate_results(results, domain, "active")
    
    async def enumerate_subdomains_combined(self, domain: str, servers: Optional[List[str]] = None, 
                                          passive_config: Optional[Dict] = None, 
                                          active_config: Optional[Dict] = None) -> Dict[str, Any]:
        """Perform both passive and active subdomain enumeration"""
        if servers is None:
            servers = [name for name, server in self.servers.items() if server.enabled]
        
        results = {}
        
        for server_name in servers:
            try:
                arguments = {
                    "domain": domain,
                    "passive_config": passive_config or {},
                    "active_config": active_config or {}
                }
                result = await self.call_tool(
                    server_name,
                    "combined_subdomain_enum",
                    arguments
                )
                results[server_name] = result
            except Exception as e:
                results[server_name] = {"error": str(e)}
        
        return self._consolidate_results(results, domain, "combined")
    
    def _consolidate_results(self, results: Dict[str, Any], domain: str, method: str) -> Dict[str, Any]:
        """Consolidate results from multiple servers"""
        all_subdomains = set()
        successful_servers = []
        failed_servers = []
        
        for server_name, result in results.items():
            if isinstance(result, dict) and result.get("success", False):
                successful_servers.append(server_name)
                if "subdomains" in result:
                    all_subdomains.update(result["subdomains"])
                elif "combined_subdomains" in result:
                    all_subdomains.update(result["combined_subdomains"])
            else:
                failed_servers.append(server_name)
        
        return {
            "domain": domain,
            "method": method,
            "success": len(successful_servers) > 0,
            "subdomains": sorted(list(all_subdomains)),
            "total_count": len(all_subdomains),
            "successful_servers": successful_servers,
            "failed_servers": failed_servers,
            "server_results": results,
            "timestamp": time.time()
        }
    
    async def list_available_tools(self, server_name: str) -> Dict[str, Any]:
        """List available tools on a specific server"""
        try:
            request = {"method": "tools/list", "params": {}}
            
            server = self.servers.get(server_name)
            if not server or not server.process:
                return {"error": "Server not running"}
            
            request_json = json.dumps(request) + "\\n"
            server.process.stdin.write(request_json.encode())
            await server.process.stdin.drain()
            
            response_line = await server.process.stdout.readline()
            if response_line:
                response = json.loads(response_line.decode().strip())
                return response
            else:
                return {"error": "No response from server"}
                
        except Exception as e:
            logger.error(f"Error listing tools on server {server_name}: {e}")
            return {"error": str(e)}
    
    async def start_all_servers(self) -> Dict[str, bool]:
        """Start all enabled MCP servers"""
        results = {}
        
        for server_name, server in self.servers.items():
            if server.enabled:
                results[server_name] = await self.start_server(server_name)
            else:
                results[server_name] = False
        
        return results
    
    async def stop_all_servers(self):
        """Stop all running MCP servers"""
        for server_name in self.servers.keys():
            await self.stop_server(server_name)
    
    def get_server_status(self) -> Dict[str, str]:
        """Get the status of all configured servers"""
        status = {}
        
        for server_name, server in self.servers.items():
            if not server.enabled:
                status[server_name] = "disabled"
            elif server.process is None:
                status[server_name] = "stopped"
            elif server.process.returncode is None:
                status[server_name] = "running"
            else:
                status[server_name] = "failed"
        
        return status
