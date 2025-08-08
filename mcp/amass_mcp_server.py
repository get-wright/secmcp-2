"""
Amass MCP Server Integration

This module provides the MCP server implementation for Amass tool integration.
Based on the official amass-mcp documentation from:
https://github.com/cyproxio/mcp-for-security/tree/main/amass-mcp

Follow the setup guide in the documentation to install and configure the amass binary.
This module only provides the MCP server interface - manual setup is required.
"""

import asyncio
import json
import logging
from typing import Any, Dict, List, Optional, Union

import mcp.server.stdio
import mcp.types as types
from mcp.server import NotificationOptions, Server
from mcp.server.models import InitializationOptions

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("amass-mcp")

# Initialize the MCP server
server = Server("amass-mcp")


@server.list_tools()
async def handle_list_tools() -> List[types.Tool]:
    """List available tools for Amass subdomain enumeration."""
    return [
        types.Tool(
            name="passive_subdomain_enum",
            description="Perform passive subdomain enumeration using Amass",
            inputSchema={
                "type": "object",
                "properties": {
                    "domain": {
                        "type": "string",
                        "description": "Target domain for subdomain enumeration"
                    },
                    "config": {
                        "type": "string",
                        "description": "Path to Amass configuration file (optional)",
                        "default": ""
                    },
                    "timeout": {
                        "type": "integer",
                        "description": "Timeout in seconds (optional)",
                        "default": 300
                    }
                },
                "required": ["domain"]
            }
        ),
        types.Tool(
            name="active_subdomain_enum", 
            description="Perform active subdomain enumeration using Amass",
            inputSchema={
                "type": "object",
                "properties": {
                    "domain": {
                        "type": "string",
                        "description": "Target domain for subdomain enumeration"
                    },
                    "brute_force": {
                        "type": "boolean",
                        "description": "Enable brute force enumeration",
                        "default": False
                    },
                    "wordlist": {
                        "type": "string", 
                        "description": "Path to custom wordlist (optional)",
                        "default": ""
                    },
                    "config": {
                        "type": "string",
                        "description": "Path to Amass configuration file (optional)",
                        "default": ""
                    },
                    "timeout": {
                        "type": "integer",
                        "description": "Timeout in seconds (optional)",
                        "default": 600
                    }
                },
                "required": ["domain"]
            }
        ),
        types.Tool(
            name="subdomain_intel",
            description="Gather intelligence on discovered subdomains",
            inputSchema={
                "type": "object",
                "properties": {
                    "domain": {
                        "type": "string",
                        "description": "Target domain for intelligence gathering"
                    },
                    "output_format": {
                        "type": "string",
                        "description": "Output format (json, txt, csv)",
                        "default": "json"
                    }
                },
                "required": ["domain"]
            }
        )
    ]


@server.call_tool()
async def handle_call_tool(
    name: str, arguments: Optional[Dict[str, Any]]
) -> List[types.TextContent]:
    """Handle tool calls for Amass operations."""
    
    if not arguments:
        arguments = {}
        
    try:
        if name == "passive_subdomain_enum":
            return await _passive_enumeration(arguments)
        elif name == "active_subdomain_enum":
            return await _active_enumeration(arguments)
        elif name == "subdomain_intel":
            return await _subdomain_intelligence(arguments)
        else:
            raise ValueError(f"Unknown tool: {name}")
            
    except Exception as e:
        logger.error(f"Error executing tool {name}: {str(e)}")
        return [types.TextContent(type="text", text=f"Error: {str(e)}")]


