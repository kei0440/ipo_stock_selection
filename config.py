import os
from datetime import timedelta


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY") or "you-will-never-guess"
    CACHE_TYPE = "SimpleCache"
    CACHE_DEFAULT_TIMEOUT = timedelta(days=30)
    DATA_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")

    # アプリケーション固有の設定
    IPO_LIST_FILE = os.path.join(DATA_FOLDER, "ipo_list.csv")
