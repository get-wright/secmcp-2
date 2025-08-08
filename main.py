#!/usr/bin/env python3
"""
Main application for CrewAI Subdomain Enumeration Agent
Demonstrates how to use the agent for subdomain discovery
"""

import asyncio
import argparse
import logging
import sys
import json
from pathlib import Path

from src.subdomain_agent import SubdomainEnumerationAgent, create_subdomain_agent

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('subdomain_enumeration.log')
    ]
)

logger = logging.getLogger(__name__)

class SubdomainEnumerationApp:
    """Main application class for subdomain enumeration"""
    
    def __init__(self, config_path: str = "config/mcp_servers.yaml"):
        self.agent = create_subdomain_agent(config_path)
        self.config_path = config_path
    
    async def setup(self):
        """Set up the application and start MCP servers"""
        logger.info("Starting subdomain enumeration application...")
        
        # Check if config file exists
        if not Path(self.config_path).exists():
            logger.warning(f"Config file {self.config_path} not found, using default configuration")
        
        # Start MCP servers
        logger.info("Starting MCP servers...")
        server_status = await self.agent.start_mcp_servers()
        
        for server_name, status in server_status.items():
            if status:
                logger.info(f"✓ MCP server '{server_name}' started successfully")
            else:
                logger.warning(f"✗ Failed to start MCP server '{server_name}'")
        
        # Check if any servers are running
        running_servers = [name for name, status in server_status.items() if status]
        if not running_servers:
            logger.error("No MCP servers are running. Cannot perform enumeration.")
            return False
        
        logger.info(f"Application ready with {len(running_servers)} running servers")
        return True
    
    async def cleanup(self):
        """Clean up resources and stop MCP servers"""
        logger.info("Cleaning up application...")
        await self.agent.stop_mcp_servers()
        logger.info("Application cleanup complete")
    
    def enumerate_domain(self, domain: str, method: str = "combined", 
                        servers: list = None, 
                        passive_config: dict = None, 
                        active_config: dict = None):
        """Perform subdomain enumeration for a domain"""
        
        logger.info(f"Starting {method} enumeration for domain: {domain}")
        
        # Show available servers
        available_servers = self.agent.list_available_servers()
        enabled_servers = self.agent.get_enabled_servers()
        
        logger.info(f"Available servers: {available_servers}")
        logger.info(f"Enabled servers: {enabled_servers}")
        
        if servers is None:
            servers = enabled_servers
        
        logger.info(f"Using servers: {servers}")
        
        # Execute enumeration
        try:
            result = self.agent.execute_enumeration(
                domain=domain,
                method=method,
                servers=servers,
                passive_config=passive_config,
                active_config=active_config
            )
            
            logger.info(f"Enumeration completed for {domain}")
            return result
            
        except Exception as e:
            logger.error(f"Error during enumeration: {e}")
            return f"Error: {str(e)}"
    
    def show_server_status(self):
        """Display the status of all MCP servers"""
        status = self.agent.get_server_status()
        
        print("\\nMCP Server Status:")
        print("-" * 50)
        for server_name, server_status in status.items():
            status_symbol = {
                "running": "🟢",
                "stopped": "🔴", 
                "disabled": "⚫",
                "failed": "🟠"
            }.get(server_status, "❓")
            
            print(f"{status_symbol} {server_name}: {server_status}")
        print("-" * 50)

