import tkinter as tk
import tkinter.simpledialog as simpledialog
import tkinter.messagebox as messagebox
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

CONFIG_FILE = "config.json"

def load_config():
    # ファイルが存在しなければデフォルト設定を書き出して作成
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            config = json.load(f)
    else:
        config = {
            "city": "東京",
            "api_key": "",
            "window_geometry": "360x600+100+100",
            "bg_color": "Pastel Pink",
        }
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(config, f, ensure_ascii=False)
    return config

def save_config():
    # 現在のウィンドウ位置や背景色、都市設定を保存
    config["window_geometry"] = root.geometry()
    config["bg_color"] = bg_color_var.get()
    config["city"] = city_var.get()
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False)

# config読み込み（存在しなければデフォルトで作成）
config = load_config()

# メインウィンドウ生成（configのwindow_geometryを適用）
root = tk.Tk()
root.overrideredirect(False)  # まずは標準ウィンドウとして生成
root.after(10, lambda: root.overrideredirect(True))  # 少し待ってから装飾を消す
root.title("天気ガジェット")
root.geometry(config.get("window_geometry", "360x600"))
root.configure(bg="#ffffff")

# APIトークンチェック（未設定の場合、入力を促す）
if not config.get("api_key"):
    messagebox.showinfo("APIトークン入力",
                        "APIトークンが必要です。\nAPIトークンは https://openweathermap.org/api から取得できます。")
    api_token = simpledialog.askstring("APIトークン入力", "OpenWeatherMapのAPIトークンを入力してください:")
    if api_token:
        config["api_key"] = api_token.strip()
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(config, f, ensure_ascii=False)
    else:
        # キャンセルされた場合でも config ファイルは作成済みなので、そのままエラー表示して終了
        messagebox.showerror("エラー", "APIトークンが入力されませんでした。")
        save_config()
        root.destroy()
        exit()

API_KEY = config["api_key"]

# 初期都市リスト
city_options = ["東京", "大阪", "札幌", "福岡", "名古屋", "京都", "広島"]
saved_city = config.get("city", "東京")
if saved_city not in city_options:
    city_options.append(saved_city)

def remove_city():
    current_city = city_var.get()
    default_cities = ["東京", "大阪", "札幌", "福岡", "名古屋", "京都", "広島"]
    if current_city in default_cities:
        messagebox.showinfo("削除できません", "デフォルトの都市は削除できません。")
        return
    if current_city in city_options:
        city_options.remove(current_city)
        # OptionMenu のメニューを再構築
        menu = city_optionmenu["menu"]
        menu.delete(0, "end")
        for city in city_options:
            menu.add_command(label=city, command=lambda value=city: city_var.set(value))
        # 削除後の選択を先頭の都市に変更
        city_var.set(city_options[0])

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
# 背景色の略称辞書（略称: フルネーム）
bg_abbr = {
    "PP": "Pastel Pink",
    "PB": "Pastel Blue",
    "PG": "Pastel Green",
    "PY": "Pastel Yellow",
    "PPu": "Pastel Purple",
    "R": "Red",
    "B": "Blue",
    "G": "Green",
    "Y": "Yellow",
    "O": "Orange"
}
# フルネームから略称への逆引き辞書
inv_bg_abbr = {v: k for k, v in bg_abbr.items()}
# config に保存されている背景色（フルネーム）を略称に変換（なければ "PP" をデフォルト）
default_bg = config.get("bg_color", "Pastel Pink")
default_bg_abbr = inv_bg_abbr.get(default_bg, "PP")

# ---【履歴データ保存用関数】---
def get_history_filename(city):
    """都市ごとに、現在年月をもとに履歴ファイル名を生成（例: history_東京_202503.json）"""
    month_str = datetime.now().strftime("%Y%m")
    return f"history_{city}_{month_str}.json"

def save_history_entry(city, entry):
    """取得データを履歴ファイルに追記（ファイルがなければ新規作成）"""
    filename = get_history_filename(city)
    if os.path.exists(filename):
        with open(filename, "r", encoding="utf-8") as f:
            data = json.load(f)
    else:
        data = []
    data.append(entry)
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def load_history(city):
    """指定都市の現在月の履歴データを読み込み"""
    filename = get_history_filename(city)
    if os.path.exists(filename):
        with open(filename, "r", encoding="utf-8") as f:
            return json.load(f)
    else:
        return []
# ---【ここまで】---

from datetime import datetime, timedelta
import tkinter.simpledialog as simpledialog
import tkinter.messagebox as messagebox

def translate_city_name(city_jp):
    return GoogleTranslator(source="ja", target="en").translate(city_jp)

