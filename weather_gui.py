import tkinter as tk
import requests
from PIL import Image, ImageTk
from io import BytesIO
from deep_translator import GoogleTranslator
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# 日本語表示用フォント設定（Windowsの場合はMS Gothic）
plt.rcParams["font.family"] = "MS Gothic"

API_KEY = "699606031de6a2c3b0c9934019844d8b"

# 初期都市リスト
city_options = ["東京", "大阪", "札幌", "福岡", "名古屋", "京都", "広島"]

# Icons8 のアイコンURLマッピング
icon_url_mapping = {
    'Clear': 'https://img.icons8.com/color/96/000000/sun.png',
    'Clouds': 'https://img.icons8.com/color/96/000000/cloud.png',
    'Rain': 'https://img.icons8.com/color/96/000000/rain.png',
    'Drizzle': 'https://img.icons8.com/color/96/000000/light-rain.png',
    'Thunderstorm': 'https://img.icons8.com/color/96/000000/storm.png',
    'Snow': 'https://img.icons8.com/color/96/000000/snow.png',
    'Mist': 'https://img.icons8.com/color/96/000000/fog.png',
}

# 履歴（最大5件）を保存するリスト
weather_history = []

def translate_city_name(city_jp):
    return GoogleTranslator(source="ja", target="en").translate(city_jp)

def get_weather():
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
        
        # 天気アイコン取得＆2/3サイズ（96px→64px）に縮小
        icon_url = icon_url_mapping.get(weather_main)
        if icon_url:
            icon_response = requests.get(icon_url)
            icon_data = icon_response.content
            icon_image = Image.open(BytesIO(icon_data)).resize((64,64))
            icon_photo = ImageTk.PhotoImage(icon_image)
            icon_label.config(image=icon_photo)
            icon_label.image = icon_photo
        else:
            icon_label.config(image="")
        
        # 天気情報更新
        weather_label.config(text=f"天気: {weather_description}")
        temp_value_label.config(text=f"{temp}°C")
        humidity_value_label.config(text=f"{humidity}%")
        wind_value_label.config(text=f"{wind_speed} m/s")
        time_label.config(text=f"情報取得時間: {current_time}")
        
        # 履歴更新（最大5件）
        if len(weather_history) >= 5:
            weather_history.pop(0)
        weather_history.append((current_time, temp, humidity, wind_speed))
        
        update_graph()
    else:
        weather_label.config(text="データ取得に失敗しました")
    
    # 15分後に全体をリフレッシュして自動更新
    root.after(900000, refresh_all)

def refresh_all():
    get_weather()

def update_graph():
    """選択されたグラフのみ表示。左右と下側の余白も調整"""
    # 横軸の時間表示： "HH:MM" を "HH時MM分" に変換
    times = [entry[0][11:16].replace(":", "時") + "分" for entry in weather_history]
    ax.clear()
    selection = graph_choice.get()
    if selection == "temperature":
        temps = [entry[1] for entry in weather_history]
        ax.plot(times, temps, marker='o', label="気温 (°C)", color="red")
        ax.set_ylabel("気温 (°C)", fontsize=8)
    elif selection == "humidity":
        humidities = [entry[2] for entry in weather_history]
        ax.plot(times, humidities, marker='s', label="湿度 (%)", color="blue")
        ax.set_ylabel("湿度 (%)", fontsize=8)
    elif selection == "wind":
        winds = [entry[3] for entry in weather_history]
        ax.plot(times, winds, marker='^', label="風速 (m/s)", color="green")
        ax.set_ylabel("風速 (m/s)", fontsize=8)
    ax.set_title("天気履歴", fontsize=10)
    ax.set_xlabel("時間", fontsize=8)
    ax.legend(fontsize=8)
    # 左右と下側の余白調整（左右は0.2～0.95、下は0.35）
    fig.subplots_adjust(left=0.2, right=0.95, bottom=0.35)
    canvas.draw()

def close_app():
    root.quit()
    root.destroy()

def start_move(event):
    root.x = event.x
    root.y = event.y

def move_window(event):
    x = root.winfo_pointerx() - root.x
    y = root.winfo_pointery() - root.y
    root.geometry(f"+{x}+{y}")

