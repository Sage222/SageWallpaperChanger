import tkinter as tk
from tkinter import filedialog, messagebox
import threading
import time
import os
from PIL import Image, ImageDraw
import ctypes
import pystray

SPI_SETDESKWALLPAPER = 20

def set_wallpaper(img_path):
    bmp_image = img_path + ".bmp"
    with Image.open(img_path) as img:
        screen_width = ctypes.windll.user32.GetSystemMetrics(0)
        screen_height = ctypes.windll.user32.GetSystemMetrics(1)
        img.thumbnail((screen_width, screen_height), Image.Resampling.LANCZOS)
        img.save(bmp_image, "BMP")
    ctypes.windll.user32.SystemParametersInfoW(SPI_SETDESKWALLPAPER, 0, bmp_image, 3)

def start_wallpaper_rotation(folder, duration):
    images = [os.path.join(folder, f) for f in os.listdir(folder)
              if f.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp'))]
    if not images:
        messagebox.showerror("No images", "No images found in selected folder!")
        return

    def rotate():
        idx = 0
        while True:
            set_wallpaper(images[idx])
            idx = (idx + 1) % len(images)
            time.sleep(duration)
    threading.Thread(target=rotate, daemon=True).start()

def browse_folder():
    folder_selected = filedialog.askdirectory()
    if folder_selected:
        folder_path.set(folder_selected)

def run_wallpaper_rotation():
    folder = folder_path.get()
    try:
        duration = float(duration_var.get())
    except ValueError:
        messagebox.showerror("Invalid input", "Duration must be a number (seconds)!")
        return
    if not os.path.isdir(folder):
        messagebox.showerror("Invalid folder", "Select a valid folder!")
        return
    start_wallpaper_rotation(folder, duration)

def make_default_icon():
    image = Image.new('RGB', (64, 64), 'black')
    draw = ImageDraw.Draw(image)
    draw.rectangle((32, 0, 64, 32), fill='white')
    draw.rectangle((0, 32, 32, 64), fill='white')
    return image

def minimize_to_tray():
    root.withdraw()
    if os.path.isfile("app.ico"):
        image = Image.open("app.ico")
    else:
        image = make_default_icon()
    menu = pystray.Menu(
        pystray.MenuItem('Show', show_window),
        pystray.MenuItem('Quit', quit_window)
    )
    icon = pystray.Icon("WallpaperRotator", image, "Wallpaper Rotator", menu)
    tray_icons.append(icon)
    icon.run()

def show_window(icon=None, item=None):
    root.after(0, root.deiconify)
    if tray_icons:
        tray_icons[-1].stop()
        tray_icons.pop()

def quit_window(icon=None, item=None):
    if tray_icons:
        tray_icons[-1].stop()
        tray_icons.pop()
    root.quit()

root = tk.Tk()
root.title("Wallpaper Rotator")
tray_icons = []

folder_path = tk.StringVar()
duration_var = tk.StringVar(value="30")

tk.Label(root, text="Select Folder with Images:").pack()
tk.Entry(root, textvariable=folder_path, width=40).pack()
tk.Button(root, text="Browse", command=browse_folder).pack()

tk.Label(root, text="Change Interval (seconds):").pack()
tk.Entry(root, textvariable=duration_var, width=10).pack()

tk.Button(root, text="Start Rotation", command=run_wallpaper_rotation).pack(pady=10)

root.protocol('WM_DELETE_WINDOW', minimize_to_tray)
root.mainloop()
