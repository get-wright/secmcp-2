"""
CrewAI Agent for Subdomain Enumeration
Uses MCP servers to perform comprehensive subdomain discovery
"""

import asyncio
import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

from crewai import Agent, Task, Crew
from crewai.tools import tool
from pydantic import BaseModel, Field

from .mcp_client import MCPClient

logger = logging.getLogger(__name__)

# Global MCP client instance - will be set when creating the agent
_mcp_client = None

def set_mcp_client(client: MCPClient):
    """Set the global MCP client instance"""
    global _mcp_client
    _mcp_client = client

@tool("subdomain_enumeration")
def enumerate_subdomains(domain: str, method: str = "combined", 
                        servers: str = "", passive_sources: str = "", 
                        active_brute: bool = False, timeout: int = 30) -> str:
    """
    Perform subdomain enumeration using Amass MCP servers.
    
    Args:
        domain: Target domain for subdomain enumeration
        method: Enumeration method - 'passive', 'active', or 'combined' (default)
        servers: Comma-separated list of MCP server names to use (optional)
        passive_sources: Comma-separated list of passive sources (optional)
        active_brute: Enable brute force for active enumeration (default: False)
        timeout: Timeout in minutes (default: 30)
    
    Returns:
        Formatted enumeration results with discovered subdomains
    """
    global _mcp_client
    
    if _mcp_client is None:
        return "Error: MCP client not initialized. Please contact support."
    
    try:
        # Parse server list
        server_list = None
        if servers.strip():
            server_list = [s.strip() for s in servers.split(",") if s.strip()]
        
        # Configure passive enumeration
        passive_config = {}
        if passive_sources.strip():
            passive_config["sources"] = [s.strip() for s in passive_sources.split(",") if s.strip()]
        if timeout:
            passive_config["timeout"] = timeout
        
        # Configure active enumeration
        active_config = {}
        if active_brute:
            active_config["brute"] = True
        if timeout:
            active_config["timeout"] = timeout
        
        # Run the async enumeration
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            if method == "passive":
                result = loop.run_until_complete(
                    _mcp_client.enumerate_subdomains_passive(domain, server_list)
                )
            elif method == "active":
                result = loop.run_until_complete(
                    _mcp_client.enumerate_subdomains_active(domain, server_list, active_config)
                )
            elif method == "combined":
                result = loop.run_until_complete(
                    _mcp_client.enumerate_subdomains_combined(domain, server_list, passive_config, active_config)
                )
            else:
                return f"Invalid method: {method}. Use 'passive', 'active', or 'combined'."
        finally:
            loop.close()
        
        # Format the results for the agent
        return _format_enumeration_results(result)
        
    except Exception as e:
        logger.error(f"Error in subdomain enumeration: {e}")
        return f"Error performing subdomain enumeration: {str(e)}"

def _format_enumeration_results(result: Dict[str, Any]) -> str:
    """Format enumeration results for the agent"""
    if not result.get("success", False):
        return f"Subdomain enumeration failed for domain {result.get('domain', 'unknown')}"
    
    domain = result.get("domain", "unknown")
    method = result.get("method", "unknown")
    subdomains = result.get("subdomains", [])
    total_count = result.get("total_count", 0)
    successful_servers = result.get("successful_servers", [])
    failed_servers = result.get("failed_servers", [])
    
    output = f"""Subdomain Enumeration Results for {domain}:
Method: {method}
Total subdomains found: {total_count}
Successful servers: {', '.join(successful_servers) if successful_servers else 'None'}
Failed servers: {', '.join(failed_servers) if failed_servers else 'None'}

Discovered Subdomains:
"""
    
    if subdomains:
        for i, subdomain in enumerate(sorted(subdomains), 1):
            output += f"{i:3d}. {subdomain}\n"
    else:
        output += "No subdomains discovered.\n"
    
    # Add analysis if we have subdomains
    if subdomains:
        interesting_subdomains = [sub for sub in subdomains 
                                if any(keyword in sub.lower() for keyword in 
                                     ['admin', 'dev', 'test', 'staging', 'internal', 'api', 'mail'])]
        
        if interesting_subdomains:
            output += f"\nPotentially Interesting Subdomains ({len(interesting_subdomains)}):\n"
            for i, subdomain in enumerate(interesting_subdomains, 1):
                output += f"  {i}. {subdomain}\n"
        
        output += "\nRecommendations:\n"
        output += "1. Perform web application assessment on discovered subdomains\n"
        output += "2. Check for common vulnerabilities on admin interfaces\n"
        output += "3. Investigate development/staging environments for information disclosure\n"
    
    return output

