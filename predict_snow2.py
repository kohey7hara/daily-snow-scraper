import pandas as pd
from datetime import datetime

def predict_weather():
    # 本日の日付を取得
    today = datetime.now().strftime("%Y%m%d")
    input_file_name = f"{today}_snow_info_data.csv"  # 修正: 正しいファイル名
    output_file_name = f"{today}_weather_info.csv"

    try:
        # yyyymmdd_snow_info_data.csv を読み込む
        df = pd.read_csv(input_file_name, encoding="utf-8-sig")

        # 日付列を抽出し、本日から2日後の日付を取得
        date_columns = [col for col in df.columns if "日付" in col or "/" in col]
        if len(date_columns) < 3:
            raise ValueError("日付列が不足しています。少なくとも3列の天気情報が必要です。")
        two_days_after_date = date_columns[2]

        # 2日後の天気情報を取得
        result_df = df[(df["項目"] == "天気") & (df[two_days_after_date].str.contains("晴れ", na=False))]

        # 「項目」列を削除して必要な列のみを抽出
        result_df = result_df[["スキー場名", two_days_after_date]].rename(
            columns={two_days_after_date: "2日後の天気"}
        )

        # 結果をCSVに保存
        result_df.to_csv(output_file_name, index=False, encoding="utf-8-sig")
        print(f"結果を {output_file_name} に保存しました。")

    except FileNotFoundError:
        print(f"ファイルが見つかりません: {input_file_name}")
    except Exception as e:
        print(f"エラーが発生しました: {e}")

if __name__ == "__main__":
    predict_weather()
