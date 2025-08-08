"""
Reconnaissance Agent for CrewAI

This module implements a specialized CrewAI agent for performing subdomain reconnaissance
using the Amass MCP server and other security tools.
"""

import asyncio
import json
from typing import Any, Dict, List, Optional, Union

from crewai import Agent, Task, Crew
from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from loguru import logger

from .mcp_adapter import MCPManager, create_amass_config, MCPResponse


class SubdomainEnumInput(BaseModel):
    """Input schema for subdomain enumeration tools."""
    domain: str = Field(..., description="Target domain for subdomain enumeration")
    config: Optional[str] = Field(None, description="Path to Amass configuration file")
    timeout: Optional[int] = Field(300, description="Timeout in seconds")


class ActiveSubdomainEnumInput(SubdomainEnumInput):
    """Input schema for active subdomain enumeration."""
    brute_force: Optional[bool] = Field(False, description="Enable brute force enumeration")
    wordlist: Optional[str] = Field(None, description="Path to custom wordlist")


class SubdomainIntelInput(BaseModel):
    """Input schema for subdomain intelligence gathering."""
    domain: str = Field(..., description="Target domain for intelligence gathering")
    output_format: Optional[str] = Field("json", description="Output format (json, txt, csv)")


class PassiveSubdomainEnumTool(BaseTool):
    """Tool for passive subdomain enumeration using Amass MCP."""
    
    name: str = "passive_subdomain_enumeration"
    description: str = "Perform passive subdomain enumeration using Amass without direct interaction with target"
    args_schema: type[BaseModel] = SubdomainEnumInput
    
    def __init__(self, mcp_manager: MCPManager):
        super().__init__()
        self.mcp_manager = mcp_manager
    
    def _run(self, domain: str, config: Optional[str] = None, timeout: Optional[int] = 300) -> str:
        """Execute passive subdomain enumeration."""
        return asyncio.run(self._async_run(domain, config, timeout))
    
    async def _async_run(self, domain: str, config: Optional[str] = None, timeout: Optional[int] = 300) -> str:
        """Async implementation of passive subdomain enumeration."""
        try:
            logger.info(f"Starting passive subdomain enumeration for {domain}")
            
            arguments = {
                "domain": domain,
                "timeout": timeout or 300
            }
            
            if config:
                arguments["config"] = config
            
            response = await self.mcp_manager.call_tool(
                "amass-mcp", 
                "passive_subdomain_enum", 
                arguments
            )
            
            if response.success:
                logger.info(f"Passive enumeration completed for {domain}")
                return json.dumps(response.data, indent=2) if response.data else "No results found"
            else:
                logger.error(f"Passive enumeration failed: {response.error}")
                return f"Error: {response.error}"
                
        except Exception as e:
            logger.error(f"Exception in passive enumeration: {str(e)}")
            return f"Exception occurred: {str(e)}"


class ActiveSubdomainEnumTool(BaseTool):
    """Tool for active subdomain enumeration using Amass MCP."""
    
    name: str = "active_subdomain_enumeration"
    description: str = "Perform active subdomain enumeration using Amass with DNS probing and brute force"
    args_schema: type[BaseModel] = ActiveSubdomainEnumInput
    
    def __init__(self, mcp_manager: MCPManager):
        super().__init__()
        self.mcp_manager = mcp_manager
    
    def _run(
        self, 
        domain: str, 
        config: Optional[str] = None, 
        timeout: Optional[int] = 600,
        brute_force: Optional[bool] = False,
        wordlist: Optional[str] = None
    ) -> str:
        """Execute active subdomain enumeration."""
        return asyncio.run(self._async_run(domain, config, timeout, brute_force, wordlist))
    
    async def _async_run(
        self, 
        domain: str, 
        config: Optional[str] = None, 
        timeout: Optional[int] = 600,
        brute_force: Optional[bool] = False,
        wordlist: Optional[str] = None
    ) -> str:
        """Async implementation of active subdomain enumeration."""
        try:
            logger.info(f"Starting active subdomain enumeration for {domain}")
            
            arguments = {
                "domain": domain,
                "timeout": timeout or 600,
                "brute_force": brute_force or False
            }
            
            if config:
                arguments["config"] = config
            if wordlist:
                arguments["wordlist"] = wordlist
            
            response = await self.mcp_manager.call_tool(
                "amass-mcp", 
                "active_subdomain_enum", 
                arguments
            )
            
            if response.success:
                logger.info(f"Active enumeration completed for {domain}")
                return json.dumps(response.data, indent=2) if response.data else "No results found"
            else:
                logger.error(f"Active enumeration failed: {response.error}")
                return f"Error: {response.error}"
                
        except Exception as e:
            logger.error(f"Exception in active enumeration: {str(e)}")
            return f"Exception occurred: {str(e)}"