def add_city():
    new_city = manual_city_entry.get().strip()
    if new_city and new_city not in city_options:
        city_options.append(new_city)
        city_optionmenu["menu"].add_command(label=new_city, command=tk._setit(city_var, new_city))
        city_var.set(new_city)
    manual_city_entry.delete(0, tk.END)

# メインウィンドウ生成
root = tk.Tk()
root.title("天気ガジェット")
root.geometry("420x520")
root.configure(bg="#fce4ec")  # パステル調の背景色（淡いピンク）
root.overrideredirect(True)
root.bind("<ButtonPress-1>", start_move)
root.bind("<B1-Motion>", move_window)

# 3D調のメインコンテナ（POPな印象）
main_frame = tk.Frame(root, bg="#fffde7", bd=5, relief="raised")
main_frame.pack(expand=True, fill="both", padx=10, pady=10)

# 閉じるボタン（main_frame内）
close_button = tk.Button(main_frame, text="✖", command=close_app, font=("Arial", 10, "bold"),
                          bg="red", fg="white")
close_button.place(x=370, y=5, width=25, height=25)

# 都市選択用フレーム
city_frame = tk.Frame(main_frame, bg="#fffde7")
city_frame.pack(pady=5)

city_var = tk.StringVar(value=city_options[0])
city_optionmenu = tk.OptionMenu(city_frame, city_var, *city_options)
city_optionmenu.pack(side=tk.LEFT, padx=5)

manual_city_entry = tk.Entry(city_frame, width=10)
manual_city_entry.pack(side=tk.LEFT, padx=5)

add_city_button = tk.Button(city_frame, text="追加", command=add_city, font=("Arial", 10, "bold"),
                            bg="#4CAF50", fg="white", relief="raised", padx=5, pady=2)
add_city_button.pack(side=tk.LEFT, padx=5)

# ※手動更新ボタンは削除（自動更新のみ）

# 天気アイコン表示
icon_label = tk.Label(main_frame, bg="#fffde7")
icon_label.pack(pady=5)

# 天気情報ラベル
weather_label = tk.Label(main_frame, text="", font=("Arial", 14, "bold"), bg="#fffde7")
weather_label.pack()

# 情報取得時間表示
time_label = tk.Label(main_frame, text="情報取得時間: --", font=("Arial", 10), bg="#fffde7")
time_label.pack()

# 天気情報（気温、湿度、風速）の表示枠
info_frame = tk.LabelFrame(main_frame, text="天気情報", padx=10, pady=10, font=("Arial", 12, "bold"),
                           bg="#fffde7", highlightbackground="black", highlightthickness=1)
info_frame.pack(pady=5, fill="both", expand=True)

temp_frame = tk.Frame(info_frame, bg="#fffde7")
temp_frame.pack()

temp_value_label = tk.Label(temp_frame, text="-- °C", font=("Arial", 12), width=10, relief="solid", bg="white")
humidity_value_label = tk.Label(temp_frame, text="-- %", font=("Arial", 12), width=10, relief="solid", bg="white")
wind_value_label = tk.Label(temp_frame, text="-- m/s", font=("Arial", 12), width=10, relief="solid", bg="white")

temp_value_label.grid(row=1, column=0, padx=5)
humidity_value_label.grid(row=1, column=1, padx=5)
wind_value_label.grid(row=1, column=2, padx=5)

# グラフ選択用フレーム（ラジオボタン）
graph_frame = tk.Frame(main_frame, bg="#fffde7")
graph_frame.pack(pady=5)

graph_choice = tk.StringVar(value="temperature")
tk.Label(graph_frame, text="グラフ選択:", font=("Arial", 10, "bold"), bg="#fffde7").pack(side=tk.LEFT, padx=5)
tk.Radiobutton(graph_frame, text="気温", variable=graph_choice, value="temperature", command=update_graph, bg="#fffde7").pack(side=tk.LEFT)
tk.Radiobutton(graph_frame, text="湿度", variable=graph_choice, value="humidity", command=update_graph, bg="#fffde7").pack(side=tk.LEFT)
tk.Radiobutton(graph_frame, text="風速", variable=graph_choice, value="wind", command=update_graph, bg="#fffde7").pack(side=tk.LEFT)

# グラフ表示
fig, ax = plt.subplots(figsize=(4, 2))
canvas = FigureCanvasTkAgg(fig, master=main_frame)
canvas.get_tk_widget().pack()

# 初回更新＆自動更新開始
get_weather()
root.mainloop()
