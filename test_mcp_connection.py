"""
MCP Connection Test Script

This script tests the connection to MCP servers and validates their functionality.
Use this script to verify that your MCP servers are properly configured and working.
"""

import asyncio
import json
import sys
from typing import Dict

from loguru import logger
from src.reconnaissance_agent import AmassServerManager


async def test_amass_mcp_server() -> Dict:
    """Test connection to the Amass MCP server."""
    
    result = {
        "server_name": "amass-mcp",
        "connection_success": False,
        "test_results": {},
        "errors": []
    }
    
    server_manager = AmassServerManager("./mcp")
    
    try:
        logger.info("Testing connection to amass-mcp...")
        
        # Test connection
        connected = await server_manager.start_server()
        result["connection_success"] = connected
        
        if not connected:
            result["errors"].append("Failed to connect to MCP server")
            return result
        
        logger.info("✓ Amass MCP server started successfully")
        
        # Give server time to initialize
        await asyncio.sleep(3)
        
        # Test if server is still running
        if server_manager.is_running:
            result["test_results"]["server_status"] = {
                "success": True,
                "message": "Server is running"
            }
            logger.info("✓ Server status check passed")
        else:
            result["test_results"]["server_status"] = {
                "success": False,
                "message": "Server stopped unexpectedly"
            }
            result["errors"].append("Server stopped unexpectedly")
        
        # Stop the server
        stopped = await server_manager.stop_server()
        if stopped:
            logger.info("✓ Server stopped successfully")
        else:
            logger.warning("✗ Failed to stop server cleanly")
            result["errors"].append("Failed to stop server cleanly")
        
    except Exception as e:
        result["errors"].append(f"Connection test failed: {str(e)}")
        logger.error(f"Error testing amass-mcp: {str(e)}")
    
    return result


async def test_reconnaissance_agent() -> Dict:
    """Test the reconnaissance agent functionality."""
    
    result = {
        "test_name": "reconnaissance_agent",
        "success": False,
        "errors": []
    }
    
    try:
        from src.reconnaissance_agent import ReconnaissanceAgent
        
        logger.info("Testing ReconnaissanceAgent initialization...")
        agent = ReconnaissanceAgent("./mcp")
        
        logger.info("Testing MCP server management...")
        start_results = await agent.start_mcp_servers()
        
        if start_results.get("amass-mcp", False):
            logger.info("✓ MCP server started via agent")
            
            # Test status check
            status = await agent.get_server_status()
            if status.get("amass-mcp") == "running":
                logger.info("✓ Server status check passed")
                result["success"] = True
            else:
                result["errors"].append(f"Unexpected server status: {status}")
            
            # Stop servers
            stop_results = await agent.stop_mcp_servers()
            if stop_results.get("amass-mcp", False):
                logger.info("✓ MCP server stopped via agent")
            else:
                result["errors"].append("Failed to stop server via agent")
        else:
            result["errors"].append("Failed to start MCP server via agent")
    
    except Exception as e:
        result["errors"].append(f"Agent test failed: {str(e)}")
        logger.error(f"Error testing ReconnaissanceAgent: {str(e)}")
    
    return result


async def test_all_mcp_functionality() -> Dict:
    """Test all MCP functionality."""
    
    logger.info("Starting comprehensive MCP tests...")
    
    test_results = {
        "timestamp": asyncio.get_event_loop().time(),
        "tests_run": 0,
        "tests_passed": 0,
        "test_results": [],
        "summary": {}
    }
    
    # Test 1: Basic server connection
    logger.info(f"\n{'='*50}")
    logger.info("Test 1: Basic MCP Server Connection")
    logger.info(f"{'='*50}")
    
    server_test = await test_amass_mcp_server()
    test_results["test_results"].append(server_test)
    test_results["tests_run"] += 1
    
    if server_test["connection_success"] and not server_test["errors"]:
        test_results["tests_passed"] += 1
        logger.info("✓ Test 1: PASSED")
    else:
        logger.error("✗ Test 1: FAILED")
        for error in server_test["errors"]:
            logger.error(f"  - {error}")
    
    # Test 2: ReconnaissanceAgent integration
    logger.info(f"\n{'='*50}")
    logger.info("Test 2: ReconnaissanceAgent Integration")
    logger.info(f"{'='*50}")
    
    agent_test = await test_reconnaissance_agent()
    test_results["test_results"].append(agent_test)
    test_results["tests_run"] += 1
    
    if agent_test["success"] and not agent_test["errors"]:
        test_results["tests_passed"] += 1
        logger.info("✓ Test 2: PASSED")
    else:
        logger.error("✗ Test 2: FAILED")
        for error in agent_test["errors"]:
            logger.error(f"  - {error}")
    
    # Generate summary
    test_results["summary"] = {
        "success_rate": test_results["tests_passed"] / test_results["tests_run"] if test_results["tests_run"] > 0 else 0,
        "all_passed": test_results["tests_passed"] == test_results["tests_run"],
        "failed_tests": [
            result["test_name"] if "test_name" in result else result["server_name"]
            for result in test_results["test_results"] 
            if not (result.get("success", False) or result.get("connection_success", False))
        ]
    }
    
    return test_results


