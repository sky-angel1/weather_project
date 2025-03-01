# Description: 天気予報を取得するGUIアプリケーション
import tkinter as tk
import requests
from deep_translator import GoogleTranslator

API_KEY = "699606031de6a2c3b0c9934019844d8b"

def translate_city_name(city_jp):
    """日本語の都市名を英語に翻訳"""
    return GoogleTranslator(source="ja", target="en").translate(city_jp)

def get_weather():
    city_jp = city_entry.get()
    city = translate_city_name(city_jp)  # 日本語の都市名を英語に翻訳

    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric&lang=ja"
    response = requests.get(url)
    data = response.json()

    if response.status_code == 200:
        weather_label.config(text=f"天気: {data['weather'][0]['description']}")
        temp_label.config(text=f"気温: {data['main']['temp']}°C")
    else:
        weather_label.config(text="データ取得に失敗しました")
        temp_label.config(text="")

# ウィンドウ作成
root = tk.Tk()
root.title("天気アプリ")

tk.Label(root, text="都市名を入力（例: 東京, 大阪, 札幌）:").pack()
city_entry = tk.Entry(root)
city_entry.pack()

tk.Button(root, text="天気を取得", command=get_weather).pack()

weather_label = tk.Label(root, text="")
weather_label.pack()

temp_label = tk.Label(root, text="")
temp_label.pack()

root.mainloop()
