import imaplib
import email
import re
import time
import unittest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
from django.conf import settings

class TestFullFlow(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        options = webdriver.ChromeOptions()
        options.add_argument('--disable-gpu')
        options.add_argument("--window-size=1920,1080")
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.set_capability("goog:loggingPrefs", {"performance": "ALL"})
        service = Service("/usr/bin/chromedriver")
        cls.driver = webdriver.Chrome(service=service, options=options)
        cls.driver.implicitly_wait(10)

        cls.email_credentials = {
            'admin_email': settings.ADMIN_EMAIL,
            'admin_app_password': settings.ADMIN_APP_PASSWORD,  # Admin's app-specific password
            'staff_email': settings.STAFF_EMAIL,
            'staff_password': settings.STAFF_PASSWORD,  # Staff's Fitopia password
            'staff_app_password': settings.STAFF_APP_PASSWORD  # Staff's app-specific password
        }

    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()

    def scroll_to_bottom(self):
        last_height = self.driver.execute_script("return document.body.scrollHeight")
        while True:
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)  # Wait for the page to load
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height

    def fetch_latest_email(self, username, password, folder='inbox', retries=5, delay=10):
        for _ in range(retries):
            try:
                mail = imaplib.IMAP4_SSL("imap.gmail.com")
                mail.login(username, password)
                mail.select(folder)
                status, messages = mail.search(None, 'UNSEEN')
                mail_ids = messages[0].split()
                if not mail_ids:
                    print("No unread emails found, retrying...")
                    time.sleep(delay)
                    continue
                latest_email_id = mail_ids[-1]
                second_latest_email_id = mail_ids[-2] if len(mail_ids) > 1 else latest_email_id
                status, latest_msg_data = mail.fetch(latest_email_id, '(RFC822)')
                status, second_latest_msg_data = mail.fetch(second_latest_email_id, '(RFC822)')
                latest_email_msg = None
                second_latest_email_msg = None
                for response_part in latest_msg_data:
                    if isinstance(response_part, tuple):
                        latest_email_msg = email.message_from_bytes(response_part[1])
                for response_part in second_latest_msg_data:
                    if isinstance(response_part, tuple):
                        second_latest_email_msg = email.message_from_bytes(response_part[1])
                return latest_email_msg, second_latest_email_msg
            except imaplib.IMAP4.error as e:
                print(f"IMAP4 login failed: {e}")
                raise
        raise ValueError("Failed to fetch latest email after several retries.")

    def extract_otp_from_email(self, email_messages, email_content, otp_length):
        for email_message in email_messages:
            if email_message is None:
                continue
            email_body = ""
            for part in email_message.walk():
                if part.get_content_type() == "text/plain":
                    email_body = part.get_payload(decode=True).decode()
                    break
                elif part.get_content_type() == "text/html":
                    html_part = part.get_payload(decode=True).decode()
                    soup = BeautifulSoup(html_part, 'html.parser')
                    email_body = soup.get_text()
                    break
            print(f"Email body: {email_body}")
            otp_pattern = re.compile(rf'{re.escape(email_content)}\s*(\w{{{otp_length}}})')
            match = otp_pattern.search(email_body)
            if match:
                print(f"OTP found: {match.group(1)}")
                return match.group(1)
        print("OTP not found")
        return None

    def test01_staff_login(self):
        print("Starting test_staff_login")
        self.driver.get("https://fitopia.fr.to/login/")

        cookie = self.driver.get_cookies()
        print(cookie)
        
        # Fill the username field
        username_field = self.driver.find_element(By.NAME, "username")
        username_field.send_keys(self.email_credentials['staff_email'])
        
        # Fill the password field
        password_field = self.driver.find_element(By.ID, "password")
        password_field.send_keys(self.email_credentials['staff_password'])
        print("Current URL before login attempt:", self.driver.current_url)

        # Locate and click the login button using JavaScript
        login_button = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Login')]")
        self.driver.execute_script("arguments[0].click();", login_button)
        print("Login form submitted")

        # Introduce a delay before fetching the OTP for staff
        time.sleep(5)

        # Retrieve the OTP from the staff's Gmail
        print("Fetching OTP from email")
        latest_email_msg, second_latest_email_msg = self.fetch_latest_email(
            self.email_credentials['staff_email'], self.email_credentials['staff_app_password']
        )
        otp = self.extract_otp_from_email([latest_email_msg, second_latest_email_msg], "OTP below to complete your login:", 6)
        self.assertIsNotNone(otp)

        # Wait for the OTP input to be present
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, "otp"))
        )
        print("OTP field located")

        # Complete the two-factor authentication for staff
        otp_field = self.driver.find_element(By.ID, "otp")
        otp_field.send_keys(otp)
        print(f"OTP field value: {otp_field.get_attribute('value')}")

        self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        print("Two-factor authentication completed")


    def test02_add_class_as_staff(self):
        time.sleep(5)
        print("Current URL after login attempt:", self.driver.current_url)
        print("Starting test_add_class_as_staff")
        # Ensure the "Add Class" button is present and clickable
        add_class_button = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "(//button[contains(text(), 'Add Class')])"))
        )
        add_class_button.click()
        print("Add Class button clicked")

        # Ensure the class name input is present
        class_name_input = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "(//input[@type='text'])[1]"))
        )
        class_name_input.click()
        class_name = "Pilates Class"
        class_name_input.send_keys(class_name)
        print("Class name entered")

        # Fill in the class details
        description_input = self.driver.find_element(By.XPATH, "(//input[@type='text'])[2]")
        description_input.click()
        class_description = "Bring your mats."
        description_input.send_keys(class_description)
        print("Class description entered")

        # Set the start date and time
        datetime_input = self.driver.find_element(By.XPATH, "(//input[@type='datetime-local'])")
        datetime_input.send_keys("020102025")
        datetime_input.send_keys(Keys.TAB)  # Navigate to the time part
        datetime_input.send_keys("12:00PM")
        print("Class start date and time entered")
        
        self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        print("Submit button clicked")

        # Scroll to the bottom of the page
        self.scroll_to_bottom()
        print("Scrolled to bottom")

        last_class_row = self.driver.find_element(By.XPATH, "(//table/tbody/tr[last()])")
        class_name_element = last_class_row.find_element(By.XPATH, "./td[1]")
        assert class_name_element.text == class_name, f"Expected class name '{class_name}', but found '{class_name_element.text}'"
        print("Class name verified")

        class_desc_element = last_class_row.find_element(By.XPATH, "./td[2]")
        assert class_desc_element.text == class_description, f"Expected class description '{class_description}', but found '{class_desc_element.text}'"
        print("Class description verified")

    def test03_view_class_details(self):
        print("Starting test_view_class_details")
        # Ensure the "View" button is present and clickable on the last row
        last_view_button = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "(//table/tbody/tr[last()]/td[last()]//button[contains(@class, 'MuiButton-containedSuccess')])[last()]"))
        )
        last_view_button.click()
        print("View button clicked")

        # Assert the class name in the details view
        class_name_element = WebDriverWait(self.driver, 5).until(
            EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'MuiTypography-h3') and text()='Pilates Class']"))
        )
        assert "Pilates Class" in class_name_element.text, "Class name not found in details view"
        print("Class name verified in details view")

        # Assert the class description in the details view
        class_desc_element = WebDriverWait(self.driver, 5).until(
            EC.presence_of_element_located((By.XPATH, "//h6[contains(@class, 'MuiTypography-h6') and text()='Bring your mats.']"))
        )
        assert "Bring your mats." in class_desc_element.text, "Class description not found in details view"
        print("Class description verified in details view")

        class_datetime_element = self.driver.find_element(By.XPATH, "//p")
        assert class_datetime_element.text == "Start DateTime: 01/02/2025, 12:00 PM", "Class start date and time not found in details view"
        print("Class start date and time verified in details view")

    def test04_edit_class_details(self):
        print("Starting test_edit_class_details")
        # Ensure the "Edit" button is present and clickable on the last row
        edit_button = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "(//button[contains(text(), 'Edit Class')])"))
        )
        edit_button.click()
        print("Edit button clicked")

        # Change the class name
        class_name_input = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "(//input[@type='text'])[1]"))
        )
        while class_name_input.get_attribute('value') != '':
            class_name_input.send_keys(Keys.BACKSPACE)
        class_name = "Yoga Class"
        class_name_input.send_keys(class_name)
        print("Class name edited")

        # Change the class description
        class_desc_input = self.driver.find_element(By.XPATH, "(//input[@type='text'])[2]")
        while class_desc_input.get_attribute('value') != '':
            class_desc_input.send_keys(Keys.BACKSPACE)
        class_description = "A relaxing yoga session."
        class_desc_input.send_keys(class_description)
        print("Class description edited")

        # Change the start date and time
        datetime_input = self.driver.find_element(By.XPATH, "(//input[@type='datetime-local'])")
        datetime_input.click()
        datetime_input.send_keys("30")
        print("Class start date and time edited")

        self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        print("Submit button clicked")

        # Navigate back to the previous page
        self.driver.back()
        print("Navigated back to the previous page")

        print("Current URL after navigating to classes:", self.driver.current_url)

        last_class_row = self.driver.find_element(By.XPATH, "(//table/tbody/tr[last()])")
        class_name_element = last_class_row.find_element(By.XPATH, "./td[1]")
        assert class_name_element.text == class_name, f"Expected class name '{class_name}', but found '{class_name_element.text}'"
        print("Class name verified after edit")

        class_desc_element = last_class_row.find_element(By.XPATH, "./td[2]")
        assert class_desc_element.text == class_description, f"Expected class description '{class_description}', but found '{class_desc_element.text}'"
        print("Class description verified after edit")

    def test05_delete_class(self):
        print("Starting test_delete_class")
        self.scroll_to_bottom()
        print("Scrolled to bottom")

        # Count the number of rows before deletion
        initial_rows = self.driver.find_elements(By.XPATH, "//table/tbody/tr")
        initial_row_count = len(initial_rows)
        print(f'Initial row count: {initial_row_count}')

        # Ensure the "Delete" button is present and clickable on the last row
        last_delete_button = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "(//table/tbody/tr[last()]/td[last()]//button[contains(@class, 'MuiButton-containedError')])[last()]"))
        )
        last_delete_button.click()
        print("Delete button clicked")

        time.sleep(5)

        # Count the number of rows after deletion
        final_rows = self.driver.find_elements(By.XPATH, "//table/tbody/tr")
        final_row_count = len(final_rows)
        print(f'Final row count: {final_row_count}')

        # Verify that the row count has decreased by one
        assert final_row_count == initial_row_count - 1, f"Expected row count to decrease by 1, but it didn't. Initial: {initial_row_count}, Final: {final_row_count}"
        print("Class deletion verified")


if __name__ == "__main__":
    unittest.main()