def print_test_summary(results: Dict):
    """Print a formatted test summary."""
    
    print(f"\n{'='*80}")
    print("MCP CONNECTION TEST SUMMARY")
    print(f"{'='*80}")
    
    print(f"Total tests run: {results['tests_run']}")
    print(f"Tests passed: {results['tests_passed']}")
    print(f"Success rate: {results['summary']['success_rate']:.1%}")
    print(f"Overall result: {'✓ PASSED' if results['summary']['all_passed'] else '✗ FAILED'}")
    
    if results['summary']['failed_tests']:
        print(f"\nFailed tests: {', '.join(results['summary']['failed_tests'])}")
    
    print(f"\n{'='*80}")
    print("DETAILED RESULTS")
    print(f"{'='*80}")
    
    for test_result in results['test_results']:
        test_name = test_result.get('test_name', test_result.get('server_name', 'Unknown'))
        success = test_result.get('success', test_result.get('connection_success', False))
        
        print(f"\nTest: {test_name}")
        print(f"  Result: {'✓ PASSED' if success else '✗ FAILED'}")
        
        if test_result.get('errors'):
            print("  Errors:")
            for error in test_result['errors']:
                print(f"    - {error}")


async def quick_connectivity_check():
    """Perform a quick connectivity check."""
    
    print("Performing quick connectivity check...")
    
    server_manager = AmassServerManager("./mcp")
    
    try:
        # Quick connection test
        logger.info("Testing server startup...")
        success = await server_manager.start_server()
        
        if success:
            print("✓ Amass MCP server: Connected")
            await asyncio.sleep(1)
            await server_manager.stop_server()
            print("✓ Amass MCP server: Disconnected cleanly")
        else:
            print("✗ Amass MCP server: Failed to connect")
            
    except Exception as e:
        print(f"✗ Connectivity check failed: {str(e)}")


async def interactive_test():
    """Run interactive test mode."""
    
    print("MCP Server Connection Tester")
    print("=" * 40)
    
    while True:
        print("\nOptions:")
        print("1. Run all tests")
        print("2. Quick connectivity check")
        print("3. Test server startup/shutdown only")
        print("4. Exit")
        
        choice = input("\nSelect option (1-4): ").strip()
        
        if choice == "1":
            results = await test_all_mcp_functionality()
            print_test_summary(results)
            
            # Save results to file
            with open("mcp_test_results.json", "w") as f:
                json.dump(results, f, indent=2)
            print("\nDetailed results saved to: mcp_test_results.json")
            
        elif choice == "2":
            await quick_connectivity_check()
            
        elif choice == "3":
            result = await test_amass_mcp_server()
            print(f"\nServer test result:")
            print(json.dumps(result, indent=2))
            
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
        elif sys.argv[1] == "--quick":
            await quick_connectivity_check()
        elif sys.argv[1] == "--help":
            print("MCP Connection Test Script")
            print("Usage:")
            print("  python test_mcp_connection.py              # Run full test suite")
            print("  python test_mcp_connection.py --interactive # Interactive mode")
            print("  python test_mcp_connection.py --quick      # Quick connectivity check")
            print("  python test_mcp_connection.py --help       # Show this help")
        else:
            print(f"Unknown option: {sys.argv[1]}")
            print("Use --help for usage information")
    else:
        # Run full test suite
        results = await test_all_mcp_functionality()
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