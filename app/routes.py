from flask import (
    Blueprint,
    render_template,
    request,
    jsonify,
    send_file,
    redirect,
    url_for,
    flash,
    current_app,
)
import pandas as pd
import os
from datetime import datetime
import io
from app.utils.jpx_scraper import scrape_jpx_ipo_list
from app.utils.yahoo_finance_scraper import fetch_yahoo_data
from app.utils.irbank_scraper import fetch_irbank_data
from app.utils.filter_ipo_data import clean_and_filter_ipo_data
from config import Config

# Blueprintの作成
main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def index():
    """ホームページを表示"""
    return render_template("index.html")


@main_bp.route("/about")
def about():
    """プロジェクトについての説明ページを表示"""
    return render_template("about.html")


@main_bp.route("/fetch-data", methods=["POST"])
def fetch_data():
    """データ取得処理"""
    try:
        # データフォルダが存在しない場合は作成
        os.makedirs(Config.DATA_FOLDER, exist_ok=True)

        # Step 1: 既存のIPOリストを読み込む
        is_new_list = False
        try:
            ipo_df = pd.read_csv(Config.IPO_LIST_FILE)
        except FileNotFoundError:
            ipo_df = pd.DataFrame()
            is_new_list = True

        # Step 2: JPXからIPOデータを取得
        jpx_df = scrape_jpx_ipo_list()

        # 既存データとマージ
        if not ipo_df.empty and not jpx_df.empty:
            ipo_df = pd.concat([ipo_df, jpx_df]).drop_duplicates(
                subset=["stock_code"], keep="last"
            )
        elif not jpx_df.empty:
            ipo_df = jpx_df

        # Step 3: Yahoo Financeから追加データを取得
        force_scrape = request.form.get("force_scrape", "false").lower() == "true"
        ipo_df = fetch_yahoo_data(ipo_df, force_scrape=force_scrape or is_new_list)

        # Step 4: IRBankからデータを取得し、成長フラグを追加
        ipo_df = fetch_irbank_data(ipo_df, force_scrape=force_scrape or is_new_list)

        # データを保存
        ipo_df.to_csv(Config.IPO_LIST_FILE, index=False)

        flash("データの取得が完了しました。", "success")
        return redirect(url_for("main.filter_data"))

    except Exception as e:
        flash(f"データ取得中にエラーが発生しました: {str(e)}", "danger")
        return redirect(url_for("main.index"))


@main_bp.route("/filter", methods=["GET", "POST"])
def filter_data():
    """データフィルタリングページ"""
    try:
        # IPOリストが存在するか確認
        if not os.path.exists(Config.IPO_LIST_FILE):
            flash(
                "IPOデータが見つかりません。先にデータを取得してください。", "warning"
            )
            return redirect(url_for("main.index"))

        # IPOリストを読み込む
        ipo_df = pd.read_csv(Config.IPO_LIST_FILE)

        if request.method == "POST":
            # フォームからフィルタリングパラメータを取得
            filter_params = {
                "growth_flag": request.form.get("growth_flag") == "on",
                "per_max": (
                    float(request.form.get("per_max"))
                    if request.form.get("per_max")
                    else None
                ),
                "dividend_yield_min": (
                    float(request.form.get("dividend_yield_min"))
                    if request.form.get("dividend_yield_min")
                    else None
                ),
            }

            # データをフィルタリング
            filtered_df = clean_and_filter_ipo_data(ipo_df, filter_params)

            # フィルタリング結果を保存
            today_str = datetime.now().strftime("%Y%m%d")
            filtered_filename = f"filtered_ipo_list_{today_str}.csv"
            filtered_filepath = os.path.join(Config.DATA_FOLDER, filtered_filename)
            filtered_df.to_csv(filtered_filepath, index=False)

            return render_template(
                "results.html",
                data=filtered_df.to_dict("records"),
                filename=filtered_filename,
                filter_params=filter_params,
            )
        else:
            # GETリクエストの場合はフィルタリングフォームを表示
            return render_template("filter.html")

    except Exception as e:
        flash(f"フィルタリング中にエラーが発生しました: {str(e)}", "danger")
        return redirect(url_for("main.index"))


@main_bp.route("/results")
def results():
    """フィルタリング結果の表示"""
    try:
        # 最新のフィルタリング結果ファイルを探す
        data_files = [
            f
            for f in os.listdir(Config.DATA_FOLDER)
            if f.startswith("filtered_ipo_list_")
        ]
        if not data_files:
            flash("フィルタリング結果が見つかりません。", "warning")
            return redirect(url_for("main.filter_data"))

        # 最新のファイルを取得
        latest_file = sorted(data_files)[-1]
        filepath = os.path.join(Config.DATA_FOLDER, latest_file)

        # CSVを読み込む
        filtered_df = pd.read_csv(filepath)

        return render_template(
            "results.html", data=filtered_df.to_dict("records"), filename=latest_file
        )

    except Exception as e:
        flash(f"結果の表示中にエラーが発生しました: {str(e)}", "danger")
        return redirect(url_for("main.index"))


@main_bp.route("/download/<filename>")
def download_file(filename):
    """フィルタリング結果のCSVダウンロード"""
    try:
        filepath = os.path.join(Config.DATA_FOLDER, filename)
        return send_file(filepath, as_attachment=True)

    except Exception as e:
        flash(f"ファイルのダウンロード中にエラーが発生しました: {str(e)}", "danger")
        return redirect(url_for("main.results"))


@main_bp.route("/api/ipo-data")
def api_ipo_data():
    """IPOデータのJSON API"""
    try:
        if not os.path.exists(Config.IPO_LIST_FILE):
            return jsonify({"error": "データが見つかりません"}), 404

        ipo_df = pd.read_csv(Config.IPO_LIST_FILE)
        return jsonify(ipo_df.to_dict("records"))

    except Exception as e:
        return jsonify({"error": str(e)}), 500
