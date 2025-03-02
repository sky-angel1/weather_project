import tkinter as tk
import requests
from PIL import Image, ImageTk
from io import BytesIO
from deep_translator import GoogleTranslator
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import os, json

# 日本語表示用フォント設定（Windowsの場合はMS Gothic）
plt.rcParams["font.family"] = "MS Gothic"

API_KEY = "699606031de6a2c3b0c9934019844d8b"
CONFIG_FILE = "config.json"


def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            config = json.load(f)
            return config.get("city", "東京")
    else:
        return "東京"


def save_config(city):
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump({"city": city}, f, ensure_ascii=False)


# 初期都市リスト
city_options = ["東京", "大阪", "札幌", "福岡", "名古屋", "京都", "広島"]
saved_city = load_config()
if saved_city not in city_options:
    city_options.append(saved_city)

# 背景色選択用の色リスト（パステル＋原色）
bg_colors = {
    "Pastel Pink": "#ffb3ba",
    "Pastel Blue": "#bae1ff",
    "Pastel Green": "#baffc9",
    "Pastel Yellow": "#ffffba",
    "Pastel Purple": "#e0bbff",
    "Red": "red",
    "Blue": "blue",
    "Green": "green",
    "Yellow": "yellow",
    "Orange": "orange",
}

# 各都市ごとの履歴データ保持用辞書
city_history = {}


def translate_city_name(city_jp):
    return GoogleTranslator(source="ja", target="en").translate(city_jp)


def update_bg_color(*args):
    col = bg_colors.get(bg_color_var.get(), "#fffde7")
    current_panel.config(bg=col)
    forecast_panel.config(bg=col)
    for widget in current_panel.winfo_children():
        widget.config(bg=col)
    for widget in forecast_panel.winfo_children():
        widget.config(bg=col)


def get_weather():
    city_jp = city_var.get()
    save_config(city_jp)
    selected_city_label.config(text=f"選択都市: {city_jp}")
    city_eng = translate_city_name(city_jp)
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city_eng}&appid={API_KEY}&units=metric&lang=ja"
    response = requests.get(url)
    data = response.json()

    if response.status_code == 200:
        weather_desc = data["weather"][0]["description"]
        temp = data["main"]["temp"]
        humidity = data["main"]["humidity"]
        wind_speed = data["wind"]["speed"]
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # 統一：openweathermap の icon を利用（64×64）
        icon_code = data["weather"][0]["icon"]
        icon_url = f"http://openweathermap.org/img/wn/{icon_code}@2x.png"
        r = requests.get(icon_url)
        if r.status_code == 200:
            img = Image.open(BytesIO(r.content)).resize((64, 64))
            icon_photo = ImageTk.PhotoImage(img)
            current_icon_label.config(image=icon_photo)
            current_icon_label.image = icon_photo
        else:
            current_icon_label.config(image="")

        current_info_label.config(
            text=f"{weather_desc}\n{temp}°C\n湿度: {humidity}%\n風速: {wind_speed} m/s"
        )
        time_label.config(text=f"情報取得時間: {current_time}")

        history = city_history.setdefault(city_jp, [])
        if len(history) >= 5:
            history.pop(0)
        history.append((current_time, temp, humidity, wind_speed))
        update_graph()

        # 1時間後の予報取得（5日間／3時間間隔予報 API）
        forecast_url = f"http://api.openweathermap.org/data/2.5/forecast?q={city_eng}&appid={API_KEY}&units=metric&lang=ja"
        f_response = requests.get(forecast_url)
        if f_response.status_code == 200:
            f_data = f_response.json()
            now_ts = datetime.now().timestamp()
            target_ts = now_ts + 3600
            candidate = None
            for item in f_data["list"]:
                if item["dt"] >= target_ts:
                    candidate = item
                    break
            if candidate is None:
                candidate = f_data["list"][0]
            f_temp = candidate["main"]["temp"]
            f_desc = candidate["weather"][0]["description"]
            f_humidity = candidate["main"]["humidity"]
            f_wind = candidate["wind"]["speed"]
            f_icon_code = candidate["weather"][0]["icon"]
            f_icon_url = f"http://openweathermap.org/img/wn/{f_icon_code}@2x.png"
            r2 = requests.get(f_icon_url)
            if r2.status_code == 200:
                f_img = Image.open(BytesIO(r2.content)).resize((64, 64))
                f_photo = ImageTk.PhotoImage(f_img)
                forecast_icon_label.config(image=f_photo)
                forecast_icon_label.image = f_photo
            else:
                forecast_icon_label.config(image="")
            forecast_info_label.config(
                text=f"{f_desc}\n{f_temp}°C\n湿度: {f_humidity}%\n風速: {f_wind} m/s"
            )
        else:
            forecast_info_label.config(text="予報データ取得失敗")
    else:
        current_info_label.config(text="データ取得に失敗しました")
        forecast_info_label.config(text="データ取得に失敗しました")

    root.after(900000, get_weather)
    if graph_toggle.get() == "表示":
        root.geometry("360x600")
    else:
        root.geometry("360x420")


