from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from django.test import TestCase, override_settings
from django.contrib.auth import get_user_model
from datetime import timezone
from apps.authentication.models import fitopiaUser, Administrator, Staff, Customer
from .models import Customer, Otp
from django.utils import timezone
from datetime import timedelta
from rest_framework_simplejwt.tokens import RefreshToken
from django.core import mail
from .models import Administrator, Staff, fitopiaUser, Customer
from django.conf import settings
import bcrypt

User = get_user_model()

class UserFirstLoginResetPasswordViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', password='old_password')
        self.admin_user = User.objects.create_user(username='adminuser', password='adminpass')
        self.admin = Administrator.objects.create(user=self.admin_user)
        self.staff = Staff.objects.create(user=self.user, created_by=self.admin, password_reset=True)
        self.url = reverse('userResetPassword')  # Corrected URL name
        self.client.force_authenticate(user=self.user)

    def test_reset_password_success(self):
        # Test successful password reset
        data = {'new_password': 'Newpassword123!'}
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['success'], 'Password reset successfully')
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('Newpassword123!'))

    def test_reset_password_missing(self):
        # Test password reset with missing new password
        data = {}
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error'], 'New password is required')

    def test_reset_password_validation_error(self):
        # Test password reset with invalid new password
        data = {'new_password': 'short'}
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)

    def test_reset_password_not_required(self):
        # Test password reset when it's not required
        self.staff.password_reset = False
        self.staff.save()
        data = {'new_password': 'Newpassword123!'}
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error'], 'Password reset not required')

    def test_reset_password_user_not_found(self):
        # Test password reset for a non-existent user
        self.staff.delete()
        data = {'new_password': 'Newpassword123!'}
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['error'], 'User not found')



