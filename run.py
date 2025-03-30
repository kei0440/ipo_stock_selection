#!/usr/bin/env python
# -*- coding: utf-8 -*-

from app import create_app
import os

app = create_app()

if __name__ == "__main__":
    # データフォルダが存在しない場合は作成
    os.makedirs("data", exist_ok=True)

    # デバッグモードで実行
    app.run(debug=True)
