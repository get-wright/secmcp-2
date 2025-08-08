"""
Reconnaissance Agent for CrewAI

This module implements a specialized CrewAI agent for performing subdomain reconnaissance
using the Amass MCP server and other security tools.
"""

import asyncio
import json
import subprocess
import sys
from typing import Any, Dict, List, Optional, Union

from crewai import Agent, Task, Crew
from crewai_tools import MCPTool
from loguru import logger


class AmassServerManager:
    """Manager for the Amass MCP server process."""
    
    def __init__(self, working_directory: str = "./mcp"):
        self.working_directory = working_directory
        self.process: Optional[subprocess.Popen] = None
        self.is_running = False
    
    async def start_server(self) -> bool:
        """Start the Amass MCP server."""
        if self.is_running:
            logger.info("Amass MCP server is already running")
            return True
        
        try:
            logger.info("Starting Amass MCP server...")
            
            # Start the MCP server process
            self.process = subprocess.Popen(
                [sys.executable, "-m", "mcp.amass_mcp_server"],
                cwd=self.working_directory,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Give the server time to start up
            await asyncio.sleep(2)
            
            if self.process.poll() is None:
                self.is_running = True
                logger.info("Amass MCP server started successfully")
                return True
            else:
                stderr_output = self.process.stderr.read() if self.process.stderr else "Unknown error"
                logger.error(f"Amass MCP server failed to start: {stderr_output}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to start Amass MCP server: {str(e)}")
            return False
    
    async def stop_server(self) -> bool:
        """Stop the Amass MCP server."""
        if not self.is_running or not self.process:
            return True
        
        try:
            self.process.terminate()
            
            # Wait for graceful shutdown
            try:
                await asyncio.wait_for(self._wait_for_process(), timeout=5)
            except asyncio.TimeoutError:
                logger.warning("MCP server didn't terminate gracefully, killing...")
                self.process.kill()
            
            self.is_running = False
            logger.info("Amass MCP server stopped")
            return True
            
        except Exception as e:
            logger.error(f"Error stopping Amass MCP server: {str(e)}")
            return False
    
    async def _wait_for_process(self):
        """Wait for the process to terminate."""
        while self.process and self.process.poll() is None:
            await asyncio.sleep(0.1)


class ReconnaissanceAgent:
    """
    Reconnaissance Agent for performing comprehensive subdomain enumeration.
    
    This agent uses CrewAI framework with MCP integration to perform both
    passive and active subdomain reconnaissance using Amass and other tools.
    """
    
    def __init__(self, working_directory: str = "./mcp"):
        """Initialize the Reconnaissance Agent."""
        self.server_manager = AmassServerManager(working_directory)
        self._setup_tools()
        self._setup_agent()
    
    def _setup_tools(self):
        """Setup tools for the agent using CrewAI MCP tools."""
        try:
            # Create MCP tools using the official CrewAI MCP integration
            self.passive_enum_tool = MCPTool(
                name="passive_subdomain_enum",
                description="Perform passive subdomain enumeration using Amass without direct interaction with target",
                server_name="amass-mcp"
            )
            
            self.active_enum_tool = MCPTool(
                name="active_subdomain_enum", 
                description="Perform active subdomain enumeration using Amass with DNS probing and brute force",
                server_name="amass-mcp"
            )
            
            self.intel_tool = MCPTool(
                name="subdomain_intel",
                description="Gather intelligence and additional information about discovered subdomains",
                server_name="amass-mcp"
            )
            
            self.tools = [
                self.passive_enum_tool,
                self.active_enum_tool,
                self.intel_tool
            ]
            
        except Exception as e:
            logger.warning(f"Could not setup MCP tools (server may not be running): {e}")
            self.tools = []
    
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
        success = await self.server_manager.start_server()
        
        results = {"amass-mcp": success}
        
        if success:
            logger.info("✓ amass-mcp started successfully")
            # Refresh tools now that server is running
            self._setup_tools()
            self._setup_agent()
        else:
            logger.error("✗ Failed to start amass-mcp")
        
        return results
    
    async def stop_mcp_servers(self) -> Dict[str, bool]:
        """Stop all MCP servers."""
        logger.info("Stopping MCP servers...")
        success = await self.server_manager.stop_server()
        
        results = {"amass-mcp": success}
        
        if success:
            logger.info("✓ amass-mcp stopped successfully")
        else:
            logger.error("✗ Failed to stop amass-mcp")
        
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
        return {
            "amass-mcp": "running" if self.server_manager.is_running else "stopped"
        }


# Convenience function to create and run reconnaissance
async def run_reconnaissance(
    domain: str, 
    comprehensive: bool = True,
    auto_manage_servers: bool = True,
    working_directory: str = "./mcp"
) -> str:
    """
    Convenience function to run reconnaissance on a domain.
    
    Args:
        domain: Target domain for reconnaissance
        comprehensive: Whether to perform comprehensive (active + passive) or passive-only recon
        auto_manage_servers: Whether to automatically start/stop MCP servers
        working_directory: Directory containing MCP server implementations
    
    Returns:
        Reconnaissance report as string
    """
    
    agent = ReconnaissanceAgent(working_directory)
    
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
