"""
Basic Usage Examples for Reconnaissance Agent

This file demonstrates various ways to use the Reconnaissance Agent
for subdomain enumeration and intelligence gathering.
"""

import asyncio
import json
from src.reconnaissance_agent import (
    ReconnaissanceAgent, 
    run_reconnaissance
)
from src.mcp_adapter import MCPManager, create_amass_config


async def example_1_simple_passive_recon():
    """
    Example 1: Simple passive reconnaissance
    This is the quickest way to get started.
    """
    print("=" * 60)
    print("Example 1: Simple Passive Reconnaissance")
    print("=" * 60)
    
    # Run passive reconnaissance on a domain
    result = await run_reconnaissance(
        domain="example.com",
        comprehensive=False,  # Passive only
        auto_manage_servers=True
    )
    
    print("Results:")
    print(result)
    print("\n")


async def example_2_comprehensive_recon():
    """
    Example 2: Comprehensive reconnaissance (passive + active)
    This performs both passive and active enumeration.
    """
    print("=" * 60)
    print("Example 2: Comprehensive Reconnaissance")
    print("=" * 60)
    
    # Run comprehensive reconnaissance
    result = await run_reconnaissance(
        domain="example.com",
        comprehensive=True,  # Both passive and active
        auto_manage_servers=True
    )
    
    print("Results:")
    print(result)
    print("\n")


async def example_3_custom_agent_setup():
    """
    Example 3: Custom agent setup with manual MCP management
    This gives you more control over the agent configuration.
    """
    print("=" * 60)
    print("Example 3: Custom Agent Setup")
    print("=" * 60)
    
    # Create MCP manager
    mcp_manager = MCPManager()
    
    # Configure Amass MCP server
    amass_config = create_amass_config(
        name="amass-mcp",
        working_directory="./mcp",
        config_file="./config/amass_config_example.yaml"  # Optional custom config
    )
    mcp_manager.register_server(amass_config)
    
    # Create reconnaissance agent
    agent = ReconnaissanceAgent(mcp_manager)
    
    try:
        # Start MCP servers
        print("Starting MCP servers...")
        server_results = await agent.start_mcp_servers()
        
        for server_name, success in server_results.items():
            status = "✓" if success else "✗"
            print(f"  {status} {server_name}")
        
        if not all(server_results.values()):
            print("Some servers failed to start. Check your MCP setup.")
            return
        
        # Check server status
        status = await agent.get_server_status()
        print(f"Server status: {status}")
        
        # Run reconnaissance
        print("\nRunning reconnaissance...")
        result = agent.execute_reconnaissance(
            domain="example.com",
            comprehensive=False
        )
        
        print("Results:")
        print(result)
        
    finally:
        # Always cleanup
        print("\nStopping MCP servers...")
        await agent.stop_mcp_servers()
        print("Cleanup completed.")
    
    print("\n")


async def example_4_direct_tool_usage():
    """
    Example 4: Direct tool usage
    This shows how to use individual tools directly.
    """
    print("=" * 60)
    print("Example 4: Direct Tool Usage")
    print("=" * 60)
    
    # Setup MCP manager
    mcp_manager = MCPManager()
    amass_config = create_amass_config(working_directory="./mcp")
    mcp_manager.register_server(amass_config)
    
    try:
        # Start MCP server
        await mcp_manager.connect_server("amass-mcp")
        
        # Direct tool calls
        print("Calling passive subdomain enumeration...")
        response = await mcp_manager.call_tool(
            "amass-mcp",
            "passive_subdomain_enum",
            {
                "domain": "example.com",
                "timeout": 60
            }
        )
        
        if response.success:
            print("Passive enumeration results:")
            print(json.dumps(response.data, indent=2))
        else:
            print(f"Error: {response.error}")
        
        print("\nCalling subdomain intelligence...")
        intel_response = await mcp_manager.call_tool(
            "amass-mcp",
            "subdomain_intel",
            {
                "domain": "example.com",
                "output_format": "json"
            }
        )
        
        if intel_response.success:
            print("Intelligence results:")
            print(json.dumps(intel_response.data, indent=2))
        else:
            print(f"Error: {intel_response.error}")
    
    finally:
        await mcp_manager.disconnect_server("amass-mcp")
    
    print("\n")


async def example_5_multiple_domains():
    """
    Example 5: Processing multiple domains
    This shows how to process multiple domains efficiently.
    """
    print("=" * 60)
    print("Example 5: Multiple Domains")
    print("=" * 60)
    
    domains = ["example.com", "test.com", "demo.org"]
    
    # Create agent once
    agent = ReconnaissanceAgent()
    
    try:
        # Start servers once
        await agent.start_mcp_servers()
        
        results = {}
        
        for domain in domains:
            print(f"\nProcessing {domain}...")
            
            try:
                result = agent.execute_reconnaissance(
                    domain=domain,
                    comprehensive=False  # Keep it fast for multiple domains
                )
                results[domain] = result
                print(f"✓ Completed {domain}")
                
            except Exception as e:
                results[domain] = f"Error: {str(e)}"
                print(f"✗ Failed {domain}: {str(e)}")
        
        # Summary
        print("\n" + "=" * 40)
        print("SUMMARY")
        print("=" * 40)
        
        for domain, result in results.items():
            status = "✓" if not result.startswith("Error:") else "✗"
            print(f"{status} {domain}")
    
    finally:
        await agent.stop_mcp_servers()
    
    print("\n")


async def example_6_error_handling():
    """
    Example 6: Proper error handling
    This shows how to handle various error conditions.
    """
    print("=" * 60)
    print("Example 6: Error Handling")
    print("=" * 60)
    
    agent = ReconnaissanceAgent()
    
    try:
        # Try to run without starting servers (should fail gracefully)
        print("Testing without MCP servers...")
        
        # This should handle the error gracefully
        result = agent.execute_reconnaissance(
            domain="example.com",
            comprehensive=False
        )
        
        print("Result:")
        print(result)
        
    except Exception as e:
        print(f"Caught exception: {str(e)}")
        print("This is expected when MCP servers aren't running.")
    
    # Now try with proper setup
    try:
        print("\nTesting with proper setup...")
        await agent.start_mcp_servers()
        
        # Test with invalid domain
        result = agent.execute_reconnaissance(
            domain="invalid-domain-that-does-not-exist.invalid",
            comprehensive=False
        )
        
        print("Result for invalid domain:")
        print(result)
        
    except Exception as e:
        print(f"Error with invalid domain: {str(e)}")
    
    finally:
        await agent.stop_mcp_servers()
    
    print("\n")


async def main():
    """Run all examples."""
    
    print("RECONNAISSANCE AGENT - USAGE EXAMPLES")
    print("=" * 80)
    print("This script demonstrates various ways to use the Reconnaissance Agent.")
    print("Make sure you have:")
    print("1. Installed Amass: https://github.com/owasp-amass/amass")
    print("2. Setup Amass MCP server according to documentation")
    print("3. Installed requirements: pip install -r requirements.txt")
    print("=" * 80)
    print()
    
    try:
        # Run examples
        await example_1_simple_passive_recon()
        await example_2_comprehensive_recon()
        await example_3_custom_agent_setup()
        await example_4_direct_tool_usage()
        await example_5_multiple_domains()
        await example_6_error_handling()
        
        print("=" * 80)
        print("All examples completed!")
        print("=" * 80)
        
    except KeyboardInterrupt:
        print("\nExamples interrupted by user.")
    except Exception as e:
        print(f"\nExample execution failed: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
