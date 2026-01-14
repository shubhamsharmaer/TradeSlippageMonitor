from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # app_name: str
    # env: str

    mongo_uri: str
    mongo_db: str

    backoffice_mongo_uri: str
    backoffice_mongo_db: str
    backoffice_live_trade_collection: str
    backoffice_algo_collection: str # for quantity_multiplier

    finsage_mongo_uri: str
    finsage_mongo_db: str
    backtest_trade_collection: str

    class Config:
        env_file = ".env"

settings = Settings()
