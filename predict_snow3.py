import pandas as pd
from datetime import datetime, timedelta

def predict_weather():
    # 本日の日付を取得（ファイル名から取得）
    today = datetime.now().strftime("%Y%m%d")
    input_file_name = f"{today}_snow_info_data.csv"  # 修正: 正しいファイル名
    output_file_name = f"{today}_weather_info.csv"

    try:
        # yyyymmdd_snow_info_data.csv を読み込む
        df = pd.read_csv(input_file_name, encoding="utf-8-sig")

        # 日付列を抽出（曜日部分を除去して正しいフォーマットに）
        date_columns = [col for col in df.columns if "/" in col]
        original_date_columns = date_columns  # 元の日付列を保持
        date_columns = [
            datetime.strptime(col.split("(")[0].strip(), "%m/%d").strftime("%m/%d")
            for col in date_columns
        ]

        # 本日から7日間の列を作成
        start_date = datetime.strptime(today, "%Y%m%d")
        new_date_columns = [(start_date + timedelta(days=i)).strftime("%m/%d") for i in range(7)]

        # 天気データのみを抽出
        result_df = df[df["項目"] == "天気"].copy()

        # 元の日付列と新しい日付列を対応付け
        date_mapping = dict(zip(original_date_columns, new_date_columns))

        # 日付列の名称を変更
        result_df.rename(columns=date_mapping, inplace=True)

        # 天気を絵文字に変換する関数
        def weather_to_emoji(weather):
            emoji = ""
            if "晴れ" in weather:
                emoji += "☀️"
            if "曇り" in weather:
                emoji += "☁️"
            if "雪" in weather:
                emoji += "❄️"
            return emoji or weather  # 該当なしの場合は元の文字列を返す

        # 改行前までの文字を抽出して絵文字に変換
        for col in new_date_columns:
            if col in result_df.columns:
                result_df.loc[:, col] = result_df[col].str.split("\n").str[0].apply(weather_to_emoji)

        # 必要な列だけを抽出（スキー場名 + 新しい日付列）
        weather_data = result_df[["スキー場名"] + new_date_columns]

        # 結果をCSVに保存
        weather_data.to_csv(output_file_name, index=False, encoding="utf-8-sig")
        print(f"結果を {output_file_name} に保存しました。")

    except FileNotFoundError:
        print(f"ファイルが見つかりません: {input_file_name}")
    except Exception as e:
        print(f"エラーが発生しました: {e}")

if __name__ == "__main__":
    predict_weather()
