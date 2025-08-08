#!/usr/bin/env python3
"""
Amass MCP Server
A Model Control Protocol server for subdomain enumeration using Amass.
This server provides tools for passive and active subdomain enumeration.
"""

import asyncio
import json
import sys
from typing import Any, Dict, List, Optional
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import (
    Tool,
    TextContent,
    CallToolRequest,
    CallToolResult,
)
import subprocess
import logging
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global server instance
server = Server("amass-mcp")

@server.list_tools()
async def list_tools() -> List[Tool]:
    """List available Amass tools."""
    return [
        Tool(
            name="amass_passive_enum",
            description="Perform passive subdomain enumeration using Amass",
            inputSchema={
                "type": "object",
                "properties": {
                    "domain": {
                        "type": "string",
                        "description": "Target domain for subdomain enumeration"
                    },
                    "config_file": {
                        "type": "string",
                        "description": "Optional path to Amass configuration file",
                        "default": ""
                    },
                    "timeout": {
                        "type": "integer",
                        "description": "Timeout in seconds (default: 300)",
                        "default": 300
                    },
                    "wordlist": {
                        "type": "string",
                        "description": "Optional wordlist file for enumeration",
                        "default": ""
                    }
                },
                "required": ["domain"]
            }
        ),
        Tool(
            name="amass_active_enum",
            description="Perform active subdomain enumeration using Amass",
            inputSchema={
                "type": "object",
                "properties": {
                    "domain": {
                        "type": "string",
                        "description": "Target domain for subdomain enumeration"
                    },
                    "config_file": {
                        "type": "string",
                        "description": "Optional path to Amass configuration file",
                        "default": ""
                    },
                    "timeout": {
                        "type": "integer",
                        "description": "Timeout in seconds (default: 600)",
                        "default": 600
                    },
                    "brute_force": {
                        "type": "boolean",
                        "description": "Enable brute force enumeration",
                        "default": False
                    },
                    "wordlist": {
                        "type": "string",
                        "description": "Wordlist file for brute force enumeration",
                        "default": ""
                    }
                },
                "required": ["domain"]
            }
        ),
        Tool(
            name="amass_intel",
            description="Gather intelligence on domain using Amass",
            inputSchema={
                "type": "object",
                "properties": {
                    "domain": {
                        "type": "string",
                        "description": "Target domain for intelligence gathering"
                    },
                    "whois": {
                        "type": "boolean",
                        "description": "Include WHOIS information",
                        "default": True
                    },
                    "config_file": {
                        "type": "string",
                        "description": "Optional path to Amass configuration file",
                        "default": ""
                    }
                },
                "required": ["domain"]
            }
        )
    ]

async def run_amass_command(command: List[str], timeout: int = 300) -> Dict[str, Any]:
    """Run an Amass command and return the results."""
    try:
        logger.info(f"Running command: {' '.join(command)}")
        
        # Run the command with timeout
        process = await asyncio.create_subprocess_exec(
            *command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        try:
            stdout, stderr = await asyncio.wait_for(
                process.communicate(), 
                timeout=timeout
            )
        except asyncio.TimeoutError:
            process.kill()
            await process.wait()
            return {
                "success": False,
                "error": f"Command timed out after {timeout} seconds",
                "subdomains": []
            }
        
        # Process the output
        if process.returncode == 0:
            output = stdout.decode('utf-8').strip()
            subdomains = [line.strip() for line in output.split('\n') if line.strip()]
            
            return {
                "success": True,
                "subdomains": subdomains,
                "count": len(subdomains),
                "stderr": stderr.decode('utf-8') if stderr else ""
            }
        else:
            error_msg = stderr.decode('utf-8') if stderr else "Unknown error"
            return {
                "success": False,
                "error": f"Amass command failed: {error_msg}",
                "subdomains": []
            }
            
    except Exception as e:
        logger.error(f"Error running Amass command: {e}")
        return {
            "success": False,
            "error": f"Exception occurred: {str(e)}",
            "subdomains": []
        }

@server.call_tool()
async def call_tool(name: str, arguments: Dict[str, Any]) -> CallToolResult:
    """Handle tool calls for Amass operations."""
    
    if name == "amass_passive_enum":
        domain = arguments.get("domain")
        config_file = arguments.get("config_file", "")
        timeout = arguments.get("timeout", 300)
        wordlist = arguments.get("wordlist", "")
        
        if not domain:
            return CallToolResult(
                content=[TextContent(
                    type="text",
                    text="Error: Domain parameter is required"
                )]
            )
        
        # Build the Amass command for passive enumeration
        command = ["amass", "enum", "-passive", "-d", domain]
        
        if config_file:
            command.extend(["-config", config_file])
        
        if wordlist:
            command.extend(["-w", wordlist])
        
        result = await run_amass_command(command, timeout)
        
        return CallToolResult(
            content=[TextContent(
                type="text",
                text=json.dumps(result, indent=2)
            )]
        )
    
    elif name == "amass_active_enum":
        domain = arguments.get("domain")
        config_file = arguments.get("config_file", "")
        timeout = arguments.get("timeout", 600)
        brute_force = arguments.get("brute_force", False)
        wordlist = arguments.get("wordlist", "")
        
        if not domain:
            return CallToolResult(
                content=[TextContent(
                    type="text",
                    text="Error: Domain parameter is required"
                )]
            )
        
        # Build the Amass command for active enumeration
        command = ["amass", "enum", "-active", "-d", domain]
        
        if config_file:
            command.extend(["-config", config_file])
        
        if brute_force:
            command.append("-brute")
            if wordlist:
                command.extend(["-w", wordlist])
        
        result = await run_amass_command(command, timeout)
        
        return CallToolResult(
            content=[TextContent(
                type="text",
                text=json.dumps(result, indent=2)
            )]
        )
    
    elif name == "amass_intel":
        domain = arguments.get("domain")
        whois = arguments.get("whois", True)
        config_file = arguments.get("config_file", "")
        
        if not domain:
            return CallToolResult(
                content=[TextContent(
                    type="text",
                    text="Error: Domain parameter is required"
                )]
            )
        
        # Build the Amass command for intelligence gathering
        command = ["amass", "intel", "-d", domain]
        
        if whois:
            command.append("-whois")
        
        if config_file:
            command.extend(["-config", config_file])
        
        result = await run_amass_command(command, 300)
        
        return CallToolResult(
            content=[TextContent(
                type="text",
                text=json.dumps(result, indent=2)
            )]
        )
    
    else:
        return CallToolResult(
            content=[TextContent(
                type="text",
                text=f"Error: Unknown tool '{name}'"
            )]
        )

async def main():
    """Main function to run the MCP server."""
    logger.info("Starting Amass MCP Server...")
    
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )

if __name__ == "__main__":
    asyncio.run(main())
