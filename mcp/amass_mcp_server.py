#!/usr/bin/env python3
"""
Amass MCP Server for Subdomain Enumeration
Provides both passive and active subdomain enumeration capabilities
"""

import json
import asyncio
import subprocess
import tempfile
import os
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging

# MCP Server implementation
try:
    from mcp.server import Server
    from mcp.server.models import InitializationOptions
    from mcp.server.stdio import stdio_server
    from mcp.types import Tool, TextContent
except ImportError:
    print("MCP package not found. Installing required dependencies...")
    subprocess.run(["pip", "install", "mcp"], check=True)
    from mcp.server import Server
    from mcp.server.models import InitializationOptions
    from mcp.server.stdio import stdio_server
    from mcp.types import Tool, TextContent

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AmassEnumerator:
    """Handles Amass subdomain enumeration operations"""
    
    def __init__(self):
        self.amass_path = self._find_amass()
        
    def _find_amass(self) -> str:
        """Find Amass executable in system PATH"""
        try:
            result = subprocess.run(["which", "amass"], capture_output=True, text=True)
            if result.returncode == 0:
                return result.stdout.strip()
        except FileNotFoundError:
            # Try Windows where command
            try:
                result = subprocess.run(["where", "amass"], capture_output=True, text=True, shell=True)
                if result.returncode == 0:
                    return result.stdout.strip().split('\n')[0]
            except FileNotFoundError:
                pass
        
        # Check common installation paths
        common_paths = [
            "/usr/local/bin/amass",
            "/usr/bin/amass",
            "/opt/amass/amass",
            "C:\\Program Files\\Amass\\amass.exe",
            "./amass"
        ]
        
        for path in common_paths:
            if os.path.exists(path):
                return path
        
        raise FileNotFoundError("Amass not found in PATH or common installation directories")
    
    async def passive_enum(self, domain: str, config: Optional[Dict] = None) -> Dict[str, Any]:
        """Perform passive subdomain enumeration"""
        try:
            cmd = [
                self.amass_path,
                "enum",
                "-passive",
                "-d", domain,
                "-json"
            ]
            
            if config:
                # Add configuration options
                if config.get("sources"):
                    cmd.extend(["-src", ",".join(config["sources"])])
                if config.get("timeout"):
                    cmd.extend(["-timeout", str(config["timeout"])])
            
            logger.info(f"Running passive enumeration for {domain}")
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode != 0:
                error_msg = stderr.decode() if stderr else "Unknown error"
                logger.error(f"Amass passive enumeration failed: {error_msg}")
                return {
                    "success": False,
                    "error": error_msg,
                    "subdomains": [],
                    "domain": domain,
                    "method": "passive"
                }
            
            # Parse JSON output
            subdomains = []
            output_lines = stdout.decode().strip().split('\n')
            
            for line in output_lines:
                if line.strip():
                    try:
                        data = json.loads(line)
                        if 'name' in data:
                            subdomains.append(data['name'])
                    except json.JSONDecodeError:
                        # Handle non-JSON lines
                        if line.strip() and '.' in line:
                            subdomains.append(line.strip())
            
            return {
                "success": True,
                "subdomains": list(set(subdomains)),  # Remove duplicates
                "domain": domain,
                "method": "passive",
                "count": len(set(subdomains)),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error in passive enumeration: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "subdomains": [],
                "domain": domain,
                "method": "passive"
            }
    
    async def active_enum(self, domain: str, config: Optional[Dict] = None) -> Dict[str, Any]:
        """Perform active subdomain enumeration"""
        try:
            cmd = [
                self.amass_path,
                "enum",
                "-active",
                "-d", domain,
                "-json"
            ]
            
            if config:
                # Add configuration options
                if config.get("brute"):
                    cmd.append("-brute")
                if config.get("wordlist"):
                    cmd.extend(["-w", config["wordlist"]])
                if config.get("timeout"):
                    cmd.extend(["-timeout", str(config["timeout"])])
                if config.get("resolvers"):
                    cmd.extend(["-r", config["resolvers"]])
            
            logger.info(f"Running active enumeration for {domain}")
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode != 0:
                error_msg = stderr.decode() if stderr else "Unknown error"
                logger.error(f"Amass active enumeration failed: {error_msg}")
                return {
                    "success": False,
                    "error": error_msg,
                    "subdomains": [],
                    "domain": domain,
                    "method": "active"
                }
            
            # Parse JSON output
            subdomains = []
            output_lines = stdout.decode().strip().split('\n')
            
            for line in output_lines:
                if line.strip():
                    try:
                        data = json.loads(line)
                        if 'name' in data:
                            subdomains.append(data['name'])
                    except json.JSONDecodeError:
                        # Handle non-JSON lines
                        if line.strip() and '.' in line:
                            subdomains.append(line.strip())
            
            return {
                "success": True,
                "subdomains": list(set(subdomains)),  # Remove duplicates
                "domain": domain,
                "method": "active",
                "count": len(set(subdomains)),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error in active enumeration: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "subdomains": [],
                "domain": domain,
                "method": "active"
            }

