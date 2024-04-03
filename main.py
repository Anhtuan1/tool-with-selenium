import sys
import time
import os  # Thêm thư viện os
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
from concurrent.futures import ThreadPoolExecutor, wait, as_completed
from datetime import datetime

accList = {}

class ChromeProfileManager(QMainWindow):
    threads = []
    def __init__(self):
        super().__init__()

        self.initUI()
        self.profiles = []

    def initUI(self):
        self.setWindowTitle('Quản lý Profile Chrome')
        self.setGeometry(100, 100, 1200, 800)

        # Giao diện người dùng
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.layout = QHBoxLayout(self.central_widget)

        # Cột trái - Nhập thông tin và tạo profile
        self.input_layout = QVBoxLayout()


        self.input_label = QLabel('Nhập thông tin (email|password|2fa):')
        self.input_text = QTextEdit()
        self.input_text.setPlaceholderText('email1|password1|2fa1\nemail2|password2|2fa2')
        self.create_button = QPushButton('Create Profile')
        self.create_button.clicked.connect(self.create_profile)
        self.load_button = QPushButton('Load Profile')
        self.load_button.clicked.connect(self.load_profile)
        self.input_layout.addWidget(self.input_label)
        self.input_layout.addWidget(self.input_text)
        self.input_layout.addWidget(self.create_button)
        self.input_layout.addWidget(self.load_button)
        # Cột phải - Hiển thị thông tin profile
        self.profile_table = QTableWidget()
        self.profile_table.setColumnCount(6)
        self.profile_table.setHorizontalHeaderLabels(['Email', 'Password', '2FA', 'Wallet', 'Time', 'Next Time'])

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
        self.input_thread.setText('6')
        self.input_thread.setPlaceholderText('Number thread')

        self.input_custom = QTextEdit()
        self.input_custom.setFixedHeight(50)
        self.input_custom.setText('https://bot.ec2network.info')
        self.input_custom.setPlaceholderText('Url custom')

        self.morning_shift_mining = QPushButton('Shift start')
        self.all_mining = QPushButton('All start')

        self.actionLayout.addWidget(self.input_custom)
        self.actionLayout.addWidget(self.input_thread)
        self.actionLayout.addWidget(self.input_morning)
        self.actionLayout.addWidget(self.morning_shift_mining)
        self.actionLayout.addWidget(self.all_mining)

        self.morning_shift_mining.clicked.connect(self.morning_shift_mining_acction)

        self.input_layout.addLayout(self.actionLayout)
        self.layout.addLayout(self.input_layout)
        self.layout.addLayout(self.right_layout)

    def open_url_in_thread(self, profile_path, web, email):
        # def run_thread():
        chrome_options = Options()
        print('Run profile')
        driver2 = None
        global accList
        try:
            chrome_options.add_argument(f'--user-data-dir={profile_path}')
            chrome_options.add_argument('--no-experiments')
            driver2 = webdriver.Chrome(options=chrome_options)
            if web is not None:
                driver2.get(web)
            else:
                driver2.get('https://www.mycloudwallet.com')
            try:
                WebDriverWait(driver2, 40).until(EC.number_of_windows_to_be(2))
                driver2.switch_to.window(driver2.window_handles[1])
                element_on_B = WebDriverWait(driver2, 20).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "sc-vuxumm-0")))
                element_on_B.click()
                driver2.switch_to.window(driver2.window_handles[0])
                # Get the current time
                current_time = datetime.now()
                time_string = current_time.strftime("%Y-%m-%d %H:%M:%S")

                accList[email]['time'] = time_string
                self.clear_table()
                self.add_profile_to_table(accList)

                time.sleep(2)
                # wait.until(EC.url_to_be('https://www.mycloudwallet.com/cloud-wallet/signing/'))


            except TimeoutException:
                print("Không tìm thấy phần tử email. Xử lý tại đây...")

        except (NoSuchElementException, TimeoutException) as e:
            print(f"Xảy ra lỗi: {str(e)}")
        finally:
            if driver2 is not None:
                print('Quit')
                driver2.quit()
                # threading.Thread(target=run_thread).start()

    def morning_shift_mining_acction(self):
        input_text = self.input_text.toPlainText()
        profiles_data = input_text.strip().split('\n')
        num_threads_text = self.input_thread.toPlainText()
        global accList
        try:
            num_threads = int(num_threads_text)
        except ValueError:
            print("Invalid input for number of threads")
            num_threads = 1  # Default to 1 thread if input is invalid

        event = threading.Event()
        keys_list = list(accList.keys())
        length = len(keys_list)
        with ThreadPoolExecutor(max_workers=num_threads) as executor:
            futures = []
            for i in range(length // 2):
                email = keys_list[i]
                future = executor.submit(self.open_url, email, event)
                futures.append(future)
                if len(futures) >= num_threads:
                    # Wait for at least one future to complete
                    for future in as_completed(futures):
                        pass  # Ensure all threads have started before continuing
                    futures.clear()
        self.morning_shift_mining_acction()

            # Wait for remaining futures to complete
            # for future in as_completed(futures):
            #     print(future)
            #     pass  # Ensure all threads have started before continuing



    def open_url(self, email, event):
        web = self.input_custom.toPlainText()
        profile_path = f"C:/path/to/profiles/{email}"
        if os.path.exists(profile_path):
            # event.wait()
            self.open_url_in_thread(profile_path, web, email)

    def load_profile(self):
        global accList
        input_text = self.input_text.toPlainText()
        profiles_data = input_text.strip().split('\n')
        for profile_data in profiles_data:
            email, password, twofa = profile_data.split('|')
            accList[email] = {
                'wallet': '',
                'password': password,
                'twofa': twofa,
            }
            # profile_path = f"C:/path/to/profiles/{email}"
            # if not os.path.exists(profile_path):
            #     os.makedirs(profile_path)
            # chrome_options = Options()
            # chrome_options.add_argument(f'--user-data-dir={profile_path}')
            # driver = webdriver.Chrome(options=chrome_options)
            # driver.get('https://www.mycloudwallet.com/dashboard')
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
    def create_profile(self):
        input_text = self.input_text.toPlainText()
        profiles_data = input_text.strip().split('\n')
        global accList
        for profile_data in profiles_data:
            email, password, twofa = profile_data.split('|')
            accList[email] = {
                'wallet': '',
                'password': password,
                'twofa': twofa
            }
            profile = {'email': email, 'password': password, 'twofa': twofa}
            self.profiles.append(profile)

            # Tạo trình duyệt Chrome
            profile_path = f"C:/path/to/profiles/{email}"  # Đường dẫn thư mục lưu trữ hồ sơ
            if not os.path.exists(profile_path):
                os.makedirs(profile_path)
            chrome_options = Options()
            chrome_options.add_argument(f'--user-data-dir={profile_path}')
            # chrome_options.add_argument('--no-experiments')

            driver = webdriver.Chrome(options=chrome_options)
            driver.get('https://www.mycloudwallet.com/signin')
            # Đợi cho đến khi phần tử input email xuất hiện


            # Đợi cho đến khi phần tử input password xuất hiện

            # Điền thông tin đăng nhập
            # email_field = driver.find_element_by_css_selector('input[placeholder="Enter profile username or email address"]')
            # password_field = driver.find_element_by_css_selector('input[placeholder="Enter profile username or email address"]')

            try:
                wait = WebDriverWait(driver, 3)
                email_field = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'input[placeholder="Enter profile username or email address"]')))

                # Bạn có thể tiếp tục tương tác với phần tử email_input nếu nó đã xuất hiện
                password_field = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, 'input[placeholder="Enter password"]')))

                email_field.send_keys(email)
                password_field.send_keys(password)
                time.sleep(1)
                login_button = driver.find_element(By.XPATH, "//button[contains(., 'Sign In')]")
                login_button.click()

                # Thêm thông tin profile vào bảng
                wait = WebDriverWait(driver, 10)
                twofa_input = wait.until(EC.presence_of_element_located((By.ID, 'tfacode')))

                twofa_string = self.get_twofa_string(twofa)
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
        self.clear_table()
        self.add_profile_to_table(accList)

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
            self.profile_table.setItem(row_position, 1, QTableWidgetItem(value.get('password', '')))
            self.profile_table.setItem(row_position, 2, QTableWidgetItem(value.get('twofa', '')))
            self.profile_table.setItem(row_position, 3, QTableWidgetItem(value.get('wallet', '')))
            self.profile_table.setItem(row_position, 4, QTableWidgetItem(value.get('time', '')))
            self.profile_table.setItem(row_position, 5, QTableWidgetItem(value.get('next', '')))

    def open_profile(self, email, web):
        # Kiểm tra xem thư mục lưu trữ hồ sơ đã tồn tại
        profile_path = f"C:/path/to/profiles/{email}"  # Đường dẫn thư mục lưu trữ hồ sơ
        if os.path.exists(profile_path):
            # Tạo trình duyệt Chrome và truy cập trang web
            chrome_options = Options()
            print('Run profile')
            driver2 = None
            try:
                chrome_options.add_argument(f'--user-data-dir={profile_path}')
                chrome_options.add_argument('--no-experiments')
                driver2 = webdriver.Chrome(options=chrome_options)
                if web is not None:
                    driver2.get(web)
                else:
                    driver2.get('https://www.mycloudwallet.com')
                time.sleep(20)
                # driver2.quit()
            except (NoSuchElementException, TimeoutException) as e:
                print(f"Xảy ra lỗi: {str(e)}")
            finally:
                if driver2 is not None:
                    driver2.quit()
if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = ChromeProfileManager()
    window.show()
    sys.exit(app.exec_())
