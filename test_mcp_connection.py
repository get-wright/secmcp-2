"""
MCP Connection Test Script

This script tests the connection to MCP servers and validates their functionality.
Use this script to verify that your MCP servers are properly configured and working.
"""

import asyncio
import json
import sys
from typing import Dict, List

from loguru import logger
from src.mcp_adapter import MCPManager, create_amass_config, MCPServerStatus


async def test_mcp_server_connection(mcp_manager: MCPManager, server_name: str) -> Dict:
    """Test connection to a specific MCP server."""
    
    result = {
        "server_name": server_name,
        "connection_success": False,
        "tools_available": [],
        "test_results": {},
        "errors": []
    }
    
    try:
        logger.info(f"Testing connection to {server_name}...")
        
        # Test connection
        connected = await mcp_manager.connect_server(server_name)
        result["connection_success"] = connected
        
        if not connected:
            result["errors"].append("Failed to connect to MCP server")
            return result
        
        # Give server time to initialize
        await asyncio.sleep(2)
        
        # Test tool listing
        try:
            tools = await mcp_manager.list_tools(server_name)
            result["tools_available"] = [tool.get("name", "unknown") for tool in tools]
            logger.info(f"Found {len(tools)} tools: {result['tools_available']}")
        except Exception as e:
            result["errors"].append(f"Failed to list tools: {str(e)}")
        
        # Test basic tool functionality (if it's Amass MCP)
        if server_name == "amass-mcp" and "passive_subdomain_enum" in result["tools_available"]:
            try:
                logger.info("Testing passive subdomain enumeration with example.com...")
                
                # Use a safe test domain
                test_response = await mcp_manager.call_tool(
                    server_name,
                    "passive_subdomain_enum",
                    {"domain": "example.com", "timeout": 30}
                )
                
                result["test_results"]["passive_enum_test"] = {
                    "success": test_response.success,
                    "has_data": test_response.data is not None,
                    "error": test_response.error
                }
                
                if test_response.success:
                    logger.info("✓ Passive enumeration test passed")
                else:
                    logger.warning(f"✗ Passive enumeration test failed: {test_response.error}")
                    
            except Exception as e:
                result["test_results"]["passive_enum_test"] = {
                    "success": False,
                    "error": str(e)
                }
                result["errors"].append(f"Tool test failed: {str(e)}")
        
        # Disconnect after testing
        await mcp_manager.disconnect_server(server_name)
        
    except Exception as e:
        result["errors"].append(f"Connection test failed: {str(e)}")
        logger.error(f"Error testing {server_name}: {str(e)}")
    
    return result


async def test_all_mcp_servers() -> Dict:
    """Test all registered MCP servers."""
    
    logger.info("Starting MCP server connection tests...")
    
    # Initialize MCP manager
    mcp_manager = MCPManager()
    
    # Register Amass MCP server
    amass_config = create_amass_config(
        name="amass-mcp",
        working_directory="./mcp"
    )
    mcp_manager.register_server(amass_config)
    
    # Test results
    test_results = {
        "timestamp": asyncio.get_event_loop().time(),
        "total_servers": len(mcp_manager.clients),
        "servers_tested": 0,
        "servers_passed": 0,
        "server_results": [],
        "summary": {}
    }
    
    # Test each server
    for server_name in mcp_manager.clients.keys():
        logger.info(f"\n{'='*50}")
        logger.info(f"Testing: {server_name}")
        logger.info(f"{'='*50}")
        
        server_result = await test_mcp_server_connection(mcp_manager, server_name)
        test_results["server_results"].append(server_result)
        test_results["servers_tested"] += 1
        
        if server_result["connection_success"]:
            test_results["servers_passed"] += 1
            logger.info(f"✓ {server_name}: PASSED")
        else:
            logger.error(f"✗ {server_name}: FAILED")
            for error in server_result["errors"]:
                logger.error(f"  - {error}")
    
    # Generate summary
    test_results["summary"] = {
        "success_rate": test_results["servers_passed"] / test_results["servers_tested"] if test_results["servers_tested"] > 0 else 0,
        "all_passed": test_results["servers_passed"] == test_results["servers_tested"],
        "failed_servers": [
            result["server_name"] 
            for result in test_results["server_results"] 
            if not result["connection_success"]
        ]
    }
    
    return test_results


