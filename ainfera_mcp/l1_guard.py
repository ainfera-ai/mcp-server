"""L1 hard-deny pre-call guard for MCP tool invocations (P0).

Mirrors valinor Phase-C D4 L1 classes (``agents._triage._L1_PATTERNS``): banking,
payments-adjacent spend, trading, equity, identity, medical, family, hire, board.
Enforcement is structural — matched on the tool name, serialized arguments, and
tool description — never on model self-reporting.

Read-shaped wallet tools (``get_wallet``) are allowed unless arguments themselves
carry an L1 match.
"""

from __future__ import annotations

import json
import re
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any, Final

# Wallet top-up bounds (USD). Out-of-range or missing amounts are denied pre-call.
TOPUP_MIN_USD: Final[float] = 0.01
TOPUP_MAX_USD: Final[float] = 500.0

# Optional hook: ``(tool_name, arguments) -> reason | None``. Return a string to deny.
ScopeCheckHook = Callable[[str, dict[str, Any]], str | None]
_scope_check_hook: ScopeCheckHook | None = None

_L1_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = tuple(
    (label, re.compile(rx, re.IGNORECASE))
    for label, rx in [
        ("equity", r"\b(equity|cap.?table|shares?\b|stock\s+grant)"),
        ("sign", r"\b(sign(ing)?\s+(contract|agreement|term\s*sheet)|docusign)"),
        ("board", r"\bboard\s+(seat|vote|resolution|meeting\s+decision)"),
        ("hire", r"\b(hire|fire|terminat\w+\s+employ|offer\s+letter)"),
        ("banking", r"\b(bank\s+(transfer|account|wire)|iban|swift\s+code)"),
        ("payments", r"\b(payment\s+rails?|invoice|payroll|wire\s+funds?)"),
        ("trading", r"\b(trade|trading|swap\s+tokens?|exchange\s+order)"),
        ("identity", r"\b(press\s+release|public\s+statement|founder\s+identity)"),
        ("medical", r"\bmedical\b"),
        ("family", r"\bfamily\b"),
    ]
)

_READ_TOOLS: frozenset[str] = frozenset(
    {
        "get_wallet",
        "get_agent",
        "read_audit_chain",
        "verify_audit_chain",
        "verify_agent_card",
    }
)


@dataclass(frozen=True)
class L1GuardResult:
    allowed: bool
    reason: str | None = None

    @classmethod
    def allow(cls) -> L1GuardResult:
        return cls(allowed=True)

    @classmethod
    def deny(cls, reason: str) -> L1GuardResult:
        return cls(allowed=False, reason=reason)


def set_scope_check_hook(hook: ScopeCheckHook | None) -> None:
    """Register or clear the optional scope-check hook (tests / deployment wiring)."""
    global _scope_check_hook
    _scope_check_hook = hook


def get_scope_check_hook() -> ScopeCheckHook | None:
    return _scope_check_hook


def l1_match_label(action_text: str) -> str | None:
    """Return the matched L1 class label, or None."""
    for label, rx in _L1_PATTERNS:
        if rx.search(action_text or ""):
            return label
    return None


def _serialize_action(tool_name: str, arguments: dict[str, Any] | None) -> str:
    return f"{tool_name} {json.dumps(arguments or {}, default=str)[:2000]}"


def _check_topup_wallet(arguments: dict[str, Any] | None) -> L1GuardResult | None:
    args = arguments or {}
    amount = args.get("amount_usd")
    if amount is None:
        return L1GuardResult.deny(
            "topup_wallet denied: amount_usd is required and must be within bounds"
        )
    try:
        value = float(amount)
    except (TypeError, ValueError):
        return L1GuardResult.deny(
            "topup_wallet denied: amount_usd must be a number within bounds"
        )
    if not (TOPUP_MIN_USD <= value <= TOPUP_MAX_USD):
        return L1GuardResult.deny(
            f"topup_wallet denied: amount_usd must be between "
            f"{TOPUP_MIN_USD} and {TOPUP_MAX_USD} inclusive"
        )
    return None


def check_l1_guard(
    tool_name: str,
    arguments: dict[str, Any] | None = None,
    *,
    description: str | None = None,
) -> L1GuardResult:
    """Pre-call guard. Deny when L1 categories match or wallet spend is out of bounds."""
    hook = _scope_check_hook
    if hook is not None:
        scope_reason = hook(tool_name, arguments or {})
        if scope_reason:
            return L1GuardResult.deny(scope_reason)

    if tool_name == "topup_wallet":
        topup_result = _check_topup_wallet(arguments)
        if topup_result is not None:
            return topup_result

    serialized = _serialize_action(tool_name, arguments)
    if description:
        serialized = f"{serialized} {description}"

    label = l1_match_label(serialized)
    if label is not None and tool_name not in _READ_TOOLS:
        return L1GuardResult.deny(f"L1 hard-deny: {label}")

    # Read tools: still block explicit L1 content in arguments (e.g. nested messages).
    if label is not None and tool_name in _READ_TOOLS:
        arg_only = l1_match_label(json.dumps(arguments or {}, default=str))
        if arg_only is not None:
            return L1GuardResult.deny(f"L1 hard-deny: {arg_only}")

    return L1GuardResult.allow()
