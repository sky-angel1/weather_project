from PIL import Image

# 画像を開く
img = Image.open("A_minimal_and_modern_icon_for_an_information_gadge.png")

# ICO形式に変換（サイズ指定）
img.save(
    "info_gadget_icon.ico",
    format="ICO",
    sizes=[(256, 256), (128, 128), (64, 64), (32, 32), (16, 16)],
)