def print_test_summary(results: Dict):
    """Print a formatted test summary."""
    
    print(f"\n{'='*80}")
    print("MCP CONNECTION TEST SUMMARY")
    print(f"{'='*80}")
    
    print(f"Total servers tested: {results['servers_tested']}")
    print(f"Servers passed: {results['servers_passed']}")
    print(f"Success rate: {results['summary']['success_rate']:.1%}")
    print(f"Overall result: {'✓ PASSED' if results['summary']['all_passed'] else '✗ FAILED'}")
    
    if results['summary']['failed_servers']:
        print(f"\nFailed servers: {', '.join(results['summary']['failed_servers'])}")
    
    print(f"\n{'='*80}")
    print("DETAILED RESULTS")
    print(f"{'='*80}")
    
    for server_result in results['server_results']:
        print(f"\nServer: {server_result['server_name']}")
        print(f"  Connection: {'✓' if server_result['connection_success'] else '✗'}")
        print(f"  Tools found: {len(server_result['tools_available'])}")
        
        if server_result['tools_available']:
            print(f"  Available tools: {', '.join(server_result['tools_available'])}")
        
        if server_result['test_results']:
            print("  Tool tests:")
            for test_name, test_result in server_result['test_results'].items():
                status = "✓" if test_result['success'] else "✗"
                print(f"    {test_name}: {status}")
                if not test_result['success'] and test_result.get('error'):
                    print(f"      Error: {test_result['error']}")
        
        if server_result['errors']:
            print("  Errors:")
            for error in server_result['errors']:
                print(f"    - {error}")


async def interactive_test():
    """Run interactive test mode."""
    
    print("MCP Server Connection Tester")
    print("=" * 40)
    
    while True:
        print("\nOptions:")
        print("1. Test all MCP servers")
        print("2. Test specific server")
        print("3. Quick connectivity check")
        print("4. Exit")
        
        choice = input("\nSelect option (1-4): ").strip()
        
        if choice == "1":
            results = await test_all_mcp_servers()
            print_test_summary(results)
            
            # Save results to file
            with open("mcp_test_results.json", "w") as f:
                json.dump(results, f, indent=2)
            print("\nDetailed results saved to: mcp_test_results.json")
            
        elif choice == "2":
            server_name = input("Enter server name (e.g., 'amass-mcp'): ").strip()
            if not server_name:
                print("Invalid server name")
                continue
                
            mcp_manager = MCPManager()
            
            if server_name == "amass-mcp":
                config = create_amass_config(working_directory="./mcp")
                mcp_manager.register_server(config)
            else:
                print(f"Unknown server: {server_name}")
                continue
            
            result = await test_mcp_server_connection(mcp_manager, server_name)
            print(f"\nTest result for {server_name}:")
            print(json.dumps(result, indent=2))
            
        elif choice == "3":
            print("Performing quick connectivity check...")
            mcp_manager = MCPManager()
            
            # Register servers
            config = create_amass_config(working_directory="./mcp")
            mcp_manager.register_server(config)
            
            # Quick connection test
            results = await mcp_manager.connect_all()
            
            print("\nConnectivity results:")
            for server, success in results.items():
                status = "✓ Connected" if success else "✗ Failed"
                print(f"  {server}: {status}")
            
            # Cleanup
            await mcp_manager.disconnect_all()
            
        elif choice == "4":
            print("Exiting...")
            break
            
        else:
            print("Invalid option. Please select 1-4.")


async def main():
    """Main entry point."""
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "--interactive":
            await interactive_test()
        elif sys.argv[1] == "--help":
            print("MCP Connection Test Script")
            print("Usage:")
            print("  python test_mcp_connection.py              # Run full test suite")
            print("  python test_mcp_connection.py --interactive # Interactive mode")
            print("  python test_mcp_connection.py --help       # Show this help")
        else:
            print(f"Unknown option: {sys.argv[1]}")
            print("Use --help for usage information")
    else:
        # Run full test suite
        results = await test_all_mcp_servers()
        print_test_summary(results)
        
        # Save results
        with open("mcp_test_results.json", "w") as f:
            json.dump(results, f, indent=2)
        
        print(f"\nDetailed results saved to: mcp_test_results.json")
        
        # Exit with appropriate code
        exit_code = 0 if results['summary']['all_passed'] else 1
        sys.exit(exit_code)


if __name__ == "__main__":
    asyncio.run(main())