def update_graph():
    if graph_toggle.get() == "非表示":
        graph_frame.pack_forget()
        root.geometry("360x420")
    else:
        graph_frame.pack(pady=5, fill="both", expand=True)
        root.geometry("360x600")  # グラフの縦幅を増やす分、ウィンドウ全体も大きく
        city_key = city_var.get()
        history = city_history.get(city_key, [])
        times = [entry[0][11:16].replace(":", "時") + "分" for entry in history]
        ax.clear()
        selection = graph_choice.get()
        if selection == "気温":
            vals = [entry[1] for entry in history]
            ax.plot(
                times, vals, marker="o", markersize=3, label="気温(°C)", color="red"
            )
            ax.set_ylabel("気温(°C)", fontsize=9)
        elif selection == "湿度":
            vals = [entry[2] for entry in history]
            ax.plot(
                times, vals, marker="s", markersize=3, label="湿度(%)", color="blue"
            )
            ax.set_ylabel("湿度(%)", fontsize=9)
        elif selection == "風速":
            vals = [entry[3] for entry in history]
            ax.plot(
                times, vals, marker="^", markersize=3, label="風速(m/s)", color="green"
            )
            ax.set_ylabel("風速(m/s)", fontsize=9)
        ax.set_title("天気履歴", fontsize=9)
        ax.set_xlabel("時間", fontsize=9)
        ax.legend(fontsize=9)
        ax.tick_params(labelsize=9)
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
        city_optionmenu["menu"].add_command(
            label=new_city, command=tk._setit(city_var, new_city)
        )
    manual_city_entry.delete(0, tk.END)


# メインウィンドウ生成
root = tk.Tk()
root.title("天気ガジェット")
root.geometry("360x600")
root.configure(bg="#ffffff")
root.overrideredirect(True)
root.bind("<ButtonPress-1>", start_move)
root.bind("<B1-Motion>", move_window)

# メインフレーム（3D外観、余白を削除）
main_frame = tk.Frame(root, bg="#fffde7", bd=5, relief="raised")
main_frame.pack(expand=True, fill="both")  # padx, pady 削除

# ヘッダー：閉じるボタンを含む
header_frame = tk.Frame(main_frame, bg="#fffde7")
header_frame.pack(fill="x")
close_button = tk.Button(
    header_frame,
    text="✖",
    command=close_app,
    font=("Arial", 9, "bold"),
    bg="red",
    fg="white",
    relief="raised",
)
close_button.pack(side="right", padx=5, pady=5)

# 上部：都市選択（上段）
top_frame = tk.Frame(main_frame, bg="#fffde7")
top_frame.pack(pady=5, fill="x")
city_var = tk.StringVar(value=saved_city)
city_optionmenu = tk.OptionMenu(top_frame, city_var, *city_options)
city_optionmenu.config(font=("Arial", 9))
city_optionmenu.pack(side=tk.LEFT, padx=5)
manual_city_entry = tk.Entry(top_frame, width=10, font=("Arial", 9))
manual_city_entry.pack(side=tk.LEFT, padx=5)
add_city_button = tk.Button(
    top_frame,
    text="追加",
    command=add_city,
    font=("Arial", 9),
    bg="#4CAF50",
    fg="white",
    relief="raised",
    padx=5,
    pady=2,
)
add_city_button.pack(side=tk.LEFT, padx=5)
bg_color_var = tk.StringVar(value="Pastel Pink")
bg_optionmenu = tk.OptionMenu(
    top_frame,
    bg_color_var,
    *list(bg_colors.keys()),
    command=lambda v: update_bg_color(),
)
bg_optionmenu.config(font=("Arial", 9))
bg_optionmenu.pack(side=tk.RIGHT, padx=5)

# 下段：選択都市表示と天気取得ボタンを同じ行に配置
action_frame = tk.Frame(main_frame, bg="#fffde7")
action_frame.pack(pady=2, fill="x")
selected_city_label = tk.Label(
    action_frame, text="選択都市: " + city_var.get(), font=("Arial", 9), bg="#fffde7"
)
selected_city_label.pack(side=tk.LEFT, padx=5)
update_button = tk.Button(
    action_frame,
    text="天気を取得",
    command=get_weather,
    font=("Arial", 9),
    bg="#ff4d4d",
    fg="white",
    relief="raised",
    padx=5,
    pady=2,
)
update_button.pack(side=tk.RIGHT, padx=5)

