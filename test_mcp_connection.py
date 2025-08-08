#!/usr/bin/env python3
"""
Test MCP Connection Script
Tests the connection to MCP servers and validates tool availability.
"""

import asyncio
import logging
import sys
from typing import Dict, List
from mcp.config import MCPConfigManager, MCPServerConfig
from mcp.adapter import MCPManager, ReconnaissanceMCPTools

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class MCPConnectionTester:
    """Test MCP server connections and tool availability."""
    
    def __init__(self):
        self.config_manager = MCPConfigManager()
        self.mcp_manager = MCPManager(self.config_manager)
    
    def test_server_config(self) -> bool:
        """Test that server configurations are properly loaded."""
        logger.info("Testing server configuration...")
        
        try:
            servers = self.config_manager.list_servers()
            logger.info(f"Configured servers: {list(servers.keys())}")
            
            for name, description in servers.items():
                config = self.config_manager.get_server_config(name)
                logger.info(f"  - {name}: {description}")
                logger.info(f"    Type: {config.server_type}")
                logger.info(f"    Command: {config.command}")
                logger.info(f"    Args: {config.args}")
                logger.info(f"    Enabled: {config.enabled}")
            
            return len(servers) > 0
            
        except Exception as e:
            logger.error(f"Server configuration test failed: {e}")
            return False
    
    def test_stdio_parameters(self) -> bool:
        """Test creation of StdioServerParameters."""
        logger.info("Testing StdioServerParameters creation...")
        
        try:
            amass_params = self.config_manager.create_stdio_parameters("amass-mcp")
            if amass_params:
                logger.info(f"Successfully created parameters for amass-mcp")
                logger.info(f"  Command: {amass_params.command}")
                logger.info(f"  Args: {amass_params.args}")
                return True
            else:
                logger.error("Failed to create parameters for amass-mcp")
                return False
                
        except Exception as e:
            logger.error(f"StdioServerParameters test failed: {e}")
            return False
    
    def test_mcp_connection(self) -> bool:
        """Test actual connection to MCP servers."""
        logger.info("Testing MCP server connection...")
        
        try:
            with ReconnaissanceMCPTools(self.mcp_manager) as tools:
                logger.info(f"Successfully connected to MCP servers")
                logger.info(f"Available tools: {[tool.name for tool in tools]}")
                
                # Test tool details
                for tool in tools:
                    logger.info(f"Tool: {tool.name}")
                    logger.info(f"  Description: {tool.description}")
                    if hasattr(tool, 'inputSchema'):
                        logger.info(f"  Input Schema: {tool.inputSchema}")
                
                return len(tools) > 0
                
        except Exception as e:
            logger.error(f"MCP connection test failed: {e}")
            logger.error("Possible issues:")
            logger.error("  1. Amass MCP server script not found")
            logger.error("  2. Python dependencies not installed")
            logger.error("  3. MCP server dependencies not available")
            logger.error("  4. Path or configuration issues")
            return False
    
    async def test_tool_execution(self) -> bool:
        """Test basic tool execution (if possible without actual domain testing)."""
        logger.info("Testing tool execution capabilities...")
        
        try:
            with ReconnaissanceMCPTools(self.mcp_manager) as tools:
                amass_tools = [tool for tool in tools if 'amass' in tool.name.lower()]
                
                if not amass_tools:
                    logger.warning("No Amass tools found for testing")
                    return False
                
                logger.info(f"Found {len(amass_tools)} Amass tools:")
                for tool in amass_tools:
                    logger.info(f"  - {tool.name}: {tool.description}")
                
                # We won't actually execute tools that require real domains
                # but we can verify they are callable
                logger.info("Tool execution test completed (no actual execution)")
                return True
                
        except Exception as e:
            logger.error(f"Tool execution test failed: {e}")
            return False
    
    def test_modular_design(self) -> bool:
        """Test the modular design for adding new MCP servers."""
        logger.info("Testing modular design...")
        
        try:
            # Test adding a new server configuration
            test_config = MCPServerConfig(
                name="test-server",
                server_type="stdio",
                command="echo",
                args=["test"],
                description="Test server for validation",
                enabled=False  # Disabled so it won't interfere
            )
            
            self.config_manager.add_server_config(test_config)
            
            # Verify it was added
            added_config = self.config_manager.get_server_config("test-server")
            if added_config and added_config.name == "test-server":
                logger.info("Successfully added test server configuration")
                
                # Test server listing
                servers = self.config_manager.list_servers()
                if "test-server" in servers:
                    logger.info("Test server appears in server listing")
                    return True
                else:
                    logger.error("Test server not found in server listing")
                    return False
            else:
                logger.error("Failed to add test server configuration")
                return False
                
        except Exception as e:
            logger.error(f"Modular design test failed: {e}")
            return False
    
    def run_all_tests(self) -> Dict[str, bool]:
        """Run all tests and return results."""
        logger.info("Starting MCP Connection Tests...")
        logger.info("=" * 50)
        
        results = {}
        
        # Test 1: Server Configuration
        results['server_config'] = self.test_server_config()
        
        # Test 2: StdioServerParameters
        results['stdio_parameters'] = self.test_stdio_parameters()
        
        # Test 3: MCP Connection
        results['mcp_connection'] = self.test_mcp_connection()
        
        # Test 4: Tool Execution
        results['tool_execution'] = asyncio.run(self.test_tool_execution())
        
        # Test 5: Modular Design
        results['modular_design'] = self.test_modular_design()
        
        logger.info("=" * 50)
        logger.info("Test Results Summary:")
        
        all_passed = True
        for test_name, result in results.items():
            status = "PASS" if result else "FAIL"
            logger.info(f"  {test_name}: {status}")
            if not result:
                all_passed = False
        
        logger.info(f"\nOverall Status: {'ALL TESTS PASSED' if all_passed else 'SOME TESTS FAILED'}")
        
        if not all_passed:
            logger.info("\nTroubleshooting Tips:")
            logger.info("1. Ensure all dependencies are installed:")
            logger.info("   pip install 'crewai-tools[mcp]' mcp")
            logger.info("2. Verify the amass-mcp server script is executable")
            logger.info("3. Check that Python path includes the mcp module")
            logger.info("4. Ensure Amass is installed and available in PATH")
        
        return results


def main():
    """Main function to run the MCP connection tests."""
    tester = MCPConnectionTester()
    results = tester.run_all_tests()
    
    # Exit with error code if any tests failed
    if not all(results.values()):
        sys.exit(1)
    else:
        logger.info("All tests passed! MCP connection is ready.")
        sys.exit(0)


if __name__ == "__main__":
    main()
