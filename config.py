from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_mode: str = "demo"

    mongo_uri: str = "mongodb://localhost:27017"
    mongo_db: str = "demo_db"

    backoffice_mongo_uri: str = "mongodb://localhost:27017"
    nb_backoffice_mongo_db: str = "demo_db"
    nb_backoffice_live_trade_collection: str = "live_trades_demo"
    nb_backoffice_algo_collection: str = "nb_algo_demo"  # for quantity_multiplier
    alpha_backoffice_algo_collection: str = "alpha_algo_demo"  # for quantity_multiplier of alpha
    alpha_backoffice_live_trade_collection: str = "alpha_live_trades_demo"  # for alpha live trades

    all_brokers_backoffice_db: str = "demo_db"
    all_brokers_live_trade_collection: str = "all_brokers_live_trades_demo"
    all_brokers_algo_collection: str = "all_brokers_algo_demo"  # for quantity_multiplier

    finsage_mongo_uri: str = "mongodb://localhost:27017"
    finsage_mongo_db: str = "demo_finsage_db"
    backtest_trade_collection: str = "backtest_trades_demo"

    # auto backtest config uri is same as finsage_mongo_uri
    auto_backtest_db: str = "demo_finsage_db"
    auto_backtest_collection: str = "auto_backtest_demo"

    # mcp auth
    MCP_BEARER_TOKEN: str

    class Config:
        env_file = ".env"
        extra = "ignore"

    @property
    def is_demo_mode(self) -> bool:
        return self.app_mode.lower() == "demo"


settings = Settings()
