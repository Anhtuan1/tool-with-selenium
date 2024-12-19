
import time
import os
import sys
import asyncio
import random
import requests
import json
import threading
import pyperclip
import re
import math
import shutil
import sqlite3
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, wait, as_completed
from qasync import QEventLoop
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTextEdit, QPushButton, QLineEdit, QTableWidget, QTableWidgetItem, QFileDialog
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from urllib.parse import urlparse, parse_qs, unquote
from tkinter import Tk, Button, filedialog

from script import SCRIPT_GAME_MEMEX, SCRIPT_GAME_SEED, SCRIPT_GAME_MAJOR, SCRIPT_AUTO_NOTPIXEL, SCRIPT_QUIT, SCRIPT_GAME_CONTROL_PAWS, SCRIPT_WALLET_CONTROL_PAWS, SCRIPT_TELE_CONTROL_START1, SCRIPT_WALLET_INIT1, SCRIPT_TELE_CONTROL_START2, SCRIPT_WALLET_INIT2, SCRIPT_TELE_CONTROL_START3, SCRIPT_WALLET_INIT3, SCRIPT_TELE_CONTROL_START4, SCRIPT_WALLET_CLICK_TON, SCRIPT_WALLET_INIT4, SCRIPT_GAME_BLUM, SCRIPT_GAME_TOMARKET, SCRIPT_GAME_START, SCRIPT_SET_NAME, SCRIPT_IFRAME_BYPASS_MOBILE, SCRIPT_GAME_CONTROL, SCRIPT_WALLET_CONTROL, SCRIPT_GAME_SET_WALLET_DEFAULT , script_popup, headers_tomarket            
# from webdriver_manager.chrome import ChromeDriverManager

# chrome_driver_path = ChromeDriverManager().install()

try:
    from telethon.sync import TelegramClient, events
    from telethon.sessions import StringSession
    from telethon import functions, errors as t_errors
    from telethon.tl.types import Channel
except (ImportError, ModuleNotFoundError):
    print("\n―― ⚠️ The Telethon library is not installed.")
    print("―― Please install it by running: `pip install telethon`")
    sys.exit()
accList = {}
proxy = []
num_thread_running = 0
futures = []
url_ref = 'https://t.me/waveonsuibot/walletapp?startapp='
url_tele = 'https://t.me/dogshouse_bot/join?startapp=zySPSgu7Qvmqqaao3JoL4Q'
# URL_LIST = 'https://t.me/drop_shit_game_bot?start=null'
# URL_LIST = 'https://t.me/notpixel/app?startapp=f1641277785 https://t.me/Tomarket_ai_bot/app?startapp=00020R5H https://web.telegram.org/k/#@BlumCryptoBot'
URL_LIST = 'https://t.me/PAWSOG_bot/PAWS?startapp=Xe4l4CvT https://web.telegram.org/k/#@BlumCryptoBot https://t.me/dogshouse_bot/join?startapp=zySPSgu7Qvmqqaao3JoL4Q https://web.telegram.org/k/#@BlumCryptoBot'
URL_INFO = 'https://t.me/MemeX_prelaunch_airdrop_bot?start=ref_code=MX2IMWSD https://web.telegram.org/a https://web.telegram.org/k/#@wallet https://web.telegram.org/k/#@BlumCryptoBot https://t.me/notpixel/app?startapp=f1641277785 https://web.telegram.org/k/#@Tomarket_ai_bot https://t.me/PAWSOG_bot/PAWS?startapp=Xe4l4CvT https://t.me/blum/app?startapp=ref_x2QGrP78j3 https://t.me/tonstationgames_bot/app?startapp=ref_xbu3wqeht67331gphr4gwm https://t.me/major/start?startapp=1641277785'
#https://web.telegram.org/k/#@BlumCryptoBot https://t.me/major/start?startapp=1641277785 https://t.me/bwcwukong_bot/Play?startapp=1641277785 https://web.telegram.org/k/#@wallet https://web.telegram.org/k/#@hamster_kombat_bot https://t.me/Tomarket_ai_bot/app?startapp=00020R5H

CHROME_SIZE = {
    "width": 470,  # user agent
    "height": 686,  # user agent
    "height_window": 790,  # height chrome windows
}

mobile_emulation = {
    # "deviceName": "iPhone 6/7/8 plus"

    # iphone 6/7/8
    "deviceMetrics": {"width": CHROME_SIZE["width"], "height": CHROME_SIZE["height"], "pixelRatio": 3.0},
    "userAgent": "Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.1"
}

