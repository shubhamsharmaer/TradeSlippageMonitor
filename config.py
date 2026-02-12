from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # app_name: str
    # env: str

    mongo_uri: str
    mongo_db: str

    backoffice_mongo_uri: str
    nb_backoffice_mongo_db: str
    nb_backoffice_live_trade_collection: str
    nb_backoffice_algo_collection: str # for quantity_multiplier
    alpha_backoffice_algo_collection: str # for quantity_multiplier of alpha
    alpha_backoffice_live_trade_collection: str # for alpha live trades

    all_brokers_backoffice_db: str
    all_brokers_live_trade_collection: str
    all_brokers_algo_collection: str # for quantity_multiplier

    finsage_mongo_uri: str
    finsage_mongo_db: str
    backtest_trade_collection: str

    class Config:
        env_file = ".env"

settings = Settings()
