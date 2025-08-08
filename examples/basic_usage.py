#!/usr/bin/env python3
"""
Basic usage examples for the CrewAI Subdomain Enumeration Agent
"""

import asyncio
import sys
import os

# Add the parent directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.subdomain_agent import create_subdomain_agent

async def example_passive_enumeration():
    """Example of passive subdomain enumeration"""
    print("\\n" + "="*60)
    print("EXAMPLE: Passive Subdomain Enumeration")
    print("="*60)
    
    # Create the agent
    agent = create_subdomain_agent()
    
    try:
        # Start MCP servers
        print("Starting MCP servers...")
        server_status = await agent.start_mcp_servers()
        print(f"Server status: {server_status}")
        
        # Show server status
        agent.show_server_status()
        
        # Perform passive enumeration
        print("\\nPerforming passive enumeration for example.com...")
        result = agent.execute_enumeration(
            domain="example.com",
            method="passive"
        )
        
        print("\\nResults:")
        print(result)
        
    finally:
        # Clean up
        print("\\nCleaning up...")
        await agent.stop_mcp_servers()

async def example_active_enumeration():
    """Example of active subdomain enumeration"""
    print("\\n" + "="*60)
    print("EXAMPLE: Active Subdomain Enumeration")
    print("="*60)
    
    # Create the agent
    agent = create_subdomain_agent()
    
    try:
        # Start MCP servers
        print("Starting MCP servers...")
        await agent.start_mcp_servers()
        
        # Configure active enumeration
        active_config = {
            "brute": True,
            "timeout": 10  # Short timeout for example
        }
        
        # Perform active enumeration
        print("\\nPerforming active enumeration for example.com...")
        result = agent.execute_enumeration(
            domain="example.com",
            method="active",
            active_config=active_config
        )
        
        print("\\nResults:")
        print(result)
        
    finally:
        # Clean up
        print("\\nCleaning up...")
        await agent.stop_mcp_servers()

async def example_combined_enumeration():
    """Example of combined passive and active enumeration"""
    print("\\n" + "="*60)
    print("EXAMPLE: Combined Subdomain Enumeration")
    print("="*60)
    
    # Create the agent
    agent = create_subdomain_agent()
    
    try:
        # Start MCP servers
        print("Starting MCP servers...")
        await agent.start_mcp_servers()
        
        # Configure both passive and active settings
        passive_config = {
            "sources": ["crtsh", "hackertarget"],
            "timeout": 5
        }
        
        active_config = {
            "brute": False,  # Disable brute force for faster example
            "timeout": 5
        }
        
        # Perform combined enumeration
        print("\\nPerforming combined enumeration for example.com...")
        result = agent.execute_enumeration(
            domain="example.com",
            method="combined",
            passive_config=passive_config,
            active_config=active_config
        )
        
        print("\\nResults:")
        print(result)
        
    finally:
        # Clean up
        print("\\nCleaning up...")
        await agent.stop_mcp_servers()

async def example_multiple_servers():
    """Example using multiple MCP servers"""
    print("\\n" + "="*60)
    print("EXAMPLE: Multiple MCP Servers")
    print("="*60)
    
    # Create the agent
    agent = create_subdomain_agent()
    
    try:
        # Start MCP servers
        print("Starting MCP servers...")
        await agent.start_mcp_servers()
        
        # List available servers
        available_servers = agent.list_available_servers()
        enabled_servers = agent.get_enabled_servers()
        
        print(f"Available servers: {available_servers}")
        print(f"Enabled servers: {enabled_servers}")
        
        # Use specific servers (if multiple are available)
        servers_to_use = enabled_servers[:1] if enabled_servers else None
        
        # Perform enumeration
        print(f"\\nPerforming enumeration using servers: {servers_to_use}")
        result = agent.execute_enumeration(
            domain="example.com",
            method="passive",
            servers=servers_to_use
        )
        
        print("\\nResults:")
        print(result)
        
    finally:
        # Clean up
        print("\\nCleaning up...")
        await agent.stop_mcp_servers()

async def example_mcp_client_direct():
    """Example of using the MCP client directly"""
    print("\\n" + "="*60)
    print("EXAMPLE: Direct MCP Client Usage")
    print("="*60)
    
    from src.mcp_client import MCPClient
    
    # Create MCP client
    client = MCPClient()
    
    try:
        # Start servers
        print("Starting MCP servers...")
        server_status = await client.start_all_servers()
        print(f"Server status: {server_status}")
        
        # Show server status
        status = client.get_server_status()
        print(f"Current status: {status}")
        
        # Perform direct enumeration
        print("\\nPerforming direct passive enumeration...")
        result = await client.enumerate_subdomains_passive("example.com")
        
        print(f"Success: {result.get('success', False)}")
        print(f"Domain: {result.get('domain', 'unknown')}")
        print(f"Method: {result.get('method', 'unknown')}")
        print(f"Subdomains found: {result.get('total_count', 0)}")
        
        if result.get('subdomains'):
            print("\\nFirst 5 subdomains:")
            for i, subdomain in enumerate(result['subdomains'][:5], 1):
                print(f"  {i}. {subdomain}")
        
    finally:
        # Clean up
        print("\\nCleaning up...")
        await client.stop_all_servers()

def main():
    """Run all examples"""
    print("CrewAI Subdomain Enumeration Agent - Examples")
    print("=" * 80)
    
    examples = [
        ("Passive Enumeration", example_passive_enumeration),
        ("Active Enumeration", example_active_enumeration),
        ("Combined Enumeration", example_combined_enumeration),
        ("Multiple Servers", example_multiple_servers),
        ("Direct MCP Client", example_mcp_client_direct),
    ]
    
    for name, example_func in examples:
        try:
            print(f"\\n🚀 Running example: {name}")
            asyncio.run(example_func())
            print(f"✅ Completed example: {name}")
        except KeyboardInterrupt:
            print(f"\\n⏹️  Interrupted example: {name}")
            break
        except Exception as e:
            print(f"❌ Error in example {name}: {e}")
            import traceback
            traceback.print_exc()
        
        # Pause between examples
        try:
            input("\\nPress Enter to continue to the next example (or Ctrl+C to exit)...")
        except KeyboardInterrupt:
            print("\\nExiting examples...")
            break
    
    print("\\n🎉 Examples completed!")

if __name__ == "__main__":
    main()