class ChromeProfileManager(QMainWindow):
    threads = []
    def __init__(self, folder_path):
        super().__init__()
        self.task = None
        self.folder_path = folder_path
        self.initUI()
        self.profiles = []

    def initUI(self):
        loaddataPath = self.folder_path + "/loaddata.txt"
        # proxyPath = self.folder_path + "/proxy.txt"
        # Check if the file exists
        if os.path.exists(loaddataPath):
            # Open the file in read mode
            with open(loaddataPath, 'r') as file:
                # Read the contents of the file
                file_contents = file.read()
                # Now you can work with the contents, for example:

        else:
            with open(self.folder_path + '/loaddata.txt', 'w') as file:
                file.write('')
            file_contents = ''

        # if os.path.exists(proxyPath):
        #     # Open the file in read mode
        #     with open(proxyPath, 'r') as file:
        #         file_proxy = file.read()
        # else:
        #     with open(self.folder_path + '/proxy.txt', 'w') as file:
        #         file.write('')
        #     file_proxy = ''
        

        self.setWindowTitle('Quản lý Profile Chrome')
        self.setGeometry(100, 100, 1200, 800)

        # Giao diện người dùng
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.layout = QHBoxLayout(self.central_widget)

        # Cột trái - Nhập thông tin và tạo profile
        self.input_layout = QVBoxLayout()

        self.create_button = QPushButton('Load Session Folder')
        self.create_button.clicked.connect(lambda: self.load_session())
        self.input_layout.addWidget(self.create_button)

        self.login_with_session = QPushButton('Login with Tele')
        self.login_with_session.clicked.connect(self.on_login_with_session_clicked)
        self.input_layout.addWidget(self.login_with_session)

        self.input_label = QLabel('Nhập thông tin (id|wallet|key):')
        self.input_layout.addWidget(self.input_label)
        self.input_text = QTextEdit()
        self.input_text.setPlaceholderText('id|wallet|key')
        if file_contents != '':
            self.input_text.setPlainText(file_contents)
        self.input_layout.addWidget(self.input_text)

        

        self.load_button = QPushButton('Load Profile')
        self.load_button.clicked.connect(self.load_profile)
        self.input_layout.addWidget(self.load_button)

        # self.setRefBtn = QPushButton('Set referent')
        # self.setRefBtn.clicked.connect(self.setRef)
        # self.input_layout.addWidget(self.setRefBtn)
        self.input_label_info = QLabel('Danh sach url')
        self.input_layout.addWidget(self.input_label_info)
        self.input_text_list = QTextEdit()
        self.input_text_list.setFixedHeight(80)
        self.input_text_list.setPlainText(URL_INFO)
        
        self.input_layout.addWidget(self.input_text_list)

        # Cột phải - Hiển thị thông tin profile
        self.profile_table = QTableWidget()
        self.profile_table.setColumnCount(7)
        self.profile_table.setHorizontalHeaderLabels(['ID', 'Wallet', 'Key', 'Action', 'Login', 'Auto Login Telegram', 'Create game'])

        self.right_layout = QVBoxLayout()
        self.right_layout.addWidget(QLabel('Thông tin profile:'))
        self.right_layout.addWidget(self.profile_table)

        self.actionLayout = QVBoxLayout()


        

        self.input_label_url = QLabel('Url')
        self.input_layout.addWidget(self.input_label_url)

        self.input_custom = QTextEdit()
        self.input_custom.setFixedHeight(50)
        self.input_custom.setText(URL_LIST)
        self.input_custom.setPlaceholderText('Url custom')
        self.input_layout.addWidget(self.input_custom)

        self.input_label_thread = QLabel('So profile 1 lan chay')
        self.input_layout.addWidget(self.input_label_thread)
        self.input_thread = QTextEdit()
        self.input_thread.setFixedHeight(30)
        self.input_thread.setText('3')
        self.input_thread.setPlaceholderText('Number thread')
        self.input_layout.addWidget(self.input_thread)

        self.input_label_rows = QLabel('So hang tren man hinh')
        self.input_layout.addWidget(self.input_label_rows)
        self.input_rows = QTextEdit()
        self.input_rows.setPlaceholderText('Number Row')
        self.input_rows.setFixedHeight(30)
        self.input_rows.setText('3')
        self.input_layout.addWidget(self.input_rows)

        self.all_mining = QPushButton('All start')

        
        
        
        self.actionLayout.addWidget(self.all_mining)
        self.all_mining.clicked.connect(self.all_acction)
        self.input_layout.addLayout(self.actionLayout)
        self.layout.addLayout(self.input_layout)
        self.layout.addLayout(self.right_layout)

    def load_session(self):
        loaddataSession = self.folder_path + "/data_session"

        # Check if the file exists
        if os.path.exists(loaddataSession):
            entries = os.listdir(loaddataSession)

            folders = [entry for entry in entries if os.path.isdir(os.path.join(loaddataSession, entry))]
            list_session = []
            # Print all folders
            for folder in folders:
                list_session.append(f"{folder}|wallet|key")

            self.input_text.setPlainText('\n'.join(list_session))

        else:
            os.makedirs(loaddataSession)

    def setRef(self):
        global accList
        accList_items = list(accList.items())
        driver2 = None
        for index in range(len(accList_items)):
            key, value = accList_items[index]
            if(index == 0):
                key1, value1 = accList_items[-1]
                address = value1['wallet']
            else:
                key1, value1 = accList_items[index - 1]
                address = value1['wallet']
            profile_path = f"{self.folder_path}/profiles/{key}"
            print(key)
            script_ref = f"""
               var key = '{address}';
               setInterval(() => {{
                   if (document.querySelector("#section-bind-inviter input")) {{
                       document.querySelector("#section-bind-inviter input").value = key;
                       document.querySelector("#section-bind-inviter input").dispatchEvent(new Event('input'));
                       document.querySelector("#section-bind-inviter input").value = key;
                       setTimeout(() => {{
                           document.querySelector("#section-bind-inviter button").click()
                          
                       }}, 1000);
                   }}
               }}, 3000);
               """

            try:
                chrome_options = Options()
                chrome_options.add_argument(f'--user-data-dir={profile_path}')
                chrome_options.add_argument('--no-experiments')
                driver2 = webdriver.Chrome(options=chrome_options)
                data_path = f"{self.folder_path}/data_login/{key}/url.txt"
                if os.path.exists(data_path):
                    with open(data_path, 'r') as file:
                        url = file.read().strip()
                        driver2.get(url)
                        time.sleep(3)
                        driver2.get('https://walletapp.waveonsui.com/recover-inviter')
                        time.sleep(3)
                        driver2.execute_script(script_ref)
                        time.sleep(13)
            except (NoSuchElementException, TimeoutException) as e:
                print(f"Xảy ra lỗi")
            finally:
                if driver2 is not None:
                    print('Quit')
                    driver2.quit()

    async def handle_incoming_message(event):
        otp = re.search(r'\b(\d{5})\b', event.raw_text)
        if otp:
            print("OTP received ✅\nYour login code:", otp.group(0))
            await event.client.disconnect()
    def on_login_with_session_clicked(self):
        print('Task login')
        asyncio.create_task(self.on_login_with_session())

    def stop_login_task(self):
        if self.task is not None:
            print('Stopping login task...')
            self.task.cancel()  # Cancel the task
            self.task = None

    async def on_login_with_session(self):
        global accList
        input_text = self.input_text.toPlainText()
        profiles_data = input_text.strip().split('\n')
        print('OK')
        for profile_data in profiles_data:
            parts = profile_data.split('|')
            email = parts[0]
            print('Running Login', email)
            data_path = f"{self.folder_path}/data_login/{email}/url.txt"
            if not os.path.exists(data_path):
                try:
                    await asyncio.wait_for(self.login_tele(email), timeout=120)
                except asyncio.TimeoutError:
                    print(f"Timeout reached for {email}. Skipping to the next profile.")
                except Exception as e:
                    print(f"An error occurred for {email}: {e}")
           
    
    def open_url_in_thread(self, profile_path, web, email):
        # def run_thread():
        
        chrome_options = Options()
        print(f"Running: {str(email)}")
        driver2 = None
        global accList
        global proxy
        num_threads_text = int(self.input_thread.toPlainText()) 
        width = 475
        height = 816
        scale = 0.6
        rows = int(self.input_rows.toPlainText()) 
        
        cols = math.ceil(num_threads_text / rows)
        key = accList[email]["key"]
        wallet = accList[email]["wallet"]
        print(wallet)
        email_keys = list(accList.keys())
        index = email_keys.index(email) % (num_threads_text)
        proxyHeader = None
        
        row = index % rows
        col = math.floor(index / rows)
        # Calculate the position for the window based on scale
        x_position = int(col * (width))
        y_position = int(row * (height - 40))
        scaled_width = int(width)
        scaled_height = int(height)
        CHROME_EXTENSION_CRX_PATH = self.folder_path + '/chrome_extension/ignore-x-frame-headers/2.0.0_0.crx'
        iframe = None
        if web == 'https://web.telegram.org/k/#@BlumCryptoBot' or web == 'https://t.me/blum/app?startapp=ref_x2QGrP78j3' or 'https://t.me/blum/app' in web:
            try:
                print('Running Blum')
                chrome_options.add_argument(f'--user-data-dir={profile_path}')
                chrome_options.add_argument('--no-experiments')
                # Add the mobile emulation to the chrome options variable
                chrome_options.add_experimental_option("mobileEmulation", mobile_emulation)
                chrome_options.add_argument(f"window-size={scaled_width},{scaled_height}")
                chrome_options.add_argument(f"window-position={x_position},{y_position}")
                chrome_options.add_argument("force-device-scale-factor=0.6") 
                
                CHROME_EXTENSION_CRX_PATH = self.folder_path + '/chrome_extension/ignore-x-frame-headers/2.0.0_0.crx'
                chrome_options.add_extension(CHROME_EXTENSION_CRX_PATH)
                driver2 = webdriver.Chrome(options=chrome_options)
                data_path = f"{self.folder_path}/data_login_blums/{email}/url.txt"
                if web is not None:
                    driver2.get(web)
                    time.sleep(3)

                try:
                    if web == 'https://web.telegram.org/k/#@BlumCryptoBot':
                        driver2.execute_script(script_popup)
                        time.sleep(5)
                        try:
                            start_button = driver2.find_element(By.CSS_SELECTOR, "div.new-message-bot-commands-view")
                            start_button.click()
                        except (NoSuchElementException, TimeoutException):
                            continue_button = driver2.find_element(By.XPATH, "//button[contains(., 'START')]")
                            continue_button.click()
                    else:
                        wait = WebDriverWait(driver2, 30)
                        try:
                            element = wait.until(
                                EC.presence_of_element_located((By.CLASS_NAME, 'tgme_action_web_button'))
                            )
                            ref_link = element.get_attribute('href')
                            driver2.get(ref_link)
                        except TimeoutException:
                            print("Element with class 'tgme_action_web_button' not found or not clickable within 30 seconds.")

                    time.sleep(10)

                    try:
                        continue_button = driver2.find_element(By.XPATH, "//button[contains(., 'Launch')]")
                        continue_button.click()
                    except (NoSuchElementException, TimeoutException):
                        print("Launch not found")
                    time.sleep(2)

                    try:
                        continue_button = driver2.find_element(By.XPATH, "//button[contains(., 'Confirm')]")
                        continue_button.click()
                    except (NoSuchElementException, TimeoutException):
                        print("confirm not found")
                    time.sleep(2)

                    iframe_allow_attr = 'camera; microphone; geolocation;'
                    iframe = WebDriverWait(driver2, 20).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, f'iframe[allow="{iframe_allow_attr}"]')))
                    # get iframe url
                    iframe_url = iframe.get_attribute('src')
                    iframe_url = iframe_url.replace("tgWebAppPlatform=weba", "tgWebAppPlatform=ios").replace(
                        "tgWebAppPlatform=web", "tgWebAppPlatform=ios")
                    try:
                        data_path = f"{self.folder_path}/data_login_blums/{email}"
                        if not os.path.exists(data_path):
                            os.makedirs(data_path)
                        with open(data_path + '/url.txt', 'w') as file:
                            file.write(iframe_url)
                    except Exception as e:
                        print(f"An error occurred: {e}")

                    if web == 'https://web.telegram.org/k/#@BlumCryptoBot':
                        driver2.switch_to.frame(iframe)
                        print("- SCRIPT GAME CONTROL")
                        # driver2.execute_script(script_login)
                        time.sleep(3)
                        driver2.execute_script(SCRIPT_GAME_BLUM)
                        time.sleep(10)
                        token = driver2.execute_script("return localStorage;")
                        self.run_script_from_file(driver2, self.folder_path + "/blum.txt", 42)
                    else:
                        driver2.execute_script(SCRIPT_GAME_START)
                        time.sleep(10)
                        

                        driver2.switch_to.frame(iframe)
                        print("- SCRIPT WALLET")
                        driver2.execute_script(SCRIPT_GAME_CONTROL)
                        time.sleep(10)
                        #wait for show wallet
                        time.sleep(10)


                        print("- SCRIPT WALLET CONTROL")
                        driver2.switch_to.default_content()
                        driver2.execute_script(SCRIPT_WALLET_CONTROL)
                        time.sleep(10)

                        #run browser script
                        driver2.switch_to.frame(iframe)
                        print("- SCRIPT GAME SET WALLET DEFAULT")
                        driver2.execute_script(SCRIPT_GAME_SET_WALLET_DEFAULT)
                        time.sleep(15)

                    print("- Done")
                    driver2.switch_to.default_content()

                except (NoSuchElementException, TimeoutException):
                    print(f"Lỗi: {str(e)}")
            except (NoSuchElementException, TimeoutException) as e:
                print(f"Xảy ra lỗi")
            finally:
                if driver2 is not None:
                    print('Quit')
                    driver2.quit()

        if web == 'https://web.telegram.org/a':
            print('Running set name')
            try:
                chrome_options.add_argument(f'--user-data-dir={profile_path}')
                chrome_options.add_argument('--no-experiments')
                chrome_options.add_experimental_option("mobileEmulation", mobile_emulation)
                chrome_options.add_argument(f"window-size={scaled_width},{scaled_height}")
                chrome_options.add_argument(f"window-position={x_position},{y_position}")
                chrome_options.add_argument("force-device-scale-factor=0.55") 
                driver2 = webdriver.Chrome(options=chrome_options)

                #run by tele web
                if web is not None:
                    driver2.get(web)
                    time.sleep(5)

                try:
                    print("- SCRIPT Set Name")
                    driver2.execute_script(SCRIPT_SET_NAME)
                    time.sleep(30)
                except (NoSuchElementException, TimeoutException):
                    print(f"Lỗi: {str(e)}")

            except (NoSuchElementException, TimeoutException) as e:
                print(f"Xảy ra lỗi")
            finally:
                if driver2 is not None:
                    print('Quit')
                    driver2.quit()
        
        if web == 'https://web.telegram.org/k/#@Tomarket_ai_bot' or web == 'https://t.me/Tomarket_ai_bot/app?startapp=00020R5H' or 'https://t.me/Tomarket_ai_bot/app' in web:
            print('Running Tomarket')
            try:
                chrome_options.add_argument(f'--user-data-dir={profile_path}')
                chrome_options.add_argument('--no-experiments')
                # Add the mobile emulation to the chrome options variable
                chrome_options.add_experimental_option("mobileEmulation", mobile_emulation)
                chrome_options.add_argument(f"window-size={scaled_width},{scaled_height}")
                chrome_options.add_argument(f"window-position={x_position},{y_position}")
                chrome_options.add_argument("force-device-scale-factor=0.6") 

                chrome_options.add_extension(CHROME_EXTENSION_CRX_PATH)
                driver2 = webdriver.Chrome(options=chrome_options)
                if web is not None:
                    driver2.get(web)
                    time.sleep(3)

                try:
                    if web == 'https://web.telegram.org/k/#@Tomarket_ai_bot':
                        driver2.execute_script(script_popup)
                        time.sleep(5)
                        try:
                            start_button = driver2.find_element(By.CSS_SELECTOR, "div.new-message-bot-commands-view")
                            start_button.click()
                        except (NoSuchElementException, TimeoutException):
                            continue_button = driver2.find_element(By.XPATH, "//button[contains(., 'START')]")
                            continue_button.click()
                    else:
                        wait = WebDriverWait(driver2, 20)
                        try:
                            element = wait.until(
                                EC.presence_of_element_located((By.CLASS_NAME, 'tgme_action_web_button'))
                            )

                            ref_link = element.get_attribute('href')
                            ref_link = ref_link.replace('https://web.telegram.org/a/', 'https://web.telegram.org/k/')
                            driver2.get(ref_link)
                        except TimeoutException:
                            print("Element with class 'tgme_action_web_button' not found or not clickable within 30 seconds.")
                            driver2.quit()
                    time.sleep(10)

                    try:
                        continue_button = driver2.find_element(By.XPATH, "//button[contains(., 'Launch')]")
                        continue_button.click()
                    except (NoSuchElementException, TimeoutException):
                        print("Launch not found")
                    time.sleep(5)

                    try:
                        continue_button = driver2.find_element(By.XPATH, "//button[contains(., 'Confirm')]")
                        continue_button.click()
                    except (NoSuchElementException, TimeoutException):
                        print("confirm not found")
                    time.sleep(5)

                    iframe_allow_attr = 'camera; microphone; geolocation;'
                    iframe = WebDriverWait(driver2, 20).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, f'iframe[allow="{iframe_allow_attr}"]')))

                    iframe_url = iframe.get_attribute('src')
                    iframe_url = iframe_url.replace("tgWebAppPlatform=web", "tgWebAppPlatform=ios").replace(
                        "tgWebAppPlatform=web", "tgWebAppPlatform=ios")
                    driver2.switch_to.frame(iframe)
                    time.sleep(10)
                    driver2.execute_script(SCRIPT_GAME_TOMARKET)
                    time.sleep(100)
                    parsed_url = urlparse(iframe_url)
                    fragment = parsed_url.fragment
                    params = parse_qs(fragment)
                    tg_web_app_data = params.get('tgWebAppData', [None])[0]
                    
                    query = tg_web_app_data
                    try:
                        token = get_token_tomarket(query, 'https://api-web.tomarket.ai/tomarket-game/v1/user/login', 'https://mini-app.tomarket.ai/', proxyHeader)
                        print('token-tomarket done')
                        if(wallet != 'wallet'):
                            start_connect =  self.set_wallet_game_tomarket(token=token, wallet=wallet, proxy=proxyHeader)
                            if start_connect.status_code == 200:
                                print(f"Connect done...{wallet}")

                        # start_game = self.start_game_tomarket(token=token, proxy=proxyHeader)
                        
                        # if start_game.status_code == 200:
                        #     print(f"Playing game in 30s...")
                        #     time.sleep(30)
                        #     point = random.randint(500, 600)
                        #     claim_game = self.claim_game_tomarket(
                        #         token=token, point=point, proxy=proxyHeader
                        #     )
                        #     if claim_game.status_code == 200:
                        #         print(f"Claim point from game success")
                        #     else:
                        #         print(f"Claim point from game failed")
                        # else:
                        #     print(f"Start game failed")
                    except (NoSuchElementException, TimeoutException):
                        print(f"Lỗi: {str(e)}")
                    time.sleep(5)

                except (NoSuchElementException, TimeoutException):
                    print(f"Lỗi: {str(e)}")
            except (NoSuchElementException, TimeoutException) as e:
                print(f"Xảy ra lỗi")
            finally:
                if driver2 is not None:
                    print('Quit')
                    driver2.quit()

        if web == 'https://t.me/notpixel/app?startapp=f1641277785' or web == 'https://web.telegram.org/k/#@notpixel' or 'https://t.me/notpixel/app' in web:
            print('Running NotPixcel')
            try:
                chrome_options.add_argument(f'--user-data-dir={profile_path}')
                chrome_options.add_argument('--no-experiments')
                # Add the mobile emulation to the chrome options variable
                chrome_options.add_experimental_option("mobileEmulation", mobile_emulation)
                chrome_options.add_argument(f"window-size={scaled_width},{scaled_height}")
                chrome_options.add_argument(f"window-position={x_position},{y_position}")
                chrome_options.add_argument("force-device-scale-factor=0.6") 

                chrome_options.add_extension(CHROME_EXTENSION_CRX_PATH)
                driver2 = webdriver.Chrome(options=chrome_options)
                if web is not None:
                    driver2.get(web)
                    time.sleep(3)
                wait = WebDriverWait(driver2, 30)
                try:
                    element = wait.until(
                        EC.presence_of_element_located((By.CLASS_NAME, 'tgme_action_web_button'))
                    )
                    ref_link = element.get_attribute('href')
                    ref_link = ref_link.replace('https://web.telegram.org/a/', 'https://web.telegram.org/k/')
                    driver2.get(ref_link)
                except TimeoutException:
                    print("Element with class 'tgme_action_web_button' not found or not clickable within 30 seconds.")
                time.sleep(5)
                try:
                    continue_button = driver2.find_element(By.XPATH, "//button[contains(., 'Launch')]")
                    continue_button.click()
                except (NoSuchElementException, TimeoutException):
                    print("Launch not found")
                time.sleep(5)

                try:
                    continue_button = driver2.find_element(By.XPATH, "//button[contains(., 'Confirm')]")
                    continue_button.click()
                except (NoSuchElementException, TimeoutException):
                    print("confirm not found")
                time.sleep(5)

                iframe_allow_attr = 'camera; microphone; geolocation;'
                iframe = WebDriverWait(driver2, 20).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, f'iframe[allow="{iframe_allow_attr}"]')))

                iframe_url = iframe.get_attribute('src')
                iframe_url = iframe_url.replace("tgWebAppPlatform=web", "tgWebAppPlatform=ios").replace(
                    "tgWebAppPlatform=web", "tgWebAppPlatform=ios")
                try:
                    data_path = f"{self.folder_path}/data_login_notpixcel/{email}"
                    if not os.path.exists(data_path):
                        os.makedirs(data_path)
                    with open(data_path + '/url.txt', 'w') as file:
                        file.write(iframe_url)
                except Exception as e:
                    print(f"An error occurred: {e}")
                time.sleep(5)
                driver2.switch_to.frame(iframe)
                driver2.execute_script(SCRIPT_AUTO_NOTPIXEL)
                time.sleep(40)
                # self.run_script_from_file(driver2, self.folder_path + "/notpixel.txt", 36)

            except (NoSuchElementException, TimeoutException) as e:
                print(f"Xảy ra lỗi")
            finally:
                if driver2 is not None:
                    print('Quit')
                    driver2.quit()
        
        if web == 'https://web.telegram.org/k/#@wallet':
            print('Running Wallet')
            try:
                chrome_options.add_argument(f'--user-data-dir={profile_path}')
                chrome_options.add_argument('--no-experiments')
                # Add the mobile emulation to the chrome options variable
                chrome_options.add_experimental_option("mobileEmulation", mobile_emulation)
                chrome_options.add_argument(f"window-size={scaled_width},{scaled_height}")
                chrome_options.add_argument(f"window-position={x_position},{y_position}")
                chrome_options.add_argument("force-device-scale-factor=0.6")
                driver2 = webdriver.Chrome(options=chrome_options)
                if web is not None:
                    driver2.get(web)
                    time.sleep(10)
                try:
                    print("- SCRIPT init wallet")
                    driver2.execute_script(SCRIPT_TELE_CONTROL_START1)
                    time.sleep(15)


                    iframe_allow_attr = 'camera; microphone; geolocation;'
                    iframe = WebDriverWait(driver2, 50).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, f'iframe[allow="{iframe_allow_attr}"]')))
                    # get iframe url
                    driver2.switch_to.frame(iframe)
                    driver2.execute_script(SCRIPT_WALLET_INIT1)
                    time.sleep(10)
                    print("- SCRIPT open setting page from telegram")
                    driver2.switch_to.default_content()
                    driver2.execute_script(SCRIPT_TELE_CONTROL_START2)
                    time.sleep(10)

                    # run iframe script
                    print("- SCRIPT enable TON space + go to phrase page")
                    driver2.switch_to.frame(iframe)
                    driver2.execute_script(SCRIPT_WALLET_INIT2)
                    time.sleep(15)
                    phrase = []
                    phrasestr = ''
                    accWalletUpdate = f'{email}|wallet|key'
                    try:
                        print("- GET PHRASE KEY")
                        phrase_elm = driver2.find_elements(By.CSS_SELECTOR, 'div[variant="body"] > div[variant="body"]')
                        for word in phrase_elm:
                            phrase.append(word.text)
                        print('phrase1', phrase)
                        phrase = ' '.join(phrase)
                        
                        elements = driver2.find_elements("css selector", ".cpHh.IqPa.CF5m.Ka5f.En4C")
                        alltext = " ".join([element.get_attribute("textContent") for element in elements])
                        print('phrase2', alltext)
                        time.sleep(5)

                        # run root page script
                        print("- SCRIPT click continue from telegram")
                        driver2.switch_to.default_content()
                        driver2.execute_script(SCRIPT_TELE_CONTROL_START3)
                        time.sleep(10)

                        # run iframe script
                        print("- SCRIPT verify phrase key")
                        driver2.switch_to.frame(iframe)
                        driver2.execute_script(SCRIPT_WALLET_INIT3.replace('_PHRASE_KEY_', phrase))
                        phrasestr = re.sub(r'\d+\.\s*', '', phrase)
                        accWalletUpdate = accWalletUpdate.replace('key', phrasestr)
                        print('accWalletUpdate', accWalletUpdate)
                        time.sleep(10)

                        # run root page script
                        print("- SCRIPT click next from telegram")
                        driver2.switch_to.default_content()
                        driver2.execute_script(SCRIPT_TELE_CONTROL_START4)
                        time.sleep(10)

                        # run iframe script
                        print("- SCRIPT View TON Space")
                        driver2.switch_to.frame(iframe)
                        driver2.execute_script(SCRIPT_WALLET_INIT4)
                        time.sleep(15)
                        

                       
                    except Exception as e:
                        print(f"{email}: An error occurred: {e}")
                    
                    try:
                        copy_button = WebDriverWait(driver2, 30).until(
                            EC.presence_of_element_located((By.XPATH, "//button[contains(., 'Copy Address')]")))
                        copy_button.click()

                        elements = driver2.find_elements("class name", "uDr2")
                        for element in elements:
                            wallet = element.get_attribute("textContent")
                            wallet = wallet.replace("\n", "")
                            print("wallet:", wallet)
                        time.sleep(5)
                        
                        if wallet is not None:
                            accWalletUpdate = accWalletUpdate.replace('wallet', wallet)
                        print('accWalletUpdate:', accWalletUpdate)

                        if phrasestr == '':
                            driver2.get(web)
                            driver2.execute_script(SCRIPT_TELE_CONTROL_START1)
                            time.sleep(5)
                            iframe_allow_attr = 'camera; microphone; geolocation;'
                            iframe = WebDriverWait(driver2, 20).until(
                                EC.presence_of_element_located((By.CSS_SELECTOR, f'iframe[allow="{iframe_allow_attr}"]')))
                            driver2.switch_to.frame(iframe)
                            driver2.execute_script(SCRIPT_WALLET_INIT1)
                            time.sleep(8)
                            
                            print("- SCRIPT open setting page from telegram")
                            driver2.switch_to.default_content()
                            driver2.execute_script(SCRIPT_TELE_CONTROL_START2)
                            time.sleep(8)

                            # run iframe script
                            print("- SCRIPT enable TON space + go to phrase page")
                            driver2.switch_to.frame(iframe)
                            driver2.execute_script(SCRIPT_WALLET_CLICK_TON)
                            time.sleep(8)
                            
                            elements = driver2.find_elements("css selector", ".cpHh.IqPa.PmUA.Fx5C.EJ6D")
                            all_text = " ".join([element.get_attribute("textContent") for element in elements])
                            phrasestr = re.sub(r'\d+\.\s*', '', all_text)
                            accWalletUpdate = accWalletUpdate.replace('key', phrasestr)
                            time.sleep(2)
                        print('file update data:', accWalletUpdate)

                        file_path = f"{self.folder_path}/data_wallet.txt"
                        try:
                            # Read the file and check if loadDataText is already included
                            with open(file_path, 'r') as file:
                                file_content = file.read()

                            # If loadDataText is not in file, append it
                            if accWalletUpdate not in file_content:
                                with open(file_path, 'a') as file:
                                    file.write(accWalletUpdate + "\n")
                                print(f"Added '{accWalletUpdate}' to '{file_path}'")
                            else:
                                print(f"'{accWalletUpdate}' is already present in '{file_path}'")

                        except FileNotFoundError:
                            # If file doesn't exist, create it and write loadDataText
                            with open(file_path, 'w') as file:
                                file.write(accWalletUpdate + "\n")
                            print(f"File '{file_path}' created and '{accWalletUpdate}' added.")
                        
                        time.sleep(5)
                    except (NoSuchElementException, TimeoutException):
                        print("Copy button not found")
                    time.sleep(10)
                    print("- LOG TO FILE")
                    data_path = f"{self.folder_path}/data_login_wallet/{email}"
                    if not os.path.exists(data_path):
                        os.makedirs(data_path)
                    with open(data_path + '/url.txt', 'w') as file:
                        file.write(accWalletUpdate)
                        print(f"{email}: create wallet successfully")

                except (NoSuchElementException, TimeoutException) as e:
                    print(f"Xảy ra lỗi")
            except (NoSuchElementException, TimeoutException) as e:
                print(f"Xảy ra lỗi")
            finally:
                if driver2 is not None:
                    print('Quit')
                    driver2.quit()

        if web == 'https://t.me/PAWSOG_bot/PAWS?startapp=Xe4l4CvT' or 'https://t.me/PAWSOG_bot/PAWS' in web:
            try:
                print('Running Paws')
                chrome_options.add_argument(f'--user-data-dir={profile_path}')
                chrome_options.add_argument('--no-experiments')
                # Add the mobile emulation to the chrome options variable
                chrome_options.add_experimental_option("mobileEmulation", mobile_emulation)
                chrome_options.add_argument(f"window-size={scaled_width},{scaled_height}")
                chrome_options.add_argument(f"window-position={x_position},{y_position}")
                chrome_options.add_argument("force-device-scale-factor=0.6") 
                
                CHROME_EXTENSION_CRX_PATH = self.folder_path + '/chrome_extension/ignore-x-frame-headers/2.0.0_0.crx'
                chrome_options.add_extension(CHROME_EXTENSION_CRX_PATH)
                driver2 = webdriver.Chrome(options=chrome_options)
                if web is not None:
                    driver2.get(web)
                    time.sleep(3)
                wait = WebDriverWait(driver2, 30)
                try:
                    element = wait.until(
                        EC.presence_of_element_located((By.CLASS_NAME, 'tgme_action_web_button'))
                    )
                    ref_link = element.get_attribute('href')
                    ref_link = ref_link.replace('https://web.telegram.org/a/', 'https://web.telegram.org/k/')
                    driver2.get(ref_link)
                except TimeoutException:
                    print("Element with class 'tgme_action_web_button' not found or not clickable within 30 seconds.")
                time.sleep(5)

                try:
                    continue_button = driver2.find_element(By.XPATH, "//button[contains(., 'Launch')]")
                    continue_button.click()
                except (NoSuchElementException, TimeoutException):
                    print("Launch not found")
                time.sleep(5)

                try:
                    # continue_button = driver2.find_element(By.XPATH, "//button[contains(., 'Confirm')]")
                    continue_button = driver2.find_element(By.CSS_SELECTOR, ".confirm-dialog-button")
                    continue_button.click()
                except (NoSuchElementException, TimeoutException):
                    print("confirm not found")
                
                #wait to game load
                time.sleep(10)

                iframe_allow_attr = 'camera; microphone; geolocation;'
                iframe = WebDriverWait(driver2, 50).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, f'iframe[allow="{iframe_allow_attr}"]')))
                
                #get iframe url
                iframe_url = iframe.get_attribute('src')
                iframe_url = iframe_url.replace("tgWebAppPlatform=weba", "tgWebAppPlatform=ios").replace("tgWebAppPlatform=web", "tgWebAppPlatform=ios")
                
                print("Src attribute of the iframe:", iframe_url)
                # driver2.get(iframe_url)

                try:
                    data_path = f"{self.folder_path}/data_login_paws/{email}"
                    if not os.path.exists(data_path):
                        os.makedirs(data_path)
                    with open(data_path + '/url.txt', 'w') as file:
                        file.write(iframe_url)
                except Exception as e:
                    print(f"An error occurred: {e}")

                #wait to game loading
                time.sleep(15)

                print("- SCRIPT GAME CONTROL")
                driver2.switch_to.frame(iframe)
                driver2.execute_script(SCRIPT_GAME_CONTROL_PAWS)
                time.sleep(52)
                # driver2.switch_to.default_content()
                # driver2.execute_script(SCRIPT_WALLET_CONTROL_PAWS)
                # time.sleep(45)

                # driver2.switch_to.default_content()
            except (NoSuchElementException, TimeoutException) as e:
                print(f"Xảy ra lỗi")
            finally:
                if driver2 is not None:
                    print('Quit')
                    driver2.quit()    
    
        if web== 'https://t.me/dogshouse_bot/join?startapp=zySPSgu7Qvmqqaao3JoL4Q' or web == 'https://t.me/dogshouse_bot/join?startapp=zySPSgu7Qvmqqaao3JoL4Q' or 'https://t.me/dogshouse_bot/' in web:
            print('Running DOGS')
            try:
                chrome_options.add_argument(f'--user-data-dir={profile_path}')
                chrome_options.add_argument('--no-experiments')
                chrome_options.add_experimental_option("mobileEmulation", mobile_emulation)
                chrome_options.add_argument(f"window-size={scaled_width},{scaled_height}")
                chrome_options.add_argument(f"window-position={x_position},{y_position}")
                chrome_options.add_argument("force-device-scale-factor=0.6") 


                chrome_options.add_extension(CHROME_EXTENSION_CRX_PATH)
                driver2 = webdriver.Chrome(options=chrome_options)
                if web is not None:
                    driver2.get(web)
                    time.sleep(3)

                try:
                    if web == 'https://web.telegram.org/k/#@major':
                        driver2.execute_script(script_popup)
                        time.sleep(5)
                        try:
                            start_button = driver2.find_element(By.CSS_SELECTOR, "div.new-message-bot-commands-view")
                            start_button.click()
                        except (NoSuchElementException, TimeoutException):
                            continue_button = driver2.find_element(By.XPATH, "//button[contains(., 'START')]")
                            continue_button.click()
                    else:
                        wait = WebDriverWait(driver2, 20)
                        try:
                            element = wait.until(
                                EC.presence_of_element_located((By.CLASS_NAME, 'tgme_action_web_button'))
                            )

                            ref_link = element.get_attribute('href')
                            ref_link = ref_link.replace('https://web.telegram.org/a/', 'https://web.telegram.org/k/')
                            driver2.get(ref_link)
                        except TimeoutException:
                            print(
                                "Element with class 'tgme_action_web_button' not found or not clickable within 30 seconds.")
                            driver2.quit()
                    time.sleep(5)

                    try:
                        continue_button = driver2.find_element(By.XPATH, "//button[contains(., 'Launch')]")
                        continue_button.click()
                    except (NoSuchElementException, TimeoutException):
                        print("Launch not found")
                    time.sleep(2)

                    try:
                        continue_button = driver2.find_element(By.XPATH, "//button[contains(., 'Confirm')]")
                        continue_button.click()
                    except (NoSuchElementException, TimeoutException):
                        print("confirm not found")
                    time.sleep(2)

                    iframe_allow_attr = 'camera; microphone; geolocation;'
                    iframe = WebDriverWait(driver2, 20).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, f'iframe[allow="{iframe_allow_attr}"]')))
                    # get iframe url
                    iframe_url = iframe.get_attribute('src')
                    iframe_url = iframe_url.replace("tgWebAppPlatform=web", "tgWebAppPlatform=ios").replace(
                        "tgWebAppPlatform=web", "tgWebAppPlatform=ios")
                    driver2.switch_to.frame(iframe)
                    driver2.execute_script(SCRIPT_GAME_MAJOR)
                    time.sleep(40)
                    
                except (NoSuchElementException, TimeoutException):
                    print(f"Lỗi: {str(e)}")
            except (NoSuchElementException, TimeoutException) as e:
                print(f"Xảy ra lỗi")
            finally:
                if driver2 is not None:
                    print('Quit')
                    driver2.quit()
        if web == 'https://t.me/MemeX_prelaunch_airdrop_bot?start=ref_code=MX2IMWSD' or 'https://t.me/MemeX_prelaunch_airdrop_bot' in web:
            print('Running MEMEX')
            try:
                chrome_options.add_argument(f'--user-data-dir={profile_path}')
                chrome_options.add_argument('--no-experiments')
                chrome_options.add_experimental_option("mobileEmulation", mobile_emulation)
                chrome_options.add_argument(f"window-size={scaled_width},{scaled_height}")
                chrome_options.add_argument(f"window-position={x_position},{y_position}")
                chrome_options.add_argument("force-device-scale-factor=0.6") 


                chrome_options.add_extension(CHROME_EXTENSION_CRX_PATH)
                driver2 = webdriver.Chrome(options=chrome_options)
                if web is not None:
                    driver2.get(web)
                    time.sleep(3)

                try:
                    
                    
                    wait = WebDriverWait(driver2, 30)
                    try:
                        element = wait.until(
                            EC.presence_of_element_located((By.CLASS_NAME, 'tgme_action_web_button'))
                        )
                        ref_link = element.get_attribute('href')
                        driver2.get(ref_link)
                    except TimeoutException:
                        print("Element with class 'tgme_action_web_button' not found or not clickable within 30 seconds.")
                    time.sleep(2)

                    
                    try:
                        StartBtn = driver2.find_element(By.XPATH, "//button[contains(., 'START')]")
                        StartBtn.click()
                    except (NoSuchElementException, TimeoutException):
                        print("Not found start button ") 
                    time.sleep(10)

                    try:
                        start_button = driver2.find_element(By.CSS_SELECTOR, "div.new-message-bot-commands-view")
                        start_button.click()
                    except (NoSuchElementException, TimeoutException):
                        print("Not found play button")
                        
                    time.sleep(10)

                    try:
                        continue_button = driver2.find_element(By.XPATH, "//button[contains(., 'Launch')]")
                        continue_button.click()
                    except (NoSuchElementException, TimeoutException):
                        print("Launch not found")
                    time.sleep(2)


                    iframe_allow_attr = 'camera; microphone; geolocation;'
                    iframe = WebDriverWait(driver2, 20).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, f'iframe[allow="{iframe_allow_attr}"]')))
                    # get iframe url
                    iframe_url = iframe.get_attribute('src')
                    iframe_url = iframe_url.replace("tgWebAppPlatform=web", "tgWebAppPlatform=ios").replace(
                        "tgWebAppPlatform=web", "tgWebAppPlatform=ios")
                    driver2.switch_to.frame(iframe)
                    driver2.execute_script(SCRIPT_GAME_MEMEX)
                    time.sleep(60)
                    
                except (NoSuchElementException, TimeoutException):
                    print(f"Lỗi: {str(e)}")
            except (NoSuchElementException, TimeoutException) as e:
                print(f"Xảy ra lỗi")
            finally:
                if driver2 is not None:
                    print('Quit')
                    driver2.quit()

        if web == 'http://t.me/seed_coin_bot/app?startapp=7300524587' or 'https://t.me/seed_coin_bot' in web:
            try:
                print('Running seed')
                chrome_options.add_argument(f'--user-data-dir={profile_path}')
                chrome_options.add_argument('--no-experiments')
                # Add the mobile emulation to the chrome options variable
                chrome_options.add_experimental_option("mobileEmulation", mobile_emulation)
                chrome_options.add_argument(f"window-size={scaled_width},{scaled_height}")
                chrome_options.add_argument(f"window-position={x_position},{y_position}")
                chrome_options.add_argument("force-device-scale-factor=0.6") 
                
                CHROME_EXTENSION_CRX_PATH = self.folder_path + '/chrome_extension/ignore-x-frame-headers/2.0.0_0.crx'
                chrome_options.add_extension(CHROME_EXTENSION_CRX_PATH)
                driver2 = webdriver.Chrome(options=chrome_options)
                data_path = f"{self.folder_path}/data_login_seed/{email}/url.txt"
                if web is not None:
                    driver2.get(web)
                    time.sleep(3)

                try:
                    if web == 'https://t.me/seed_coin_bot':
                        driver2.execute_script(script_popup)
                        time.sleep(5)
                        try:
                            start_button = driver2.find_element(By.CSS_SELECTOR, "div.new-message-bot-commands-view")
                            start_button.click()
                        except (NoSuchElementException, TimeoutException):
                            continue_button = driver2.find_element(By.XPATH, "//button[contains(., 'START')]")
                            continue_button.click()
                    else:
                        wait = WebDriverWait(driver2, 30)
                        try:
                            element = wait.until(
                                EC.presence_of_element_located((By.CLASS_NAME, 'tgme_action_web_button'))
                            )
                            ref_link = element.get_attribute('href')
                            driver2.get(ref_link)
                        except TimeoutException:
                            print("Element with class 'tgme_action_web_button' not found or not clickable within 30 seconds.")

                    time.sleep(10)

                    try:
                        continue_button = driver2.find_element(By.XPATH, "//button[contains(., 'Launch')]")
                        continue_button.click()
                    except (NoSuchElementException, TimeoutException):
                        print("Launch not found")
                    time.sleep(2)

                    try:
                        continue_button = driver2.find_element(By.XPATH, "//button[contains(., 'Confirm')]")
                        continue_button.click()
                    except (NoSuchElementException, TimeoutException):
                        print("confirm not found")
                    time.sleep(2)

                    iframe_allow_attr = 'camera; microphone; geolocation;'
                    iframe = WebDriverWait(driver2, 20).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, f'iframe[allow="{iframe_allow_attr}"]')))
                    # get iframe url
                    iframe_url = iframe.get_attribute('src')
                    iframe_url = iframe_url.replace("tgWebAppPlatform=weba", "tgWebAppPlatform=ios").replace(
                        "tgWebAppPlatform=web", "tgWebAppPlatform=ios")
                    try:
                        data_path = f"{self.folder_path}/data_login_seed/{email}"
                        if not os.path.exists(data_path):
                            os.makedirs(data_path)
                        with open(data_path + '/url.txt', 'w') as file:
                            file.write(iframe_url)
                    except Exception as e:
                        print(f"An error occurred: {e}")

                    driver2.switch_to.frame(iframe)
                    print("- SCRIPT GAME CONTROL")
                    time.sleep(10)
                    # driver2.execute_script(script_login)
                    driver2.execute_script(SCRIPT_GAME_SEED)
                    time.sleep(25)
                    print("- Done")

                except (NoSuchElementException, TimeoutException):
                    print(f"Lỗi: {str(e)}")
            except (NoSuchElementException, TimeoutException) as e:
                print(f"Xảy ra lỗi")
            finally:
                if driver2 is not None:
                    print('Quit')
                    driver2.quit()

    def run_script_from_file(self, driver, file_path, run_time):
        try:
            print(f"Start run script from file: {file_path}")
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding="utf8") as file:
                    script_auto_tap = file.read()
                    driver.execute_script(script_auto_tap)
                    time.sleep(run_time)

                    file.close()
            else:
                print(f"Not exist script file: {file_path}")
        except Exception as e:
            print(f"Run script from file error: {e}")

    def stop_event(self):
        # Event to indicate whether the threads should continue running
        stop_event = threading.Event()


        time.sleep(5)
        stop_event.set()

        # Wait for the worker thread to finish
        print("Worker thread stopped")

    def hold_coin(self, token, coins_hold, proxies=None):
        url = "https://major.bot/api/bonuses/coins/"
        payload = {"coins": coins_hold}
        data = self.request("POST", url, token, proxies=proxies, json=payload)

        if data:
            if data.get("success", False):
                return True

            detail = data.get("detail", {})
            blocked_until = detail.get("blocked_until")

            if blocked_until is not None:
                blocked_until_time = datetime.fromtimestamp(blocked_until).strftime('%Y-%m-%d %H:%M:%S')
        return False

    def all_acction(self):
        # input_text = self.input_text.toPlainText()
        # profiles_data = input_text.strip().split('\n')
        global accList
        global futures
        num_threads_text = self.input_thread.toPlainText()

        try:
            num_threads = int(num_threads_text)
        except ValueError:
            print("Invalid input for number of threads")
            num_threads = 1  # Default to 1 thread if input is invalid

        event = threading.Event()
        keys_list = list(accList.keys())
        length = len(keys_list)

        with ThreadPoolExecutor(max_workers=num_threads) as executor:
            for i in range(length):
                email = keys_list[i]
                future = executor.submit(self.open_url, email, event)
                futures.append(future)
                time.sleep(2)
        self.all_acction()

    def open_url(self, email, event):
        webStr = self.input_custom.toPlainText()
        webList = webStr.split(" ")
        profile_path = f"{self.folder_path}/profiles/{email}"
        for web in webList:
            if os.path.exists(profile_path):
                # event.wait()
                self.open_url_in_thread(profile_path, web, email)

    def request(self, method, url, token, proxies=None, json=None, url_root="https://major.bot/"):
        try:
            response = requests.request(
                method, url, headers=headers(token=token, url_root=url_root), proxies=proxies, json=json, timeout=20
            )
            return response.json()
        except requests.exceptions.RequestException as e:
            return None

    
    def start_game_tomarket(self, token, proxy=None):
        url = "https://api-web.tomarket.ai/tomarket-game/v1/game/play"
        print('Playing game tomarket')
        headers = headers_tomarket

        headers["Authorization"] = token

        payload = {"game_id": "59bcd12e-04e2-404c-a172-311a0084587d"}

        data = json.dumps(payload)

        headers["Content-Length"] = str(len(data))
        headers["Content-Type"] = "application/json"
        if proxy:
            response = requests.post(url=url, headers=headers, data=data, proxies=proxy)
        else:
            response = requests.post(url=url, headers=headers, data=data)

        return response
    
    def set_wallet_game_tomarket(self, token, wallet, proxy=None):
        url = "https://api-web.tomarket.ai/tomarket-game/v1/tasks/address"
        print('wallet game tomarket')
        headers = headers_tomarket

        headers["Authorization"] = token

        payload = {"wallet_address": wallet}

        data = json.dumps(payload)

        headers["Content-Length"] = str(len(data))
        headers["Content-Type"] = "application/json"
        if proxy:
            response = requests.post(url=url, headers=headers, data=data, proxies=proxy)
        else:
            response = requests.post(url=url, headers=headers, data=data)

        return response
    
    def claim_game_tomarket(self, token, point, proxy=None):
        url = "https://api-web.tomarket.ai/tomarket-game/v1/game/claim"
        print('Claim game tomarket')
        headers = headers_tomarket

        headers["Authorization"] = token

        payload = {"game_id": "59bcd12e-04e2-404c-a172-311a0084587d", "points": point}

        data = json.dumps(payload)

        headers["Content-Length"] = str(len(data))
        headers["Content-Type"] = "application/json"
        if proxy:
            response = requests.post(url=url, headers=headers, data=data, proxies=proxy)
        else:
            response = requests.post(url=url, headers=headers, data=data)

        return response

    def load_profile(self):
        global accList
        global proxy
        input_text = self.input_text.toPlainText()
        profiles_data = input_text.strip().split('\n')

        for profile_data in profiles_data:
            if '|' in profile_data:
                email, wallet, key = profile_data.split('|')
            accList[email] = {
                'wallet': wallet,
                'key': key,
            }

        

        self.clear_table()
        self.add_profile_to_table(accList)

    def clear_table(self):
        self.profile_table.setRowCount(0)

    def add_profile_to_table(self, accList):
        for email, value in accList.items():
            row_position = self.profile_table.rowCount()
            self.profile_table.insertRow(row_position)
            self.profile_table.setItem(row_position, 0, QTableWidgetItem(email))
            open_cmd_button = QPushButton('Delete profile')
            open_cmd_button.clicked.connect(lambda _, email=email: self.open_cmd(email))
            self.profile_table.setCellWidget(row_position, 1, open_cmd_button)
            
            open_blums_button = QPushButton('Go to Blums')
            open_blums_button.clicked.connect(lambda _, email=email: self.open_blums(email))
            self.profile_table.setCellWidget(row_position, 2, open_blums_button)
            open_profile_button = QPushButton('Go to profile')
            open_profile_button.clicked.connect(lambda _, email=email: self.open_profile(email))
            self.profile_table.setCellWidget(row_position, 3, open_profile_button)
            data_path = f"{self.folder_path}/data_login_blums/{email}"
            if os.path.exists(data_path):
                self.profile_table.setItem(row_position, 4, QTableWidgetItem('Login Blumns'))
            else:
                self.profile_table.setItem(row_position, 4, QTableWidgetItem('-'))
            auto_login_tele = QPushButton('Login tele')
            auto_login_tele.clicked.connect(lambda _, email=email: self.start_asyncio_task(email))
            self.profile_table.setCellWidget(row_position, 5 , auto_login_tele)

    def start_asyncio_task(self, email):
        print('Task')
        asyncio.ensure_future(self.login_tele(email))


    async def login_tele(self, email):
        profile_path = f"{self.folder_path}/profiles/{email}"
        print('Account')
        print(email)
        script_tele = f"""
                function clickButtonLogin() {{
                    console.log('Running')
                    var button_login = document.querySelector('#auth-pages .input-wrapper button')
                    if(button_login && button_login.textContent == 'Log in by phone Number'){{
                        button_login.click();
                    }}
                    
                }}
                function pressInputLogin() {{
                    var input_login = document.querySelector('#auth-pages .input-wrapper .input-field-phone .input-field-input')
                    if(input_login){{
                        input_login.textContent = '+' + {email};
                        var event = new Event('input', {{
                            bubbles: true,
                        }});
                        input_login.dispatchEvent(event);
                        input_login.textContent = '+' + {email};
                        setTimeout(() => {{
                            var button_next = document.querySelector('#auth-pages .input-wrapper button')
                            if(button_next && button_next.textContent == 'Next'){{
                                button_next.click()
                            }}
                        }}, 1500)
                        
                        
                    }}
                    
                }}
                setInterval(clickButtonLogin, 3000);
                setInterval(pressInputLogin, 5000);
            """
        if not os.path.exists(profile_path):
            os.makedirs(profile_path)
        try:
            options = Options()
            options.add_argument(f'--user-data-dir={profile_path}')
            options.add_argument('--no-experiments')
            driver3 = webdriver.Chrome(options=options)
            driver3.get('https://web.telegram.org/k')
            driver3.execute_script(script_tele)

            time.sleep(15)
            WebDriverWait(driver3, 25).until(EC.presence_of_element_located((By.ID, 'auth-pages')))
            
            
            print('Start OTP')
            session_name = f"{self.folder_path}/data_session/{email}/{email}.session"
            api_id = '24557220'
            api_hash = ''
            
            try:
                client = TelegramClient(session_name, api_id, api_hash)
                client.connect()
                time.sleep(3)
                if client.is_user_authorized():
                    print("\n―― 🟢 User Authorized!")

                    @client.on(events.NewMessage(from_users=777000))  # '777000' is the ID of Telegram Notification Service.
                    async def catch_msg(event):
                        otp = re.search(r'\b(\d{5})\b', event.raw_text)
                        if otp:
                            print("\n―― OTP received ✅\n―― Your login code:", otp.group(0))
                            path_opt = f"{self.folder_path}/otp/{email}"
                            
                            if not os.path.exists(path_opt):
                                os.makedirs(path_opt)
                            
                            with open(path_opt + '/otp.txt', 'w') as file:
                                file.write(otp)

                            script_otp = f"""
                                setInterval(() => {{
                                    var input_otp = document.querySelector('#auth-pages .input-wrapper input.input-field-input');
                                    if(input_otp){{
                                        input_otp.removeAttribute('disabled');
                                        input_otp.value = '{otp}';
                                        var event = new Event('input', {{
                                            bubbles: true,
                                        }});
                                        input_otp.dispatchEvent(event);
                                        var changeEvent = new Event('change', {{
                                            bubbles: true
                                        }});
                                        input_otp.dispatchEvent(changeEvent);
                                        input_otp.focus();
                                    }}
                                }}, 3000);
                            """
                            await asyncio.sleep(15)
                            asyncio.create_task(driver3.execute_script(script_otp))

                    print("Please login to your telegram app. [Listening for OTP...]\n")
                    driver3.get('https://web.telegram.org/k')
                    driver3.execute_script(script_tele)
                    time.sleep(30)
                    try:
                        await asyncio.wait_for(client.run_until_disconnected(), timeout=80)
                    except asyncio.CancelledError:
                        print("Telegram client was cancelled.")
                        driver3.quit()
                        return
                    finally:
                        await client.disconnect()
                        driver3.quit()
                        return
                    
                else:
                    print("\n―― 🔴 Authorization Failed!"
                        "\n―― Invalid Telethon session file or the session has expired.")
            except sqlite3.OperationalError:
                print("\n―― ⚠️ Invalid Telethon session file. Please ensure you are using a Telethon session file.")
            except t_errors.RPCError as e:
                print(f"\n―― ❌ An RPC error occurred: {e}")
            except Exception as e:
                print(f"\n―― ❌ An unexpected error occurred: {e}")

           
            time.sleep(5)

        except TimeoutException:
            print('Error')
            if driver3 is not None:
                print('Quit')
                driver3.quit()
        finally:
            if driver3 is not None:
                print('Quit')
                driver3.quit()

    def stop_script_execution(self):
        # Method to stop the task
        if self.script_task:
            self.script_task.cancel()
            print("Script execution stopped.")
    def open_cmd(self, email):
        print(email)
        profile_dir = f"{self.folder_path}/profiles/{email}"
        for item in os.listdir(profile_dir):
            item_path = os.path.join(profile_dir, item)
            if os.path.isdir(item_path):
                shutil.rmtree(item_path)
            else:
                os.remove(item_path)
        print('Delete OK')
    def open_profile(self, email):
        # Kiểm tra xem thư mục lưu trữ hồ sơ đã tồn tại
        profile_path = f"{self.folder_path}/profiles/{email}"
        print('Account')
        print(email)
        chrome_options = Options()
        driver3 = None
        if not os.path.exists(profile_path):
            os.makedirs(profile_path)
        try:
            chrome_options.add_argument(f'--user-data-dir={profile_path}')
            chrome_options.add_argument('--no-experiments')
            
            driver3 = webdriver.Chrome(options=chrome_options)
            time.sleep(2)
            driver3.get('https://web.telegram.org/k')

            driver3.execute_script(SCRIPT_QUIT)
            try:
                WebDriverWait(driver3, 3000).until(EC.presence_of_element_located((By.ID, 'facebook')))
            except Exception as e:
                    print(f"An error occurred: {e}")

            return driver3

        except Exception as e:
            print(f"An error occurred: {e}")
            if driver3 is not None:
                print('Quit')
                driver3.quit()
        finally:
            if driver3 is not None:
                print('Quit')
                driver3.quit()

    def open_blums(self, email):
        profile_path = f"{self.folder_path}/profiles/{email}"
        print('Account')
        print(email)
        chrome_options = Options()
        driver3 = None
        if not os.path.exists(profile_path):
            os.makedirs(profile_path)
        try:
            chrome_options.add_argument(f'--user-data-dir={profile_path}')
            chrome_options.add_argument('--no-experiments')
            # Add the mobile emulation to the chrome options variable
            chrome_options.add_experimental_option("mobileEmulation", mobile_emulation)
            chrome_options.add_argument(f"window-size=400,886")

            CHROME_EXTENSION_CRX_PATH = self.folder_path + '/chrome_extension/ignore-x-frame-headers/2.0.0_0.crx'
            chrome_options.add_extension(CHROME_EXTENSION_CRX_PATH)
            driver3 = webdriver.Chrome(options=chrome_options)
            time.sleep(2)
            driver3.get('https://web.telegram.org/k/#@BlumCryptoBot')

            driver3.execute_script(SCRIPT_QUIT)
            try:
                iframe_allow_attr = 'camera; microphone; geolocation;'
                iframe = WebDriverWait(driver3, 50).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, f'iframe[allow="{iframe_allow_attr}"]')))
                # get iframe url
                iframe_url = iframe.get_attribute('src')
                iframe_url = iframe_url.replace("tgWebAppPlatform=weba", "tgWebAppPlatform=ios").replace(
                    "tgWebAppPlatform=web", "tgWebAppPlatform=ios")
                try:
                    data_path = f"{self.folder_path}/data_login_blums/{email}"
                    if not os.path.exists(data_path):
                        os.makedirs(data_path)
                    with open(data_path + '/url.txt', 'w') as file:
                        file.write(iframe_url)
                except Exception as e:
                    print(f"An error occurred: {e}")
                driver3.switch_to.frame(iframe)
                print("- SCRIPT GAME CONTROL")
                # driver2.execute_script(script_login)
                driver3.execute_script(SCRIPT_GAME_BLUM)
                time.sleep(13)
                token = driver3.execute_script("return localStorage;")
                print(token)
                self.run_script_from_file(driver3, self.folder_path + "/blum.txt", 36)

                print("- Done")
                driver3.switch_to.default_content()

                WebDriverWait(driver3, 3000).until(EC.presence_of_element_located((By.ID, 'facebook')))
            except TimeoutException:
                print("Element with class 'tgme_action_web_button' not found or not clickable within 30 seconds.")

            return driver3

        except TimeoutException:
            print('Error')
            if driver3 is not None:
                print('Quit')
                driver3.quit()
        finally:
            if driver3 is not None:
                print('Quit')
                driver3.quit()