class SubdomainIntelligenceTool(BaseTool):
    """Tool for gathering intelligence on discovered subdomains."""
    
    name: str = "subdomain_intelligence"
    description: str = "Gather intelligence and additional information about discovered subdomains"
    args_schema: type[BaseModel] = SubdomainIntelInput
    
    def __init__(self, mcp_manager: MCPManager):
        super().__init__()
        self.mcp_manager = mcp_manager
    
    def _run(self, domain: str, output_format: Optional[str] = "json") -> str:
        """Execute subdomain intelligence gathering."""
        return asyncio.run(self._async_run(domain, output_format))
    
    async def _async_run(self, domain: str, output_format: Optional[str] = "json") -> str:
        """Async implementation of subdomain intelligence gathering."""
        try:
            logger.info(f"Gathering subdomain intelligence for {domain}")
            
            arguments = {
                "domain": domain,
                "output_format": output_format or "json"
            }
            
            response = await self.mcp_manager.call_tool(
                "amass-mcp", 
                "subdomain_intel", 
                arguments
            )
            
            if response.success:
                logger.info(f"Intelligence gathering completed for {domain}")
                return json.dumps(response.data, indent=2) if response.data else "No intelligence found"
            else:
                logger.error(f"Intelligence gathering failed: {response.error}")
                return f"Error: {response.error}"
                
        except Exception as e:
            logger.error(f"Exception in intelligence gathering: {str(e)}")
            return f"Exception occurred: {str(e)}"


