import time
import os
import sqlite3
import asyncio
from concurrent.futures import ThreadPoolExecutor, wait, as_completed
from datetime import datetime
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTextEdit, \
    QPushButton, QLineEdit, QTableWidget, QTableWidgetItem, QFileDialog
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
DISK_PATH = 'C:/path/tete_set_username/'
DISK_PATH_PROFILE = 'C:/path/to/'
TELEGRAM_WEB_APP_URL = 'https://web.telegram.org/a/'

CHROME_SIZE = {
    "width": 414,  # user agent
    "height": 736,  # user agent
    "height_window": 900,  # height chrome windows
}
mobile_emulation = {
    # "deviceName": "iPhone 6/7/8 plus"

    # iphone 6/7/8
    "deviceMetrics": {"width": CHROME_SIZE["width"], "height": CHROME_SIZE["height"], "pixelRatio": 3.0},
    "userAgent": "Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.1"
}

SCRIPT_GAME_CONTROL = """
(async function () {
    await openSetUserNamePage();
})();

async function openSetUserNamePage() {
	console.log('- openSetUserNamePage');
	return new Promise(resolve => {
		setTimeout(async () => {
            let openMenuLoop = setInterval(() => {
                let ribbonMenu = document.querySelector('button[title="Open menu"]');
                if(ribbonMenu) {
                    ribbonMenu.click();
                    clearInterval(openMenuLoop);

                    setTimeout(async () => {
                        //open setting page
            			await clickByLabel(document.querySelectorAll('div[role="menuitem"]'), 'Settings');

                        setTimeout(async () => {
                             //open profile page
            				document.querySelector('button[title="Edit profile"]').click();
                            await getUserName();
                            //click save
                            let saveBtn = document.querySelector('button[aria-label="Save"]');
                            await simulateMouseClick(saveBtn);

                            setTimeout(() => {
                                resolve();
                            }, 2000);
            			}, 1000);
        			}, 1000);
                }
            }, 500);
		}, 2000);
	});
}

async function getUserName() {
	console.log('- getUserName');
	return new Promise(resolve => {
		setTimeout(async () => {
            let firstName = document.querySelector('input[aria-label="First name (required)"]').value;
			let lastName = document.querySelector('input[aria-label="Last name (optional)"]').value;
			let userNameInput =  document.querySelector('input[aria-label="Username"');
            let userNameVal =  userNameInput.value;

            if(!userNameVal) {
                let userName = firstName ? (firstName.toLowerCase() + '_' ): '';
                userName += makeid(3);
                userName += lastName ? lastName.toLowerCase() : '';
                //remove number at start string
                userName = userName.replace(/^\d{0,}/, '');

                console.log('--- set username: ', userName);
                userNameInput.value = userName;
                await simulateMouseInput(userNameInput);
            } else {
                console.log('--- username already exists: ', userNameVal);
            }

			setTimeout(() => {
				resolve();
			}, 3000);
        }, 2000);
    });
}

function makeid(length) {
    let result = '';
    const characters = 'abcdefghijklmnopqrstuvwxyz0123456789';
    const charactersLength = characters.length;
    let counter = 0;
    while (counter < length) {
      result += characters.charAt(Math.floor(Math.random() * charactersLength));
      counter += 1;
    }
    return result;
}

async function simulateMouseClick(el) {
  let opts = {view: window, bubbles: true, cancelable: true, buttons: 1};
  el.dispatchEvent(new MouseEvent("mousedown", opts));
  await new Promise(r => setTimeout(r, 50));
  el.dispatchEvent(new MouseEvent("mouseup", opts));
  el.dispatchEvent(new MouseEvent("click", opts));
}

async function simulateMouseInput(el) {
  let opts = {view: window, bubbles: true, cancelable: true, buttons: 1};
  el.dispatchEvent(new MouseEvent("mousedown", opts));
  await new Promise(r => setTimeout(r, 50));
  el.dispatchEvent(new MouseEvent("mouseup", opts));
  el.dispatchEvent(new MouseEvent("input", opts));
}

async function waitClick(btn, time = 1000) {
	if (btn) btn.click();
	return new Promise(resolve => setTimeout(resolve, time));
}
async function clickByLabel(btnList, label, time = 1000) {
	if (btnList.length && label) {
		for (let btnItem of btnList) {
			if(btnItem.textContent.includes(label)){
				btnItem.click();
			}
		}
	}
	return new Promise(resolve => setTimeout(resolve, time));
}
        """