def select_folder():
    root = Tk()
    root.withdraw()  # Hide the root window
    selected_folder = filedialog.askdirectory(initialdir="C:/", title="Select Folder")
    return selected_folder


def headers(token=None, url_root="https://major.bot/"):
    headers = {
        "Accept": "application/json, text/plain, */*",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Accept-Language": "id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7",
        "Priority": "u=1, i",
        "Referer": url_root,
        "Sec-CH-UA": '"Chromium";v="128", "Not;A=Brand";v="24", "Google Chrome";v="128"',
        "Sec-CH-UA-Mobile": "?0",
        "Sec-CH-UA-Platform": '"Windows"',
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",

    }

    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers

def get_token(data, urlAuth, url_root, proxy=None):
    url = urlAuth
    payload = {"init_data": data}
    print('Get Token')
    try:
        if proxy:
            response = requests.post(
                url=url, headers=headers(None, url_root), json=payload, timeout=30, proxies=proxy
            )
        else:
            response = requests.post(
                url=url, headers=headers(None, url_root), json=payload, timeout=30
            )
        
        data = response.json()
        token = data["access_token"]
        return token
    except:
        return None

def get_token_tomarket(data, urlAuth, url_root, proxy=None):
    url = "https://api-web.tomarket.ai/tomarket-game/v1/user/login"
    data = json.dumps(
        {
            "init_data": data,
            "invite_code": "",
        }
    )
    headers = headers_tomarket
    print('Get Token Tomarket')
    try:
        response = requests.post(
            url=url, headers=headers, data=data, timeout=20
        )
        if proxy:
            response = requests.post(
                url=url, headers=headers, data=data, timeout=30, proxies=proxy
            )
        else:
            response = requests.post(
                url=url, headers=headers, data=data, timeout=30
            )
        data_res = response.json().get("data")
        token = data_res.get("access_token")
        return token
    except:
        return None


async def main():
    # Create an instance of QApplication
    app = QApplication(sys.argv)

    # Select folder before running ChromeProfileManager
    folder_path = select_folder()
    if not folder_path:
        print("No folder selected.")
        return

    # Create an instance of ChromeProfileManager with the selected folder path
    ex = ChromeProfileManager(folder_path)
    ex.show()
    
    # Integrate asyncio event loop with PyQt5 event loop using qasync
    loop = QEventLoop(app)
    asyncio.set_event_loop(loop)

    with loop:
        await loop.run_forever()
    # sys.exit(app.exec_())
if __name__ == "__main__":
    asyncio.run(main())


