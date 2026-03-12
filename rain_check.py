import os
import requests

def get_weather(api_key: str, city: str) -> dict:
    """OpenWeatherMap APIから今日の天気を取得"""
    url = "https://api.openweathermap.org/data/2.5/forecast"
    params = {
        "q": city,
        "appid": api_key,
        "units": "metric",
        "lang": "ja",
        "cnt": 4,  # 今日の最初の12時間分（3時間ごと×4）
    }
    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json()

def will_it_rain(weather_data: dict) -> tuple[bool, list[str]]:
    """今日の天気データから雨が降るか判定"""
    rain_times = []
    for item in weather_data["list"]:
        weather_id = item["weather"][0]["id"]
        description = item["weather"][0]["description"]
        # 天気コード 200-699 が降水（雨・雪・嵐など）
        if 200 <= weather_id < 700:
            dt_txt = item["dt_txt"]
            rain_times.append(f"{dt_txt} - {description}")
    return len(rain_times) > 0, rain_times

def send_discord_notification(webhook_url: str, message: str) -> None:
    """Discordに通知を送信"""
    payload = {"content": message}
    response = requests.post(webhook_url, json=payload)
    response.raise_for_status()
    print("Discord通知を送信しました")

def main():
    api_key = os.environ.get("OPENWEATHER_API_KEY")
    webhook_url = os.environ.get("DISCORD_WEBHOOK_URL")
    city = os.environ.get("CITY", "Tokyo")

    if not api_key or not webhook_url:
        raise ValueError("OPENWEATHER_API_KEY と DISCORD_WEBHOOK_URL を設定してください")

    print(f"{city} の天気を確認中...")
    weather_data = get_weather(api_key, city)

    is_rainy, rain_details = will_it_rain(weather_data)

    if is_rainy:
        message = "☔ **本日は雨が降る予定です。傘を忘れずに！**"
        print("雨の予報あり → Discord通知を送信します")
        send_discord_notification(webhook_url, message)
    else:
        print("雨の予報なし → 通知しません")

if __name__ == "__main__":
    main()
