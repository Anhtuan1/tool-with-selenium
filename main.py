
import time
import os
import sqlite3
import asyncio
from concurrent.futures import ThreadPoolExecutor, wait, as_completed
from datetime import datetime
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTextEdit, QPushButton, QLineEdit, QTableWidget, QTableWidgetItem, QFileDialog
import qasync
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import requests
import json
import threading
from selenium.common.exceptions import NoSuchElementException, TimeoutException, NoAlertPresentException
from selenium.webdriver.common.keys import Keys

import pyperclip
import re
import csv

try:
    from telethon.sync import TelegramClient, events
    from telethon.sessions import StringSession
    from telethon.tl.types import Channel
    from telethon import functions
    import telethon.errors
except ModuleNotFoundError:
    print("Error: Telethon library is not installed. Please install it using 'pip install telethon'")


accList = {}
num_thread_running = 0
futures = []
url_ref = 'https://t.me/waveonsuibot/walletapp?startapp='
class ChromeProfileManager(QMainWindow):
    threads = []
    def __init__(self):
        super().__init__()

        self.initUI()
        self.profiles = []

    def initUI(self):
        loaddataPath = "C:/path/to/loaddata.txt"

        # Check if the file exists
        if os.path.exists(loaddataPath):
            # Open the file in read mode
            with open(loaddataPath, 'r') as file:
                # Read the contents of the file
                file_contents = file.read()
                # Now you can work with the contents, for example:

        else:
            with open('C:/path/to/loaddata.txt', 'w') as file:
                file.write('')
            file_contents = ''

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

        self.setRefBtn = QPushButton('Set referent')
        self.setRefBtn.clicked.connect(self.setRef)
        self.input_layout.addWidget(self.setRefBtn)




        # Cột phải - Hiển thị thông tin profile
        self.profile_table = QTableWidget()
        self.profile_table.setColumnCount(7)
        self.profile_table.setHorizontalHeaderLabels(['ID', 'Wallet', 'Key', 'Action', 'Login', 'Auto Login Telegram', 'Create game'])

        self.right_layout = QVBoxLayout()
        self.right_layout.addWidget(QLabel('Thông tin profile:'))
        self.right_layout.addWidget(self.profile_table)

        self.actionLayout = QVBoxLayout()

        self.input_morning = QTextEdit()
        self.input_morning.setFixedHeight(30)
        self.input_morning.setText('8')
        self.input_morning.setPlaceholderText('Time of morning')

        self.input_thread = QTextEdit()
        self.input_thread.setFixedHeight(30)
        self.input_thread.setText('1')
        self.input_thread.setPlaceholderText('Number thread')

        self.input_custom = QTextEdit()
        self.input_custom.setFixedHeight(50)
        self.input_custom.setText('https://web.telegram.org/a/#6430669852')
        self.input_custom.setPlaceholderText('Url custom')

        self.all_mining = QPushButton('All start')
        self.stop_mining = QPushButton('Stop')

        self.actionLayout.addWidget(self.input_custom)
        self.actionLayout.addWidget(self.input_thread)
        self.actionLayout.addWidget(self.input_morning)
        self.actionLayout.addWidget(self.all_mining)
        self.actionLayout.addWidget(self.stop_mining)
        self.all_mining.clicked.connect(self.all_acction)
        self.stop_mining.clicked.connect(self.stop_event)
        self.input_layout.addLayout(self.actionLayout)
        self.layout.addLayout(self.input_layout)
        self.layout.addLayout(self.right_layout)

    def load_session(self):
        loaddataSession = "C:/path/to/data_session"

        # Check if the file exists
        if os.path.exists(loaddataSession):
            # Get a list of all entries in the directory
            entries = os.listdir(loaddataSession)

            # Filter out entries that are not directories
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
            profile_path = f"C:/path/to/profiles/{key}"
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
                data_path = f"C:/path/to/data_login/{key}/url.txt"
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
        asyncio.ensure_future(self.on_login_with_session())

    async def on_login_with_session(self):
        global accList
        input_text = self.input_text.toPlainText()
        profiles_data = input_text.strip().split('\n')
        for profile_data in profiles_data:
            parts = profile_data.split('|')
            email = parts[0]
            data_path = f"C:/path/to/data_login/{email}/url.txt"
            if not os.path.exists(data_path):
                await self.login_tele(email)
                self.open_url_setup_game(email)

        self.all_acction()


    def open_url_setup_game(self, email):
        # def run_thread():
        profile_path = f"C:/path/to/profiles/{email}"
        data_path_ref = f"C:/path/to/url_ref.txt"
        if not os.path.exists(data_path_ref):
            with open(data_path_ref, 'w') as file:
                file.write(url_ref + '1724221')
        with open(data_path_ref, 'r') as file:
            web = file.read().strip()
            chrome_options = Options()
            print(f"Running: {str(email)}")
            driver2 = None
            global accList
            key = accList[email]["key"]
            print(key)
            script_login = f"""
                        var key = '{key}';
                        setInterval(() => {{
                            if (document.querySelector(".body_button .btn-login")) {{
                                document.querySelector(".body_button .btn-login").click();
                                setTimeout(() => {{
                                    document.querySelector("#section-login textarea").value = key;
                                    document.querySelector("#section-login textarea").dispatchEvent(new Event('input'));
                                    setTimeout(() => {{
                                        document.querySelector("#section-login .btn-continue").click();
                                    }}, 1000);
                                }}, 1000);
                            }}
                        }}, 3000);
                        """
            script = """
                            function clickButton() {
                                var button = document.querySelector("button.btn_claim");
                                if (button) {
                                    button.click();
                                }
                            }
                            function clickButtonGetClaim() {
                                var button = document.querySelector(".claim.cursor-pointer");
                                if (button) {
                                    button.click();
                                }
                            }
                            function checkBalance() {
                                var wave_balance = document.querySelector(".wave-balance").textContent;
                                var fish_block = document.querySelector(".block-data .right .btn-add").textContent;
                                var is_running = document.querySelector(".block-data .info .boat_balance").textContent
                                var level = document.querySelector(".menu-block .menu_2  .menu_title .time").textContent
                                if(wave_balance < 10 && fish_block == 'x 1' && is_running < 2 && is_running != 1) {
                                    document.querySelector(".block-data .absolute .cursor-pointer").click();
                                    setTimeout(() => {
                                        document.querySelector('#section-mission .block-gas button').click();
                                        setTimeout(() => {
                                            if(document.querySelectorAll('.btn-upgrade')[1].textContent == 'Claim'){
                                                document.querySelectorAll('.btn-upgrade')[1].click();
                                            }
                                        },3000)
                                    },1000)
    
                                }
                                if(level == '1 /hours' && is_running < 2.5 && wave_balance >= 20){
                                    document.querySelector(".menu-block .menu_2  .block-btn button").click();
                                    setTimeout(() => {
                                        document.querySelector(".modal-content .btn-upgrade").click();
                                    }, 1000)
                                }
                            }
                            setInterval(clickButton, 1000);
                            setInterval(clickButtonGetClaim, 2000);
                            setTimeout(checkBalance, 3000);
                            """
            script_start_button = """
                    setInterval(() =>{
                        var start_btn = document.querySelector(".chat-input-control-button");
                        if(start_btn && start_btn.textContent == 'START'){
                            start_btn.click()
                        }
                    }, 6000);
                """
            print(web)

            if web is not None:
                try:
                    chrome_options.add_argument(f'--user-data-dir={profile_path}')
                    chrome_options.add_argument('--no-experiments')

                    driver2 = webdriver.Chrome(options=chrome_options)

                    driver2.get(web)
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
                    driver2.execute_script(script_start_button)
                    time.sleep(8)
                    try:
                        play_button = WebDriverWait(driver2, 15).until(EC.presence_of_element_located(
                            (By.CSS_SELECTOR, 'span.bot-menu-text')))
                        play_button.click()
                    except (NoSuchElementException, TimeoutException):
                        print('Play button not found')
                        try:
                            start_button = WebDriverWait(driver2, 15).until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.new-message-bot-commands-view")))
                            start_button.click()
                        except (NoSuchElementException, TimeoutException):
                            print('start button not found')


                    try:
                        continue_button = WebDriverWait(driver2, 15).until(EC.presence_of_element_located((By.XPATH, "//button[contains(., 'Launch')]")))
                        continue_button.click()
                    except (NoSuchElementException, TimeoutException):
                        print("Launch not found")

                    try:
                        continue_button = WebDriverWait(driver2, 10).until(EC.presence_of_element_located((By.XPATH, "//button[contains(., 'Confirm')]")))
                        continue_button.click()
                    except (NoSuchElementException, TimeoutException):
                        print("confirm not found")

                    iframe_allow_attr = 'camera; microphone; geolocation;'
                    iframe = WebDriverWait(driver2, 80).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, f'iframe[allow="{iframe_allow_attr}"]')))
                    iframe_url = iframe.get_attribute('src')
                    # driver2.get(iframe_url)
                    try:
                        data_path = f"C:/path/to/data_login/{email}"
                        if not os.path.exists(data_path):
                            os.makedirs(data_path)
                        with open(data_path + '/url.txt', 'w') as file:
                            file.write(iframe_url)
                    except Exception as e:
                        print(f"An error occurred: {e}")

                    driver2.switch_to.frame(iframe)
                    driver2.execute_script(script_login)
                    driver2.execute_script(script)
                    time.sleep(40)
                    data_path = f"C:/path/to/data_login/{email}/url.txt"
                    if os.path.exists(data_path):
                        with open(data_path, 'r') as file:
                            url = file.read().strip()
                            driver2.get(url)
                            time.sleep(3)
                            driver2.get('https://walletapp.waveonsui.com/friends')
                            time.sleep(5)
                    try:
                        btn_invite = driver2.find_element(By.XPATH, "//button[contains(., 'Invite a Friend')]")
                        btn_invite.click()
                        time.sleep(2)
                        clipboard_content = pyperclip.paste()
                        pattern = r"startapp=(\d+)"
                        match = re.search(pattern, clipboard_content)
                        if match:
                            numeric_id = match.group(1)
                            print(f"Extracted numeric ID: {numeric_id}")
                            with open('C://path/to/url_ref.txt', 'w') as file:
                                file.write(url_ref + str(numeric_id))
                        else:
                            print("No match found")

                    except (NoSuchElementException, TimeoutException):
                        print(f"Lỗi: {str(e)}")

                except (NoSuchElementException, TimeoutException) as e:
                    print(f"Xảy ra lỗi")
                finally:
                    if driver2 is not None:
                        print('Quit')
                        driver2.quit()
                # threading.Thread(target=run_thread).start()

    def open_url_in_thread(self, profile_path, web, email):
        # def run_thread():
        chrome_options = Options()
        print(f"Running: {str(email)}")
        driver2 = None
        global accList
        key = accList[email]["key"]
        print(key)
        script_login = f"""
            var key = '{key}';
            setInterval(() => {{
                if (document.querySelector(".body_button .btn-login")) {{
                    document.querySelector(".body_button .btn-login").click();
                    setTimeout(() => {{
                        document.querySelector("#section-login textarea").value = key;
                        document.querySelector("#section-login textarea").dispatchEvent(new Event('input'));
                        setTimeout(() => {{
                            document.querySelector("#section-login .btn-continue").click();
                        }}, 1000);
                    }}, 1000);
                }}
            }}, 3000);
            """
        script = """
                function clickButton() {
                    var button = document.querySelector("button.btn_claim");
                    if (button) {
                        button.click();
                    }
                }
                function clickButtonGetClaim() {
                    var button = document.querySelector(".claim.cursor-pointer");
                    if (button) {
                        button.click();
                    }
                }
                function checkBalance() {
                    var wave_balance = document.querySelector(".wave-balance").textContent;
                    var fish_block = document.querySelector(".block-data .right .btn-add").textContent;
                    var is_running = document.querySelector(".block-data .info .boat_balance").textContent
                    var level = document.querySelector(".menu-block .menu_2  .menu_title .time").textContent
                    if(wave_balance < 10 && fish_block == 'x 1' && is_running < 2 && is_running != 1) {
                        document.querySelector(".block-data .absolute .cursor-pointer").click();
                        setTimeout(() => {
                            document.querySelector('#section-mission .block-gas button').click();
                            setTimeout(() => {
                                if(document.querySelectorAll('.btn-upgrade')[1].textContent == 'Claim'){
                                    document.querySelectorAll('.btn-upgrade')[1].click();
                                }
                            },3000)
                        },1000)
    
                    }
                    if(level == '1 /hours' && is_running < 2.5 && wave_balance >= 20){
                        document.querySelector(".menu-block .menu_2  .block-btn button").click();
                        setTimeout(() => {
                            document.querySelector(".modal-content .btn-upgrade").click();
                        }, 1000)
                    }
                }
                setInterval(clickButton, 1000);
                setInterval(clickButtonGetClaim, 2000);
                setTimeout(checkBalance, 3000);
                """
        if web == 'https://web.telegram.org/a/#6430669852':
            print(web)
            try:
                chrome_options.add_argument(f'--user-data-dir={profile_path}')
                chrome_options.add_argument('--no-experiments')
                driver2 = webdriver.Chrome(options=chrome_options)
                data_path = f"C:/path/to/data_login/{email}/url.txt"
                if os.path.exists(data_path):
                    with open(data_path, 'r') as file:
                        url = file.read().strip()
                    driver2.get(url)
                    time.sleep(2)
                    driver2.execute_script(script_login)
                    driver2.execute_script(script)
                    time.sleep(13)
                else:
                    if web is not None:
                        driver2.get(web)
                        time.sleep(5)

                    try:

                        try:
                            wait = WebDriverWait(driver2, 20)
                            play_button = wait.until(EC.presence_of_element_located(
                                (By.CSS_SELECTOR, 'span.bot-menu-text')))
                            play_button.click()
                        except (NoSuchElementException, TimeoutException):
                            start_button = driver2.find_element(By.CSS_SELECTOR, "div.new-message-bot-commands-view")
                            start_button.click()

                        time.sleep(2)

                        try:
                            continue_button = driver2.find_element(By.XPATH, "//button[contains(., 'Launch')]")
                            continue_button.click()
                        except (NoSuchElementException, TimeoutException):
                            print("Launch not found")

                        try:
                            continue_button = driver2.find_element(By.XPATH, "//button[contains(., 'Confirm')]")
                            continue_button.click()
                        except (NoSuchElementException, TimeoutException):
                            print("confirm not found")

                        iframe_allow_attr = 'camera; microphone; geolocation;'
                        iframe = WebDriverWait(driver2, 50).until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, f'iframe[allow="{iframe_allow_attr}"]')))
                        iframe_url = iframe.get_attribute('src')
                        print("Src attribute of the iframe:", iframe_url)
                        try:
                            data_path = f"C:/path/to/data_login/{email}"
                            if not os.path.exists(data_path):
                                os.makedirs(data_path)
                            with open(data_path + '/url.txt', 'w') as file:
                                file.write(iframe_url)
                        except Exception as e:
                            print(f"An error occurred: {e}")

                        driver2.switch_to.frame(iframe)
                        driver2.execute_script(script_login)
                        driver2.execute_script(script)
                        time.sleep(20)

                        driver2.switch_to.default_content()
                    except (NoSuchElementException, TimeoutException):
                        print(f"Lỗi: {str(e)}")

            except (NoSuchElementException, TimeoutException) as e:
                print(f"Xảy ra lỗi")
            finally:
                if driver2 is not None:
                    print('Quit')
                    driver2.quit()
                # threading.Thread(target=run_thread).start()

    def stop_event(self):
        # Event to indicate whether the threads should continue running
        stop_event = threading.Event()


        time.sleep(5)
        stop_event.set()

        # Wait for the worker thread to finish
        print("Worker thread stopped")


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
        self.all_acction()

    def open_url(self, email, event):
        web = self.input_custom.toPlainText()
        profile_path = f"C:/path/to/profiles/{email}"
        if os.path.exists(profile_path):
            # event.wait()
            self.open_url_in_thread(profile_path, web, email)

    def open_url_login(self, email, event):
        web = self.input_custom.toPlainText()
        profile_path = f"C:/path/to/profiles/{email}"
        if os.path.exists(profile_path):
            # event.wait()
            self.open_url_in_thread(profile_path, 'https://www.mycloudwallet.com/signin', email)

    def load_profile(self):
        global accList
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
            self.profile_table.setItem(row_position, 1, QTableWidgetItem(value.get('wallet', '')))
            self.profile_table.setItem(row_position, 2, QTableWidgetItem(value.get('key', '')))
            open_profile_button = QPushButton('Add Session')
            open_profile_button.clicked.connect(lambda _, email=email: self.open_profile(email))
            self.profile_table.setCellWidget(row_position, 3, open_profile_button)
            data_path = f"C:/path/to/data_login/{email}"
            if os.path.exists(data_path):
                self.profile_table.setItem(row_position, 4, QTableWidgetItem('Login OK'))
            else:
                self.profile_table.setItem(row_position, 4, QTableWidgetItem('-'))
            auto_login_tele = QPushButton('Login tele')
            auto_login_tele.clicked.connect(lambda _, email=email: self.start_asyncio_task(email))
            self.profile_table.setCellWidget(row_position, 5 , auto_login_tele)

            auto_create_game = QPushButton('Create game')
            auto_create_game.clicked.connect(lambda _, email=email: self.open_url_setup_game(email))
            self.profile_table.setCellWidget(row_position, 6, auto_create_game)

    def start_asyncio_task(self, email):
        print('Task')
        asyncio.ensure_future(self.login_tele(email))


    async def login_tele(self, email):
        profile_path = f"C:/path/to/profiles/{email}"
        print('Account')
        print(email)
        data_path = f"C:/path/to/data_login/{email}/url.txt"
        if not os.path.exists(data_path):
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

                print('Start OTP')
                api_id = ''
                api_hash = ''
                session_name = f"C:/path/to/data_session/{email}/{email}.session"

                try:
                    async with TelegramClient(session_name, api_id, api_hash) as client:
                        print("Telegram client started")

                        @client.on(events.NewMessage(from_users=777000))
                        async def handler(event):
                            print("Message received:", event.raw_text)
                            otp_match = re.search(r'\b(\d{5})\b', event.raw_text)
                            if otp_match:
                                print("OTP received:", otp_match.group(0))
                                otp = otp_match.group(0)
                                path_opt = f"C://path/to/otp/{email}"
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
                                        }},3000);
                                    """
                                try:
                                    await asyncio.sleep(8)
                                    asyncio.create_task(driver3.execute_script(script_otp))
                                except Exception as e:
                                    print(f"Error executing script: {e}")
                                    # Print detailed error information
                                    print(f"Script: {script_otp}")
                                    raise
                                await client.disconnect()
                        print("Please login to your telegram app. [Listening for OTP...]\n")
                        driver3.get('https://web.telegram.org/k')
                        driver3.execute_script(script_tele)
                        try:
                            await asyncio.wait_for(client.run_until_disconnected(), timeout=110)
                        except asyncio.TimeoutError:
                            print("Timeout reached. No OTP received.")
                            await client.disconnect()
                except Exception as e:
                    print("\nUnable to generate the session string. Please ensure you are using a Telethon session file.")
                print('Start tele')
                class_search = 'chatlist-top'
                input_search = WebDriverWait(driver3, 20).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, f'div[class="{class_search}"]')))

                return driver3
                # try:
                #     class_search = 'chatlist-top'
                #     input_search = WebDriverWait(driver3, 120).until(
                #         EC.presence_of_element_located((By.CSS_SELECTOR, f'div[class="{class_search}"]')))
                #     return driver3
                #     driver3.quit()
                # except Exception as e:
                #     print(f"Not Loading Tele: {e}")
                #     if driver3:
                #         driver3.quit()

            except TimeoutException:
                print('Error')
            finally:
                driver3.quit()
        else:
            self.open_url_setup_game(email)




    def open_profile(self, email):
        # Kiểm tra xem thư mục lưu trữ hồ sơ đã tồn tại
        profile_path = f"C:/path/to/profiles/{email}"
        print('Account')
        print(email)
        if not os.path.exists(profile_path):
            os.makedirs(profile_path)
        try:
            options = Options()
            options.add_argument(f'--user-data-dir={profile_path}')
            options.add_argument('--no-experiments')
            driver3 = webdriver.Chrome(options=options)
            driver3.get('https://web.telegram.org/k')

            iframe_allow_attr = 'camera; microphone; geolocation;'

            iframe = WebDriverWait(driver3, 500).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, f'iframe[allow="{iframe_allow_attr}"]')))
            iframe_url = iframe.get_attribute('src')
            print("Src attribute of the iframe:", iframe_url)
            try:
                data_path = f"C:/path/to/data_login/{email}"
                if not os.path.exists(data_path):
                    os.makedirs(data_path)
                with open(data_path + '/url.txt', 'w') as file:
                    file.write(iframe_url)
            except Exception as e:
                print(f"An error occurred: {e}")

            WebDriverWait(driver3, 800).until(EC.presence_of_element_located((By.ID, 'facebook')))
            return driver3

        except TimeoutException:
            print('Error')
        finally:
            driver3.quit()

if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    ex = ChromeProfileManager()
    ex.show()
    # Integrate asyncio event loop with PyQt5 event loop using qasync
    loop = qasync.QEventLoop(app)
    asyncio.set_event_loop(loop)

    with loop:
        loop.run_forever()