class SubdomainEnumerationAgent:
    """CrewAI Agent for subdomain enumeration using MCP servers"""
    
    def __init__(self, config_path: str = "config/mcp_servers.yaml"):
        self.mcp_client = MCPClient(config_path)
        # Set the global MCP client for the tool
        set_mcp_client(self.mcp_client)
        self.agent = None
        self.crew = None
        self._setup_agent()
    
    def _setup_agent(self):
        """Set up the CrewAI agent"""
        self.agent = Agent(
            role="Cybersecurity Reconnaissance Specialist",
            goal="Perform comprehensive subdomain enumeration to map the attack surface of target domains",
            backstory="""You are an expert cybersecurity professional specializing in reconnaissance and 
            attack surface mapping. You use advanced subdomain enumeration techniques to discover 
            all possible subdomains associated with a target domain. You understand the importance 
            of both passive and active enumeration methods and can adapt your approach based on 
            the target and requirements.""",
            tools=[enumerate_subdomains],
            verbose=True,
            memory=True,
            allow_delegation=False
        )
    
    def create_enumeration_task(self, domain: str, method: str = "combined", 
                              servers: Optional[List[str]] = None,
                              passive_config: Optional[Dict] = None,
                              active_config: Optional[Dict] = None) -> Task:
        """Create a subdomain enumeration task"""
        
        # Build tool parameters
        tool_params = {
            "domain": domain,
            "method": method
        }
        
        if servers:
            tool_params["servers"] = ",".join(servers)
        
        if passive_config and passive_config.get("sources"):
            tool_params["passive_sources"] = ",".join(passive_config["sources"])
        
        if active_config:
            if active_config.get("brute"):
                tool_params["active_brute"] = True
            if active_config.get("timeout"):
                tool_params["timeout"] = active_config["timeout"]
        elif passive_config and passive_config.get("timeout"):
            tool_params["timeout"] = passive_config["timeout"]
        
        task_description = f"""Perform {method} subdomain enumeration for the domain: {domain}
        
        Use the subdomain_enumeration tool with these parameters:
        - domain: {domain}
        - method: {method}
        """
        
        if tool_params.get("servers"):
            task_description += f"\n- servers: {tool_params['servers']}"
        if tool_params.get("passive_sources"):
            task_description += f"\n- passive_sources: {tool_params['passive_sources']}"
        if tool_params.get("active_brute"):
            task_description += f"\n- active_brute: {tool_params['active_brute']}"
        if tool_params.get("timeout"):
            task_description += f"\n- timeout: {tool_params['timeout']}"
        
        task_description += """
        
        After getting the results, provide analysis and insights about:
        1. Total number of subdomains discovered
        2. Patterns in subdomain naming conventions
        3. Potentially interesting subdomains for security assessment
        4. Recommendations for further investigation
        """
        
        return Task(
            description=task_description,
            agent=self.agent,
            expected_output="""A comprehensive report containing the complete enumeration results, 
            analysis of discovered subdomains, identification of interesting targets, and 
            recommendations for further security assessment."""
        )
    
    async def start_mcp_servers(self) -> Dict[str, bool]:
        """Start all configured MCP servers"""
        return await self.mcp_client.start_all_servers()
    
    async def stop_mcp_servers(self):
        """Stop all MCP servers"""
        await self.mcp_client.stop_all_servers()
    
    def get_server_status(self) -> Dict[str, str]:
        """Get the status of all MCP servers"""
        return self.mcp_client.get_server_status()
    
    def execute_enumeration(self, domain: str, method: str = "combined",
                          servers: Optional[List[str]] = None,
                          passive_config: Optional[Dict] = None,
                          active_config: Optional[Dict] = None) -> str:
        """Execute subdomain enumeration task"""
        
        # Create the task
        task = self.create_enumeration_task(domain, method, servers, passive_config, active_config)
        
        # Create and execute the crew
        crew = Crew(
            agents=[self.agent],
            tasks=[task],
            verbose=True,
            memory=True
        )
        
        try:
            result = crew.kickoff()
            return str(result)
        except Exception as e:
            logger.error(f"Error executing enumeration crew: {e}")
            return f"Error executing subdomain enumeration: {str(e)}"
    
    def list_available_servers(self) -> List[str]:
        """List all configured MCP servers"""
        return list(self.mcp_client.servers.keys())
    
    def get_enabled_servers(self) -> List[str]:
        """Get list of enabled MCP servers"""
        return [name for name, server in self.mcp_client.servers.items() if server.enabled]

# Convenience function for quick enumeration
@tool("quick_subdomain_enum")
def quick_subdomain_enum(domain: str, method: str = "passive") -> str:
    """Quick subdomain enumeration tool for immediate use without full agent setup"""
    try:
        # Use the global enumerate_subdomains tool directly
        return enumerate_subdomains(domain=domain, method=method)
        
    except Exception as e:
        logger.error(f"Error in quick enumeration: {e}")
        return f"Error performing quick subdomain enumeration: {str(e)}"

def create_subdomain_agent(config_path: str = "config/mcp_servers.yaml") -> SubdomainEnumerationAgent:
    """Factory function to create a subdomain enumeration agent"""
    return SubdomainEnumerationAgent(config_path)