def update_bg_color(*args):
    full_color_name = bg_abbr.get(bg_color_var.get(), "Pastel Pink")
    col = bg_colors.get(full_color_name, "#fffde7")
    current_panel.config(bg=col)
    forecast_panel.config(bg=col)
    for widget in current_panel.winfo_children():
        widget.config(bg=col)
    for widget in forecast_panel.winfo_children():
        widget.config(bg=col)

def get_weather():
    city_jp = city_var.get()
    # 都市設定を保存
    config["city"] = city_jp
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False)
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

        # ---【履歴データへの保存】---
        entry = [current_time, temp, humidity, wind_speed]
        save_history_entry(city_jp, entry)
        # ---【ここまで】---

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
            # ---【予報計算結果のログ出力】---
            forecast_log = (
                f"Forecast calculation at {current_time} for {city_jp}: "
                f"selected candidate dt={candidate.get('dt', 'N/A')}, "
                f"temp={f_temp}, desc={f_desc}, humidity={f_humidity}, wind={f_wind}\n"
            )
            with open("forecast_log.txt", "a", encoding="utf-8") as flog:
                flog.write(forecast_log)
            # ---【ここまで】---
        else:
            forecast_info_label.config(text="予報データ取得失敗")
    else:
        current_info_label.config(text="データ取得に失敗しました")
        forecast_info_label.config(text="データ取得に失敗しました")

    root.after(900000, get_weather)
    if graph_toggle.get() == "表示":
        root.geometry("360x600")
    else:
        root.geometry("360x440")
 # グローバル変数として、ユーザーが指定した表示範囲を保持（指定がなければ None のまま）
graph_range = None

def set_graph_range():
    global graph_range
    # ユーザーに開始日時を入力してもらう
    start_str = simpledialog.askstring("表示範囲の指定", "開始日時を入力してください (YYYY-MM-DD HH:MM:SS):")
    if not start_str:
        return
    end_str = simpledialog.askstring("表示範囲の指定", "終了日時を入力してください (YYYY-MM-DD HH:MM:SS):")
    if not end_str:
        return
    try:
        start_dt = datetime.strptime(start_str, "%Y-%m-%d %H:%M:%S")
        end_dt = datetime.strptime(end_str, "%Y-%m-%d %H:%M:%S")
    except ValueError:
        messagebox.showerror("入力エラー", "日時の形式が正しくありません。")
        return
    graph_range = (start_dt, end_dt)
    update_graph()  # 範囲指定後にグラフ更新

def update_graph():
    if graph_toggle.get() == "非表示":
        graph_frame.pack_forget()
        root.geometry("360x440")
        return
    else:
        graph_frame.pack(pady=5, fill="both", expand=True)
        root.geometry("360x600")
    city_key = city_var.get()
    history = load_history(city_key)
    
    # デフォルトは直近48時間のみ表示
    if graph_range is None:
        end_time = datetime.now()
        start_time = end_time - timedelta(hours=48)
    else:
        start_time, end_time = graph_range

    # 履歴データから日時の範囲でフィルタ
    filtered_history = [
        entry for entry in history
        if start_time <= datetime.strptime(entry[0], "%Y-%m-%d %H:%M:%S") <= end_time
    ]
    
    if not filtered_history:
        messagebox.showwarning("データなし", "指定された範囲の過去データがありません。")
        ax.clear()
        ax.set_title("データがありません", fontsize=9)
        canvas.draw()
        return

    # 時間順にソートし、時刻部分をラベルに変換
    filtered_history.sort(key=lambda entry: datetime.strptime(entry[0], "%Y-%m-%d %H:%M:%S"))
    times = [datetime.strptime(entry[0], "%Y-%m-%d %H:%M:%S").strftime("%H:%M") for entry in filtered_history]
    
    ax.clear()
    selection = graph_choice.get()
    if selection == "気温":
        vals = [entry[1] for entry in filtered_history]
        ax.plot(times, vals, marker="o", markersize=3, label="気温(°C)", color="red")
        ax.set_ylabel("気温(°C)", fontsize=9)
    elif selection == "湿度":
        vals = [entry[2] for entry in filtered_history]
        ax.plot(times, vals, marker="s", markersize=3, label="湿度(%)", color="blue")
        ax.set_ylabel("湿度(%)", fontsize=9)
    elif selection == "風速":
        vals = [entry[3] for entry in filtered_history]
        ax.plot(times, vals, marker="^", markersize=3, label="風速(m/s)", color="green")
        ax.set_ylabel("風速(m/s)", fontsize=9)
    ax.set_title("天気履歴", fontsize=9)
    ax.set_xlabel("時間", fontsize=9)
    ax.legend(fontsize=9)
    ax.tick_params(labelsize=9)
    fig.subplots_adjust(left=0.2, right=0.95, bottom=0.35)
    canvas.draw()


