import tkinter as tk
import requests
from PIL import Image, ImageTk
from io import BytesIO
from deep_translator import GoogleTranslator

API_KEY = "699606031de6a2c3b0c9934019844d8b"

# よく使う都市リスト
city_options = ["東京", "大阪", "札幌", "福岡", "名古屋", "京都", "広島"]

# アイコンURLマッピング（Icons8）
icon_url_mapping = {
    'Clear': 'https://img.icons8.com/color/96/000000/sun.png',
    'Clouds': 'https://img.icons8.com/color/96/000000/cloud.png',
    'Rain': 'https://img.icons8.com/color/96/000000/rain.png',
    'Drizzle': 'https://img.icons8.com/color/96/000000/light-rain.png',
    'Thunderstorm': 'https://img.icons8.com/color/96/000000/storm.png',
    'Snow': 'https://img.icons8.com/color/96/000000/snow.png',
    'Mist': 'https://img.icons8.com/color/96/000000/fog.png',
}

# 過去の天気データ履歴
weather_history = []

def translate_city_name(city_jp):
    """日本語の都市名を英語に翻訳"""
    return GoogleTranslator(source="ja", target="en").translate(city_jp)

def get_weather():
    """天気データを取得して表示 & 履歴を管理"""
    city_jp = city_var.get()
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

        # アイコン取得
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

        # 履歴更新
        if len(weather_history) >= 5:
            weather_history.pop(0)  # 古いデータを削除
        weather_history.append(f"{temp}°C | {humidity}% | {wind_speed}m/s")

        # 履歴表示
        history_text.set("\n".join(weather_history[::-1]))  # 最新を上に

    else:
        weather_label.config(text="データ取得に失敗しました")

    # 15分後に再更新（900000ミリ秒 = 15分）
    root.after(900000, get_weather)

def move_window(event):
    """ウィンドウをドラッグで移動"""
    root.geometry(f"+{event.x_root}+{event.y_root}")

# Tkinter ウィンドウ作成
root = tk.Tk()
root.title("天気ガジェット")
root.geometry("350x300")  # 小さめのウィンドウ
root.configure(bg="lightblue")  # 背景色
root.overrideredirect(True)  # タイトルバーを非表示

# ウィンドウ移動用
root.bind("<B1-Motion>", move_window)

# ======= UI要素 =======
# 都市選択（ドロップダウン & 手入力可能）
city_var = tk.StringVar(value=city_options[0])
city_dropdown = tk.OptionMenu(root, city_var, *city_options)
city_dropdown.pack(pady=5)

# 手入力用エントリー
city_entry = tk.Entry(root, textvariable=city_var, width=15)
city_entry.pack()

# 更新ボタン
tk.Button(root, text="天気を取得", command=get_weather).pack(pady=5)

# 天気アイコン
icon_label = tk.Label(root)
icon_label.pack(pady=5)

# 天気ラベル
weather_label = tk.Label(root, text="", font=("Arial", 14, "bold"), bg="lightblue")
weather_label.pack()

# データ枠
info_frame = tk.LabelFrame(root, text="天気情報", padx=10, pady=10, font=("Arial", 12, "bold"), bg="lightblue", highlightbackground="black", highlightthickness=1)
info_frame.pack(pady=5)

# 横並びのデータ
temp_frame = tk.Frame(info_frame, bg="lightblue")
temp_frame.pack()

tk.Label(temp_frame, text="気温", font=("Arial", 12, "bold"), width=10).grid(row=0, column=0, padx=5)
tk.Label(temp_frame, text="湿度", font=("Arial", 12, "bold"), width=10).grid(row=0, column=1, padx=5)
tk.Label(temp_frame, text="風速", font=("Arial", 12, "bold"), width=10).grid(row=0, column=2, padx=5)

temp_value_label = tk.Label(temp_frame, text="-- °C", font=("Arial", 12), width=10)
temp_value_label.grid(row=1, column=0, padx=5)

humidity_value_label = tk.Label(temp_frame, text="-- %", font=("Arial", 12), width=10)
humidity_value_label.grid(row=1, column=1, padx=5)

wind_value_label = tk.Label(temp_frame, text="-- m/s", font=("Arial", 12), width=10)
wind_value_label.grid(row=1, column=2, padx=5)

# 履歴表示
history_text = tk.StringVar()
history_label = tk.Label(root, textvariable=history_text, font=("Arial", 10), bg="lightblue", justify="left")
history_label.pack(pady=5)

# 初回の天気取得
get_weather()

# メインループ
root.mainloop()
