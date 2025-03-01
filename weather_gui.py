import tkinter as tk
import requests
from deep_translator import GoogleTranslator
from PIL import Image, ImageTk
import io

API_KEY = "699606031de6a2c3b0c9934019844d8b"

def translate_city_name(city_jp):
    """日本語の都市名を英語に翻訳"""
    return GoogleTranslator(source="ja", target="en").translate(city_jp)

def get_weather():
    city_jp = city_entry.get()
    city = translate_city_name(city_jp)
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric&lang=ja"
    response = requests.get(url)
    data = response.json()

    if response.status_code == 200:
        # 天気の詳細情報を取得
        weather_description = data['weather'][0]['description']
        temp = data['main']['temp']
        humidity = data['main']['humidity']
        wind_speed = data['wind']['speed']
        
        # 天気アイコンを取得して表示
        icon_code = data['weather'][0]['icon']
        icon_url = f"http://openweathermap.org/img/wn/{icon_code}@2x.png"
        icon_response = requests.get(icon_url)
        icon_image_data = icon_response.content
        icon_image = Image.open(io.BytesIO(icon_image_data))
        icon_photo = ImageTk.PhotoImage(icon_image)

        # 各ラベルの更新
        weather_label.config(text=f"天気: {weather_description}")
        temp_label.config(text=f"気温: {temp}°C")
        humidity_label.config(text=f"湿度: {humidity}%")
        wind_label.config(text=f"風速: {wind_speed} m/s")
        icon_label.config(image=icon_photo)
        icon_label.image = icon_photo  # 参照を保持
    else:
        weather_label.config(text="データ取得に失敗しました")
        temp_label.config(text="")
        humidity_label.config(text="")
        wind_label.config(text="")
        icon_label.config(image="")

# ウィンドウの作成
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

humidity_label = tk.Label(root, text="")
humidity_label.pack()

wind_label = tk.Label(root, text="")
wind_label.pack()

icon_label = tk.Label(root)
icon_label.pack()

root.mainloop()
