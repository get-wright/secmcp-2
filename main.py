"""
Reconnaissance Agent - Main Entry Point

This is the main entry point for the Reconnaissance Agent.
It provides a command-line interface to run reconnaissance tasks.
"""

import asyncio
import argparse
import sys
from typing import Optional

from loguru import logger
from src.reconnaissance_agent import run_reconnaissance


def setup_logging(verbose: bool = False):
    """Setup logging configuration."""
    
    # Remove default handler
    logger.remove()
    
    # Add custom handler
    log_level = "DEBUG" if verbose else "INFO"
    logger.add(
        sys.stderr,
        level=log_level,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
    )
    
    # Add file handler for detailed logs
    logger.add(
        "logs/reconnaissance.log",
        level="DEBUG",
        rotation="10 MB",
        retention="7 days",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}"
    )


async def main():
    """Main entry point."""
    
    parser = argparse.ArgumentParser(
        description="Reconnaissance Agent - Subdomain Enumeration Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py example.com                    # Passive reconnaissance only
  python main.py example.com --comprehensive   # Full reconnaissance (passive + active)
  python main.py example.com --verbose         # Enable verbose logging
  python main.py test.com --no-auto-manage     # Manual MCP server management
  
Note: Make sure to setup Amass MCP server according to the documentation
at https://github.com/cyproxio/mcp-for-security/tree/main/amass-mcp
        """
    )
    
    parser.add_argument(
        "domain",
        help="Target domain for reconnaissance"
    )
    
    parser.add_argument(
        "--comprehensive",
        action="store_true",
        help="Perform comprehensive reconnaissance (passive + active)"
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose logging"
    )
    
    parser.add_argument(
        "--no-auto-manage",
        action="store_true",
        help="Don't automatically start/stop MCP servers"
    )
    
    parser.add_argument(
        "--output", "-o",
        type=str,
        help="Output file for reconnaissance report"
    )
    
    args = parser.parse_args()
    
    # Setup logging
    setup_logging(args.verbose)
    
    try:
        logger.info(f"Starting reconnaissance for domain: {args.domain}")
        
        # Run reconnaissance
        result = await run_reconnaissance(
            domain=args.domain,
            comprehensive=args.comprehensive,
            auto_manage_servers=not args.no_auto_manage,
            working_directory="./mcp"
        )
        
        # Output results
        print("\n" + "="*80)
        print("RECONNAISSANCE REPORT")
        print("="*80)
        print(result)
        
        # Save to file if requested
        if args.output:
            with open(args.output, 'w') as f:
                f.write("RECONNAISSANCE REPORT\n")
                f.write("="*80 + "\n")
                f.write(f"Domain: {args.domain}\n")
                f.write(f"Comprehensive: {args.comprehensive}\n")
                f.write("="*80 + "\n\n")
                f.write(result)
            
            logger.info(f"Report saved to: {args.output}")
        
        logger.info("Reconnaissance completed successfully")
        
    except KeyboardInterrupt:
        logger.warning("Reconnaissance interrupted by user")
        sys.exit(130)
        
    except Exception as e:
        logger.error(f"Reconnaissance failed: {str(e)}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
