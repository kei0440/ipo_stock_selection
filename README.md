<div align="center">
  <img src="assets/header.svg" alt="IPO Stock Selection System" width="800">
</div>

# 📊 IPO銘柄選定システム

## 📝 概要

このプロジェクトは、日本の新規株式公開（IPO）銘柄から投資価値の高い銘柄を自動的に選定するシステムです。以下の条件に基づいて銘柄をフィルタリングします：

- 📈 **成長性**: 過去3年間の売上高と営業利益が継続的に成長している
- 💰 **PER（株価収益率）**: 15以下
- 💸 **配当利回り**: 3%以上

## 🚀 特徴

- JPX（日本取引所グループ）から最新のIPO情報を自動取得
- Yahoo Finance Japanから株価情報を取得
- IRBankから企業の財務パフォーマンスデータを取得
- 設定した条件に基づいて投資価値の高い銘柄を自動選定
- 結果をCSVファイルとして出力
- Webインターフェースでの操作が可能

## 🔧 インストール方法

### 前提条件

- Python 3.13以上
- pipenv（依存関係管理用）

### セットアップ手順

1. リポジトリをクローン：

```bash
git clone https://github.com/yourusername/ipo_stock_selection.git
cd ipo_stock_selection
```

2. 依存関係のインストール：

```bash
pipenv install
```

## 📋 使用方法

### コマンドラインインターフェース

1. 仮想環境を有効化：

```bash
pipenv shell
```

2. メインスクリプトを実行：

```bash
python main_script.py
```

3. 実行結果：
   - `ipo_list.csv`: フィルタリング前の全IPOデータ
   - `filtered_ipo_list_YYYYMMDD.csv`: フィルタリング後の投資候補銘柄（日付付き）

### Webインターフェース

1. 仮想環境を有効化：

```bash
pipenv shell
```

2. Flaskアプリケーションを実行：

```bash
python run.py
```

3. ブラウザで以下のURLにアクセス：

```
http://127.0.0.1:5000/
```

4. Webインターフェースの使用方法：
   - **ホーム画面**: データ取得ボタンでIPO情報を取得
   - **フィルタリング画面**: 条件を設定してIPO銘柄をフィルタリング
   - **結果画面**: フィルタリング結果の表示とCSVダウンロード
   - **概要画面**: プロジェクトの説明

## 🗂️ プロジェクト構造

```
ipo_stock_selection/
├── app/                     # Flaskアプリケーション
│   ├── __init__.py          # アプリケーション初期化
│   ├── routes.py            # ルート定義
│   ├── utils/               # ユーティリティ関数
│   │   ├── __init__.py
│   │   ├── jpx_scraper.py   # JPXスクレイパー
│   │   ├── yahoo_finance_scraper.py # Yahoo Financeスクレイパー
│   │   ├── irbank_scraper.py # IRBankスクレイパー
│   │   └── filter_ipo_data.py # データフィルタリングロジック
│   ├── static/              # 静的ファイル
│   │   ├── css/             # CSSファイル
│   │   ├── js/              # JavaScriptファイル
│   │   └── images/          # 画像ファイル
│   └── templates/           # HTMLテンプレート
│       ├── base.html        # ベーステンプレート
│       ├── index.html       # ホームページ
│       ├── filter.html      # フィルタリングページ
│       ├── results.html     # 結果表示ページ
│       └── about.html       # プロジェクト説明ページ
├── assets/                  # プロジェクトアセット
│   └── header.svg           # READMEヘッダー画像
├── data/                    # データ保存ディレクトリ
│   ├── ipo_list.csv         # フィルタリング前のIPOデータ
│   └── filtered_ipo_list_*.csv # フィルタリング後の投資候補銘柄
├── main_script.py           # CLIメインスクリプト
├── run.py                   # Flaskアプリケーション実行スクリプト
├── config.py                # 設定ファイル
├── Pipfile                  # 依存関係定義
└── Pipfile.lock             # 依存関係のロックファイル
```

## 📚 依存ライブラリ

- pandas: データ処理と分析
- requests: HTTPリクエスト
- BeautifulSoup4: HTMLパース
- lxml: XMLおよびHTMLの処理
- yfinance: Yahoo Financeデータ取得
- Flask: Webアプリケーションフレームワーク
- Flask-WTF: フォーム処理
- Flask-Bootstrap: レスポンシブデザイン

## 🔄 更新頻度

このシステムは定期的に実行することで、最新のIPO情報を取得し、投資候補を更新することができます。データは30日以内に更新された場合はスキップされるため、月に1回程度の実行が推奨されます。

## 📜 ライセンス

このプロジェクトはMITライセンスの下で公開されています。詳細は[LICENSE](LICENSE)ファイルを参照してください。

## ⚠️ 免責事項

このシステムは投資判断の参考情報を提供するものであり、投資の成功を保証するものではありません。投資判断は自己責任で行ってください。