# ------ Testcase for currentpasswordview -----
class CurrentPasswordViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = fitopiaUser.objects.create_user(
            username="testuser",
            password="current_password",
            email="testuser@example.com"
        )
        self.url = reverse('current-password')
        self.client.force_authenticate(user=self.user)

    def test_correct_current_password(self):
        # Test current password validation
        data = {
            'current_password': 'current_password',
            'new_password': 'new_valid_password123!'
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['match'], True)

    def test_incorrect_current_password(self):
        # Test incorrect current password
        data = {
            'current_password': 'wrong_password',
            'new_password': 'new_valid_password123!'
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error'], 'Current password is incorrect')

    def test_new_password_same_as_current(self):
        # Test new password being the same as the current password
        data = {
            'current_password': 'current_password',
            'new_password': 'current_password'
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error'], 'New password cannot be the same as the current password')

    def test_valid_new_password(self):
        # Test updating to a valid new password
        data = {
            'current_password': 'current_password',
            'new_password': 'new_valid_password123!'
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['match'], True)

    def test_sql_injection_attempt(self):
        # Test SQL injection attempt
        data = {
            'current_password': 'testpass',
            'new_password': "' OR '1'='1'; DROP TABLE users; --"
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)



# # ----- SIGN UP -----
class SignupViewTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.signup_url = reverse('signup')  # Ensure you have named your URL in urls.py

    def test_signup_success(self):
        # Test successful user signup
        data = {
            'first_name': 'John',
            'last_name': 'Doe',
            'username': 'newuser@example.com',
            'password': 'newpassword123'
        }

        response = self.client.post(self.signup_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # Check that the User was created
        self.assertTrue(User.objects.filter(username='newuser@example.com').exists())
        # Check that the Customer was created
        self.assertTrue(Customer.objects.filter(user__username='newuser@example.com').exists())

    def test_signup_failure(self):
        # Test signup failure with invalid data
        data = {
            'first_name': 'John',
            'last_name': 'Doe',
            'username': 'newuser@example.com',
            'password': ''  # Invalid or missing password should trigger an error
        }
        response = self.client.post(self.signup_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('password', response.data)  # Check if password errors are returned

    def test_signup_duplicate_username(self):
        # Test signup failure with duplicate username
        existing_user = User.objects.create(username='existinguser@example.com', first_name='Jane', last_name='Smith')
        existing_user.set_password('password123')
        existing_user.save()
        
        data = {
            'first_name': 'John',
            'last_name': 'Doe',
            'username': 'existinguser@example.com',
            'password': 'newpassword123'
        }
        response = self.client.post(self.signup_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('username', response.data)  # Check if username errors are returned

    def test_sql_injection_attempts_signup(self):
        # Test SQL injection attempts on signup
        sql_injection_payloads = [
            "'; DROP TABLE users; --",
            "' OR '1'='1",
            "' OR '1'='1' --",
            "' OR '1'='1' ({",
            "' OR 1=1--",
            "' OR 1=1#",
            "' OR 1=1/*",
            "' OR '' = '",
            "' OR 1 -- -",
            "admin'--",
            "admin' #",
            "admin'/*",
            "' OR 1=1 LIMIT 1 --",
            "' OR 1=1 LIMIT 1#",
            "' OR 1=1 LIMIT 1/*"
        ]

        for payload in sql_injection_payloads:
            data = {
                'first_name': 'John',
                'last_name': 'Doe',
                'username': payload,
                'password': 'newpassword123'
            }
            response = self.client.post(self.signup_url, data, format='json')
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertIn('username', response.data)
            self.assertFalse(User.objects.filter(username=payload).exists())


# # ---- LOGIN -----
@override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend")
class LoginViewTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.User = get_user_model()
        self.active_user = self.User.objects.create_user(
            username='activeuser@example.com',
            password='testpassword123',
            first_name='Active',
            last_name='User',
            email='activeuser@example.com',
            is_active=True
        )
        self.inactive_user = self.User.objects.create_user(
            username='inactiveuser@example.com',
            password='testpassword123',
            first_name='Inactive',
            last_name='User',
            email='inactiveuser@example.com',
            is_active=False
        )

    def test_login_success(self):
        # Test successful login
        data = {
            'username': 'activeuser@example.com',
            'password': 'testpassword123'
        }
        response = self.client.post(reverse('login'), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('Success', response.data)

    def test_login_failure_invalid_credentials(self):
        # Test login failure with invalid credentials
        data = {
            'username': 'activeuser@example.com',
            'password': 'wrongpassword'
        }
        response = self.client.post(reverse('login'), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn('error', response.data)
        self.assertEqual(response.data['error'], 'Invalid credentials')

    def test_login_failure_inactive_user(self):
        # Test login failure for inactive user
        data = {
            'username': 'inactiveuser@example.com',
            'password': 'testpassword123'
        }
        response = self.client.post(reverse('login'), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn('error', response.data)
        self.assertEqual(response.data['error'], 'Invalid credentials')

    def test_login_triggers_otp_email(self):
        # Test login triggering OTP email
        login_data = {
            'username': 'activeuser@example.com',
            'password': 'testpassword123'
        }
        login_response = self.client.post(reverse('login'), login_data, format='json')

        self.assertEqual(login_response.status_code, status.HTTP_200_OK)
        self.assertIn('Success', login_response.data)

        self.assertEqual(len(mail.outbox), 1)
        sent_mail = mail.outbox[0]

        self.assertEqual(sent_mail.subject, 'Your One-Time Password (OTP)')
        self.assertIn('Dear user,', sent_mail.body)
        self.assertIn('You have requested a One-Time Password (OTP) for authentication. Please use the OTP below to complete your login:', sent_mail.body)
        self.assertIn('For security reasons, this OTP is valid for 1 minute and can be used only once.', sent_mail.body)
        self.assertIn('If you did not request this OTP, please ignore this email or contact support immediately.', sent_mail.body)
        self.assertEqual(sent_mail.to, ['activeuser@example.com'])

    def test_sql_injection_attempts(self):
        # Test login failure with SQL injection attempts
        sql_injection_payloads = [
            "'; DROP TABLE users; --",
            "' OR '1'='1",
            "' OR '1'='1' --",
            "' OR '1'='1' ({",
            "' OR 1=1--",
            "' OR 1=1#",
            "' OR 1=1/*",
            "' OR '' = '",
            "' OR 1 -- -",
            "admin'--",
            "admin' #",
            "admin'/*",
            "' OR 1=1 LIMIT 1 --",
            "' OR 1=1 LIMIT 1#",
            "' OR 1=1 LIMIT 1/*"
        ]
        for payload in sql_injection_payloads:
            data = {
                'username': payload,
                'password': 'testpassword123'
            }
            response = self.client.post(reverse('login'), data, format='json')
            self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
            self.assertIn('error', response.data)
            self.assertEqual(response.data['error'], 'Invalid credentials')


@override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend")
class OTPVerificationTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.User = get_user_model()
        self.active_user = self.User.objects.create_user(
            username='activeuser@example.com',
            password='testpassword123',
            first_name='Active',
            last_name='User',
            email='activeuser@example.com',
            is_active=True
        )
        otp = '123456'
        hashed_otp = bcrypt.hashpw(otp.encode(), bcrypt.gensalt()).decode()
        self.otp = Otp.objects.create(
            user=self.active_user,
            otp=hashed_otp,
            expires_at=timezone.now() + timedelta(minutes=5),
            is_used=False,
            attempts=0,
            last_attempt_at=timezone.now()
        )
        self.verify_otp_url = reverse('verify-otp')

    def test_verify_otp_success(self):
        # Test successful OTP verification
        session = self.client.session
        session['pre_2fa_user_id'] = self.active_user.id
        session.save()

        # Now verify OTP
        otp_data = {
            'otp': '123456'
        }
        response = self.client.post(self.verify_otp_url, otp_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('message', response.data)
        self.assertEqual(response.data['message'], 'OTP verified successfully')

    def test_verify_invalid_otp(self):
        # Test invalid OTP verification
        session = self.client.session
        session['pre_2fa_user_id'] = self.active_user.id
        session.save()
        otp_data = {'otp': '654321'}
        response = self.client.post(self.verify_otp_url, otp_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
        self.assertEqual(response.data['error'], 'Invalid OTP')

    def test_verify_expired_otp(self):
        # Test expired OTP verification
        self.otp.expires_at = timezone.now() - timedelta(minutes=1)
        self.otp.save()

        session = self.client.session
        session['pre_2fa_user_id'] = self.active_user.id
        session.save()

        otp_data = {'otp': '123456'}
        response = self.client.post(self.verify_otp_url, otp_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
        self.assertEqual(response.data['error'], 'OTP has expired and is now invalidated.')

    def test_verify_too_many_attempts(self):
        # Test OTP verification with too many attempts
        self.otp.attempts = 4
        self.otp.last_attempt_at = timezone.now() - timedelta(seconds=30)
        self.otp.save()

        session = self.client.session
        session['pre_2fa_user_id'] = self.active_user.id
        session.save()

        otp_data = {'otp': '123456'}
        response = self.client.post(self.verify_otp_url, otp_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
        self.assertEqual(response.data['error'], 'Too many attempts. Try again later.')

    def test_sql_injection_attempts(self):
        # Test SQL injection attempts on OTP verification
        session = self.client.session
        session['pre_2fa_user_id'] = self.active_user.id
        session.save()

        sql_injection_payloads = [
            "'; DROP TABLE users; --",
            "' OR '1'='1",
            "' OR '1'='1' --",
            "' OR '1'='1' ({",
            "' OR 1=1--",
            "' OR 1=1#",
            "' OR 1=1/*",
            "' OR '' = '",
            "' OR 1 -- -",
            "admin'--",
            "admin' #",
            "admin'/*",
            "' OR 1=1 LIMIT 1 --",
            "' OR 1=1 LIMIT 1#",
            "' OR 1=1 LIMIT 1/*"
        ]

        for payload in sql_injection_payloads:
            # Reset OTP attempts to zero before each test
            self.otp.attempts = 0
            self.otp.save()
            otp_data = {'otp': payload}
            response = self.client.post(self.verify_otp_url, otp_data, format='json')
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertIn('error', response.data)
            self.assertEqual(response.data['error'], 'Invalid OTP')


@override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend")
class AdminFunctionTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.User = get_user_model()

        # Create admin account
        self.admin_user = self.User.objects.create_superuser(
            username="admin", email="admin@example.com", password="adminpass"
        )
        admin = Administrator.objects.create(user=self.admin_user)

        # Create staff account
        self.staff_user = fitopiaUser.objects.create(
            username="staff@example.com",
            password="testpassword123",
            email="customer@example.com",
            first_name="staff",
            last_name="staff",
        )
        staff = Staff.objects.create(user=self.staff_user, created_by=admin)
        self.staff_id = staff.id
        # Create customer account
        self.customer_user = fitopiaUser.objects.create(
            username="customer@example.com",
            password="testpassword123",
            email="customer@example.com",
            first_name="customer",
            last_name="customer",
        )
        customer = Customer.objects.create(user=self.customer_user)
        self.customer_id = customer.id

        refresh = RefreshToken.for_user(self.admin_user)
        self.admin_jwt_token = str(refresh.access_token)

    def test_unauthenticated_admin_function(self):
        urls = [
            "/api/authentication/getCustomerData/",
            "/api/authentication/getStaffData/",
            "/api/authentication/addStaff/",
            "/api/authentication/toggleAccountStatus/",
            "/api/authentication/resetPassword/",
        ]
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, 401)

    def test_authenticated_admin_function(self):
        self.client.cookies[settings.SIMPLE_JWT["AUTH_COOKIE"]] = self.admin_jwt_token
        urls = [
            "/api/authentication/getCustomerData/",
            "/api/authentication/getStaffData/",
            "/api/authentication/addStaff/",
            "/api/authentication/toggleAccountStatus/",
            "/api/authentication/resetPassword/",
        ]
        for url in urls:
            response = self.client.get(url)
            self.assertNotEqual(response.status_code, 401)

    def test_getStaffData(self):
        # test unauthorized api call
        url = "/api/authentication/getStaffData/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 401)

        # test authorized api call
        self.client.cookies[settings.SIMPLE_JWT["AUTH_COOKIE"]] = self.admin_jwt_token
        url = "/api/authentication/getStaffData/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_getUserData(self):
        # test unauthorized api call
        url = "/api/authentication/getCustomerData/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 401)

        # test authorized api call
        self.client.cookies[settings.SIMPLE_JWT["AUTH_COOKIE"]] = self.admin_jwt_token
        url = "/api/authentication/getCustomerData/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_add_staff(self):
        self.client.cookies[settings.SIMPLE_JWT["AUTH_COOKIE"]] = self.admin_jwt_token
        url = "/api/authentication/addStaff/"

        staff_data = {
            "first_name": "John",
            "last_name": "Doe",
            "email": "john.doe@example.com",
            "username": "john.doe@example.com",
        }

        response = self.client.post(url, data=staff_data, format="json")
        self.assertEqual(response.status_code, 201)

        # Verify staff member is added
        self.assertTrue(
            Staff.objects.filter(user__username="john.doe@example.com").exists()
        )

        # Verify the email was "sent"
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, "Welcome to the Team")
        self.assertIn("Dear Staff Member", mail.outbox[0].alternatives[0][0])
        self.assertEqual(mail.outbox[0].to, [staff_data["email"]])

    def test_add_duplicate_staff(self):
        self.client.cookies[settings.SIMPLE_JWT["AUTH_COOKIE"]] = self.admin_jwt_token

        url = "/api/authentication/addStaff/"

        staff_data = {
            "first_name": "John",
            "last_name": "Doe",
            "email": "john.doe@example.com",
            "username": "john.doe@example.com",
        }

        response = self.client.post(url, data=staff_data, format="json")
        self.assertEqual(response.status_code, 201)

        # Verify staff member is added
        self.assertTrue(
            Staff.objects.filter(user__username="john.doe@example.com").exists()
        )

        response = self.client.post(url, data=staff_data, format="json")
        self.assertEqual(response.status_code, 400)
    

    def test_toggleAccountStatus(self):
        self.client.cookies[settings.SIMPLE_JWT["AUTH_COOKIE"]] = self.admin_jwt_token
        url = "/api/authentication/toggleAccountStatus/"
        staff_data = {"id": self.staff_id, "type": "staff"}
        user_data = {"id": self.customer_id, "type": "customer"}
        wrong_type_data = {"id": self.customer_id, "type": "bad"}
        #Need to change if you have existing of this ID in your table.
        wrong_id_data = {"id": self.staff_id, "type": "customer"}

        response = self.client.post(url, data=staff_data, format="json")
        self.assertEqual(response.status_code, 200)
        response = self.client.post(url, data=user_data, format="json")
        self.assertEqual(response.status_code, 200)
        response = self.client.post(url, data=wrong_type_data, format="json")
        self.assertEqual(response.status_code, 400)
        response = self.client.post(url, data=wrong_id_data, format="json")
        self.assertEqual(response.status_code, 400)

    def test_resetPassword(self):
        self.client.cookies[settings.SIMPLE_JWT["AUTH_COOKIE"]] = self.admin_jwt_token
        url = "/api/authentication/resetPassword/"
        staff_data = {"id": self.staff_id, "type": "staff"}
        user_data = {"id": self.customer_id, "type": "customer"}

        response = self.client.post(url, data=staff_data, format="json")
        self.assertEqual(response.status_code, 205)
        # Verify the email was "sent"
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, "Password Reset")
        self.assertIn("requested a temporary password", mail.outbox[0].alternatives[0][0])
        self.assertEqual(mail.outbox[0].to, [self.staff_user.email])

        response = self.client.post(url, data=user_data, format="json")
        self.assertEqual(response.status_code, 205)
        self.assertEqual(len(mail.outbox), 2)
        self.assertEqual(mail.outbox[1].subject, "Password Reset")
        self.assertIn("requested a temporary password", mail.outbox[1].alternatives[0][0])
        self.assertEqual(mail.outbox[1].to, [self.customer_user.email])

