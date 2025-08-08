from __future__ import annotations

from typing import List

from crewai import Agent

from src.tools.amass_mcp import AmassMCPTool


def create_reconnaissance_agent(tools: List[object] | None = None) -> Agent:
    """
    Create the single Reconnaissance Agent, equipped to perform passive and active
    subdomain enumeration via MCP tools.

    The agent is intentionally minimal and focused on reconnaissance tasks.
    Additional MCP tools can be passed for expandability.
    """
    agent_tools = tools or [AmassMCPTool()]

    return Agent(
        role="Reconnaissance Agent",
        goal=(
            "Perform passive and active subdomain enumeration using amass-mcp "
            "via Model Context Protocol tools."
        ),
        backstory=(
            "A security reconnaissance specialist skilled at leveraging MCP-enabled "
            "tools for domain intelligence and subdomain discovery."
        ),
        tools=agent_tools,
        allow_code_execution=False,
    )


