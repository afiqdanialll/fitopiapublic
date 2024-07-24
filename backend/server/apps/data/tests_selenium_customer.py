import os
import time
import unittest
import imaplib
import email
import re
from bs4 import BeautifulSoup
from django.conf import settings
from django.core import mail
from django.test import TestCase
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException,
    UnexpectedAlertPresentException,
    NoAlertPresentException,
    StaleElementReferenceException,
    NoSuchElementException,
)
from django.contrib.auth import get_user_model
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains


class BaseTest(TestCase):

    @classmethod
    def setUpClass(cls):
        options = webdriver.ChromeOptions()
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.set_capability("goog:loggingPrefs", {"performance": "ALL"})
        service = Service("/usr/bin/chromedriver")
        cls.driver = webdriver.Chrome(service=service, options=options)
        cls.driver.implicitly_wait(10)

        cls.email_credentials = {
            "customer_email": settings.CUSTOMER_EMAIL,
            "customer_password": settings.CUSTOMER_PASSWORD,  # Customer's Fitopia password
            "customer_app_password": settings.CUSTOMER_APP_PASSWORD,  # Customer's app-specific password
        }

        cls.screenshot_dir = "/mnt/data"
        os.makedirs(cls.screenshot_dir, exist_ok=True)

        # cls.sign_up()

    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()

    @classmethod
    def sign_up(cls):
        driver = cls.driver
        driver.get("https://fitopia.fr.to/login")  # Change to your own IP address

        # Click on the "Sign up" link
        try:
            sign_up_link = driver.find_element(
                By.XPATH, '//a[contains(text(), "Don\'t have an account? Sign up.")]'
            )
            sign_up_link.click()
            time.sleep(2)  # Adding sleep to allow for navigation

            # Wait for the signup page to load
            WebDriverWait(driver, 40).until(
                EC.visibility_of_element_located((By.NAME, "username"))
            )
            print("Signup page loaded successfully")

            # Fill out the signup form
            driver.find_element(By.NAME, "first_name").send_keys("John")
            driver.find_element(By.NAME, "last_name").send_keys("Doe")
            driver.find_element(By.NAME, "username").send_keys(
                cls.email_credentials["customer_email"]
            )
            driver.find_element(By.NAME, "password").send_keys(
                cls.email_credentials["customer_password"]
            )

            # Submit the signup form
            sign_up_button = driver.find_element(
                By.XPATH, "//button[contains(text(), 'Sign Up')]"
            )
            driver.execute_script("arguments[0].click();", sign_up_button)
            time.sleep(15)  # Adding sleep to allow form submission to process

            # Wait for redirection to the login page
            WebDriverWait(driver, 40).until(EC.url_contains("login"))

        except Exception as e:
            print("TimeoutException or Element not found.")
            page_source_path = os.path.join(
                cls.screenshot_dir, "signup_error_page_source.html"
            )
            with open(page_source_path, "w") as file:
                file.write(driver.page_source)

            raise e

        # Check if the user has been created in the database
        user_exists = (
            get_user_model()
            .objects.filter(username=cls.email_credentials["customer_email"])
            .exists()
        )
        assert user_exists, "User was not created in the database"

    def fetch_latest_email(
        self, username, password, folder="inbox", retries=5, delay=10
    ):
        for _ in range(retries):
            try:
                mail = imaplib.IMAP4_SSL("imap.gmail.com")
                mail.login(username, password)
                mail.select(folder)
                status, messages = mail.search(None, "UNSEEN")
                mail_ids = messages[0].split()
                if not mail_ids:
                    print("No unread emails found, retrying...")
                    time.sleep(delay)
                    continue
                latest_email_id = mail_ids[-1]
                status, latest_msg_data = mail.fetch(latest_email_id, "(RFC822)")
                for response_part in latest_msg_data:
                    if isinstance(response_part, tuple):
                        latest_email_msg = email.message_from_bytes(response_part[1])
                        subject = latest_email_msg["subject"]
                        print(f"Email subject: {subject}")
                        if "OTP" in subject:
                            return latest_email_msg
                print("No OTP email found, retrying...")
                time.sleep(delay)
            except imaplib.IMAP4.error as e:
                print(f"IMAP4 login failed: {e}")
                raise
        raise ValueError("Failed to fetch latest OTP email after several retries.")

    def extract_otp_from_email(self, email_message, otp_length=6):
        if email_message is None:
            print("No email message provided.")
            return None
        email_body = ""
        for part in email_message.walk():
            if part.get_content_type() == "text/plain":
                email_body = part.get_payload(decode=True).decode()
                break
            elif part.get_content_type() == "text/html":
                html_part = part.get_payload(decode=True).decode()
                soup = BeautifulSoup(html_part, "html.parser")
                email_body = soup.get_text()
                break
        print(f"Email body: {email_body}")
        otp_pattern = re.compile(r"(\b[A-Z0-9]{6}\b)")
        match = otp_pattern.search(email_body)
        if match:
            print(f"OTP found: {match.group(1)}")
            return match.group(1)
        print("OTP not found")
        return None

    def test01_login(self):
        print("Starting test_customer_login")
        self.driver.get("https://fitopia.fr.to/login/")

        cookie = self.driver.get_cookies()
        print(cookie)

        # Fill the username field
        username_field = self.driver.find_element(By.ID, "username")
        username_field.send_keys(self.email_credentials["customer_email"])

        # Fill the password field
        password_field = self.driver.find_element(By.ID, "password")
        password_field.send_keys(self.email_credentials["customer_password"])
        print("Current URL before login attempt:", self.driver.current_url)

        # Locate and click the login button using JavaScript
        login_button = self.driver.find_element(
            By.XPATH, "//button[contains(text(), 'Login')]"
        )
        self.driver.execute_script("arguments[0].click();", login_button)
        print("Login form submitted")

        # Introduce a delay before fetching the OTP for customer
        time.sleep(5)

        # Retrieve the OTP from the customer's Gmail
        print("Fetching OTP from email")
        latest_email_msg = self.fetch_latest_email(
            self.email_credentials["customer_email"],
            self.email_credentials["customer_app_password"],
        )
        otp = self.extract_otp_from_email(latest_email_msg)
        self.assertIsNotNone(otp)

        # Wait for the OTP input to be present
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, "otp"))
        )
        print("OTP field located")

        # Complete the two-factor authentication for customer
        otp_field = self.driver.find_element(By.ID, "otp")
        otp_field.send_keys(otp)
        print(f"OTP field value: {otp_field.get_attribute('value')}")

        self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        print("Two-factor authentication completed")

    def test02_edit_profile(self):
        driver = self.driver
        time.sleep(5)
        # Navigate to profile page
        print("Navigating to profile page")
        try:
            profile_link = WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.LINK_TEXT, "PROFILE"))
            )
            profile_link.click()

            # Wait for the profile page to load
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located(
                    (By.XPATH, "//button[contains(text(), 'Edit')]")
                )
            )
            print("Profile page loaded successfully.")
        except Exception as e:
            print("Failed to navigate to the profile page.")
            self.save_debug_info(driver, "profile_navigation_failed")
            raise e

        # Click on the Edit button
        print("Clicking on the Edit button")
        try:
            edit_button_locator = (By.XPATH, "//button[contains(text(), 'Edit')]")
            self.click_with_retry(
                driver, edit_button_locator
            )  # Using JavaScript to click the button

            # Wait for the edit form to appear
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.NAME, "first_name"))
            )
            print("Edit form appeared successfully.")
        except Exception as e:
            print("Failed to click the Edit button or wait for the edit form.")
            self.save_debug_info(driver, "edit_button_click_failed")
            raise e

        # Change first and last name
        print("Editing first name and last name")
        first_name_locator = (By.NAME, "first_name")
        last_name_locator = (By.XPATH, "//input[@name='last_name']")  # Changed to XPath

        # Ensure fields are interactable
        try:
            print("Ensuring fields are interactable")
            driver.execute_script(
                "arguments[0].scrollIntoView(true);",
                driver.find_element(*first_name_locator),
            )
            driver.execute_script(
                "arguments[0].scrollIntoView(true);",
                driver.find_element(*last_name_locator),
            )
        except Exception as e:
            print("Failed to ensure fields are interactable.")
            self.save_debug_info(driver, "fields_not_interactable")
            raise e

        # Clear and enter new values
        try:
            print("Clearing and entering new value in First Name field")
            self.clear_and_type(driver, first_name_locator, "NewFirstName")
            print("Clearing and entering new value in Last Name field")
            self.clear_and_type(driver, last_name_locator, "NewLastName")

            # Log field values after entering new values
            print(
                "First Name after entering new value:",
                driver.find_element(*first_name_locator).get_attribute("value"),
            )
            print(
                "Last Name after entering new value:",
                driver.find_element(*last_name_locator).get_attribute("value"),
            )
        except Exception as e:
            print("Failed to clear and enter new values in the fields.")
            self.save_debug_info(driver, "clear_and_type_failed")
            raise e

        # Submit the form
        print("Submitting the form")
        try:
            submit_button_locator = (By.XPATH, "//button[contains(text(), 'Save')]")
            self.click_with_retry(
                driver, submit_button_locator
            )  # Using JavaScript to click the button
            print("Form submitted successfully.")
        except Exception as e:
            print("Failed to submit the form.")
            self.save_debug_info(driver, "form_submit_failed")
            raise e

        # Explicitly navigate back to the profile page to check updates
        print("Navigating back to profile page to check updates")
        try:
            profile_link = WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.LINK_TEXT, "PROFILE"))
            )
            profile_link.click()

            # Wait for the profile page to reload and reflect changes
            WebDriverWait(driver, 20).until(
                EC.presence_of_element_located(
                    (By.XPATH, "//h6[text()='NewFirstName']")
                )
            )
        except Exception as e:
            print("TimeoutException: Element not found.")
            self.save_debug_info(driver, "profile_reload_failed")
            raise e

        # Assert that the names have been updated
        print("Asserting the changes")
        try:
            self.assert_with_retry(
                driver, (By.XPATH, "//h6[text()='NewFirstName']"), "NewFirstName"
            )
            self.assert_with_retry(
                driver, (By.XPATH, "//h6[text()='NewLastName']"), "NewLastName"
            )
        except Exception as e:
            print("Failed to assert the changes.")
            self.save_debug_info(driver, "assert_changes_failed")
            raise e

    def test03_check_for_membership(self):
        driver = self.driver

        # Navigate to the membership page.
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.LINK_TEXT, "MEMBERSHIP"))
        )
        driver.find_element(By.LINK_TEXT, "MEMBERSHIP").click()

        # Check for active membership message.
        try:
            active_message = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located(
                    (By.XPATH, "//button[contains(text(),'Go to Homepage')]")
                )
            )
            print("Active membership detected, navigating to homepage.")
            driver.find_element(
                By.XPATH, "//button[contains(text(),'Go to Homepage')]"
            ).click()

        except TimeoutException:
            print("No active membership detected, proceeding with purchase.")
            # Continue with membership purchase if no active membership was found
            self.purchase_membership()

    def purchase_membership(self):
        driver = self.driver
        # Ensure the page has loaded and the correct options are being displayed
        WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.XPATH, "//div[contains(., 'Month')]"))
        )

        # Wait for the specific membership type (12 Months) to be clickable, then find the button and click it.
        membership_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable(
                (
                    By.XPATH,
                    "//div[contains(., '12 Months')]//button[contains(@class, 'MuiButton-root')]",
                )
            )
        )
        # Scroll the membership button into view to ensure it is visible on screen.
        driver.execute_script("arguments[0].scrollIntoView(true);", membership_button)
        # Wait briefly to ensure the page is fully loaded.
        WebDriverWait(driver, 2).until(
            lambda driver: driver.execute_script("return document.readyState")
            == "complete"
        )
        # Click the button to select the 12 Months membership.
        membership_button.click()

        # Wait for the payment form fields to appear.
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "card-number"))
        )
        # Enter payment details: card number, expiry date, and CVV.
        driver.find_element(By.ID, "card-number").send_keys("4242424242424242")
        driver.find_element(By.ID, "expiry-date").send_keys("1229")
        driver.find_element(By.ID, "cvv").send_keys("987")
        # Click the pay now button to submit the payment.
        driver.find_element(By.ID, "pay-button").click()

        # Wait for the success message to appear
        try:
            success_message = WebDriverWait(driver, 10).until(
                EC.visibility_of_element_located(
                    (
                        By.XPATH,
                        "//div[contains(text(), 'Purchase successful! Redirecting...')]",
                    )
                )
            )
            print("Success alert found:", success_message.text)

            # Optionally, check the text explicitly
            assert "Purchase successful! Redirecting..." in success_message.text
            # WebDriverWait(driver, 10).until(EC.url_changes(expected_url))

        except TimeoutException:
            print("The success message did not appear within the expected time.")

    def test04_book_class(self):
        driver = self.driver

        # Navigate to classes page
        print("Navigating to classes page")
        driver.find_element(By.LINK_TEXT, "CLASSES").click()

        # Wait for classes to load and click on the first class' "Book Class" button
        print("Waiting for classes to load")
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (By.XPATH, "//button[contains(text(), 'Book Class')]")
            )
        )
        print("Clicking on Book Class button")
        book_class_button = driver.find_element(
            By.XPATH, "(//button[contains(text(), 'Book Class')])[1]"
        )

        # Get the class name before booking
        class_name = book_class_button.find_element(
            By.XPATH, "./ancestor::tr/td[1]"
        ).text
        print(f"Class name to be booked: {class_name}")

        driver.execute_script(
            "arguments[0].click();", book_class_button
        )  # Using JavaScript to click the button

        try:
            # Wait for the specific class page to load and click on the "Confirm Booking" button
            print("Waiting for specific class page to load")
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located(
                    (By.XPATH, "//button[contains(text(), 'Confirm Booking')]")
                )
            )
            print("Clicking on Confirm Booking button")
            confirm_booking_button = driver.find_element(
                By.XPATH, "//button[contains(text(), 'Confirm Booking')]"
            )
            driver.execute_script(
                "arguments[0].click();", confirm_booking_button
            )  # Using JavaScript to click the button

            # Navigate to bookings page
            print("Navigating to bookings page")
            driver.find_element(By.LINK_TEXT, "BOOKINGS").click()

            # Wait for upcoming bookings to load
            print("Waiting for upcoming bookings to load")
            WebDriverWait(driver, 20).until(
                EC.presence_of_element_located(
                    (By.XPATH, f"//table//td[contains(text(), '{class_name}')]")
                )
            )

            # Assert that the class name is in the upcoming bookings
            print(
                f"Asserting that the class '{class_name}' is in the upcoming bookings"
            )
            self.assertTrue(
                driver.find_element(
                    By.XPATH, f"//table//td[contains(text(), '{class_name}')]"
                )
                is not None
            )

        except UnexpectedAlertPresentException as e:
            alert = driver.switch_to.alert
            alert_text = alert.text
            print(f"Alert text: {alert_text}")
            alert.accept()
            self.fail(f"Could not book class due to alert: {alert_text}")

        except NoAlertPresentException:
            print("No alert present when attempting to switch to it.")
            raise

        except TimeoutException as e:
            print("TimeoutException: Element not found within the given time.")
            
            raise e

    def test05_cancel_class(self):
        driver = self.driver

        # Navigate to bookings page
        print("Navigating to bookings page")
        driver.find_element(By.LINK_TEXT, "BOOKINGS").click()

        # Wait for upcoming bookings to load and click on the first class' "Cancel" button
        print("Waiting for upcoming bookings to load")
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (By.XPATH, "//table//button[contains(text(), 'Cancel')]")
            )
        )
        print("Clicking on Cancel button for the first upcoming booking")
        cancel_button = driver.find_element(
            By.XPATH, "(//table//button[contains(text(), 'Cancel')])[1]"
        )
        print("Cancel button found:", cancel_button is not None)

        # Identify the row by finding the parent elements manually
        try:
            cancel_row = cancel_button
            for _ in range(6):  # Adjust the range as needed to find the <tr> element
                cancel_row = cancel_row.find_element(By.XPATH, "..")
                if cancel_row.tag_name == "tr":
                    break
            print("Cancel row found:", cancel_row is not None)
        except Exception as e:
            print("Error locating cancel row:", e)
            driver.quit()
            return

        try:
            class_name_cell = cancel_row.find_element(By.XPATH, "./td[1]")
            print("Class name cell found:", class_name_cell is not None)
        except Exception as e:
            print("Error locating class name cell:", e)
            driver.quit()
            return

        class_name = class_name_cell.text
        print(f"Class name to be canceled: {class_name}")

        driver.execute_script(
            "arguments[0].click();", cancel_button
        )  # Using JavaScript to click the button

        # Navigate to cancelled bookings tab
        print("Navigating to cancelled bookings tab")
        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located(
                    (By.XPATH, "//button[contains(text(), 'Cancelled')]")
                )
            )
            driver.find_element(
                By.XPATH, "//button[contains(text(), 'Cancelled')]"
            ).click()
        except Exception as e:
            print("Error locating 'Cancelled' tab:", e)
            driver.quit()
            return

        # Wait for cancelled bookings to load and check if the class is listed
        print("Waiting for cancelled bookings to load")
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (By.XPATH, f"//td[contains(text(), '{class_name}')]")
            )
        )
        print(f"Asserting that the class '{class_name}' is in the cancelled bookings")
        self.assertTrue(
            driver.find_element(By.XPATH, f"//td[contains(text(), '{class_name}')]")
            is not None
        )

        # Navigate to classes page
        print("Navigating to classes page")
        driver.find_element(By.LINK_TEXT, "CLASSES").click()

        # Wait for classes to load and check if the cancelled class is back on the list
        print("Waiting for classes to load")
        try:
            WebDriverWait(driver, 20).until(
                EC.presence_of_element_located(
                    (By.XPATH, f"//td[contains(text(), '{class_name}')]")
                )
            )
            print(
                f"Asserting that the class '{class_name}' is back on the classes list"
            )
            self.assertTrue(
                driver.find_element(By.XPATH, f"//td[contains(text(), '{class_name}')]")
                is not None
            )
        except Exception as e:
            print(f"Error locating class '{class_name}' in classes list: {e}")
            print(driver.page_source)  # Print the page source for debugging
            raise e

    def clear_and_type(self, driver, locator, new_value):
        retries = 5  # Increase number of retries for handling stale element
        for attempt in range(retries):
            try:
                # Wait for the element to be present and visible
                element = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located(locator)
                )
                element = WebDriverWait(driver, 10).until(
                    EC.visibility_of_element_located(locator)
                )

                print(f"Value before clearing: {element.get_attribute('value')}")

                # Clear the field using JavaScript
                driver.execute_script("arguments[0].value = '';", element)

                # Verify the field is empty
                print(f"Value after clearing: {element.get_attribute('value')}")

                # Click the field to ensure it is active and clear any remaining text
                element.click()
                element.send_keys(Keys.CONTROL + "a")
                element.send_keys(Keys.DELETE)

                # Ensure the field is empty
                driver.execute_script("arguments[0].value = '';", element)
                print(f"Value after extra clearing: {element.get_attribute('value')}")

                # Send new value using ActionChains
                actions = ActionChains(driver)
                actions.click(element).send_keys(new_value).perform()

                print(f"Typing new value '{new_value}' in the element: {element}")
                print(f"Value after typing: {element.get_attribute('value')}")
                return  # Successfully typed the new value, exit the function

            except (StaleElementReferenceException, NoSuchElementException) as e:
                print(
                    f"Element became stale or not found on attempt {attempt + 1}. Retrying..."
                )
                time.sleep(1)  # Small delay before retrying

        # If all retries fail, raise an exception
        raise TimeoutException(
            f"Failed to interact with the element after {retries} attempts due to staleness or not found."
        )

    def click_with_retry(self, driver, locator):
        try:
            element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located(locator)
            )
            driver.execute_script("arguments[0].click();", element)
        except StaleElementReferenceException:
            print("Element became stale. Re-locating the element for click.")
            element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located(locator)
            )
            self.click_with_retry(driver, locator)  # Recursively retry the action

    def assert_with_retry(self, driver, locator, expected_text, retries=3):
        for attempt in range(retries):
            try:
                element = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located(locator)
                )
                self.assertEqual(element.text, expected_text)
                return
            except StaleElementReferenceException:
                print(f"Stale element reference on attempt {attempt + 1}. Retrying...")
                time.sleep(1)
            except TimeoutException as e:
                print(
                    f"TimeoutException: Element not found on attempt {attempt + 1}. Retrying..."
                )
                time.sleep(1)
                if attempt == retries - 1:
                    # Take screenshot and save page source on the last attempt
                    page_source_path = os.path.join(
                        self.screenshot_dir,
                        f"assert_timeout_page_source_{int(time.time())}.html",
                    )
                    with open(page_source_path, "w") as file:
                        file.write(driver.page_source)
                    print(f"Page source saved to {page_source_path}")

                    screenshot_path = os.path.join(
                        self.screenshot_dir,
                        f"assert_timeout_screenshot_{int(time.time())}.png",
                    )
                    if driver.save_screenshot(screenshot_path):
                        print(f"Screenshot saved to {screenshot_path}")
                    else:
                        print("Failed to save screenshot")

                    raise e

    def save_debug_info(self, driver, stage):
        timestamp = int(time.time())
        screenshot_path = os.path.join(
            self.screenshot_dir, f"{stage}_screenshot_{timestamp}.png"
        )
        page_source_path = os.path.join(
            self.screenshot_dir, f"{stage}_page_source_{timestamp}.html"
        )
        if driver.save_screenshot(screenshot_path):
            print(f"Screenshot saved to {screenshot_path}")
        else:
            print("Failed to save screenshot")
        with open(page_source_path, "w") as file:
            file.write(driver.page_source)
        print(f"Page source saved to {page_source_path}")


if __name__ == "__main__":
    unittest.main()