async def main():
    """Main application entry point"""
    parser = argparse.ArgumentParser(description="CrewAI Subdomain Enumeration Agent")
    parser.add_argument("domain", help="Target domain for subdomain enumeration")
    parser.add_argument("--method", choices=["passive", "active", "combined"], 
                       default="combined", help="Enumeration method")
    parser.add_argument("--servers", nargs="+", help="MCP servers to use")
    parser.add_argument("--config", default="config/mcp_servers.yaml", 
                       help="Path to MCP server configuration file")
    parser.add_argument("--passive-sources", nargs="+", 
                       help="Data sources for passive enumeration")
    parser.add_argument("--active-brute", action="store_true", 
                       help="Enable brute force for active enumeration")
    parser.add_argument("--wordlist", help="Wordlist file for brute force")
    parser.add_argument("--timeout", type=int, help="Timeout in minutes")
    parser.add_argument("--status", action="store_true", 
                       help="Show MCP server status and exit")
    parser.add_argument("--output", help="Output file for results")
    parser.add_argument("--verbose", "-v", action="store_true", 
                       help="Enable verbose logging")
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Create the application
    app = SubdomainEnumerationApp(args.config)
    
    try:
        # Set up the application
        setup_success = await app.setup()
        
        if not setup_success:
            logger.error("Application setup failed")
            return 1
        
        # Show server status if requested
        if args.status:
            app.show_server_status()
            return 0
        
        # Prepare configuration
        passive_config = {}
        if args.passive_sources:
            passive_config["sources"] = args.passive_sources
        if args.timeout:
            passive_config["timeout"] = args.timeout
        
        active_config = {}
        if args.active_brute:
            active_config["brute"] = True
        if args.wordlist:
            active_config["wordlist"] = args.wordlist
        if args.timeout:
            active_config["timeout"] = args.timeout
        
        # Perform enumeration
        result = app.enumerate_domain(
            domain=args.domain,
            method=args.method,
            servers=args.servers,
            passive_config=passive_config if passive_config else None,
            active_config=active_config if active_config else None
        )
        
        # Output results
        print("\\n" + "="*80)
        print("SUBDOMAIN ENUMERATION RESULTS")
        print("="*80)
        print(result)
        print("="*80)
        
        # Save to file if requested
        if args.output:
            with open(args.output, 'w') as f:
                f.write(result)
            logger.info(f"Results saved to {args.output}")
        
        return 0
        
    except KeyboardInterrupt:
        logger.info("Enumeration interrupted by user")
        return 1
    except Exception as e:
        logger.error(f"Application error: {e}")
        return 1
    finally:
        # Clean up
        await app.cleanup()

def interactive_mode():
    """Interactive mode for the application"""
    print("CrewAI Subdomain Enumeration Agent - Interactive Mode")
    print("Type 'help' for available commands or 'quit' to exit")
    
    app = None
    
    async def setup_app():
        nonlocal app
        app = SubdomainEnumerationApp()
        await app.setup()
        app.show_server_status()
    
    # Set up the application
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(setup_app())
    
    try:
        while True:
            try:
                command = input("\\nEnumeration> ").strip()
                
                if command.lower() in ['quit', 'exit', 'q']:
                    break
                elif command.lower() == 'help':
                    print("""
Available commands:
  enum <domain> [method]     - Enumerate subdomains (method: passive/active/combined)
  status                     - Show MCP server status
  servers                    - List available servers
  help                       - Show this help message
  quit                       - Exit the application
  
Examples:
  enum example.com
  enum example.com passive
  enum example.com active
  enum example.com combined
                    """)
                elif command.lower() == 'status':
                    app.show_server_status()
                elif command.lower() == 'servers':
                    servers = app.agent.list_available_servers()
                    enabled = app.agent.get_enabled_servers()
                    print(f"Available servers: {servers}")
                    print(f"Enabled servers: {enabled}")
                elif command.startswith('enum '):
                    parts = command.split()
                    if len(parts) < 2:
                        print("Usage: enum <domain> [method]")
                        continue
                    
                    domain = parts[1]
                    method = parts[2] if len(parts) > 2 else "combined"
                    
                    if method not in ["passive", "active", "combined"]:
                        print("Invalid method. Use: passive, active, or combined")
                        continue
                    
                    print(f"Starting {method} enumeration for {domain}...")
                    result = app.enumerate_domain(domain, method)
                    print("\\n" + "="*60)
                    print(result)
                    print("="*60)
                else:
                    print("Unknown command. Type 'help' for available commands.")
                    
            except EOFError:
                break
            except KeyboardInterrupt:
                print("\\nUse 'quit' to exit.")
                continue
    
    finally:
        print("\\nCleaning up...")
        loop.run_until_complete(app.cleanup())
        loop.close()

if __name__ == "__main__":
    if len(sys.argv) == 1:
        # No arguments provided, start interactive mode
        interactive_mode()
    else:
        # Command line arguments provided
        sys.exit(asyncio.run(main()))