class ReconnaissanceAgent:
    """
    Reconnaissance Agent for performing comprehensive subdomain enumeration.
    
    This agent uses CrewAI framework with MCP integration to perform both
    passive and active subdomain reconnaissance using Amass and other tools.
    """
    
    def __init__(self, mcp_manager: Optional[MCPManager] = None):
        """Initialize the Reconnaissance Agent."""
        self.mcp_manager = mcp_manager or MCPManager()
        self._setup_mcp_servers()
        self._setup_tools()
        self._setup_agent()
    
    def _setup_mcp_servers(self):
        """Setup MCP servers for the agent."""
        # Register Amass MCP server
        amass_config = create_amass_config(
            name="amass-mcp",
            working_directory="./mcp"
        )
        self.mcp_manager.register_server(amass_config)
    
    def _setup_tools(self):
        """Setup tools for the agent."""
        self.tools = [
            PassiveSubdomainEnumTool(self.mcp_manager),
            ActiveSubdomainEnumTool(self.mcp_manager),
            SubdomainIntelligenceTool(self.mcp_manager)
        ]
    
    def _setup_agent(self):
        """Setup the CrewAI agent."""
        self.agent = Agent(
            role="Reconnaissance Specialist",
            goal="Perform comprehensive subdomain enumeration and reconnaissance",
            backstory="""You are an expert reconnaissance specialist focused on subdomain discovery 
            and intelligence gathering. You use both passive and active techniques to uncover 
            subdomains and gather valuable intelligence about target domains. You are thorough, 
            methodical, and always prioritize stealth when possible.""",
            tools=self.tools,
            verbose=True,
            allow_delegation=False
        )
    
    async def start_mcp_servers(self) -> Dict[str, bool]:
        """Start all MCP servers."""
        logger.info("Starting MCP servers...")
        results = await self.mcp_manager.connect_all()
        
        for server_name, success in results.items():
            if success:
                logger.info(f"✓ {server_name} started successfully")
            else:
                logger.error(f"✗ Failed to start {server_name}")
        
        return results
    
    async def stop_mcp_servers(self) -> Dict[str, bool]:
        """Stop all MCP servers."""
        logger.info("Stopping MCP servers...")
        results = await self.mcp_manager.disconnect_all()
        
        for server_name, success in results.items():
            if success:
                logger.info(f"✓ {server_name} stopped successfully")
            else:
                logger.error(f"✗ Failed to stop {server_name}")
        
        return results
    
    def create_reconnaissance_task(self, domain: str, comprehensive: bool = True) -> Task:
        """Create a reconnaissance task for the agent."""
        
        if comprehensive:
            description = f"""
            Perform comprehensive reconnaissance on the domain: {domain}
            
            Your task includes:
            1. Start with passive subdomain enumeration to gather initial subdomains without alerting the target
            2. Perform active subdomain enumeration with DNS probing for more complete coverage
            3. Gather intelligence on discovered subdomains to understand the target's infrastructure
            4. Provide a detailed summary of findings including:
               - Number of subdomains discovered
               - Key subdomains of interest
               - Potential security implications
               - Recommendations for further investigation
            
            Be thorough but efficient. Use passive techniques first, then active techniques.
            Analyze and interpret the results, don't just list them.
            """
        else:
            description = f"""
            Perform basic passive reconnaissance on the domain: {domain}
            
            Your task includes:
            1. Perform passive subdomain enumeration only
            2. Analyze the results and provide a summary of findings
            3. Highlight any interesting or potentially valuable subdomains
            
            Focus on stealth and passive information gathering only.
            """
        
        return Task(
            description=description,
            agent=self.agent,
            expected_output="Detailed reconnaissance report with findings, analysis, and recommendations"
        )
    
    def execute_reconnaissance(self, domain: str, comprehensive: bool = True) -> str:
        """Execute reconnaissance on a target domain."""
        
        # Create task and crew
        task = self.create_reconnaissance_task(domain, comprehensive)
        crew = Crew(
            agents=[self.agent],
            tasks=[task],
            verbose=True
        )
        
        # Execute the task
        logger.info(f"Starting reconnaissance mission for domain: {domain}")
        result = crew.kickoff()
        
        logger.info("Reconnaissance mission completed")
        return result
    
    async def get_server_status(self) -> Dict[str, str]:
        """Get status of all MCP servers."""
        statuses = self.mcp_manager.get_all_statuses()
        return {name: status.value for name, status in statuses.items()}


# Convenience function to create and run reconnaissance
async def run_reconnaissance(
    domain: str, 
    comprehensive: bool = True,
    auto_manage_servers: bool = True
) -> str:
    """
    Convenience function to run reconnaissance on a domain.
    
    Args:
        domain: Target domain for reconnaissance
        comprehensive: Whether to perform comprehensive (active + passive) or passive-only recon
        auto_manage_servers: Whether to automatically start/stop MCP servers
    
    Returns:
        Reconnaissance report as string
    """
    
    agent = ReconnaissanceAgent()
    
    try:
        if auto_manage_servers:
            await agent.start_mcp_servers()
        
        # Give servers time to fully initialize
        await asyncio.sleep(2)
        
        result = agent.execute_reconnaissance(domain, comprehensive)
        
        return result
        
    finally:
        if auto_manage_servers:
            await agent.stop_mcp_servers()


if __name__ == "__main__":
    # Example usage
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python reconnaissance_agent.py <domain> [comprehensive]")
        sys.exit(1)
    
    domain = sys.argv[1]
    comprehensive = len(sys.argv) > 2 and sys.argv[2].lower() in ('true', '1', 'yes', 'y')
    
    result = asyncio.run(run_reconnaissance(domain, comprehensive))
    print("\n" + "="*80)
    print("RECONNAISSANCE REPORT")
    print("="*80)
    print(result)
