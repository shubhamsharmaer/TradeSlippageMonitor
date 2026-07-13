from fastmcp import FastMCP
from fastmcp.server.auth.providers.jwt import StaticTokenVerifier
from config import settings
from datetime import date
from typing import Optional
from dependency import backtest_repo, live_repo, flow_service

verifier = StaticTokenVerifier(
    tokens={
        settings.MCP_BEARER_TOKEN: {
            "client_id": "leakage-admin",
            "scopes": ["leakage:read", "leakage:run"],
        }
    },
    required_scopes=["leakage:read"],
)

mcp = FastMCP(
    name="Leakage Detector",
    instructions=(
        "Tools to reconcile live trades against backtest expectations. "
        "Call list_backtest_algos to discover available strategies before "
        "running detection."
    ),
    auth=verifier,
)

@mcp.tool()
def list_backtest_algos() -> list[str]:
    """Return all backtest strategy names known to the system, sorted."""
    return backtest_repo.list_strategies()

@mcp.tool()
def list_live_algos() -> list[str]:
    """Return all live strategy/algorithm names known to the system, sorted."""
    return live_repo.list_algonames()


@mcp.tool()
def list_clients() -> list[str]:
    """Return all client IDs that appear in any live-trade collection, sorted."""
    return live_repo.list_clients()

@mcp.tool()
def list_brokers() -> list[str]:
    """Return all broker names that appear in any live-trade collection, sorted."""
    return live_repo.list_brokers()

@mcp.tool()
def detect_leakage(
    live_algo: str,
    backtest_algo: str,
    start_date: date,
    end_date: date,
    price_tolerance: float,
    clientId: Optional[str] = None,
    min_price_for_hedge: Optional[float] = None,
    check_qnt: bool = False,
    broker: Optional[str] = None,
) -> dict:
    """
    Reconcile live broker trades against backtest expectations and return a
    mismatch report.

    Use list_live_algos / list_backtest_algos / list_clients / list_brokers
    first to discover valid argument values.

    Args:
        live_algo: Live algo name (from list_live_algos).
        backtest_algo: Backtest strategy name (from list_backtest_algos).
        start_date: Inclusive start date (YYYY-MM-DD).
        end_date: Inclusive end date (YYYY-MM-DD).
        price_tolerance: Absolute price difference allowed before flagging a
            price mismatch.
        clientId: If provided, restrict to one client. Otherwise reconcile
            across every client that traded the live algo in the window.
        min_price_for_hedge: Minimum price filter applied to live trades to
            distinguish hedges from primary trades. Optional.
        check_qnt: If True, quantity mismatches are also flagged.
        broker: If provided, restrict to one broker.

    Returns:
        A MismatchReport dict containing matched, missing, and extra trades
        plus a summary block (counts and match_rate).
    """

    report = flow_service.reconcile(
        backtest_algo=backtest_algo,
        live_algo=live_algo,
        start_date=start_date,
        end_date=end_date,
        price_tolerance=price_tolerance,
        clientId=clientId,
        min_price_for_hedge=min_price_for_hedge,
        check_qnt=check_qnt,
        broker=broker,
    )
    return report.model_dump() if hasattr(report, "model_dump") else report