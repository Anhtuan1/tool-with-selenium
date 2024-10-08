import time
import os
import sys
import asyncio
import subprocess
from concurrent.futures import ThreadPoolExecutor, wait, as_completed
from qasync import QEventLoop
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

from tkinter import Tk, Button, filedialog

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
url_tele = 'https://t.me/dogshouse_bot/join?startapp=zySPSgu7Qvmqqaao3JoL4Q'
URL_LIST = 'https://web.telegram.org/k/#@wallet https://web.telegram.org/k/#@hamster_kombat_bot'

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


class ChromeProfileManager(QMainWindow):
    threads = []

    def __init__(self, folder_path):
        super().__init__()
        self.folder_path = folder_path
        self.initUI()
        self.profiles = []

    def initUI(self):
        loaddataPath = self.folder_path + "/loaddata.txt"

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
        self.profile_table.setHorizontalHeaderLabels(
            ['ID', 'Wallet', 'Key', 'Action', 'Login', 'Auto Login Telegram', 'Create game'])

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
        self.input_custom.setText(URL_LIST)
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
        loaddataSession = self.folder_path + "/data_session"

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
            if (index == 0):
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
        asyncio.ensure_future(self.on_login_with_session())

    async def on_login_with_session(self):
        global accList
        input_text = self.input_text.toPlainText()
        profiles_data = input_text.strip().split('\n')
        for profile_data in profiles_data:
            parts = profile_data.split('|')
            email = parts[0]
            data_path = f"{self.folder_path}/data_login/{email}/url.txt"
            if not os.path.exists(data_path):
                await self.login_tele(email)
                self.open_url_setup_game(email)

        self.all_acction()

    def open_url_setup_game(self, email):
        # def run_thread():
        profile_path = f"{self.folder_path}/profiles/{email}"
        data_path_ref = f"{self.folder_path}/url_ref.txt"
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
                        print(
                            "Element with class 'tgme_action_web_button' not found or not clickable within 30 seconds.")

                    time.sleep(2)
                    driver2.execute_script(script_start_button)
                    time.sleep(8)
                    try:
                        play_button = WebDriverWait(driver2, 10).until(EC.presence_of_element_located(
                            (By.CSS_SELECTOR, 'span.bot-menu-text')))
                        play_button.click()
                    except (NoSuchElementException, TimeoutException):
                        print('Play button not found')
                        try:
                            start_button = WebDriverWait(driver2, 10).until(
                                EC.presence_of_element_located((By.CSS_SELECTOR, "div.new-message-bot-commands-view")))
                            start_button.click()
                        except (NoSuchElementException, TimeoutException):
                            print('start button not found')

                    try:
                        continue_button = WebDriverWait(driver2, 15).until(
                            EC.presence_of_element_located((By.XPATH, "//button[contains(., 'Launch')]")))
                        continue_button.click()
                    except (NoSuchElementException, TimeoutException):
                        print("Launch not found")

                    try:
                        continue_button = WebDriverWait(driver2, 10).until(
                            EC.presence_of_element_located((By.XPATH, "//button[contains(., 'Confirm')]")))
                        continue_button.click()
                    except (NoSuchElementException, TimeoutException):
                        print("confirm not found")

                    iframe_allow_attr = 'camera; microphone; geolocation;'
                    iframe = WebDriverWait(driver2, 80).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, f'iframe[allow="{iframe_allow_attr}"]')))
                    iframe_url = iframe.get_attribute('src')
                    # driver2.get(iframe_url)
                    try:
                        data_path = f"{self.folder_path}/data_login/{email}"
                        if not os.path.exists(data_path):
                            os.makedirs(data_path)
                        with open(data_path + '/url.txt', 'w') as file:
                            file.write(iframe_url)
                    except Exception as e:
                        print(f"An error occurred: {e}")

                    driver2.switch_to.frame(iframe)
                    driver2.execute_script(script_login)
                    driver2.execute_script(script)
                    time.sleep(30)
                    data_path = f"{self.folder_path}/data_login/{email}/url.txt"
                    if os.path.exists(data_path):
                        with open(data_path, 'r') as file:
                            url = file.read().strip()
                            driver2.get(url)
                            driver2.execute_script(script_login)
                            driver2.execute_script(script)
                            time.sleep(20)
                            driver2.get('https://walletapp.waveonsui.com/friends')
                            time.sleep(5)
                            try:
                                btn_invite = driver2.find_element(By.XPATH, "//button[contains(., 'Invite a Friend')]")
                                btn_invite.click()
                                time.sleep(1)
                                clipboard_content = pyperclip.paste()
                                pattern = r"startapp=(\d+)"
                                match = re.search(pattern, clipboard_content)
                                if match:
                                    numeric_id = match.group(1)
                                    print(f"Extracted numeric ID: {numeric_id}")
                                    with open(self.folder_path + '/url_ref.txt', 'w') as file:
                                        file.write(url_ref + str(numeric_id))
                                    time.sleep(1)
                                else:
                                    print("No match found")

                            except (NoSuchElementException, TimeoutException) as e:
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

        SCRIPT_GAME_HAMTER = """
        (async function () {
            setInterval(() => {
                if(document.querySelector('.season-end-bottom-inner')){
                    document.querySelector('.season-end-bottom-inner button').click()
                }
                if(document.querySelector('.slider-onb-next')){
                    document.querySelector('.slider-onb-next').click()
                }
                if(document.querySelector('.slider-onb-button button')){
                    document.querySelector('.slider-onb-button button').click()
                }
                if(document.querySelector('.user-tap-button')){
                    document.querySelector('.user-tap-button').click()
                }
                if(document.querySelector('.daily-reward-bottom-button')){
                    document.querySelector('.daily-reward-bottom-button button').click()
                }
                if(document.querySelector('.bottom-sheet-button ')){
                    document.querySelector('.bottom-sheet-button ').click()
                }
            }, 1000)
            await start();
        })();

        async function start() {
        	console.log('- start');
        	return new Promise(resolve => {
        		setTimeout(async () => {

                    await waitClick(document.querySelector('.achievements-show .bottom-sheet-close'), "Play", 1000, true);
                    await clickByLabel(document.querySelectorAll('.slider-onb-next'), "Next", 1000, true);
                    await clickByLabel(document.querySelectorAll('.slider-onb-next'), "Next", 1000, true);
                    await clickByLabel(document.querySelectorAll('.slider-onb-next'), "Next", 1000, true);
                    await clickByLabel(document.querySelectorAll('.slider-onb-next'), "Next", 1000, true);
                    await clickByLabel(document.querySelectorAll('button'), "Play", 2000, true);

        			//touch click button
        			await simulateMouseTouch(document.querySelector('button.user-tap-button'), 2000);

                    resolve();
        		}, 1000);
        	});
        }


        async function checkExistElm(elmList, label, time = 0) {
        	let result = false;
        	if (elmList.length && label) {
        		for (let btnItem of elmList) {
        			if(btnItem.textContent.includes(label)){
                        console.log('--- elm exist', btnItem);
                        result = true;
        				break;
        			}
        		}
        	}
        	return new Promise(resolve => setTimeout(resolve(result), time));
        }

        async function simulateMouseClick(el) {
          let opts = {view: window, bubbles: true, cancelable: true, buttons: 1};
          el.dispatchEvent(new MouseEvent("mousedown", opts));
          await new Promise(r => setTimeout(r, 50));
          el.dispatchEvent(new MouseEvent("mouseup", opts));
          el.dispatchEvent(new MouseEvent("click", opts));
        }

        async function simulateMouseTouch(el, time = 0) {
        	const evt1 = new PointerEvent('pointerdown', {clientX: 150, clientY: 300});
        	const evt2 = new PointerEvent('pointerup', {clientX: 150, clientY: 300});

        	el.dispatchEvent(evt1);
        	el.dispatchEvent(evt2);

            return new Promise(resolve => setTimeout(resolve, time));
        }


        //For React ≥ 15.6.1
        async function simulateMouseInput(el, value) {
            const nativeInputValueSetter = Object.getOwnPropertyDescriptor(
              window.HTMLInputElement.prototype,
              'value').set;
            nativeInputValueSetter.call(el, value);
            const event = new Event('input', { bubbles: true });
            el.dispatchEvent(event);
        }

        async function waitClick(btn, time = 1000) {
        	if (btn) {
                console.log(btn);
                await simulateMouseClick(btn);
            }
        	return new Promise(resolve => setTimeout(resolve, time));
        }
        async function clickByLabel(btn_list, label, time = 1000, must_same = false) {
        	if (btn_list.length && label) {
                for await (const btnItem of btn_list) {
                    //console.log('--', btnItem.textContent, btnItem);
                    if((!must_same && btnItem.textContent.includes(label)) || (must_same && btnItem.textContent == label)) {
                        console.log('->', btnItem.textContent, btnItem);
                        await simulateMouseClick(btnItem);
                        break;
        			}
                }
        	}
        	return new Promise(resolve => setTimeout(resolve, time));
        }
                """
        SCRIPT_TELE_CONTROL_START1 = """
        (async function () {
            await teleWallet1();
        })();

        async function teleWallet1() {
        	console.log('- teleWallet 1: init wallet');
        	return new Promise(resolve => {
        		setTimeout(async () => {
                    let openStartLoop = setInterval(async() => {
                        let startBtn = document.querySelector('button.chat-input-control-button');
                        if(startBtn) {
        					clearInterval(openStartLoop);
                            await waitClick(startBtn, 4000);                    

                            //open wallet
                            await clickByLabel(document.querySelectorAll('span.reply-markup-button-text'), 'Open Wallet');
                            await clickByLabel(document.querySelectorAll('span.checkbox-caption'), 'I agree to the');
                            await clickByLabel(document.querySelectorAll('button.popup-button'), 'Continue');
                            await clickByLabel(document.querySelectorAll('button.popup-button'), 'Launch', 2000);

        					resolve();
                        }
                    }, 1000);
        		}, 2000);
        	});
        }


        async function simulateMouseClick(el) {
          let opts = {view: window, bubbles: true, cancelable: true, buttons: 1};
          el.dispatchEvent(new MouseEvent("mousedown", opts));
          await new Promise(r => setTimeout(r, 50));
          el.dispatchEvent(new MouseEvent("mouseup", opts));
          el.dispatchEvent(new MouseEvent("click", opts));
        }

        //For React ≥ 15.6.1
        async function simulateMouseInput(el, value) {
            const nativeInputValueSetter = Object.getOwnPropertyDescriptor(
              window.HTMLInputElement.prototype,
              'value').set;
            nativeInputValueSetter.call(el, value);
            const event = new Event('input', { bubbles: true });
            el.dispatchEvent(event);
        }

        async function waitClick(btn, time = 1000) {
        	if (btn) await simulateMouseClick(btn);
        	return new Promise(resolve => setTimeout(resolve, time));
        }
        async function clickByLabel(btnList, label, time = 1000) {
        	if (btnList.length && label) {
        		for (let btnItem of btnList) {
        			if(btnItem.textContent.includes(label)){
        				await simulateMouseClick(btnItem);
                        break;
        			}
        		}
        	}
        	return new Promise(resolve => setTimeout(resolve, time));
        }
                """
        SCRIPT_WALLET_INIT1 = """
        (async function () {
            await walletInit1();
        })();

        async function walletInit1() {
        	console.log('- walletInit 1: click lets go');
        	return new Promise(resolve => {
        		setTimeout(async () => {
                    await clickByLabel(document.querySelectorAll('button'), "Let's go");
                    resolve();
        		}, 2000);
        	});
        }


        async function simulateMouseClick(el) {
          let opts = {view: window, bubbles: true, cancelable: true, buttons: 1};
          el.dispatchEvent(new MouseEvent("mousedown", opts));
          await new Promise(r => setTimeout(r, 50));
          el.dispatchEvent(new MouseEvent("mouseup", opts));
          el.dispatchEvent(new MouseEvent("click", opts));
        }

        //For React ≥ 15.6.1
        async function simulateMouseInput(el, value) {
            const nativeInputValueSetter = Object.getOwnPropertyDescriptor(
              window.HTMLInputElement.prototype,
              'value').set;
            nativeInputValueSetter.call(el, value);
            const event = new Event('input', { bubbles: true });
            el.dispatchEvent(event);
        }

        async function waitClick(btn, time = 1000) {
        	if (btn) await simulateMouseClick(btn);
        	return new Promise(resolve => setTimeout(resolve, time));
        }
        async function clickByLabel(btnList, label, time = 1000) {
        	if (btnList.length && label) {
        		for (let btnItem of btnList) {
        			if(btnItem.textContent.includes(label)){
        				await simulateMouseClick(btnItem);
        			}
        		}
        	}
        	return new Promise(resolve => setTimeout(resolve, time));
        }
                """

        SCRIPT_TELE_CONTROL_START2 = """
        (async function () {
            await teleWallet2();
        })();

        async function teleWallet2() {
        	console.log('- teleWallet 2: open setting page from telegram');
        	return new Promise(resolve => {
        		setTimeout(async () => {
                    await waitClick(document.querySelector('.popup-header button.btn-menu-toggle'));
                    await clickByLabel(document.querySelectorAll('.btn-menu-item span.btn-menu-item-text'), "Settings");

                    resolve();
        		}, 2000);
        	});
        }


        async function simulateMouseClick(el) {
          let opts = {view: window, bubbles: true, cancelable: true, buttons: 1};
          el.dispatchEvent(new MouseEvent("mousedown", opts));
          await new Promise(r => setTimeout(r, 50));
          el.dispatchEvent(new MouseEvent("mouseup", opts));
          el.dispatchEvent(new MouseEvent("click", opts));
        }

        //For React ≥ 15.6.1
        async function simulateMouseInput(el, value) {
            const nativeInputValueSetter = Object.getOwnPropertyDescriptor(
              window.HTMLInputElement.prototype,
              'value').set;
            nativeInputValueSetter.call(el, value);
            const event = new Event('input', { bubbles: true });
            el.dispatchEvent(event);
        }

        async function waitClick(btn, time = 1000) {
        	if (btn) await simulateMouseClick(btn);
        	return new Promise(resolve => setTimeout(resolve, time));
        }
        async function clickByLabel(btnList, label, time = 1000) {
        	if (btnList.length && label) {
        		for (let btnItem of btnList) {
        			if(btnItem.textContent.includes(label)){
        				await simulateMouseClick(btnItem);
        			}
        		}
        	}
        	return new Promise(resolve => setTimeout(resolve, time));
        }
                """

        SCRIPT_WALLET_INIT2 = """
        (async function () {
            await walletInit2();
        })();

        async function walletInit2() {
        	console.log('- walletInit 2: enable TON space + go to phrase page');
        	return new Promise(resolve => {
        		setTimeout(async () => {
                    //if wallet inited
                    /*let openTonSpace = document.querySelector('a[href="/scw/settings"]');
                    if(!openTonSpace) {

                    }*/

                    let isChecked = document.querySelector('input[type="checkbox"]').checked;

                    if(!isChecked) {
                        await clickByLabel(document.querySelectorAll('span'), "Show TON Space");
                    }
                    history.go(-1);

                    setTimeout(async () => {
                        await clickByLabel(document.querySelectorAll('span'), "TON Space");
                        await clickByLabel(document.querySelectorAll('div'), "Start exploring TON", 3000);
                        //python get phrase key
                        await clickByLabel(document.querySelectorAll('div'), "Back up manually", 2000);
                        resolve();
                    }, 1000);
        		}, 2000);
        	});
        }


        async function simulateMouseClick(el) {
          let opts = {view: window, bubbles: true, cancelable: true, buttons: 1};
          el.dispatchEvent(new MouseEvent("mousedown", opts));
          await new Promise(r => setTimeout(r, 50));
          el.dispatchEvent(new MouseEvent("mouseup", opts));
          el.dispatchEvent(new MouseEvent("click", opts));
        }

        //For React ≥ 15.6.1
        async function simulateMouseInput(el, value) {
            const nativeInputValueSetter = Object.getOwnPropertyDescriptor(
              window.HTMLInputElement.prototype,
              'value').set;
            nativeInputValueSetter.call(el, value);
            const event = new Event('input', { bubbles: true });
            el.dispatchEvent(event);
        }

        async function waitClick(btn, time = 1000) {
        	if (btn) await simulateMouseClick(btn);
        	return new Promise(resolve => setTimeout(resolve, time));
        }
        async function clickByLabel(btnList, label, time = 1000) {
        	if (btnList.length && label) {
        		for (let btnItem of btnList) {
        			if(btnItem.textContent.includes(label)){
        				await simulateMouseClick(btnItem);
        			}
        		}
        	}
        	return new Promise(resolve => setTimeout(resolve, time));
        }
                """

        SCRIPT_TELE_CONTROL_START3 = """
        (async function () {
            await teleWallet3();
        })();

        async function teleWallet3() {
        	console.log('- teleWallet 3: click continue from telegram');
        	return new Promise(resolve => {
        		setTimeout(async () => {
                    await clickByLabel(document.querySelectorAll('.popup-footer button'), "Continue");                

                    resolve();
        		}, 2000);
        	});
        }


        async function simulateMouseClick(el) {
          let opts = {view: window, bubbles: true, cancelable: true, buttons: 1};
          el.dispatchEvent(new MouseEvent("mousedown", opts));
          await new Promise(r => setTimeout(r, 50));
          el.dispatchEvent(new MouseEvent("mouseup", opts));
          el.dispatchEvent(new MouseEvent("click", opts));
        }

        //For React ≥ 15.6.1
        async function simulateMouseInput(el, value) {
            const nativeInputValueSetter = Object.getOwnPropertyDescriptor(
              window.HTMLInputElement.prototype,
              'value').set;
            nativeInputValueSetter.call(el, value);
            const event = new Event('input', { bubbles: true });
            el.dispatchEvent(event);
        }

        async function waitClick(btn, time = 1000) {
        	if (btn) await simulateMouseClick(btn);
        	return new Promise(resolve => setTimeout(resolve, time));
        }
        async function clickByLabel(btnList, label, time = 1000) {
        	if (btnList.length && label) {
        		for (let btnItem of btnList) {
        			if(btnItem.textContent.includes(label)){
        				await simulateMouseClick(btnItem);
        			}
        		}
        	}
        	return new Promise(resolve => setTimeout(resolve, time));
        }
                """

        SCRIPT_WALLET_INIT3 = """
        (async function () {
            await walletInit3();
        })();

        async function walletInit3() {
            let phrase = '_PHRASE_KEY_';
        	console.log('- walletInit 3: verify phrase key: ', phrase);
        	return new Promise(resolve => {
        		setTimeout(async () => {
                    //verify phrase key
                    let phraseList = phrase.split(' ');
                    let inputs = document.querySelectorAll('input[type="text"]');
                    if(inputs.length) {
                        for(const inputItem of inputs) {
                            let phraseIndex = inputItem.getAttribute('aria-label').replace(':', '');
                            phraseIndex = parseInt(phraseIndex);
                            console.log('phraseIndex:', phraseIndex);
        					await simulateMouseInput(inputItem, phraseList[phraseIndex-1])
                        }    
                    }
                    resolve();
        		}, 2000);
        	});
        }


        async function simulateMouseClick(el) {
          let opts = {view: window, bubbles: true, cancelable: true, buttons: 1};
          el.dispatchEvent(new MouseEvent("mousedown", opts));
          await new Promise(r => setTimeout(r, 50));
          el.dispatchEvent(new MouseEvent("mouseup", opts));
          el.dispatchEvent(new MouseEvent("click", opts));
        }

        //For React ≥ 15.6.1
        async function simulateMouseInput(el, value) {
            const nativeInputValueSetter = Object.getOwnPropertyDescriptor(
              window.HTMLInputElement.prototype,
              'value').set;
            nativeInputValueSetter.call(el, value);
            const event = new Event('input', { bubbles: true });
            el.dispatchEvent(event);
        }

        async function waitClick(btn, time = 1000) {
        	if (btn) await simulateMouseClick(btn);
        	return new Promise(resolve => setTimeout(resolve, time));
        }
        async function clickByLabel(btnList, label, time = 1000) {
        	if (btnList.length && label) {
        		for (let btnItem of btnList) {
        			if(btnItem.textContent.includes(label)){
        				await simulateMouseClick(btnItem);
        			}
        		}
        	}
        	return new Promise(resolve => setTimeout(resolve, time));
        }
                """

        SCRIPT_TELE_CONTROL_START4 = """
        (async function () {
            await teleWallet4();
        })();

        async function teleWallet4() {
        	console.log('- teleWallet 4: click next from telegram');
        	return new Promise(resolve => {
        		setTimeout(async () => {
                    await clickByLabel(document.querySelectorAll('.popup-footer button'), "Next");                

                    resolve();
        		}, 2000);
        	});
        }


        async function simulateMouseClick(el) {
          let opts = {view: window, bubbles: true, cancelable: true, buttons: 1};
          el.dispatchEvent(new MouseEvent("mousedown", opts));
          await new Promise(r => setTimeout(r, 50));
          el.dispatchEvent(new MouseEvent("mouseup", opts));
          el.dispatchEvent(new MouseEvent("click", opts));
        }

        //For React ≥ 15.6.1
        async function simulateMouseInput(el, value) {
            const nativeInputValueSetter = Object.getOwnPropertyDescriptor(
              window.HTMLInputElement.prototype,
              'value').set;
            nativeInputValueSetter.call(el, value);
            const event = new Event('input', { bubbles: true });
            el.dispatchEvent(event);
        }

        async function waitClick(btn, time = 1000) {
        	if (btn) await simulateMouseClick(btn);
        	return new Promise(resolve => setTimeout(resolve, time));
        }
        async function clickByLabel(btnList, label, time = 1000) {
        	if (btnList.length && label) {
        		for (let btnItem of btnList) {
        			if(btnItem.textContent.includes(label)){
        				await simulateMouseClick(btnItem);
        			}
        		}
        	}
        	return new Promise(resolve => setTimeout(resolve, time));
        }
                """

        SCRIPT_WALLET_INIT4 = """
        (async function () {
            await walletInit4();
        })();

        async function walletInit4() {
        	console.log('- walletInit 4: View TON Space');
        	return new Promise(resolve => {
        		setTimeout(async () => {
                    await clickByLabel(document.querySelectorAll('div'), "View TON Space");
                    await clickByLabel(document.querySelectorAll('span'), "TON Space");
                    await clickByLabel(document.querySelectorAll('button'), "Deposit");
                    await clickByLabel(document.querySelectorAll('button'), "Show QR");

                    resolve();
        		}, 2000);
        	});
        }


        async function simulateMouseClick(el) {
          let opts = {view: window, bubbles: true, cancelable: true, buttons: 1};
          el.dispatchEvent(new MouseEvent("mousedown", opts));
          await new Promise(r => setTimeout(r, 50));
          el.dispatchEvent(new MouseEvent("mouseup", opts));
          el.dispatchEvent(new MouseEvent("click", opts));
        }

        //For React ≥ 15.6.1
        async function simulateMouseInput(el, value) {
            const nativeInputValueSetter = Object.getOwnPropertyDescriptor(
              window.HTMLInputElement.prototype,
              'value').set;
            nativeInputValueSetter.call(el, value);
            const event = new Event('input', { bubbles: true });
            el.dispatchEvent(event);
        }

        async function waitClick(btn, time = 1000) {
        	if (btn) await simulateMouseClick(btn);
        	return new Promise(resolve => setTimeout(resolve, time));
        }
        async function clickByLabel(btnList, label, time = 1000) {
        	if (btnList.length && label) {
        		for (let btnItem of btnList) {
        			if(btnItem.textContent.includes(label)){
        				await simulateMouseClick(btnItem);
        			}
        		}
        	}
        	return new Promise(resolve => setTimeout(resolve, time));
        }
                """
        SCRIPT_GAME_WUKONG = """
        (async function () {
            await start();
        })();

        async function start() {
        	console.log('- start');
        	return new Promise(resolve => {
        		setTimeout(async () => {
                    let wHeight = window.innerHeight;
                    let wWidth = window.innerWidth;
                    let canvasButtonOptionInit = {clientX: Math.floor(wWidth/2), clientY: wHeight - 85};
                    let canvasButtonOptionClaim = {clientX: Math.floor(wWidth/2), clientY: window.innerHeight - Math.ceil((window.innerHeight/100)*24)
        }; //24% from bottom

                    //next + finish button
                    await waitClick(document.querySelector('#GameCanvas'), 2000, canvasButtonOptionInit);
                    await waitClick(document.querySelector('#GameCanvas'), 2000, canvasButtonOptionInit);
                    //claim button
                    await waitClick(document.querySelector('#GameCanvas'), 2000, canvasButtonOptionClaim);

                    resolve();
        		}, 1000);
        	});
        }


        async function checkExistElm(elmList, label, time = 0) {
        	let result = false;
        	if (elmList.length && label) {
        		for (let btnItem of elmList) {
        			if(btnItem.textContent.includes(label)){
                        console.log('--- elm exist', btnItem);
                        result = true;
        				break;
        			}
        		}
        	}
        	return new Promise(resolve => setTimeout(resolve(result), time));
        }

        async function simulateMouseClick(el, click_event_option = {}) {
          let opts = {
              ...click_event_option,
              view: window, bubbles: true, cancelable: true, buttons: 1
          };
          el.dispatchEvent(new MouseEvent("mousedown", opts));
          await new Promise(r => setTimeout(r, 50));
          el.dispatchEvent(new MouseEvent("mouseup", opts));
          el.dispatchEvent(new MouseEvent("click", opts));
        }

        async function simulateMouseTouch(el, time = 0) {
        	const evt1 = new PointerEvent('pointerdown', {clientX: 245, clientY: 700});
            const evt2 = new PointerEvent('pointerup', {clientX: 245, clientY: 700});

        	el.dispatchEvent(evt1);
        	el.dispatchEvent(evt2);

            return new Promise(resolve => setTimeout(resolve, time));
        }


        //For React ≥ 15.6.1
        async function simulateMouseInput(el, value) {
            const nativeInputValueSetter = Object.getOwnPropertyDescriptor(
              window.HTMLInputElement.prototype,
              'value').set;
            nativeInputValueSetter.call(el, value);
            const event = new Event('input', { bubbles: true });
            el.dispatchEvent(event);
        }

        async function waitClick(btn, time = 1000, click_event_option) {
        	if (btn) {
                console.log(btn);
                await simulateMouseClick(btn, click_event_option);
            }
        	return new Promise(resolve => setTimeout(resolve, time));
        }
        async function clickByLabel(btn_list, label, time = 1000, must_same = false) {
        	if (btn_list.length && label) {
                for await (const btnItem of btn_list) {
                    //console.log('--', btnItem.textContent, btnItem);
                    if((!must_same && btnItem.textContent.includes(label)) || (must_same && btnItem.textContent == label)) {
                        console.log('->', btnItem.textContent, btnItem);
                        await simulateMouseClick(btnItem);
                        break;
        			}
                }
        	}
        	return new Promise(resolve => setTimeout(resolve, time));
        }
                """
        SCRIPT_GAME_CAT = """
                (async function () {
                    await start();
                })();

                async function start() {
                	console.log('- start');
                	return new Promise(resolve => {
                		setTimeout(async () => {
                            await clickByLabel(document.querySelectorAll('button'), "Wow, let’s go!", 7000);

                            setTimeout(() => {
                                resolve();
                            }, 2000);
                		}, 2000);
                	});
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
        SCRIPT_GAME_BLUM = """
        (async function () {
            await start();
        })();

        async function start() {
        	console.log('- start');
        	return new Promise(resolve => {
        		setTimeout(async () => {
                    await clickByLabel(document.querySelectorAll('button'), "Create account", 2000);
                    await clickByLabel(document.querySelectorAll('button'), "Continue");
                    await clickByLabel(document.querySelectorAll('button'), "Start farming");
                    await clickByLabel(document.querySelectorAll('.button-label'), "Claim", 3000);
                    setTimeout(() => {
                        resolve();
                    }, 2000);
        		}, 2000);
        	});
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

        script_popup = f"""
            setInterval(() => {{
                if(document.querySelector('.popup-confirmation .checkbox-ripple')) {{
                    document.querySelector('.popup-confirmation .checkbox-ripple').click()
                    document.querySelector('.popup-confirmation .popup-button').click()
                }}
            }}, 5000)
            setInterval(() => {{
                        if(document.querySelector('.popup-footer button')) {{
                            var event = new Event('enable', {{ bubbles: true }});
                            document.querySelector('.popup-footer button').dispatchEvent(event);
                            document.querySelector('.popup-footer button').click()
                        }}
            }}, 10000)
        """

        script_click = f"""
            var key = '{key}';


            setInterval(() => {{
                console.log('Click Claim');
                if (document.querySelector("#root ._buttons_1x2ee_142 ._type-white_xn5bt_54")) {{
                    document.querySelector("#root ._buttons_1x2ee_142 ._type-white_xn5bt_54").click()
                }}
            }},5000)



            setInterval(() => {{
                if (document.querySelector("#root ._fixedBottom_xn5bt_133")) {{
                    var textCheck = document.querySelector("#root ._fixedBottom_xn5bt_133").textContent;
                    document.querySelector("#root ._fixedBottom_xn5bt_133").click()
                }}
            }},3000)

            setInterval(() => {{
                if (document.querySelector("#root ._type-white_xn5bt_54")) {{
                    var textCheck = document.querySelector("#root ._type-white_xn5bt_54").textContent;
                    document.querySelector("#root ._type-white_xn5bt_54").click()
                }}
            }},4000)



            setTimeout(() => {{
                console.log('Click tele wallet');
                if(document.querySelectorAll("#tc-widget-root button")){{
                    document.querySelectorAll("#tc-widget-root button")[2].click();
                }}

            }}, 13000);

            """
        print('web', web)
        print('profile_path', profile_path)
        if web == 'https://web.telegram.org/k/#@dogshouse_bot':
            print('Running Dogs')
            try:
                chrome_options.add_argument(f'--user-data-dir={profile_path}')
                chrome_options.add_argument('--no-experiments')
                driver2 = webdriver.Chrome(options=chrome_options)
                driver2.get(web)
                driver2.execute_script(script_popup)
                time.sleep(5)
                try:
                    start_button = driver2.find_element(By.CSS_SELECTOR, "div.new-message-bot-commands-view")
                    start_button.click()
                except (NoSuchElementException, TimeoutException):
                    continue_button = driver2.find_element(By.XPATH, "//button[contains(., 'START')]")
                    continue_button.click()

                time.sleep(2)

                try:
                    continue_button = driver2.find_element(By.XPATH, "//button[contains(., 'Launch')]")
                    continue_button.click()
                except (NoSuchElementException, TimeoutException):
                    print("Launch not found")

                iframe = WebDriverWait(driver2, 50).until(
                    EC.presence_of_element_located((By.XPATH, '//iframe[contains(@src, "onetime.dog")]')))

                driver2.switch_to.frame(iframe)
                driver2.execute_script(script_click)
                time.sleep(40)
                try:
                    balance = driver2.find_element(By.CSS_SELECTOR, "div._balance_r9zqh_1")

                    path_opt = f"{self.folder_path}/dogs_balance/{email}"
                    if not os.path.exists(path_opt):
                        os.makedirs(path_opt)
                    with open(path_opt + '/balance.txt', 'w') as file:
                        file.write(balance.text)
                except (NoSuchElementException, TimeoutException):
                    print("Balance not found")

                time.sleep(5)

            except (NoSuchElementException, TimeoutException) as e:
                print(f"Xảy ra lỗi")
            finally:
                if driver2 is not None:
                    print('Quit')
                    driver2.quit()
        if web == 'https://t.me/blum/app?startapp=ref_x2QGrP78j3' or 'https://t.me/blum/app' in web:
            try:
                print('Running Blum')
                chrome_options.add_argument(f'--user-data-dir={profile_path}')
                chrome_options.add_argument('--no-experiments')
                # Add the mobile emulation to the chrome options variable
                chrome_options.add_experimental_option("mobileEmulation", mobile_emulation)
                chrome_options.add_argument(f"window-size=400,886")

                CHROME_EXTENSION_CRX_PATH = self.folder_path + '/chrome_extension/ignore-x-frame-headers/2.0.0_0.crx'
                chrome_options.add_extension(CHROME_EXTENSION_CRX_PATH)
                driver2 = webdriver.Chrome(options=chrome_options)
                if web is not None:
                    driver2.get(web)
                    time.sleep(5)

                try:
                    wait = WebDriverWait(driver2, 30)
                    try:
                        element = wait.until(
                            EC.presence_of_element_located((By.CLASS_NAME, 'tgme_action_web_button'))
                        )
                        ref_link = element.get_attribute('href')
                        driver2.get(ref_link)
                    except TimeoutException:
                        print(
                            "Element with class 'tgme_action_web_button' not found or not clickable within 30 seconds.")
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
                    iframe = WebDriverWait(driver2, 50).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, f'iframe[allow="{iframe_allow_attr}"]')))
                    # get iframe url
                    iframe_url = iframe.get_attribute('src')
                    iframe_url = iframe_url.replace("tgWebAppPlatform=weba", "tgWebAppPlatform=ios").replace(
                        "tgWebAppPlatform=web", "tgWebAppPlatform=ios")
                    print("Src attribute of the iframe:", iframe_url)
                    try:
                        data_path = f"{self.folder_path}/data_login_blums/{email}"
                        if not os.path.exists(data_path):
                            os.makedirs(data_path)
                        with open(data_path + '/url.txt', 'w') as file:
                            file.write(iframe_url)
                            print("->iframe url update:", data_path + '/url.txt')
                    except Exception as e:
                        print(f"An error occurred: {e}")

                    driver2.switch_to.frame(iframe)
                    print("- SCRIPT GAME CONTROL")
                    # driver2.execute_script(script_login)
                    driver2.execute_script(SCRIPT_GAME_BLUM)
                    time.sleep(30)
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

        if web == 'https://t.me/catsgang_bot/join?startapp=9xaZ15mPrkB6wQaz3DKqH' or 'https://t.me/catsgang_bot' in web:
            print('Running Cat')
            try:
                chrome_options.add_argument(f'--user-data-dir={profile_path}')
                chrome_options.add_argument('--no-experiments')
                # Add the mobile emulation to the chrome options variable
                chrome_options.add_experimental_option("mobileEmulation", mobile_emulation)
                chrome_options.add_argument(f"window-size=414,736")

                CHROME_EXTENSION_CRX_PATH = self.folder_path + '/chrome_extension/ignore-x-frame-headers/2.0.0_0.crx'
                chrome_options.add_extension(CHROME_EXTENSION_CRX_PATH)
                driver2 = webdriver.Chrome(options=chrome_options)
                if web is not None:
                    driver2.get(web)
                    time.sleep(5)

                try:
                    wait = WebDriverWait(driver2, 30)
                    try:
                        element = wait.until(
                            EC.presence_of_element_located((By.CLASS_NAME, 'tgme_action_web_button'))
                        )
                        ref_link = element.get_attribute('href')
                        driver2.get(ref_link)
                    except TimeoutException:
                        print(
                            "Element with class 'tgme_action_web_button' not found or not clickable within 30 seconds.")
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
                    iframe = WebDriverWait(driver2, 50).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, f'iframe[allow="{iframe_allow_attr}"]')))
                    # get iframe url
                    iframe_url = iframe.get_attribute('src')
                    iframe_url = iframe_url.replace("tgWebAppPlatform=weba", "tgWebAppPlatform=ios").replace(
                        "tgWebAppPlatform=web", "tgWebAppPlatform=ios")
                    print("Src attribute of the iframe:", iframe_url)
                    try:
                        data_path = f"{self.folder_path}/data_login_cats/{email}"
                        if not os.path.exists(data_path):
                            os.makedirs(data_path)
                        with open(data_path + '/url.txt', 'w') as file:
                            file.write(iframe_url)
                            print("->iframe url update:", data_path + '/url.txt')
                    except Exception as e:
                        print(f"An error occurred: {e}")

                    driver2.switch_to.frame(iframe)
                    print("- SCRIPT GAME CONTROL")
                    # driver2.execute_script(script_login)
                    driver2.execute_script(SCRIPT_GAME_CAT)
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
        if web == 'https://t.me/bwcwukong_bot/Play?startapp=1641277785' or 'https://t.me/bwcwukong_bot' in web:
            print('Running Wukong')
            try:
                chrome_options.add_argument(f'--user-data-dir={profile_path}')
                chrome_options.add_argument('--no-experiments')
                # Add the mobile emulation to the chrome options variable
                chrome_options.add_experimental_option("mobileEmulation", mobile_emulation)
                chrome_options.add_argument(f"window-size=414,736")

                CHROME_EXTENSION_CRX_PATH = self.folder_path + '/chrome_extension/ignore-x-frame-headers/2.0.0_0.crx'
                chrome_options.add_extension(CHROME_EXTENSION_CRX_PATH)
                driver2 = webdriver.Chrome(options=chrome_options)
                if web is not None:
                    driver2.get(web)
                    time.sleep(5)

                try:
                    wait = WebDriverWait(driver2, 30)
                    try:
                        element = wait.until(
                            EC.presence_of_element_located((By.CLASS_NAME, 'tgme_action_web_button'))
                        )
                        ref_link = element.get_attribute('href')
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
                    time.sleep(5)

                    try:
                        continue_button = driver2.find_element(By.XPATH, "//button[contains(., 'Confirm')]")
                        continue_button.click()
                    except (NoSuchElementException, TimeoutException):
                        print("confirm not found")
                    time.sleep(5)

                    iframe_allow_attr = 'camera; microphone; geolocation;'
                    iframe = WebDriverWait(driver2, 50).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, f'iframe[allow="{iframe_allow_attr}"]')))
                    # get iframe url
                    iframe_url = iframe.get_attribute('src')
                    iframe_url = iframe_url.replace("tgWebAppPlatform=weba", "tgWebAppPlatform=ios").replace(
                        "tgWebAppPlatform=web", "tgWebAppPlatform=ios")
                    print("Src attribute of the iframe:", iframe_url)
                    try:
                        data_path = f"{self.folder_path}/data_login_wukong/{email}"
                        if not os.path.exists(data_path):
                            os.makedirs(data_path)
                        with open(data_path + '/url.txt', 'w') as file:
                            file.write(iframe_url)
                            print("->iframe url update:", data_path + '/url.txt')
                    except Exception as e:
                        print(f"An error occurred: {e}")

                    driver2.switch_to.frame(iframe)
                    print("- SCRIPT GAME CONTROL")
                    # driver2.execute_script(script_login)
                    driver2.execute_script(SCRIPT_GAME_WUKONG)
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

        if web == 'https://t.me/hamster_kombat_boT/start?startapp=kentId1641277785' or 'https://t.me/hamster_kombat_boT' in web:
            print('Running Hamter')
            try:
                chrome_options.add_argument(f'--user-data-dir={profile_path}')
                chrome_options.add_argument('--no-experiments')
                # Add the mobile emulation to the chrome options variable
                chrome_options.add_experimental_option("mobileEmulation", mobile_emulation)
                chrome_options.add_argument(f"window-size=400,884")

                CHROME_EXTENSION_CRX_PATH = self.folder_path + '/chrome_extension/ignore-x-frame-headers/2.0.0_0.crx'
                chrome_options.add_extension(CHROME_EXTENSION_CRX_PATH)
                driver2 = webdriver.Chrome(options=chrome_options)
                if web is not None:
                    driver2.get(web)
                    time.sleep(5)

                try:
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
                    time.sleep(5)

                    try:
                        continue_button = driver2.find_element(By.XPATH, "//button[contains(., 'Confirm')]")
                        continue_button.click()
                    except (NoSuchElementException, TimeoutException):
                        print("confirm not found")
                    time.sleep(5)

                    iframe_allow_attr = 'camera; microphone; geolocation;'
                    iframe = WebDriverWait(driver2, 50).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, f'iframe[allow="{iframe_allow_attr}"]')))
                    # get iframe url
                    iframe_url = iframe.get_attribute('src')
                    iframe_url = iframe_url.replace("tgWebAppPlatform=weba", "tgWebAppPlatform=ios").replace(
                        "tgWebAppPlatform=web", "tgWebAppPlatform=ios")
                    driver2.get(iframe_url)
                    try:
                        data_path = f"{self.folder_path}/data_login_hamter/{email}"
                        if not os.path.exists(data_path):
                            os.makedirs(data_path)
                        with open(data_path + '/url.txt', 'w') as file:
                            file.write(iframe_url)
                            print("->iframe url update:", data_path + '/url.txt')
                    except Exception as e:
                        print(f"An error occurred: {e}")

                    print("- SCRIPT GAME CONTROL")
                    driver2.execute_script(SCRIPT_GAME_HAMTER)
                    time.sleep(25)
                    self.run_script_from_file(driver2, self.folder_path + "/hamster_kombat_auto_click.txt", 100)
                except (NoSuchElementException, TimeoutException):
                    print(f"Lỗi: {str(e)}")
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
                chrome_options.add_argument(f"window-size=400,884")

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
                    time.sleep(5)
                    print("- SCRIPT open setting page from telegram")
                    driver2.switch_to.default_content()
                    driver2.execute_script(SCRIPT_TELE_CONTROL_START2)
                    time.sleep(5)

                    # run iframe script
                    print("- SCRIPT enable TON space + go to phrase page")
                    driver2.switch_to.frame(iframe)
                    driver2.execute_script(SCRIPT_WALLET_INIT2)
                    time.sleep(10)

                    try:
                        print("- GET PHRASE KEY")
                        phrase_elm = driver2.find_elements(By.CSS_SELECTOR, 'div[variant="body"] > div[variant="body"]')
                        phrase = []
                        for word in phrase_elm:
                            phrase.append(word.text);
                        phrase = ' '.join(phrase)
                        print('phrase:', phrase)

                        # run root page script
                        print("- SCRIPT click continue from telegram")
                        driver2.switch_to.default_content()
                        driver2.execute_script(SCRIPT_TELE_CONTROL_START3)
                        time.sleep(5)

                        # run iframe script
                        print("- SCRIPT verify phrase key")
                        driver2.switch_to.frame(iframe)
                        driver2.execute_script(SCRIPT_WALLET_INIT3.replace('_PHRASE_KEY_', phrase))
                        time.sleep(5)

                        # run root page script
                        print("- SCRIPT click next from telegram")
                        driver2.switch_to.default_content()
                        driver2.execute_script(SCRIPT_TELE_CONTROL_START4)
                        time.sleep(5)

                        # run iframe script
                        print("- SCRIPT View TON Space")
                        driver2.switch_to.frame(iframe)
                        driver2.execute_script(SCRIPT_WALLET_INIT4)
                        time.sleep(8)

                        accWalletUpdate = f'{email}|wallet|key';
                        try:
                            copy_button = WebDriverWait(driver2, 10).until(
                                EC.presence_of_element_located((By.XPATH, "//button[contains(., 'Copy Address')]")))
                            copy_button.click()

                            wallet = pyperclip.paste()
                            print('wallet:', wallet)
                            if wallet is not None:
                                accWalletUpdate = accWalletUpdate.replace('wallet', wallet);
                            if phrase is not None:
                                accWalletUpdate = accWalletUpdate.replace('key', phrase);

                            print('file update data:', accWalletUpdate)

                            # replace "12345667|wallet|key" -> "12345667|0x111..|text test .."
                            fileOpen = open(self.folder_path + '/loaddata.txt', "r+")
                            loadDataText = fileOpen.read()
                            loadDataText = loadDataText.replace(f'{email}|wallet|key', accWalletUpdate);
                            with open(self.folder_path + '/loaddata.txt', 'w') as file:
                                file.write(loadDataText)

                        except (NoSuchElementException, TimeoutException):
                            print("Copy button not found")

                        print("- LOG TO FILE")
                        data_path = f"{self.folder_path}/data_login_wallet/{email}"
                        if not os.path.exists(data_path):
                            os.makedirs(data_path)
                        with open(data_path + '/url.txt', 'w') as file:
                            file.write(accWalletUpdate)
                            print(f"{email}: create wallet successfully")
                    except Exception as e:
                        print(f"{email}: An error occurred: {e}")
                except (NoSuchElementException, TimeoutException) as e:
                    print(f"Xảy ra lỗi")
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
                    print(f"opened file")
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
        webStr = self.input_custom.toPlainText()
        webList = webStr.split(" ")
        profile_path = f"{self.folder_path}/profiles/{email}"
        for web in webList:
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
            open_profile_button = QPushButton('Go to profile')
            open_profile_button.clicked.connect(lambda _, email=email: self.open_profile(email))
            self.profile_table.setCellWidget(row_position, 3, open_profile_button)
            data_path = f"{self.folder_path}/data_login/{email}"
            if os.path.exists(data_path):
                self.profile_table.setItem(row_position, 4, QTableWidgetItem('Login OK'))
            else:
                self.profile_table.setItem(row_position, 4, QTableWidgetItem('-'))
            auto_login_tele = QPushButton('Login tele')
            auto_login_tele.clicked.connect(lambda _, email=email: self.start_asyncio_task(email))
            self.profile_table.setCellWidget(row_position, 5, auto_login_tele)

    def start_asyncio_task(self, email):
        print('Task')
        asyncio.ensure_future(self.login_tele(email))

    async def login_tele(self, email):
        profile_path = f"{self.folder_path}/profiles/{email}"
        print('Account')
        print(email)
        data_path = f"{self.folder_path}/data_login/{email}/url.txt"
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
            session_name = f"{self.folder_path}/data_session/{email}/{email}.session"

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
                                    }},3000);
                                """
                            try:
                                await asyncio.sleep(20)
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
            driver3.get('https://web.telegram.org/k')
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
            driver3.quit()
        finally:
            driver3.quit()

    def open_profile(self, email):
        # Kiểm tra xem thư mục lưu trữ hồ sơ đã tồn tại
        profile_path = f"{self.folder_path}/profiles/{email}"
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
            driver3.execute_script('''
                        function addQuitButton() {
                            var existingButton = document.getElementById("quit-button");
                            if (existingButton) {
                                return; // If the button already exists, don't add it again
                            }

                            var button = document.createElement("button");
                            button.innerHTML = "Quit";
                            button.id = "quit-button";
                            document.body.appendChild(button);

                            // Apply CSS styles to the button
                            var css = `
                                #quit-button {
                                    position: fixed;
                                    top: 10px;
                                    right: 10px;
                                    padding: 15px 30px;
                                    font-size: 20px;
                                    background-color: rgba(255, 77, 77, 0.2); /* Red background with 0.2 opacity */
                                    color: white;
                                    border: none;
                                    border-radius: 5px;
                                    cursor: pointer;
                                    z-index: 1000; /* Ensure it stays on top */
                                }

                                #quit-button:hover {
                                    background-color: rgba(255, 26, 26, 0.4); /* Darker red on hover with higher opacity */
                                }
                            `;
                            var style = document.createElement('style');
                            style.appendChild(document.createTextNode(css));
                            document.head.appendChild(style);

                            button.addEventListener("click", function() {
                                var facebookDiv = document.createElement("div");
                                facebookDiv.id = "facebook";
                                document.body.appendChild(facebookDiv);
                                window.close();
                            });
                        }


                        // Add the button immediately
                        addQuitButton();
                    ''')

            WebDriverWait(driver3, 3000).until(EC.presence_of_element_located((By.ID, 'facebook')))
            # iframe_allow_attr = 'camera; microphone; geolocation;'
            #
            # iframe = WebDriverWait(driver3, 500).until(
            #     EC.presence_of_element_located((By.CSS_SELECTOR, f'iframe[allow="{iframe_allow_attr}"]')))
            # iframe_url = iframe.get_attribute('src')
            # print("Src attribute of the iframe:", iframe_url)
            # try:
            #     data_path = f"C:/path/to/data_login/{email}"
            #     if not os.path.exists(data_path):
            #         os.makedirs(data_path)
            #     with open(data_path + '/url.txt', 'w') as file:
            #         file.write(iframe_url)
            # except Exception as e:
            #     print(f"An error occurred: {e}")

            return driver3

        except TimeoutException:
            print('Error')
            driver3.quit()
        finally:
            driver3.quit()


def select_folder():
    root = Tk()
    root.withdraw()  # Hide the root window
    selected_folder = filedialog.askdirectory(initialdir="C:/", title="Select Folder")
    return selected_folder


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

    # Start the asyncio event loop
    with loop:
        await loop.run_forever()


if __name__ == "__main__":
    asyncio.run(main())


