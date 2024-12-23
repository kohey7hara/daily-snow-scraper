from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import time
from datetime import datetime
from selenium.webdriver.chrome.options import Options

def get_snow_info():
    # Chromeのオプション設定
    options = Options()
    options.add_argument("--headless")  # ヘッドレスモードで実行
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")

    # WebDriverのセットアップ
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)

    try:
        # 対象ページリストを定義
        urls = [f"https://surfsnow.jp/search/list/spl_snow.php?areacdl=3&page={i}" for i in range(1, 9)]

        # 統合データを保存するリスト
        combined_data = []
        snow_headers = []
        weather_headers = []

        for url in urls:
            print(f"アクセス中: {url}")
            driver.get(url)
            time.sleep(5)

            ski_resorts = driver.find_elements(By.CSS_SELECTOR, "div.list_result")

            for ski_resort in ski_resorts:  # ページ内のすべてのスキー場
                resort_name = ski_resort.find_element(By.CSS_SELECTOR, "h2 a").text.strip()
                print(f"スキー場名: {resort_name}")

                # ===== 積雪情報テーブル =====
                try:
                    snow_table = ski_resort.find_elements(By.CSS_SELECTOR, "table.section_weather")[0]
                    snow_rows = snow_table.find_elements(By.TAG_NAME, "tr")

                    if snow_rows:
                        # ヘッダー（積雪日付）を取得
                        snow_headers = [col.text.strip() for col in snow_rows[0].find_elements(By.TAG_NAME, "th")][1:]

                        for row in snow_rows[1:]:
                            item = row.find_element(By.TAG_NAME, "th").text.strip()
                            values = [cell.text.strip() for cell in row.find_elements(By.TAG_NAME, "td")]
                            combined_data.append([resort_name, item] + values)
                except Exception as e:
                    print(f"積雪情報取得エラー: {e}")

                # ===== 天気情報テーブル =====
                try:
                    weather_table = ski_resort.find_elements(By.CSS_SELECTOR, "table.section_weather")[1]
                    weather_rows = weather_table.find_elements(By.TAG_NAME, "tr")

                    if weather_rows:
                        # ヘッダー（天気日付）を取得
                        weather_headers = [col.text.strip() for col in weather_rows[0].find_elements(By.TAG_NAME, "th")][1:]

                        # 天気情報の前に日付行を追加
                        combined_data.append([resort_name, "日付"] + weather_headers)

                        for row in weather_rows[1:]:
                            item = row.find_element(By.TAG_NAME, "th").text.strip()
                            values = [cell.text.strip() for cell in row.find_elements(By.TAG_NAME, "td")]
                            combined_data.append([resort_name, item] + values)
                except Exception as e:
                    print(f"天気情報取得エラー: {e}")

        # ===== データフレーム作成 =====
        all_headers = ["スキー場名", "項目"] + (snow_headers if snow_headers else weather_headers)  # ヘッダーを適切に設定
        combined_df = pd.DataFrame(combined_data, columns=all_headers)

        print(combined_df)

        # ファイル名に日付を追加
        current_date = datetime.now().strftime("%Y%m%d")  # yyyymmdd形式
        file_name = f"{current_date}_snow_info.csv"

        # CSV出力
        combined_df.to_csv(file_name, index=False, encoding="utf-8-sig")
        print(f"データをファイルに保存しました: {file_name}")

    finally:
        driver.quit()

if __name__ == "__main__":
    get_snow_info()
