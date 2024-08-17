import os
import time
import asyncio
from concurrent.futures import ThreadPoolExecutor, wait, as_completed
import tkinter as tk
from tkinter import filedialog, messagebox
import qasync
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import threading
from selenium.common.exceptions import NoSuchElementException, TimeoutException, NoAlertPresentException
import pyperclip
import re

try:
    from telethon.sync import TelegramClient, events
    from telethon.sessions import StringSession
    from telethon.tl.types import Channel
    from telethon import functions
    import telethon.errors
except ModuleNotFoundError:
    print("Error: Telethon library is not installed. Please install it using 'pip install telethon'")

def create_sample_files(folder_path):
    data_login_path = os.path.join(folder_path, "data_login")
    data_session_path = os.path.join(folder_path, "data_session")
    profiles_path = os.path.join(folder_path, "profiles")
    loaddata_file_path = os.path.join(folder_path, "loaddata.txt")

    # Kiểm tra và tạo thư mục nếu chưa tồn tại
    if not os.path.exists(data_login_path):
        os.makedirs(data_login_path)
    if not os.path.exists(data_session_path):
        os.makedirs(data_session_path)
    if not os.path.exists(profiles_path):
        os.makedirs(profiles_path)

    # Kiểm tra và tạo tệp loaddata.txt nếu chưa tồn tại
    if not os.path.exists(loaddata_file_path):
        with open(loaddata_file_path, "w") as file:
            file.write("Telegram|input1|input2|input3")


def select_folder():
    folder_path = filedialog.askdirectory()
    if folder_path:
        create_sample_files(folder_path)
        messagebox.showinfo("Success", f"Files and folders checked/created in {folder_path}")
        show_settings_screen(folder_path)


def show_settings_screen(folder_path):
    settings_window = tk.Toplevel(root)
    settings_window.title("Settings")

    loaddata_file_path = os.path.join(folder_path, "loaddata.txt")

    if os.path.exists(loaddata_file_path):
        with open(loaddata_file_path, "r") as file:
            lines = file.readlines()

        for row_idx, line in enumerate(lines):
            columns = line.strip().split('|')
            for col_idx, value in enumerate(columns):
                label = tk.Label(settings_window, text=value)
                label.grid(row=row_idx, column=col_idx, padx=5, pady=5)
    else:
        messagebox.showerror("Error", f"File {loaddata_file_path} not found")


# Khởi tạo cửa sổ chính
root = tk.Tk()
root.title("Python Installer UI")

select_folder_button = tk.Button(root, text="Select Folder", command=select_folder)
select_folder_button.pack(pady=20)

root.mainloop()
