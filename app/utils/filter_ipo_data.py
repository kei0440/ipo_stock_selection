import pandas as pd


def clean_and_filter_ipo_data(df, filter_params=None):
    """
    IPOデータをフィルタリングする関数

    Parameters:
    -----------
    df : pandas.DataFrame
        フィルタリング対象のDataFrame
    filter_params : dict, optional
        フィルタリングパラメータ。指定がない場合はデフォルト値を使用
        {
            'growth_flag': True,
            'per_max': 15,
            'dividend_yield_min': 3
        }

    Returns:
    --------
    pandas.DataFrame
        フィルタリング後のDataFrame
    """
    # デフォルトのフィルタリングパラメータ
    default_params = {"growth_flag": True, "per_max": 15, "dividend_yield_min": 3}

    # パラメータが指定されていない場合はデフォルト値を使用
    if filter_params is None:
        filter_params = default_params
    else:
        # 指定されていないパラメータにはデフォルト値を使用
        for key, value in default_params.items():
            if key not in filter_params:
                filter_params[key] = value

    # フィルタリング条件の構築
    conditions = []

    if filter_params["growth_flag"]:
        conditions.append(df["growth_flag"] == True)

    if filter_params["per_max"] is not None:
        conditions.append(df["PER"] <= filter_params["per_max"])

    if filter_params["dividend_yield_min"] is not None:
        conditions.append(df["dividend_yield"] >= filter_params["dividend_yield_min"])

    # 条件がない場合は元のDataFrameを返す
    if not conditions:
        return df

    # 条件を組み合わせてフィルタリング
    filtered_df = df
    for condition in conditions:
        filtered_df = filtered_df[condition]

    return filtered_df
