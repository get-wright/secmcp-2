#!/usr/bin/env python3
"""
Example Usage of Reconnaissance Agent
Demonstrates how to use the Reconnaissance Agent for subdomain enumeration.
"""

import logging
from reconnaissance_agent import ReconnaissanceAgent

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def example_passive_enumeration():
    """Example of passive subdomain enumeration."""
    logger.info("=== Passive Subdomain Enumeration Example ===")
    
    # Create the reconnaissance agent
    recon_agent = ReconnaissanceAgent()
    
    # Target domain (replace with actual domain for testing)
    target_domain = "example.com"
    
    try:
        # Run passive enumeration only
        result = recon_agent.run_reconnaissance(
            domain=target_domain,
            tasks=['passive'],
            passive_timeout=300
        )
        
        logger.info("Passive enumeration completed successfully")
        return result
        
    except Exception as e:
        logger.error(f"Passive enumeration failed: {e}")
        return None


def example_active_enumeration():
    """Example of active subdomain enumeration."""
    logger.info("=== Active Subdomain Enumeration Example ===")
    
    # Create the reconnaissance agent
    recon_agent = ReconnaissanceAgent()
    
    # Target domain (replace with actual domain for testing)
    target_domain = "example.com"
    
    try:
        # Run active enumeration with brute force disabled
        result = recon_agent.run_reconnaissance(
            domain=target_domain,
            tasks=['active'],
            active_timeout=600,
            brute_force=False
        )
        
        logger.info("Active enumeration completed successfully")
        return result
        
    except Exception as e:
        logger.error(f"Active enumeration failed: {e}")
        return None


def example_comprehensive_reconnaissance():
    """Example of comprehensive reconnaissance (passive + active + intel)."""
    logger.info("=== Comprehensive Reconnaissance Example ===")
    
    # Create the reconnaissance agent
    recon_agent = ReconnaissanceAgent()
    
    # Target domain (replace with actual domain for testing)
    target_domain = "example.com"
    
    try:
        # Run all reconnaissance tasks
        result = recon_agent.run_reconnaissance(
            domain=target_domain,
            tasks=['passive', 'active', 'intel'],
            passive_timeout=300,
            active_timeout=600,
            brute_force=False,
            whois=True
        )
        
        logger.info("Comprehensive reconnaissance completed successfully")
        return result
        
    except Exception as e:
        logger.error(f"Comprehensive reconnaissance failed: {e}")
        return None


def example_custom_configuration():
    """Example using custom configuration."""
    logger.info("=== Custom Configuration Example ===")
    
    # Create the reconnaissance agent
    recon_agent = ReconnaissanceAgent()
    
    # Target domain (replace with actual domain for testing)
    target_domain = "example.com"
    
    try:
        # Run with custom configuration
        result = recon_agent.run_reconnaissance(
            domain=target_domain,
            tasks=['passive', 'active'],
            passive_timeout=180,  # 3 minutes
            active_timeout=900,   # 15 minutes
            brute_force=True,     # Enable brute force
            wordlist="/path/to/custom/wordlist.txt",  # Custom wordlist
            config_file="/path/to/amass/config.ini"   # Custom Amass config
        )
        
        logger.info("Custom configuration reconnaissance completed successfully")
        return result
        
    except Exception as e:
        logger.error(f"Custom configuration reconnaissance failed: {e}")
        return None


def list_available_tools():
    """List all available MCP tools."""
    logger.info("=== Available MCP Tools ===")
    
    # Create the reconnaissance agent
    recon_agent = ReconnaissanceAgent()
    
    # List available tools
    tools = recon_agent.list_available_tools()
    
    logger.info("Available MCP servers:")
    for name, description in tools.items():
        logger.info(f"  - {name}: {description}")
    
    return tools


def main():
    """Main function demonstrating various usage examples."""
    print("Reconnaissance Agent - Example Usage")
    print("=" * 50)
    
    # List available tools
    list_available_tools()
    
    print("\nNOTE: The following examples use 'example.com' as a placeholder.")
    print("Replace with actual domains for real testing.")
    print("Be aware of legal and ethical considerations when testing.")
    print("\nUncomment the desired example below to run:\n")
    
    # Uncomment one of the following examples to run:
    
    # Example 1: Passive enumeration only
    # result = example_passive_enumeration()
    # if result:
    #     print(f"\nPassive Enumeration Result:\n{result}")
    
    # Example 2: Active enumeration only
    # result = example_active_enumeration()
    # if result:
    #     print(f"\nActive Enumeration Result:\n{result}")
    
    # Example 3: Comprehensive reconnaissance
    # result = example_comprehensive_reconnaissance()
    # if result:
    #     print(f"\nComprehensive Reconnaissance Result:\n{result}")
    
    # Example 4: Custom configuration
    # result = example_custom_configuration()
    # if result:
    #     print(f"\nCustom Configuration Result:\n{result}")
    
    print("Examples completed. Modify and uncomment to test with real domains.")


if __name__ == "__main__":
    main()
