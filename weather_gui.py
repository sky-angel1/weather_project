import tkinter as tk
import requests
from PIL import Image, ImageTk
from io import BytesIO
from deep_translator import GoogleTranslator
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.font_manager as fm

API_KEY = "699606031de6a2c3b0c9934019844d8b"

# フォント設定（Windowsの場合はMS Gothic、Mac/LinuxはIPAexGothic）
plt.rcParams["font.family"] = "MS Gothic"  

# よく使う都市リスト
city_options = ["東京", "大阪", "札幌", "福岡", "名古屋", "京都", "広島"]

# Icons8のアイコンURLマッピング
icon_url_mapping = {
    'Clear': 'https://img.icons8.com/color/96/000000/sun.png',
    'Clouds': 'https://img.icons8.com/color/96/000000/cloud.png',
    'Rain': 'https://img.icons8.com/color/96/000000/rain.png',
    'Drizzle': 'https://img.icons8.com/color/96/000000/light-rain.png',
    'Thunderstorm': 'https://img.icons8.com/color/96/000000/storm.png',
    'Snow': 'https://img.icons8.com/color/96/000000/snow.png',
    'Mist': 'https://img.icons8.com/color/96/000000/fog.png',
}

weather_history = []

def translate_city_name(city_jp):
    """日本語の都市名を英語に翻訳"""
    return GoogleTranslator(source="ja", target="en").translate(city_jp)

def get_weather():
    """天気データを取得・表示 & 履歴管理"""
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
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # アイコン取得 & 2/3サイズに縮小
        icon_url = icon_url_mapping.get(weather_main)
        if icon_url:
            icon_response = requests.get(icon_url)
            icon_data = icon_response.content
            icon_image = Image.open(BytesIO(icon_data)).resize((64, 64))  # 2/3サイズ
            icon_photo = ImageTk.PhotoImage(icon_image)
            icon_label.config(image=icon_photo)
            icon_label.image = icon_photo  
        else:
            icon_label.config(image="")

        # 天気情報の更新
        weather_label.config(text=f"天気: {weather_description}")
        temp_value_label.config(text=f"{temp}°C")
        humidity_value_label.config(text=f"{humidity}%")
        wind_value_label.config(text=f"{wind_speed} m/s")
        time_label.config(text=f"情報取得時間: {current_time}")

        # 履歴更新
        if len(weather_history) >= 5:
            weather_history.pop(0)  
        weather_history.append((current_time, temp, humidity, wind_speed))

        # グラフ更新
        update_graph()

    else:
        weather_label.config(text="データ取得に失敗しました")

    # 15分後に再更新
    root.after(900000, get_weather)

def update_graph():
    """天気履歴をグラフで表示"""
    times = [entry[0][-5:] for entry in weather_history]  # hh:mm
    temps = [entry[1] for entry in weather_history]
    humidities = [entry[2] for entry in weather_history]
    winds = [entry[3] for entry in weather_history]

    ax.clear()
    ax.plot(times, temps, marker='o', label="気温 (°C)", color="red")
    ax.plot(times, humidities, marker='s', label="湿度 (%)", color="blue")
    ax.plot(times, winds, marker='^', label="風速 (m/s)", color="green")

    ax.set_title("天気履歴", fontsize=10)
    ax.set_xlabel("時間", fontsize=8)
    ax.legend(fontsize=8)
    canvas.draw()

def close_app():
    """アプリを正しく終了"""
    root.quit()  # メインループを終了
    root.destroy()  # ウィンドウを閉じる

def start_move(event):
    """ウィンドウ移動開始"""
    root.x = event.x
    root.y = event.y

def move_window(event):
    """ウィンドウをドラッグで移動"""
    x = root.winfo_pointerx() - root.x
    y = root.winfo_pointery() - root.y
    root.geometry(f"+{x}+{y}")

# Tkinter ウィンドウ作成
root = tk.Tk()
root.title("天気ガジェット")
root.geometry("400x450")
root.configure(bg="#f0f8ff")
root.overrideredirect(True)  

# ウィンドウ移動のためのバインド
root.bind("<ButtonPress-1>", start_move)
root.bind("<B1-Motion>", move_window)

# 閉じるボタン
close_button = tk.Button(root, text="✖", command=close_app, font=("Arial", 10, "bold"), bg="red", fg="white")
close_button.place(x=370, y=5, width=25, height=25)

# 都市選択
city_var = tk.StringVar(value=city_options[0])
tk.OptionMenu(root, city_var, *city_options).pack(pady=5)

# 天気取得ボタン
tk.Button(root, text="天気を取得", command=get_weather, font=("Arial", 10, "bold"),
          bg="#ff4d4d", fg="white", relief="raised", padx=10, pady=5).pack(pady=5)

# アイコン表示
icon_label = tk.Label(root)
icon_label.pack(pady=5)

# 天気情報
weather_label = tk.Label(root, text="", font=("Arial", 14, "bold"), bg="#f0f8ff")
weather_label.pack()

# 取得時間表示
time_label = tk.Label(root, text="情報取得時間: --", font=("Arial", 10), bg="#f0f8ff")
time_label.pack()

# データ枠
info_frame = tk.LabelFrame(root, text="天気情報", padx=10, pady=10, font=("Arial", 12, "bold"))
info_frame.pack(pady=5, fill="both", expand=True)

temp_frame = tk.Frame(info_frame)
temp_frame.pack()

temp_value_label = tk.Label(temp_frame, text="-- °C", font=("Arial", 12), width=10, relief="solid")
humidity_value_label = tk.Label(temp_frame, text="-- %", font=("Arial", 12), width=10, relief="solid")
wind_value_label = tk.Label(temp_frame, text="-- m/s", font=("Arial", 12), width=10, relief="solid")

temp_value_label.grid(row=1, column=0, padx=5)
humidity_value_label.grid(row=1, column=1, padx=5)
wind_value_label.grid(row=1, column=2, padx=5)

# グラフ表示
fig, ax = plt.subplots(figsize=(4, 2))
canvas = FigureCanvasTkAgg(fig, master=root)
canvas.get_tk_widget().pack()

get_weather()
root.mainloop()
