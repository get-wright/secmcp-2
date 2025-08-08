"""
Reconnaissance Agent for Subdomain Enumeration
A CrewAI agent specialized in passive and active subdomain enumeration using Amass MCP server.
"""

import logging
from typing import List, Optional, Dict, Any
from crewai import Agent, Task, Crew, Process
from mcp.config import MCPConfigManager
from mcp.adapter import MCPManager, ReconnaissanceMCPTools

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ReconnaissanceAgent:
    """
    A specialized CrewAI agent for reconnaissance tasks including subdomain enumeration.
    Uses MCP servers for modular tool integration.
    """
    
    def __init__(self, config_manager: Optional[MCPConfigManager] = None):
        self.config_manager = config_manager or MCPConfigManager()
        self.mcp_manager = MCPManager(self.config_manager)
        self.agent = None
        self.tools = []
    
    def create_agent(self, tools: List[Any]) -> Agent:
        """Create the reconnaissance agent with specified tools."""
        self.agent = Agent(
            role="Reconnaissance Agent",
            goal="Perform comprehensive reconnaissance including passive and active subdomain enumeration to gather intelligence on target domains.",
            backstory=(
                "You are an expert cybersecurity reconnaissance specialist with deep knowledge of "
                "subdomain enumeration techniques. You excel at using various tools including Amass "
                "to discover subdomains through both passive reconnaissance (using public sources) "
                "and active reconnaissance (DNS queries, brute force). You understand the importance "
                "of thorough reconnaissance in security assessments and penetration testing."
            ),
            tools=tools,
            reasoning=True,
            verbose=True,
            memory=True
        )
        return self.agent
    
    def create_passive_enumeration_task(self, domain: str, config_file: str = "", 
                                      timeout: int = 300) -> Task:
        """Create a task for passive subdomain enumeration."""
        return Task(
            description=(
                f"Perform passive subdomain enumeration on the domain '{domain}'. "
                f"Use the amass_passive_enum tool to discover subdomains without making "
                f"direct queries to the target. This technique uses public sources like "
                f"search engines, certificate transparency logs, and DNS databases. "
                f"Timeout: {timeout} seconds. "
                f"{'Configuration file: ' + config_file if config_file else 'Using default configuration.'}"
            ),
            expected_output=(
                "A comprehensive report containing:\n"
                "1. List of discovered subdomains\n"
                "2. Total count of subdomains found\n"
                "3. Summary of the enumeration process\n"
                "4. Any errors or warnings encountered\n"
                "5. Recommendations for further reconnaissance if applicable"
            ),
            agent=self.agent
        )
    
    def create_active_enumeration_task(self, domain: str, brute_force: bool = False,
                                     config_file: str = "", timeout: int = 600,
                                     wordlist: str = "") -> Task:
        """Create a task for active subdomain enumeration."""
        return Task(
            description=(
                f"Perform active subdomain enumeration on the domain '{domain}'. "
                f"Use the amass_active_enum tool to discover subdomains through direct "
                f"DNS queries and resolution. "
                f"{'Enable brute force enumeration with' if brute_force else 'Disable brute force.'} "
                f"{'wordlist: ' + wordlist if wordlist else ''} "
                f"Timeout: {timeout} seconds. "
                f"{'Configuration file: ' + config_file if config_file else 'Using default configuration.'} "
                f"Be aware that active enumeration may be detected by monitoring systems."
            ),
            expected_output=(
                "A detailed report containing:\n"
                "1. List of discovered subdomains from active enumeration\n"
                "2. Total count of subdomains found\n"
                "3. Comparison with any previous passive enumeration results\n"
                "4. Analysis of subdomain patterns and potential services\n"
                "5. Any errors or warnings encountered\n"
                "6. Security considerations and recommendations"
            ),
            agent=self.agent
        )
    
    def create_intelligence_task(self, domain: str, whois: bool = True,
                               config_file: str = "") -> Task:
        """Create a task for domain intelligence gathering."""
        return Task(
            description=(
                f"Gather comprehensive intelligence on the domain '{domain}'. "
                f"Use the amass_intel tool to collect information about the target domain "
                f"including organizational details, IP ranges, and related domains. "
                f"{'Include WHOIS information' if whois else 'Exclude WHOIS information'}. "
                f"{'Configuration file: ' + config_file if config_file else 'Using default configuration.'}"
            ),
            expected_output=(
                "An intelligence report containing:\n"
                "1. Domain ownership and registration information\n"
                "2. Related domains and subdomains\n"
                "3. IP address ranges associated with the organization\n"
                "4. WHOIS data analysis (if enabled)\n"
                "5. Potential attack surface assessment\n"
                "6. Recommendations for further investigation"
            ),
            agent=self.agent
        )
    
    def run_reconnaissance(self, domain: str, tasks: List[str] = None,
                         **task_kwargs) -> Any:
        """
        Run reconnaissance tasks on the specified domain.
        
        Args:
            domain: Target domain for reconnaissance
            tasks: List of tasks to run ['passive', 'active', 'intel']
            **task_kwargs: Additional arguments for task creation
        
        Returns:
            Results from the crew execution
        """
        if tasks is None:
            tasks = ['passive', 'active', 'intel']
        
        try:
            with ReconnaissanceMCPTools(self.mcp_manager) as tools:
                logger.info(f"Available tools: {[tool.name for tool in tools]}")
                
                # Create the agent with available tools
                agent = self.create_agent(tools)
                
                # Create tasks based on requested operations
                task_list = []
                
                if 'passive' in tasks:
                    passive_task = self.create_passive_enumeration_task(
                        domain, 
                        task_kwargs.get('config_file', ''),
                        task_kwargs.get('passive_timeout', 300)
                    )
                    task_list.append(passive_task)
                
                if 'active' in tasks:
                    active_task = self.create_active_enumeration_task(
                        domain,
                        task_kwargs.get('brute_force', False),
                        task_kwargs.get('config_file', ''),
                        task_kwargs.get('active_timeout', 600),
                        task_kwargs.get('wordlist', '')
                    )
                    task_list.append(active_task)
                
                if 'intel' in tasks:
                    intel_task = self.create_intelligence_task(
                        domain,
                        task_kwargs.get('whois', True),
                        task_kwargs.get('config_file', '')
                    )
                    task_list.append(intel_task)
                
                if not task_list:
                    raise ValueError("No valid tasks specified")
                
                # Create and run the crew
                reconnaissance_crew = Crew(
                    agents=[agent],
                    tasks=task_list,
                    verbose=True,
                    process=Process.sequential,
                    memory=True
                )
                
                logger.info(f"Starting reconnaissance on domain: {domain}")
                logger.info(f"Tasks to execute: {tasks}")
                
                result = reconnaissance_crew.kickoff()
                
                logger.info("Reconnaissance completed successfully")
                return result
                
        except Exception as e:
            logger.error(f"Error during reconnaissance: {e}")
            raise
    
    def list_available_tools(self) -> Dict[str, str]:
        """List all available MCP servers and their descriptions."""
        return self.mcp_manager.list_available_servers()


def main():
    """Example usage of the Reconnaissance Agent."""
    # Create the reconnaissance agent
    recon_agent = ReconnaissanceAgent()
    
    # List available tools
    print("Available MCP servers:")
    for name, description in recon_agent.list_available_tools().items():
        print(f"  - {name}: {description}")
    
    # Example reconnaissance run
    # Uncomment the following lines to run with a real domain
    # target_domain = "example.com"
    # result = recon_agent.run_reconnaissance(
    #     domain=target_domain,
    #     tasks=['passive', 'active'],
    #     passive_timeout=300,
    #     active_timeout=600,
    #     brute_force=False
    # )
    # print(f"\nReconnaissance Results:\n{result}")


if __name__ == "__main__":
    main()
