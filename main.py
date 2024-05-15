import sys
import time
import os  # Thêm thư viện os
from concurrent.futures import ThreadPoolExecutor, wait, as_completed
from datetime import datetime
from telethon.sync import TelegramClient, events
from telethon.sessions import StringSession
from telethon.tl.types import Channel
from pyrogram import Client

from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTextEdit, QPushButton, QLineEdit, QTableWidget, QTableWidgetItem, QFileDialog
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import requests
import json
import threading
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.keys import Keys

import pyperclip
import re
import csv

accList = {}
num_thread_running = 0
futures = []
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
            file_contents = ''

        self.setWindowTitle('Quản lý Profile Chrome')
        self.setGeometry(100, 100, 1200, 800)

        # Giao diện người dùng
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.layout = QHBoxLayout(self.central_widget)

        # Cột trái - Nhập thông tin và tạo profile
        self.input_layout = QVBoxLayout()


        self.input_label = QLabel('Nhập thông tin (id|wallet|key):')
        self.input_text = QTextEdit()
        self.input_text.setPlaceholderText('id|wallet|key')
        if file_contents != '':
            self.input_text.setPlainText(file_contents)

        self.create_button = QPushButton('Create Profile')
        self.create_button.clicked.connect(lambda: self.create_profile('No'))
        self.create_mine_button = QPushButton('Create Profile and Mine')
        self.create_mine_button.clicked.connect(lambda: self.create_profile('Yes'))
        self.load_button = QPushButton('Load Profile')
        self.load_button.clicked.connect(self.load_profile)
        self.input_layout.addWidget(self.input_label)
        self.input_layout.addWidget(self.input_text)
        self.input_layout.addWidget(self.create_button)
        self.input_layout.addWidget(self.create_mine_button)
        self.input_layout.addWidget(self.load_button)
        # Cột phải - Hiển thị thông tin profile
        self.profile_table = QTableWidget()
        self.profile_table.setColumnCount(6)
        self.profile_table.setHorizontalHeaderLabels(['ID', 'Wallet', 'Key', 'Action'])

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




    def login_action(self, profile_path, email):
        global accList
        web = 'https://www.mycloudwallet.com/signin'
        chrome_options = Options()
        try:
            chrome_options.add_argument(f'--user-data-dir={profile_path}')
            chrome_options.add_argument('--no-experiments')
            driver = webdriver.Chrome(options=chrome_options)
            driver.get(web)
            wait = WebDriverWait(driver, 3)
            email_field = wait.until(EC.presence_of_element_located(
                (By.CSS_SELECTOR, 'input[placeholder="Enter profile username or email address"]')))

            # Bạn có thể tiếp tục tương tác với phần tử email_input nếu nó đã xuất hiện
            password_field = wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'input[placeholder="Enter password"]')))

            email_field.send_keys(email)
            password_field.send_keys(accList[email]['password'])
            time.sleep(1)
            login_button = driver.find_element(By.XPATH, "//button[contains(., 'Sign In')]")
            login_button.click()

            # Thêm thông tin profile vào bảng
            wait = WebDriverWait(driver, 10)
            twofa_input = wait.until(EC.presence_of_element_located((By.ID, 'tfacode')))

            twofa_string = self.get_twofa_string(accList[email]['twofa'])
            print(twofa_string)
            twofa_input.send_keys(twofa_string)
            continue_button = driver.find_element(By.XPATH, "//button[contains(., 'CONTINUE')]")
            continue_button.click()
            WebDriverWait(driver, 10).until(EC.url_to_be('https://www.mycloudwallet.com/dashboard'))
            time.sleep(2)
            # element = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.CLASS_NAME, "avatar-div-3")))

            # accList[email]['wallet'] = element.text.strip()

            driver.quit()
        except TimeoutException:
            print("Không tìm thấy phần tử email. Xử lý tại đây...")

    def open_url_in_thread(self, profile_path, web, email):
        # def run_thread():
        chrome_options = Options()
        print(f"Running: {str(email)}")
        driver2 = None
        global accList
        if web == 'https://web.telegram.org/a/#6430669852':
            try:
                chrome_options.add_argument(f'--user-data-dir={profile_path}')
                chrome_options.add_argument('--no-experiments')
                driver2 = webdriver.Chrome(options=chrome_options)
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

                    time.sleep(3)

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

                    print("Src attribute of the iframe:", iframe.get_attribute('src'))
                    driver2.switch_to.frame(iframe)
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
                        setInterval(clickButton, 1000);
                        setInterval(clickButtonGetClaim, 2000);
                        """
                    driver2.execute_script(script)
                    time.sleep(11)
                    driver2.switch_to.default_content()


                except (NoSuchElementException, TimeoutException):
                    print("claim_button_next not found")


            except (NoSuchElementException, TimeoutException) as e:
                print(f"Xảy ra lỗi: {str(e)}")
            finally:
                if driver2 is not None:
                    print('Quit')
                    driver2.quit()
                # threading.Thread(target=run_thread).start()

    def stop_event(self):
        # Event to indicate whether the threads should continue running
        stop_event = threading.Event()


        time.sleep(2)
        stop_event.set()

        # Wait for the worker thread to finish
        print("Worker thread stopped")

    def morning_shift_mining_acction(self):
        # input_text = self.input_text.toPlainText()
        # profiles_data = input_text.strip().split('\n')
        global accList
        global futures
        num_threads_text = self.input_thread.toPlainText()
        hour_start = int(self.input_morning.toPlainText())
        hour_end = (hour_start + 12) % 24
        current_time = datetime.now()
        current_hour = current_time.hour
        is_morning = hour_start <= current_hour < hour_end
        try:
            num_threads = int(num_threads_text)
        except ValueError:
            print("Invalid input for number of threads")
            num_threads = 1  # Default to 1 thread if input is invalid

        event = threading.Event()
        keys_list = list(accList.keys())
        length = len(keys_list)

        if is_morning:
            from_count = 0
            end_count = length // 2
        else:
            from_count = (length // 2) + 1
            end_count = length
        with ThreadPoolExecutor(max_workers=num_threads) as executor:
            for i in range(from_count, end_count):
                email = keys_list[i]
                future = executor.submit(self.open_url, email, event)
                futures.append(future)
                # if len(futures) >= num_threads:
                #     # Wait for at least one future to complete
                #     print('Wait for at least one future to complete')
                #     for future in as_completed(futures):
                #         pass  # Ensure all threads have started before continuing
                #     futures.clear()
        self.morning_shift_mining_acction()


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
    def import_data(self):
        options = QFileDialog.Options()
        options |= QFileDialog.ReadOnly

        file_name, _ = QFileDialog.getOpenFileName(self, "Chọn tệp", "", "All Files (*);;Text Files (*.txt)",
                                                   options=options)

        if file_name:
            # Đọc nội dung tệp và insert vào trường nhập liệu
            with open(file_name, 'r') as file:
                file_content = file.read()
                self.textfield.setText(file_content)

    def export_data(self):
        # Đây là nơi bạn có thể thêm mã xử lý cho nút "Export"
        print('Export button clicked')
    def create_profile(self, mine):
        input_text = self.input_text.toPlainText()
        profiles_data = input_text.strip().split('\n')
        global accList

        event = threading.Event()
        with ThreadPoolExecutor(max_workers=4) as executor:
            for profile_data in profiles_data:

                if '\t' in profile_data:
                    email, wallet, key = profile_data.split('\t')
                elif '|' in profile_data:
                    email, wallet, key = profile_data.split('|')
                accList[email] = {
                    'wallet': wallet,
                    'key': key,
                }
                profile = {'email': email, 'wallet': wallet, 'key': key}
                self.profiles.append(profile)
                # Tạo trình duyệt Chrome
                profile_path = f"C:/path/to/profiles/{email}"  # Đường dẫn thư mục lưu trữ hồ sơ
                if not os.path.exists(profile_path):
                    os.makedirs(profile_path)

                chrome_options = Options()
                chrome_options.add_argument(f'--user-data-dir={profile_path}')
                future = executor.submit(self.open_url_login, email, event)
                futures.append(future)
        self.clear_table()
        self.add_profile_to_table(accList)
        if mine == 'Yes':
            self.morning_shift_mining_acction()

    def get_twofa_string(self, twofa):
        # Gửi token đến 2fa.ec2network.info/2fa và nhận mã 2FA
        # Đây là nơi bạn có thể thêm mã gọi API để nhận mã 2FA từ token.
        # Đoạn mã này cần tương tác với API 2FA để nhận mã và trả về mã đó.
        # Dưới đây là một ví dụ giả định:


        api_url = f'https://2fa.ec2network.info/{twofa}'
        response = requests.get(api_url)
        if response.status_code == 200:
            json_string = response.text
            try:
                data = json.loads(json_string)
                token = data.get('token')
                print(token)  # In ra 550226
                return token
            except json.JSONDecodeError:
                print("Không thể phân tích chuỗi JSON")
                return

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
            driver3.get('https://web.telegram.org')
            WebDriverWait(driver3, 800).until(EC.presence_of_element_located((By.ID, 'facebook')))
            return driver3

        except TimeoutException:
            print('Error')
        finally:
            driver3.quit()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = ChromeProfileManager()
    window.show()
    sys.exit(app.exec_())