# 取得時間表示
time_label = tk.Label(
    main_frame, text="情報取得時間: --", font=("Arial", 8), bg="#fffde7"
)
time_label.pack(pady=2)

# 中央：現在の天気情報と1時間後予報パネル（横並び）
panels_frame = tk.Frame(main_frame, bg="#fffde7")
panels_frame.pack(pady=5, fill="x")
current_panel = tk.LabelFrame(
    panels_frame,
    text="現在の天気",
    font=("Arial", 9),
    bg=bg_colors.get(bg_color_var.get(), "#fffde7"),
    relief="groove",
    bd=2,
)
current_panel.pack(side=tk.LEFT, padx=5, expand=True, fill="both")
current_icon_label = tk.Label(
    current_panel, bg=bg_colors.get(bg_color_var.get(), "#fffde7")
)
current_icon_label.pack(pady=2)
current_info_label = tk.Label(
    current_panel,
    text="--",
    font=("Arial", 9),
    bg=bg_colors.get(bg_color_var.get(), "#fffde7"),
    justify="center",
)
current_info_label.pack(pady=2)
forecast_panel = tk.LabelFrame(
    panels_frame,
    text="1時間後の予報",
    font=("Arial", 9),
    bg=bg_colors.get(bg_color_var.get(), "#fffde7"),
    relief="groove",
    bd=2,
)
forecast_panel.pack(side=tk.LEFT, padx=5, expand=True, fill="both")
forecast_icon_label = tk.Label(
    forecast_panel, bg=bg_colors.get(bg_color_var.get(), "#fffde7")
)
forecast_icon_label.pack(pady=2)
forecast_info_label = tk.Label(
    forecast_panel,
    text="--",
    font=("Arial", 9),
    bg=bg_colors.get(bg_color_var.get(), "#fffde7"),
    justify="center",
)
forecast_info_label.pack(pady=2)

# グラフ表示切替
toggle_frame = tk.Frame(main_frame, bg="#fffde7")
toggle_frame.pack(pady=5)
graph_toggle = tk.StringVar(value="非表示")
tk.Label(toggle_frame, text="グラフ表示:", font=("Arial", 9), bg="#fffde7").pack(
    side=tk.LEFT, padx=5
)
tk.Radiobutton(
    toggle_frame,
    text="表示",
    variable=graph_toggle,
    value="表示",
    command=update_graph,
    font=("Arial", 9),
    bg="#fffde7",
).pack(side=tk.LEFT)
tk.Radiobutton(
    toggle_frame,
    text="非表示",
    variable=graph_toggle,
    value="非表示",
    command=update_graph,
    font=("Arial", 9),
    bg="#fffde7",
).pack(side=tk.LEFT)

graph_choice = tk.StringVar(value="気温")
graph_choice_frame = tk.Frame(main_frame, bg="#fffde7")
graph_choice_frame.pack(pady=2)
tk.Label(graph_choice_frame, text="グラフ項目:", font=("Arial", 9), bg="#fffde7").pack(
    side=tk.LEFT, padx=5
)
tk.Radiobutton(
    graph_choice_frame,
    text="気温",
    variable=graph_choice,
    value="気温",
    command=update_graph,
    font=("Arial", 9),
    bg="#fffde7",
).pack(side=tk.LEFT)
tk.Radiobutton(
    graph_choice_frame,
    text="湿度",
    variable=graph_choice,
    value="湿度",
    command=update_graph,
    font=("Arial", 9),
    bg="#fffde7",
).pack(side=tk.LEFT)
tk.Radiobutton(
    graph_choice_frame,
    text="風速",
    variable=graph_choice,
    value="風速",
    command=update_graph,
    font=("Arial", 9),
    bg="#fffde7",
).pack(side=tk.LEFT)

graph_frame = tk.Frame(main_frame, bg="#fffde7")
if graph_toggle.get() == "表示":
    graph_frame.pack(pady=5, fill="both", expand=True)
fig, ax = plt.subplots(figsize=(3, 2.8))
# 背景色を変更： "#fffde7"
fig.patch.set_facecolor("#fffde7")
ax.set_facecolor("#fffde7")
canvas = FigureCanvasTkAgg(fig, master=graph_frame)
canvas.get_tk_widget().pack(expand=True, fill="both")

update_bg_color()

get_weather()
root.mainloop()
