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
from langchain.tools import BaseTool
from pydantic import BaseModel, Field

from .mcp_client import MCPClient

logger = logging.getLogger(__name__)

class SubdomainEnumerationInput(BaseModel):
    """Input model for subdomain enumeration"""
    domain: str = Field(description="Target domain for subdomain enumeration")
    method: str = Field(default="combined", description="Enumeration method: passive, active, or combined")
    servers: Optional[List[str]] = Field(default=None, description="List of MCP server names to use")
    passive_config: Optional[Dict] = Field(default=None, description="Configuration for passive enumeration")
    active_config: Optional[Dict] = Field(default=None, description="Configuration for active enumeration")

class SubdomainEnumerationTool(BaseTool):
    """CrewAI tool for subdomain enumeration using MCP servers"""
    
    name: str = "subdomain_enumeration"
    description: str = "Perform subdomain enumeration using Amass MCP servers. Supports passive, active, and combined enumeration methods."
    args_schema = SubdomainEnumerationInput
    
    def __init__(self, mcp_client: MCPClient):
        super().__init__()
        self.mcp_client = mcp_client
    
    def _run(self, domain: str, method: str = "combined", servers: Optional[List[str]] = None,
            passive_config: Optional[Dict] = None, active_config: Optional[Dict] = None) -> str:
        """Execute subdomain enumeration"""
        try:
            # Run the async enumeration
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            if method == "passive":
                result = loop.run_until_complete(
                    self.mcp_client.enumerate_subdomains_passive(domain, servers)
                )
            elif method == "active":
                result = loop.run_until_complete(
                    self.mcp_client.enumerate_subdomains_active(domain, servers, active_config)
                )
            elif method == "combined":
                result = loop.run_until_complete(
                    self.mcp_client.enumerate_subdomains_combined(domain, servers, passive_config, active_config)
                )
            else:
                return f"Invalid method: {method}. Use 'passive', 'active', or 'combined'."
            
            loop.close()
            
            # Format the results for the agent
            return self._format_results(result)
            
        except Exception as e:
            logger.error(f"Error in subdomain enumeration: {e}")
            return f"Error performing subdomain enumeration: {str(e)}"
    
    def _format_results(self, result: Dict[str, Any]) -> str:
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
                output += f"{i:3d}. {subdomain}\\n"
        else:
            output += "No subdomains discovered.\\n"
        
        return output

class SubdomainEnumerationAgent:
    """CrewAI Agent for subdomain enumeration using MCP servers"""
    
    def __init__(self, config_path: str = "config/mcp_servers.yaml"):
        self.mcp_client = MCPClient(config_path)
        self.tool = SubdomainEnumerationTool(self.mcp_client)
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
            tools=[self.tool],
            verbose=True,
            memory=True,
            allow_delegation=False
        )
    
    def create_enumeration_task(self, domain: str, method: str = "combined", 
                              servers: Optional[List[str]] = None,
                              passive_config: Optional[Dict] = None,
                              active_config: Optional[Dict] = None) -> Task:
        """Create a subdomain enumeration task"""
        
        task_description = f"""Perform {method} subdomain enumeration for the domain: {domain}
        
        Your task is to:
        1. Use the subdomain_enumeration tool to discover subdomains for {domain}
        2. Use the {method} enumeration method
        3. Analyze the results and provide insights about the discovered subdomains
        4. Identify any interesting or potentially vulnerable subdomains
        5. Provide recommendations for further investigation
        
        Method: {method}
        Target Domain: {domain}
        """
        
        if servers:
            task_description += f"\\nMCP Servers to use: {', '.join(servers)}"
        
        if passive_config:
            task_description += f"\\nPassive Configuration: {json.dumps(passive_config, indent=2)}"
        
        if active_config:
            task_description += f"\\nActive Configuration: {json.dumps(active_config, indent=2)}"
        
        return Task(
            description=task_description,
            agent=self.agent,
            expected_output="""A comprehensive report containing:
            1. Total number of subdomains discovered
            2. Complete list of discovered subdomains
            3. Analysis of subdomain patterns and naming conventions
            4. Identification of potentially interesting subdomains (admin, staging, dev, etc.)
            5. Recommendations for further security assessment
            6. Any errors or issues encountered during enumeration"""
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
@tool
def quick_subdomain_enum(domain: str, method: str = "passive") -> str:
    """Quick subdomain enumeration tool for immediate use"""
    try:
        agent = SubdomainEnumerationAgent()
        
        # Start servers
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        server_status = loop.run_until_complete(agent.start_mcp_servers())
        logger.info(f"MCP Server status: {server_status}")
        
        # Execute enumeration
        result = agent.execute_enumeration(domain, method)
        
        # Stop servers
        loop.run_until_complete(agent.stop_mcp_servers())
        loop.close()
        
        return result
        
    except Exception as e:
        logger.error(f"Error in quick enumeration: {e}")
        return f"Error performing quick subdomain enumeration: {str(e)}"

def create_subdomain_agent(config_path: str = "config/mcp_servers.yaml") -> SubdomainEnumerationAgent:
    """Factory function to create a subdomain enumeration agent"""
    return SubdomainEnumerationAgent(config_path)