class ChromeProfileManager(QMainWindow):
    threads = []

    def __init__(self):
        super().__init__()

        self.initUI()
        self.profiles = []

    def initUI(self):
        loaddataPath = DISK_PATH + "loaddata.txt"

        # Check if the file exists
        if os.path.exists(loaddataPath):
            # Open the file in read mode
            with open(loaddataPath, 'r') as file:
                # Read the contents of the file
                file_contents = file.read()
                # Now you can work with the contents, for example:

        else:
            with open(DISK_PATH + 'loaddata.txt', 'w') as file:
                file.write('')
            file_contents = ''

        self.setWindowTitle('Tetegram function app | quáº£n lĂ½ Profile Chrome')
        self.setGeometry(100, 100, 1500, 800)

        # Giao diá»‡n ngÆ°á»i dĂ¹ng
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.layout = QHBoxLayout(self.central_widget)

        # Cá»™t trĂ¡i - Nháº­p thĂ´ng tin vĂ  táº¡o profile
        self.input_layout = QVBoxLayout()

        self.create_button = QPushButton('Load Session Folder')
        self.create_button.clicked.connect(lambda: self.load_session())
        self.input_layout.addWidget(self.create_button)

        self.login_with_session = QPushButton('Login with Tele')
        self.login_with_session.clicked.connect(self.on_login_with_session_clicked)
        self.input_layout.addWidget(self.login_with_session)

        self.input_label = QLabel('Nháº­p thĂ´ng tin (id|wallet|key):')
        self.input_layout.addWidget(self.input_label)
        self.input_text = QTextEdit()
        self.input_text.setPlaceholderText('id|wallet|key')
        if file_contents != '':
            self.input_text.setPlainText(file_contents)
        self.input_layout.addWidget(self.input_text)

        self.load_button = QPushButton('Load Profile')
        self.load_button.clicked.connect(self.load_profile)
        self.input_layout.addWidget(self.load_button)

        # Cá»™t pháº£i - Hiá»ƒn thá»‹ thĂ´ng tin profile
        self.profile_table = QTableWidget()
        self.profile_table.setColumnCount(7)
        self.profile_table.setHorizontalHeaderLabels(
            ['ID', 'Wallet', 'Key', 'Action', 'Setting', 'Auto Login Telegram', 'Create game'])

        self.right_layout = QVBoxLayout()
        self.right_layout.addWidget(QLabel('ThĂ´ng tin profile:'))
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
        self.input_custom.setText(TELEGRAM_WEB_APP_URL)
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
        loaddataSession = DISK_PATH + "data_session"

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

    async def handle_incoming_message(event):
        otp = re.search(r'\b(\d{5})\b', event.raw_text)
        if otp:
            print("OTP received âœ…\nYour login code:", otp.group(0))
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
            data_path = f"{DISK_PATH}data_login/{email}/url.txt"
            if not os.path.exists(data_path):
                # await self.login_tele(email)
                self.open_url_setup_game(email)

        # loop list account
        # self.all_acction()

    def open_url_setup_game(self, email):
        # def run_thread():
        profile_path = f"{DISK_PATH_PROFILE}profiles/{email}"
        web = TELEGRAM_WEB_APP_URL
        chrome_options = Options()
        print(f"Running: {str(email)}")
        driver2 = None
        print(web)

        if web is not None:
            try:
                chrome_options.add_argument(f'--user-data-dir={profile_path}')
                chrome_options.add_argument('--no-experiments')
                # Add the mobile emulation to the chrome options variable
                chrome_options.add_experimental_option("mobileEmulation", mobile_emulation)
                chrome_options.add_argument(f"window-size={CHROME_SIZE["
                width
                "]},{CHROME_SIZE["
                height_window
                "]}")

                driver2 = webdriver.Chrome(options=chrome_options)

                # open telegram home to set username
                driver2.get(web)
                time.sleep(5)

                driver2.execute_script(SCRIPT_GAME_CONTROL)
                time.sleep(30)

                try:
                    data_path = f"{DISK_PATH}data_login/{email}"
                    if not os.path.exists(data_path):
                        os.makedirs(data_path)
                    with open(data_path + '/url.txt', 'w') as file:
                        file.write('ser username ok')
                        print(f"{email}: set username ok")
                except Exception as e:
                    print(f"{email}: An error occurred: {e}")

            except (NoSuchElementException, TimeoutException) as e:
                print(f"Xáº£y ra lá»—i")
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

        if web == TELEGRAM_WEB_APP_URL:
            print(web)
            try:
                chrome_options.add_argument(f'--user-data-dir={profile_path}')
                chrome_options.add_argument('--no-experiments')
                # Add the mobile emulation to the chrome options variable
                chrome_options.add_experimental_option("mobileEmulation", mobile_emulation)
                driver2 = webdriver.Chrome(options=chrome_options)

                # run by tele web
                if web is not None:
                    driver2.get(web)
                time.sleep(5)

                try:
                    print("- SCRIPT GAME CONTROL")
                    driver2.execute_script(SCRIPT_GAME_CONTROL)
                    time.sleep(30)

                    try:
                        data_path = f"{DISK_PATH}data_login/{email}"
                        if not os.path.exists(data_path):
                            os.makedirs(data_path)
                        with open(data_path + '/url.txt', 'w') as file:
                            file.write('ser username ok')
                            print(f"{email}: set username ok")
                    except Exception as e:
                        print(f"{email}: An error occurred: {e}")

                except (NoSuchElementException, TimeoutException):
                    print(f"Lá»—i: {str(e)}")

            except (NoSuchElementException, TimeoutException) as e:
                print(f"Xáº£y ra lá»—i")
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

        # loop list account
        # self.all_acction()

    def open_url(self, email, event):
        web = self.input_custom.toPlainText()
        profile_path = f"{DISK_PATH_PROFILE}profiles/{email}"
        if os.path.exists(profile_path):
            # event.wait()
            self.open_url_in_thread(profile_path, web, email)

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
            data_path = f"{DISK_PATH}data_login/{email}"
            if os.path.exists(data_path):
                self.profile_table.setItem(row_position, 4, QTableWidgetItem('Setting OK'))
            else:
                self.profile_table.setItem(row_position, 4, QTableWidgetItem('-'))
            auto_login_tele = QPushButton('Login tele')
            auto_login_tele.clicked.connect(lambda _, email=email: self.start_asyncio_task(email))
            self.profile_table.setCellWidget(row_position, 5, auto_login_tele)

            auto_create_game = QPushButton('Create game')
            auto_create_game.clicked.connect(lambda _, email=email: self.open_url_setup_game(email))
            self.profile_table.setCellWidget(row_position, 6, auto_create_game)

    def start_asyncio_task(self, email):
        print('Task')
        asyncio.ensure_future(self.login_tele(email))

    async def login_tele(self, email):
        profile_path = f"{DISK_PATH_PROFILE}profiles/{email}"
        print('Account')
        print(email)
        data_path = f"{DISK_PATH}data_login/{email}/url.txt"
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
                session_name = f"{DISK_PATH}data_session/{email}/{email}.session"

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
                                path_opt = f"{DISK_PATH}otp/{email}"
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
                                    await asyncio.sleep(12)
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
                    print(
                        "\nUnable to generate the session string. Please ensure you are using a Telethon session file.")
                driver3.get('https://web.telegram.org/a')
                time.sleep(20)
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
        # Kiá»ƒm tra xem thÆ° má»¥c lÆ°u trá»¯ há»“ sÆ¡ Ä‘Ă£ tá»“n táº¡i
        profile_path = f"{DISK_PATH_PROFILE}profiles/{email}"
        print('Account')
        print(email)
        driver3 = None
        if not os.path.exists(profile_path):
            os.makedirs(profile_path)
        try:
            options = Options()
            options.add_argument(f'--user-data-dir={profile_path}')
            options.add_argument('--no-experiments')
            # Add the mobile emulation to the chrome options variable
            options.add_experimental_option("mobileEmulation", mobile_emulation)
            options.add_argument(f"window-size={CHROME_SIZE["
            width
            "]},{CHROME_SIZE["
            height_window
            "]}")
            driver3 = webdriver.Chrome(options=options)
            driver3.get('https://web.telegram.org/k')
            driver3.set_window_size(CHROME_SIZE["width"], CHROME_SIZE["height_window"])

            WebDriverWait(driver3, 8000).until(EC.presence_of_element_located((By.ID, 'facebook')))
            return driver3

        except TimeoutException:
            print('Error')
        finally:
            if driver3 is not None:
                print('Quit')
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
