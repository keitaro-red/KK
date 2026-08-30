"""全局配置"""
import os
from dotenv import load_dotenv

load_dotenv("/app/.env")


class Config:
    """KK 全局配置"""
    POSTGRES_URL: str = os.getenv("POSTGRES_URL", "")
    KK_ENV: str = os.getenv("KK_ENV", "development")
    WORKSPACE_DIR:str=os.getenv("KKMAIN_WORKSPACE","/app/data/workspace")

    SILICONFLOW_API_KEY: str = os.getenv("SILICONFLOW_API_KEY", "")
    DEFAULT_MODEL: str = os.getenv(
        "DEFAULT_MODEL", "siliconflow-cn:deepseek-ai/DeepSeek-V4-Flash")


config = Config
