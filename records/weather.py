"""天気 API（OpenWeatherMap）の呼び出しはこのファイルだけで行う。"""
import requests
from django.conf import settings

API_URL = "https://api.openweathermap.org/data/2.5/weather"

# OpenWeatherMap の main を、画面で使う 3 グループに畳む
WEATHER_GROUPS = {
    "Clear": "clear",
    "Clouds": "cloud", "Mist": "cloud", "Fog": "cloud", "Haze": "cloud",
    "Smoke": "cloud", "Dust": "cloud", "Sand": "cloud", "Ash": "cloud",
    "Squall": "cloud", "Tornado": "cloud",
    "Rain": "rain", "Drizzle": "rain", "Snow": "rain", "Thunderstorm": "rain",
}

GROUP_LABELS = {"clear": "晴れ", "cloud": "くもり", "rain": "雨", "none": "天気なし"}


def fetch_weather(city):
    """city の現在の天気を取得して dict で返す。失敗したら None。

    タイムアウト・HTTP エラー・想定外のレスポンス・API キー未設定のいずれも
    None にまとめる（呼び出し側は「天気なし」として扱う）。
    """
    if not settings.OPENWEATHER_API_KEY:
        return None

    try:
        response = requests.get(
            API_URL,
            params={
                "q": city,
                "appid": settings.OPENWEATHER_API_KEY,
                "units": "metric",
                "lang": "ja",
            },
            timeout=5,
        )
        response.raise_for_status()
        data = response.json()
        weather = data["weather"][0]
        return {
            "main": weather["main"],
            "description": weather["description"],
            "icon": weather["icon"],
            "temp": round(data["main"]["temp"], 1),
            "humidity": int(data["main"]["humidity"]),
            "wind_speed": round(data["wind"]["speed"], 1),
        }
    except (requests.RequestException, ValueError, KeyError, IndexError, TypeError):
        return None
