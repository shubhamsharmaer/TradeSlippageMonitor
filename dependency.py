from config import settings
from services.flow import TradeMatchingFlowService

if settings.is_demo_mode:
    from repositeries.json_live_repo import JsonLiveRepo
    from repositeries.json_backtest_repo import JsonBacktestRepo

    live_repo = JsonLiveRepo()
    backtest_repo = JsonBacktestRepo()
else:
    from repositeries.backtest_repo import BacktestRepo
    from repositeries.live_repo import LiveTradeRepo

    live_repo = LiveTradeRepo()
    backtest_repo = BacktestRepo()

flow_service = TradeMatchingFlowService(live_repo=live_repo, backtest_repo=backtest_repo)