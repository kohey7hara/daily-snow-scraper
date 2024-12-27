import pandas as pd
from datetime import datetime, timedelta

def predict_weather_and_snow():
    # 本日の日付を取得（ファイル名から取得）
    today = datetime.now().strftime("%Y%m%d")
    input_file_name = f"{today}_snow_info_data.csv"
    output_file_name = f"{today}_weather_and_snow_info.csv"
    snow_park_list_file = "snow_park_list2.csv"  # スキー場リストファイル

    try:
        # 必要なCSVファイルを読み込む
        df = pd.read_csv(input_file_name, encoding="utf-8-sig")
        snow_park_list = pd.read_csv(snow_park_list_file, encoding="utf-8-sig")

        # スキー場リストにあるスキー場のみを対象にする
        target_parks = snow_park_list["スキー場名"].tolist()
        df = df[df["スキー場名"].isin(target_parks)]

        # 日付列を抽出（曜日部分を除去して正しいフォーマットに）
        date_columns = [col for col in df.columns if "/" in col]
        original_date_columns = date_columns
        date_columns = [
            datetime.strptime(col.split("(")[0].strip(), "%m/%d").strftime("%m/%d")
            for col in date_columns
        ]

        # 本日から7日間の列を作成
        start_date = datetime.strptime(today, "%Y%m%d")
        new_date_columns = [(start_date + timedelta(days=i)).strftime("%m/%d") for i in range(7)]

        # 天気データと積雪データを抽出
        weather_df = df[df["項目"] == "天気"].copy()
        snow_df = df[df["項目"] == "積雪深(平均)"].copy()

        # 日付列の対応付け
        date_mapping = dict(zip(original_date_columns, new_date_columns))
        weather_df.rename(columns=date_mapping, inplace=True)
        snow_df.rename(columns=date_mapping, inplace=True)

        # 天気を絵文字に変換する関数
        def weather_to_emoji(weather):
            emoji = ""
            if "晴れ" in weather:
                emoji += "☀️"
            if "曇り" in weather:
                emoji += "☁️"
            if "雪" in weather:
                emoji += "❄️"
            if "雨" in weather:
                emoji += "☂"
            return emoji or weather

        # 天気と積雪深を統合する
        result_data = []
        for _, row in weather_df.iterrows():
            ski_resort = row["スキー場名"]
            if ski_resort == "星野リゾート ネコマ マウンテン(旧アルツ磐梯＆猫魔スキー場）":
                ski_resort = "ネコママウンテン"
            snow_row = snow_df[snow_df["スキー場名"] == ski_resort]
            combined_row = {"スキー場名": ski_resort}
            for i, col in enumerate(new_date_columns):
                if col in weather_df.columns:
                    weather = row[col].split("\n")[0] if pd.notna(row[col]) else ""
                    if i == 0:
                        snow = (
                            snow_row[col].values[0] if not snow_row.empty and col in snow_row.columns else "0"
                        )
                        combined_row[col] = f"{weather_to_emoji(weather)}({snow}cm)"
                    else:
                        combined_row[col] = weather_to_emoji(weather)
            result_data.append(combined_row)

        # 結果をデータフレーム化
        result_df = pd.DataFrame(result_data)

        # 必要な列だけを抽出（スキー場名 + 新しい日付列）
        final_columns = ["スキー場名"] + new_date_columns
        result_df = result_df[final_columns]

        # 結果をCSVに保存
        result_df.to_csv(output_file_name, index=False, encoding="utf-8-sig")
        print(f"結果を {output_file_name} に保存しました。")

    except FileNotFoundError as e:
        print(f"ファイルが見つかりません: {e}")
    except Exception as e:
        print(f"エラーが発生しました: {e}")

if __name__ == "__main__":
    predict_weather_and_snow()