async def _passive_enumeration(arguments: Dict[str, Any]) -> List[types.TextContent]:
    """Execute passive subdomain enumeration using Amass."""
    domain = arguments.get("domain")
    config_path = arguments.get("config", "")
    timeout = arguments.get("timeout", 300)
    
    if not domain:
        raise ValueError("Domain is required for passive enumeration")
    
    # Build Amass command for passive enumeration
    cmd = ["amass", "enum", "-passive", "-d", domain]
    
    if config_path:
        cmd.extend(["-config", config_path])
    
    logger.info(f"Running passive enumeration for domain: {domain}")
    
    try:
        # Execute Amass command
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        stdout, stderr = await asyncio.wait_for(
            process.communicate(), timeout=timeout
        )
        
        if process.returncode == 0:
            results = stdout.decode().strip().split('\n')
            results = [r for r in results if r.strip()]  # Remove empty lines
            
            output = {
                "status": "success",
                "domain": domain,
                "method": "passive",
                "subdomains_found": len(results),
                "subdomains": results
            }
            
            return [types.TextContent(
                type="text", 
                text=json.dumps(output, indent=2)
            )]
        else:
            error_msg = stderr.decode().strip()
            raise RuntimeError(f"Amass execution failed: {error_msg}")
            
    except asyncio.TimeoutError:
        raise RuntimeError(f"Passive enumeration timed out after {timeout} seconds")


async def _active_enumeration(arguments: Dict[str, Any]) -> List[types.TextContent]:
    """Execute active subdomain enumeration using Amass."""
    domain = arguments.get("domain")
    brute_force = arguments.get("brute_force", False)
    wordlist = arguments.get("wordlist", "")
    config_path = arguments.get("config", "")
    timeout = arguments.get("timeout", 600)
    
    if not domain:
        raise ValueError("Domain is required for active enumeration")
    
    # Build Amass command for active enumeration
    cmd = ["amass", "enum", "-active", "-d", domain]
    
    if brute_force:
        cmd.append("-brute")
        
    if wordlist:
        cmd.extend(["-w", wordlist])
        
    if config_path:
        cmd.extend(["-config", config_path])
    
    logger.info(f"Running active enumeration for domain: {domain}")
    
    try:
        # Execute Amass command
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        stdout, stderr = await asyncio.wait_for(
            process.communicate(), timeout=timeout
        )
        
        if process.returncode == 0:
            results = stdout.decode().strip().split('\n')
            results = [r for r in results if r.strip()]  # Remove empty lines
            
            output = {
                "status": "success",
                "domain": domain,
                "method": "active",
                "brute_force_enabled": brute_force,
                "subdomains_found": len(results),
                "subdomains": results
            }
            
            return [types.TextContent(
                type="text", 
                text=json.dumps(output, indent=2)
            )]
        else:
            error_msg = stderr.decode().strip()
            raise RuntimeError(f"Amass execution failed: {error_msg}")
            
    except asyncio.TimeoutError:
        raise RuntimeError(f"Active enumeration timed out after {timeout} seconds")


async def _subdomain_intelligence(arguments: Dict[str, Any]) -> List[types.TextContent]:
    """Gather intelligence on discovered subdomains."""
    domain = arguments.get("domain")
    output_format = arguments.get("output_format", "json")
    
    if not domain:
        raise ValueError("Domain is required for intelligence gathering")
    
    # Build Amass command for intelligence gathering
    cmd = ["amass", "intel", "-d", domain]
    
    logger.info(f"Gathering intelligence for domain: {domain}")
    
    try:
        # Execute Amass command
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        stdout, stderr = await process.communicate()
        
        if process.returncode == 0:
            intel_data = stdout.decode().strip()
            
            if output_format.lower() == "json":
                output = {
                    "status": "success",
                    "domain": domain,
                    "intelligence": intel_data.split('\n') if intel_data else []
                }
                return [types.TextContent(
                    type="text", 
                    text=json.dumps(output, indent=2)
                )]
            else:
                return [types.TextContent(type="text", text=intel_data)]
        else:
            error_msg = stderr.decode().strip()
            raise RuntimeError(f"Amass intelligence gathering failed: {error_msg}")
            
    except Exception as e:
        raise RuntimeError(f"Intelligence gathering error: {str(e)}")


async def main():
    """Main entry point for the Amass MCP server."""
    # Run the server using stdio transport
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="amass-mcp",
                server_version="1.0.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )


if __name__ == "__main__":
    asyncio.run(main())
