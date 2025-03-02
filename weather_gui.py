import tkinter as tk
import requests
from PIL import Image, ImageTk
from io import BytesIO
from deep_translator import GoogleTranslator

API_KEY = "699606031de6a2c3b0c9934019844d8b"

# Icons8 のオンラインアイコン URL マッピング
icon_url_mapping = {
    'Clear': 'https://img.icons8.com/color/96/000000/sun.png',
    'Clouds': 'https://img.icons8.com/color/96/000000/cloud.png',
    'Rain': 'https://img.icons8.com/color/96/000000/rain.png',
    'Drizzle': 'https://img.icons8.com/color/96/000000/light-rain.png',
    'Thunderstorm': 'https://img.icons8.com/color/96/000000/storm.png',
    'Snow': 'https://img.icons8.com/color/96/000000/snow.png',
    'Mist': 'https://img.icons8.com/color/96/000000/fog.png',
}

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
        weather_main = data['weather'][0]['main']
        weather_description = data['weather'][0]['description']
        temp = data['main']['temp']
        humidity = data['main']['humidity']
        wind_speed = data['wind']['speed']

        # 天気アイコンを取得
        icon_url = icon_url_mapping.get(weather_main)
        if icon_url:
            icon_response = requests.get(icon_url)
            icon_data = icon_response.content
            icon_image = Image.open(BytesIO(icon_data))
            icon_photo = ImageTk.PhotoImage(icon_image)
            icon_label.config(image=icon_photo)
            icon_label.image = icon_photo  # 参照を保持
        else:
            icon_label.config(image="")

        # 天気情報の更新
        weather_label.config(text=f"天気: {weather_description}")
        temp_value_label.config(text=f"{temp}°C")
        humidity_value_label.config(text=f"{humidity}%")
        wind_value_label.config(text=f"{wind_speed} m/s")
    else:
        weather_label.config(text="データ取得に失敗しました")
        temp_value_label.config(text="")
        humidity_value_label.config(text="")
        wind_value_label.config(text="")
        icon_label.config(image="")

# Tkinter ウィンドウ作成
root = tk.Tk()
root.title("天気アプリ")

# 都市入力エリア
input_frame = tk.Frame(root)
input_frame.pack(pady=10)

tk.Label(input_frame, text="都市名を入力（例: 東京, 大阪, 札幌）:").pack(side=tk.LEFT)
city_entry = tk.Entry(input_frame, width=20)
city_entry.pack(side=tk.LEFT, padx=5)
tk.Button(input_frame, text="天気を取得", command=get_weather).pack(side=tk.LEFT)

# 天気アイコン表示
icon_label = tk.Label(root)
icon_label.pack(pady=5)

# 天気情報表示
weather_label = tk.Label(root, text="", font=("Arial", 14, "bold"))
weather_label.pack()

# 天気データ表示用のフレーム（枠で囲む）
info_frame = tk.LabelFrame(root, text="天気情報", padx=10, pady=10, font=("Arial", 12, "bold"))
info_frame.pack(pady=10)

# 気温・湿度・風速を横に並べる
temp_frame = tk.Frame(info_frame)
temp_frame.pack(pady=5)

tk.Label(temp_frame, text="気温", font=("Arial", 12, "bold"), width=10, relief="ridge").grid(row=0, column=0, padx=5)
tk.Label(temp_frame, text="湿度", font=("Arial", 12, "bold"), width=10, relief="ridge").grid(row=0, column=1, padx=5)
tk.Label(temp_frame, text="風速", font=("Arial", 12, "bold"), width=10, relief="ridge").grid(row=0, column=2, padx=5)

temp_value_label = tk.Label(temp_frame, text="-- °C", font=("Arial", 12), width=10, relief="solid")
temp_value_label.grid(row=1, column=0, padx=5)

humidity_value_label = tk.Label(temp_frame, text="-- %", font=("Arial", 12), width=10, relief="solid")
humidity_value_label.grid(row=1, column=1, padx=5)

wind_value_label = tk.Label(temp_frame, text="-- m/s", font=("Arial", 12), width=10, relief="solid")
wind_value_label.grid(row=1, column=2, padx=5)

# メインループ
root.mainloop()
