"""Install the L1 pre-call guard on a FastMCP instance."""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import Any

from mcp.server.fastmcp import FastMCP
from mcp.server.fastmcp.exceptions import ToolError

from .l1_guard import check_l1_guard


def install_l1_precall_guard(mcp: FastMCP) -> None:
    """Wrap ``ToolManager.call_tool`` so every invocation passes ``check_l1_guard``."""
    manager = mcp._tool_manager
    original: Callable[..., Awaitable[Any]] = manager.call_tool

    async def guarded_call_tool(
        name: str,
        arguments: dict[str, Any],
        context: Any = None,
        convert_result: bool = False,
    ) -> Any:
        tool = manager.get_tool(name)
        description = tool.description if tool else None
        result = check_l1_guard(name, arguments, description=description)
        if not result.allowed:
            raise ToolError(result.reason or "L1 hard-deny")
        return await original(
            name,
            arguments,
            context=context,
            convert_result=convert_result,
        )

    manager.call_tool = guarded_call_tool  # type: ignore[method-assign]