# Initialize the MCP server
server = Server("amass-mcp-server")
enumerator = AmassEnumerator()

@server.list_tools()
async def list_tools() -> List[Tool]:
    """List available tools"""
    return [
        Tool(
            name="passive_subdomain_enum",
            description="Perform passive subdomain enumeration using Amass",
            inputSchema={
                "type": "object",
                "properties": {
                    "domain": {
                        "type": "string",
                        "description": "Target domain for subdomain enumeration"
                    },
                    "sources": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Optional: List of data sources to use"
                    },
                    "timeout": {
                        "type": "integer",
                        "description": "Optional: Timeout in minutes"
                    }
                },
                "required": ["domain"]
            }
        ),
        Tool(
            name="active_subdomain_enum",
            description="Perform active subdomain enumeration using Amass",
            inputSchema={
                "type": "object",
                "properties": {
                    "domain": {
                        "type": "string",
                        "description": "Target domain for subdomain enumeration"
                    },
                    "brute": {
                        "type": "boolean",
                        "description": "Enable brute force enumeration"
                    },
                    "wordlist": {
                        "type": "string",
                        "description": "Path to wordlist file for brute force"
                    },
                    "timeout": {
                        "type": "integer",
                        "description": "Optional: Timeout in minutes"
                    },
                    "resolvers": {
                        "type": "string",
                        "description": "Path to custom DNS resolvers file"
                    }
                },
                "required": ["domain"]
            }
        ),
        Tool(
            name="combined_subdomain_enum",
            description="Perform both passive and active subdomain enumeration",
            inputSchema={
                "type": "object",
                "properties": {
                    "domain": {
                        "type": "string",
                        "description": "Target domain for subdomain enumeration"
                    },
                    "passive_config": {
                        "type": "object",
                        "description": "Configuration for passive enumeration"
                    },
                    "active_config": {
                        "type": "object",
                        "description": "Configuration for active enumeration"
                    }
                },
                "required": ["domain"]
            }
        )
    ]

@server.call_tool()
async def call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
    """Handle tool calls"""
    try:
        if name == "passive_subdomain_enum":
            domain = arguments["domain"]
            config = {
                "sources": arguments.get("sources"),
                "timeout": arguments.get("timeout")
            }
            result = await enumerator.passive_enum(domain, config)
            
        elif name == "active_subdomain_enum":
            domain = arguments["domain"]
            config = {
                "brute": arguments.get("brute", False),
                "wordlist": arguments.get("wordlist"),
                "timeout": arguments.get("timeout"),
                "resolvers": arguments.get("resolvers")
            }
            result = await enumerator.active_enum(domain, config)
            
        elif name == "combined_subdomain_enum":
            domain = arguments["domain"]
            passive_config = arguments.get("passive_config", {})
            active_config = arguments.get("active_config", {})
            
            # Run both passive and active enumeration
            passive_result = await enumerator.passive_enum(domain, passive_config)
            active_result = await enumerator.active_enum(domain, active_config)
            
            # Combine results
            all_subdomains = list(set(passive_result.get("subdomains", []) + active_result.get("subdomains", [])))
            
            result = {
                "success": passive_result.get("success", False) and active_result.get("success", False),
                "domain": domain,
                "passive_results": passive_result,
                "active_results": active_result,
                "combined_subdomains": all_subdomains,
                "total_count": len(all_subdomains),
                "timestamp": datetime.now().isoformat()
            }
        else:
            result = {"error": f"Unknown tool: {name}"}
        
        return [TextContent(type="text", text=json.dumps(result, indent=2))]
        
    except Exception as e:
        logger.error(f"Error calling tool {name}: {str(e)}")
        error_result = {
            "success": False,
            "error": str(e),
            "tool": name,
            "arguments": arguments
        }
        return [TextContent(type="text", text=json.dumps(error_result, indent=2))]

async def main():
    """Main server entry point"""
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, InitializationOptions())

if __name__ == "__main__":
    asyncio.run(main())