def close_app():
    save_config()
    # 終了時に forecast_log.txt を削除
    if os.path.exists("forecast_log.txt"):
        os.remove("forecast_log.txt")
    root.quit()
    root.destroy()

# ヘッダー：ドラッグでウィンドウ移動（全体ではなくヘッダー領域のみ）
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

# メインフレーム生成
main_frame = tk.Frame(root, bg="#fffde7", bd=5, relief="raised")
main_frame.pack(expand=True, fill="both")

# ヘッダー（閉じるボタン等）
header_frame = tk.Frame(main_frame, bg="#fffde7")
header_frame.pack(fill="x")
# ※ウィンドウ移動のバインドをヘッダーに設定
header_frame.bind("<ButtonPress-1>", start_move)
header_frame.bind("<B1-Motion>", move_window)

def show_context_menu(event):
    context_menu.post(event.x_root, event.y_root)

context_menu = tk.Menu(root, tearoff=0)
context_menu.add_command(
    label="最前面に表示", command=lambda: root.attributes("-topmost", True)
)
context_menu.add_command(
    label="最前面解除", command=lambda: root.attributes("-topmost", False)
)
context_menu.add_separator()
context_menu.add_command(label="閉じる", command=close_app)
header_frame.bind("<Button-3>", show_context_menu)

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

def set_transparency(val):
    alpha = float(val)
    if alpha < 0.2:
        alpha = 0.2
    root.attributes("-alpha", alpha)

transparency_scale = tk.Scale(
    header_frame,
    from_=0.2,
    to=1.0,
    resolution=0.05,
    orient="horizontal",
    label="透明度",
    command=set_transparency,
    font=("Arial", 9),
)
transparency_scale.set(0.8)
transparency_scale.pack(side="left", padx=5)

# ヘッダーに現在時刻表示用のラベルを追加
current_time_label = tk.Label(header_frame, text="", font=("Arial", 9), bg=header_frame["bg"])
current_time_label.pack(side="left", padx=5)

def update_current_time():
    current_time_label.config(text=datetime.now().strftime("%H:%M:%S"))
    root.after(1000, update_current_time)

update_current_time()

# 上部：都市選択
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

# ここに削除ボタンを追加
remove_city_button = tk.Button(
    top_frame,
    text="削除",
    command=remove_city,
    font=("Arial", 9),
    bg="#ff9900",
    fg="white",
    relief="raised",
    padx=5,
    pady=2,
)
remove_city_button.pack(side=tk.LEFT, padx=5)

# OptionMenu 用の変数は略称を持つ
bg_color_var = tk.StringVar(value=default_bg_abbr)

def update_bg_color(*args):
    # 略称からフルネームに変換して色コードを取得
    full_color_name = bg_abbr.get(bg_color_var.get(), "Pastel Pink")
    col = bg_colors.get(full_color_name, "#fffde7")
    current_panel.config(bg=col)
    forecast_panel.config(bg=col)
    for widget in current_panel.winfo_children():
        widget.config(bg=col)
    for widget in forecast_panel.winfo_children():
        widget.config(bg=col)

def save_config():
    # 背景色は略称からフルネームに変換して保存
    config["window_geometry"] = root.geometry()
    config["bg_color"] = bg_abbr.get(bg_color_var.get(), "Pastel Pink")
    config["city"] = city_var.get()
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False)

# OptionMenu の生成を修正（略称をリストとして渡す）
bg_optionmenu = tk.OptionMenu(
    top_frame,
    bg_color_var,
    *list(bg_abbr.keys()),
    command=lambda v: update_bg_color(),
)
bg_optionmenu.config(font=("Arial", 9))
bg_optionmenu.pack(side=tk.RIGHT, padx=5)

# 下段：選択都市表示と天気取得ボタン
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

time_label = tk.Label(
    main_frame, text="情報取得時間: --", font=("Arial", 8), bg="#fffde7"
)
time_label.pack(pady=2)

# 中央：現在の天気情報と1時間後予報パネル
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

# グラフ表示切替（過去データグラフは履歴ファイルのデータを表示）
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

range_button = tk.Button(
    graph_choice_frame,
    text="範囲指定",
    command=set_graph_range,
    font=("Arial", 9),
    bg="#ddd"
)
range_button.pack(side=tk.LEFT, padx=5)
# 過去データグラフ表示用のフレーム
graph_frame = tk.Frame(main_frame, bg="#fffde7")
if graph_toggle.get() == "表示":
    graph_frame.pack(pady=5, fill="both", expand=True)
fig, ax = plt.subplots(figsize=(3, 2.8))
fig.patch.set_facecolor("#fffde7")
ax.set_facecolor("#fffde7")
canvas = FigureCanvasTkAgg(fig, master=graph_frame)
canvas.get_tk_widget().pack(expand=True, fill="both")

update_bg_color()
get_weather()
root.mainloop()
