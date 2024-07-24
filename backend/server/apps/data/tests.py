from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken
from django.core import mail
from django.conf import settings
from django.urls import reverse
from django.utils import timezone
from apps.authentication.models import fitopiaUser, Administrator, Staff, Customer
from django.test import TestCase
from rest_framework.test import APIClient
from django.urls import reverse
from .models import Class, Booking, Customer, Staff, Membership, PurchaseHistory
from django.utils import timezone
from rest_framework import status
from datetime import timedelta



# ---- working testcase for ClassCustomersView ------
class ClassCustomersViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()

        # Create administrator
        self.admin_user = fitopiaUser.objects.create_user(username="adminuser", password="adminpass")
        self.admin = Administrator.objects.create(user=self.admin_user)
        
        # Create staff user
        self.staff_user = fitopiaUser.objects.create_user(username="staffuser", password="staffpass")
        self.staff = Staff.objects.create(user=self.staff_user, created_by=self.admin)

        # Create another staff user (for permission test)
        self.other_staff_user = fitopiaUser.objects.create_user(username="otherstaffuser", password="otherstaffpass")
        self.other_staff = Staff.objects.create(user=self.other_staff_user, created_by=self.admin)

        # Create a class
        self.class_instance = Class.objects.create(
            created_by=self.staff,
            class_name="Yoga Class",
            description="A relaxing yoga session",
            start_datetime=timezone.now() + timedelta(days=1),
            deleted=False
        )

        # Create customers and bookings
        self.customer_user1 = fitopiaUser.objects.create_user(username="customer1", password="custpass")
        self.customer1 = Customer.objects.create(user=self.customer_user1)
        self.booking1 = Booking.objects.create(
            customer=self.customer1,
            class_id=self.class_instance,
            booking_datetime=timezone.now(),
            cancellation=False
        )

        self.customer_user2 = fitopiaUser.objects.create_user(username="customer2", password="custpass")
        self.customer2 = Customer.objects.create(user=self.customer_user2)
        self.booking2 = Booking.objects.create(
            customer=self.customer2,
            class_id=self.class_instance,
            booking_datetime=timezone.now(),
            cancellation=False
        )

        self.url = reverse('classCustomers', kwargs={'pk': self.class_instance.id})

    def test_get_customers_as_staff(self):
        # Authenticate as staff
        self.client.force_authenticate(user=self.staff_user)

        # Test retrieving customer emails
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        self.assertIn(self.customer_user1.email, response.data)
        self.assertIn(self.customer_user2.email, response.data)

    def test_permission_denied_for_non_staff(self):
        # Authenticate as a non-staff user
        new_user = fitopiaUser.objects.create_user(username="newuser", password="newpass")
        self.client.force_authenticate(user=new_user)
        
        # Authenticate as a non-staff user
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_class_not_found(self):
        # Authenticate as staff
        self.client.force_authenticate(user=self.staff_user)

        # Test class not found error
        invalid_url = reverse('classCustomers', kwargs={'pk': 999})  # Non-existing class ID
        response = self.client.get(invalid_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


# ----- Testcase for ClassDetailView Working -----
class ClassDetailViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()

        # Create admin, staff, and customer users
        self.admin_user = fitopiaUser.objects.create_user(username="adminuser", password="adminpass")
        self.admin = Administrator.objects.create(user=self.admin_user)

        self.staff_user = fitopiaUser.objects.create_user(username="staffuser", password="staffpass")
        self.staff = Staff.objects.create(user=self.staff_user, created_by=self.admin)

        self.user = fitopiaUser.objects.create_user(username="testuser", password="testpass")
        self.customer = Customer.objects.create(user=self.user)

        # Authenticate as staff
        self.client.force_authenticate(user=self.staff_user)

        # Create class instance
        self.class_instance = Class.objects.create(
            created_by=self.staff,
            class_name="Test Class",
            description="Test Description",
            start_datetime=timezone.now() + timedelta(days=1),
            deleted=False
        )

        self.url = reverse('classDetail', kwargs={'pk': self.class_instance.pk})

    def test_get_class_detail(self):
        # Test retrieving class details
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['class_name'], self.class_instance.class_name)

    def test_update_class_detail(self):
        # Test updating class details
        data = {
            'class_name': 'Updated Class',
            'description': 'Updated Description',
            'start_datetime': (timezone.now() + timedelta(days=2)).isoformat(),
            'created_by': self.class_instance.created_by.id  # Include 'created_by' field
        }
        response = self.client.put(self.url, data, format='json')
        if response.status_code == status.HTTP_400_BAD_REQUEST:
            print("Errors:", response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.class_instance.refresh_from_db()
        self.assertEqual(self.class_instance.class_name, 'Updated Class')

    def test_delete_class(self):
        # Test deleting class (soft delete)
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.class_instance.refresh_from_db()
        self.assertTrue(self.class_instance.deleted)

    def test_permission_denied_for_non_staff_get(self):
        # Test permission denied for non-staff user when retrieving class details
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_permission_denied_for_non_staff_put(self):
        # Test permission denied for non-staff user when updating class details
        self.client.force_authenticate(user=self.user)
        data = {
            'class_name': 'Updated Class',
            'description': 'Updated Description',
            'start_datetime': (timezone.now() + timedelta(days=2)).isoformat(),
            'created_by': self.class_instance.created_by.id  # Include 'created_by' field
        }
        response = self.client.put(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_permission_denied_for_non_staff_delete(self):
        # Test permission denied for non-staff user when deleting class
        self.client.force_authenticate(user=self.user)
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_class_not_found(self):
        # Test class not found error
        url = reverse('classDetail', kwargs={'pk': 9999})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)



# ----- Working test for CustomerClassListView -------
class CustomerClassListViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()

        # Check for existing classes
        self.initial_class_count = Class.objects.count()

        # Create test users and administrator
        self.admin_user = fitopiaUser.objects.create_user(username="adminuser", password="adminpass")
        self.admin = Administrator.objects.create(user=self.admin_user)

        # Create test staff users
        self.staff_user = fitopiaUser.objects.create_user(username="staffuser", password="staffpass")
        self.staff = Staff.objects.create(user=self.staff_user, created_by=self.admin)

        self.staff_user2 = fitopiaUser.objects.create_user(username="staffuser2", password="staffpass2")
        self.staff2 = Staff.objects.create(user=self.staff_user2, created_by=self.admin)

        # Create a test user and customer
        self.user = fitopiaUser.objects.create_user(username="testuser", password="testpass")
        self.customer = Customer.objects.create(user=self.user)

        # Authenticate the test user as the customer
        self.client.force_authenticate(user=self.user)

        # Create classes with a valid 'created_by' reference
        self.class1 = Class.objects.create(
            created_by=self.staff,
            class_name="Yoga Class",
            description="A relaxing yoga session",
            start_datetime=timezone.now() + timedelta(days=1),
            deleted=False
        )

        self.class2 = Class.objects.create(
            created_by=self.staff2,
            class_name="Pilates Class",
            description="An intense pilates session",
            start_datetime=timezone.now() + timedelta(days=2),
            deleted=False
        )

        self.class3 = Class.objects.create(
            created_by=self.staff2,
            class_name="Deleted Class",
            description="A deleted class",
            start_datetime=timezone.now() + timedelta(days=3),
            deleted=True
        )

        self.url = reverse('customer-class-list')

    def test_fetch_all_classes(self):
        # Test to fetch all classes, should only return non-deleted classes
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data) - self.initial_class_count, 2)  # Should only return non-deleted classes

    def test_filter_classes_by_name(self):
        # Test filtering classes by name
        response = self.client.get(self.url, {'name': 'Yoga'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['class_name'], 'Yoga Class')

    def test_filter_classes_by_start_date(self):
        # Test filtering classes by start date
        start_date = (timezone.now() + timedelta(days=2)).date().strftime('%Y-%m-%d')
        response = self.client.get(self.url, {'start_datetime': start_date})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['class_name'], 'Pilates Class')

    def test_sql_injection_attempt(self):
        # Test to ensure SQL injection attempts are handled properly
        response = self.client.get(self.url, {'name': "'; DROP TABLE Class; --"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Class.objects.count() - self.initial_class_count, 3)  # Ensure no class was deleted

    def test_permission_denied_for_non_customer(self):
         # Test to check if non-customers are denied access
        new_user = fitopiaUser.objects.create_user(username="newuser", password="newpass")
        self.client.force_authenticate(user=new_user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 500)

    def test_invalid_date_format(self):
        # Test to check handling of invalid date format
        response = self.client.get(self.url, {'start_datetime': 'invalid-date'})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['error'], 'Invalid date format')



# #--- Cant do all classes ---- 
class CustomerClassListViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()

        # Create user and customer
        self.user = fitopiaUser.objects.create_user(
            username="testuser", password="testpass"
        )
        self.customer = Customer.objects.create(user=self.user)

        # Create admin and staff
        self.admin_user = fitopiaUser.objects.create_user(
            username="adminuser", password="adminpass"
        )
        self.admin = Administrator.objects.create(user=self.admin_user)

        self.staff_user = fitopiaUser.objects.create_user(
            username="staffuser", password="staffpass"
        )
        self.staff = Staff.objects.create(user=self.staff_user, created_by=self.admin)

        self.client.force_authenticate(user=self.user)

        # Create classes
        self.class1 = Class.objects.create(
            created_by=self.staff,
            class_name="Yoga Class",
            description="A relaxing yoga session",
            start_datetime=timezone.now() + timedelta(days=1),
            deleted=False
        )
        self.class2 = Class.objects.create(
            created_by=self.staff,
            class_name="Pilates Class",
            description="An intense pilates session",
            start_datetime=timezone.now() + timedelta(days=2),
            deleted=False
        )

        self.url = reverse('customer-class-list')

    def test_filter_classes_by_name(self):
        # Tests filtering classes by the name field
        response = self.client.get(self.url, {'name': 'yoga'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['class_name'], 'Yoga Class')

    def test_filter_classes_by_start_date(self):
        # Tests filtering classes by the start date
        start_date = (timezone.now() + timedelta(days=2)).date().strftime('%Y-%m-%d')
        response = self.client.get(self.url, {'start_datetime': start_date})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['class_name'], 'Pilates Class')

    def test_invalid_date_format(self):
        # Tests the system's handling of an invalid date format
        response = self.client.get(self.url, {'start_datetime': 'invalid-date'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Invalid date format', response.data['error'])

    def test_customer_does_not_exist(self):
        # Tests access by a user who is not a customer, expecting a permission denied error
        # Force authenticate with a user that is not a customer
        non_customer_user = fitopiaUser.objects.create_user(
            username="noncustomer", password="testpass"
        )
        self.client.force_authenticate(user=non_customer_user)
        
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn('Permission denied', response.data['detail'])


#---- Test for ClassCustomersView -----
class ClassCustomersViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()

        # Create users
        self.staff_user = fitopiaUser.objects.create_user(
            username="staffuser", password="staffpass"
        )
        self.other_staff_user = fitopiaUser.objects.create_user(
            username="otherstaffuser", password="otherstaffpass"
        )
        self.admin_user = fitopiaUser.objects.create_user(
            username="adminuser", password="adminpass"
        )
        self.customer_user = fitopiaUser.objects.create_user(
            username="customeruser", password="customerpass"
        )

        # Create roles
        self.admin = Administrator.objects.create(user=self.admin_user)
        self.staff = Staff.objects.create(user=self.staff_user, created_by=self.admin)
        self.other_staff = Staff.objects.create(user=self.other_staff_user, created_by=self.admin)
        self.customer = Customer.objects.create(user=self.customer_user)

        # Create class
        self.class_instance = Class.objects.create(
            created_by=self.staff,
            class_name="Yoga Class",
            description="A relaxing yoga session",
            start_datetime=timezone.now() + timedelta(days=1),
            deleted=False
        )

        # Create bookings
        self.booking = Booking.objects.create(
            customer=self.customer,
            class_id=self.class_instance,
            booking_datetime=timezone.now(),
            cancellation=False
        )

        self.url = reverse('classCustomers', kwargs={'pk': self.class_instance.id})

    def test_retrieve_customer(self):
        # Test for retrieving users
        self.client.force_authenticate(user=self.staff_user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, [self.customer_user.email])

    def test_class_not_found(self):
        # Test for non existent class id
        self.client.force_authenticate(user=self.staff_user)
        url = reverse('classCustomers', kwargs={'pk': 9999})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['detail'], "Class not found.")

    def test_permission_denied_for_non_staff(self):
        # Test for RBAC
        self.client.force_authenticate(user=self.customer_user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['detail'], "Permission denied.")


#---- Testcase for userprofileview working ------
class UserProfileViewTest(TestCase):

    def setUp(self):
        self.client = APIClient()

        # Create an administrator user and instance
        self.admin_user = fitopiaUser.objects.create_user(
            username='adminuser@example.com',
            password='adminpassword',
            email='adminuser@example.com',
            first_name='Admin',
            last_name='User'
        )
        self.administrator = Administrator.objects.create(user=self.admin_user)
        
        # Create a normal user and instance
        self.user = fitopiaUser.objects.create_user(
            username='testuser@example.com',
            password='testpassword',
            email='testuser@example.com',
            first_name='Test',
            last_name='User'
        )
        
        # Create a Customer instance
        self.customer = Customer.objects.create(user=self.user)

        # Create a membership and purchase history
        self.membership = Membership.objects.create(
            customer=self.customer,
            start_date=timezone.now().date() - timezone.timedelta(days=30),
            end_date=timezone.now().date() + timezone.timedelta(days=30),
            duration=1
        )
        
        self.purchase = PurchaseHistory.objects.create(
            customer=self.customer,
            membership=self.membership,
            amount=100.00,
            purchase_datetime=timezone.now()
        )

        # Authenticate the client
        refresh = RefreshToken.for_user(self.user)
        self.client.cookies[settings.SIMPLE_JWT['AUTH_COOKIE']] = str(refresh.access_token)

    def test_get_profile_success(self):
        # Test retrieving of profile details of user
        url = reverse('profile')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['first_name'], 'Test')
        self.assertEqual(response.data['last_name'], 'User')
        self.assertEqual(response.data['username'], 'testuser@example.com')
        self.assertIn('membership', response.data)
        self.assertEqual(response.data['membership']['status'], 'Active')

    def test_update_profile_success(self):
        # Test updating of profile details
        url = reverse('profile')
        data = {
            'first_name': 'Updated',
            'last_name': 'User'
        }
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['first_name'], 'Updated')
        self.assertEqual(response.data['last_name'], 'User')

    def test_customer_not_found(self):
        # Create a new user without a customer instance
        new_user = fitopiaUser.objects.create_user(
            username='newuser@example.com',
            password='newpassword',
            email='newuser@example.com',
            first_name='New',
            last_name='User'
        )

        # Authenticate the client with the new user
        refresh = RefreshToken.for_user(new_user)
        self.client.cookies[settings.SIMPLE_JWT['AUTH_COOKIE']] = str(refresh.access_token)

        url = reverse('profile')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)  # Expecting 404 error

    def test_unauthenticated_request(self):
        # Test unauthenticated access
        self.client.cookies.clear()  # Clear the cookies to simulate an unauthenticated request
        url = reverse('profile')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 401)
        if response.get('Content-Type') == 'application/json':
            self.assertEqual(response.json()['detail'], 'Authentication credentials were not provided.')
        else:
            self.fail('Response is not JSON')

    def test_update_profile_permission_denied(self):
        # Create a new user without a customer instance
        new_user = fitopiaUser.objects.create_user(
            username='newuser@example.com',
            password='newpassword',
            email='newuser@example.com',
            first_name='New',
            last_name='User'
        )

        # Authenticate the client with the new user
        refresh = RefreshToken.for_user(new_user)
        self.client.cookies[settings.SIMPLE_JWT['AUTH_COOKIE']] = str(refresh.access_token)

        url = reverse('profile')
        data = {
            'first_name': 'Updated',
            'last_name': 'User'
        }
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, 404)  # Expecting 404 error


# --- Testcase for CustomerBookingHistoryViewTest -----
class CustomerBookingHistoryViewTest(TestCase):

    def setUp(self):
        self.client = APIClient()

        # Create an administrator user and instance
        self.admin_user = fitopiaUser.objects.create_user(
            username='adminuser@example.com', 
            password='adminpassword',
            email='adminuser@example.com',
            first_name='Admin',
            last_name='User'
        )
        self.administrator = Administrator.objects.create(user=self.admin_user)
        
        # Create a normal user and instance
        self.user = fitopiaUser.objects.create_user(
            username='testuser@example.com', 
            password='testpassword',
            email='testuser@example.com',
            first_name='Test',
            last_name='User'
        )
        
        # Create a Customer instance
        self.customer = Customer.objects.create(user=self.user)

        # Create a staff instance
        self.staff = Staff.objects.create(user=self.admin_user, created_by=self.administrator)

        # Use timezone-aware datetimes
        now = timezone.now()

        # Create bookings
        self.class_instance_upcoming = Class.objects.create(
            created_by=self.staff,
            class_name='Upcoming Class',
            description='An upcoming class session',
            start_datetime=now + timezone.timedelta(days=5),
            deleted=False
        )
        
        self.class_instance_past = Class.objects.create(
            created_by=self.staff,
            class_name='Past Class',
            description='A past class session',
            start_datetime=now - timezone.timedelta(days=5),
            deleted=False
        )
        
        self.upcoming_booking = Booking.objects.create(
            customer=self.customer,
            class_id=self.class_instance_upcoming,
            booking_datetime=now
        )
        
        self.past_booking = Booking.objects.create(
            customer=self.customer,
            class_id=self.class_instance_past,
            booking_datetime=now
        )
        
        self.cancelled_booking = Booking.objects.create(
            customer=self.customer,
            class_id=self.class_instance_upcoming,
            booking_datetime=now,
            cancellation=True
        )

        # Authenticate the client
        refresh = RefreshToken.for_user(self.user)
        self.client.cookies[settings.SIMPLE_JWT['AUTH_COOKIE']] = str(refresh.access_token)

    def test_get_booking_history_success(self):
        # Test retrieving of booking history
        url = reverse('customer-booking-history')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('upcoming', response.json())
        self.assertIn('past', response.json())
        self.assertIn('cancelled', response.json())
        self.assertEqual(len(response.json()['upcoming']), 1)
        self.assertEqual(len(response.json()['past']), 1)
        self.assertEqual(len(response.json()['cancelled']), 1)

    def test_get_booking_history_unauthenticated(self):
        # Test unauthenticated access
        self.client.cookies.clear()  # Clear the cookies to simulate unauthenticated request
        url = reverse('customer-booking-history')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 401)
        if response.get('Content-Type') == 'application/json':
            self.assertEqual(response.json()['detail'], 'Authentication credentials were not provided.')
        else:
            self.fail('Response is not JSON')



# ------- CustomerCancelBookingViewTest Working -------
class CustomerCancelBookingViewTest(TestCase):

    def setUp(self):
        self.client = APIClient()

        # Create an administrator user and instance
        self.admin_user = fitopiaUser.objects.create_user(
            username='adminuser@example.com', 
            password='adminpassword',
            email='adminuser@example.com',
            first_name='Admin',
            last_name='User'
        )
        self.administrator = Administrator.objects.create(user=self.admin_user)
        
        # Create a normal user and instance
        self.user = fitopiaUser.objects.create_user(
            username='testuser@example.com', 
            password='testpassword',
            email='testuser@example.com',
            first_name='Test',
            last_name='User'
        )
        
        # Create a Customer instance
        self.customer = Customer.objects.create(user=self.user)

        # Create a staff instance
        self.staff = Staff.objects.create(user=self.admin_user, created_by=self.administrator)

        # Create a class instance
        self.class_instance = Class.objects.create(
            created_by=self.staff,
            class_name='Yoga Class',
            description='A relaxing yoga session',
            start_datetime='2024-07-01T10:00:00Z',
            deleted=False
        )

        # Create a booking instance
        self.booking = Booking.objects.create(
            customer=self.customer,
            class_id=self.class_instance,
            booking_datetime=timezone.now()
        )

        # Authenticate the client
        refresh = RefreshToken.for_user(self.user)
        self.client.cookies[settings.SIMPLE_JWT['AUTH_COOKIE']] = str(refresh.access_token)

    def test_successful_booking_cancellation(self):
        # Test booking cancellation
        url = reverse('cancel_booking')
        data = {'booking_id': self.booking.id}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 205)
        self.booking.refresh_from_db()
        self.assertTrue(self.booking.cancellation)

    def test_booking_not_found(self):
        # Test non existent existing booking cancellation
        url = reverse('cancel_booking')
        data = {'booking_id': 9999}  # Non-existent booking ID
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 404)

    def test_unauthenticated_request(self):
        # Test unauthenticated access
        self.client.cookies.clear()  # Clear the cookies to simulate unauthenticated request
        url = reverse('cancel_booking')
        data = {'booking_id': self.booking.id}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 401)
        if response.get('Content-Type') == 'application/json':
            self.assertEqual(response.json()['detail'], 'Authentication credentials were not provided.')
        else:
            self.fail('Response is not JSON')


#----------- Working CustomerBookClassViewTest -----------
class CustomerBookClassViewTest(TestCase):

    def setUp(self):
        self.client = APIClient()

        # Create an administrator user and instance
        self.admin_user = fitopiaUser.objects.create_user(
            username='adminuser@example.com', 
            password='adminpassword',
            email='adminuser@example.com',
            first_name='Admin',
            last_name='User'
        )
        self.administrator = Administrator.objects.create(user=self.admin_user)
        
        # Create a normal user and instance
        self.user = fitopiaUser.objects.create_user(
            username='testuser@example.com', 
            password='testpassword',
            email='testuser@example.com',
            first_name='Test',
            last_name='User'
        )
        
        # Create a Customer instance
        self.customer = Customer.objects.create(user=self.user)

        # Create a staff instance
        self.staff = Staff.objects.create(user=self.admin_user, created_by=self.administrator)

        # Create a class instance
        self.class_instance = Class.objects.create(
            created_by=self.staff,
            class_name='Yoga Class',
            description='A relaxing yoga session',
            start_datetime=timezone.now() + timezone.timedelta(days=1),
            deleted=False
        )

        # Authenticate the client
        refresh = RefreshToken.for_user(self.user)
        self.client.cookies[settings.SIMPLE_JWT['AUTH_COOKIE']] = str(refresh.access_token)

    def test_successful_booking(self):
        # Test successful booking of class
        url = reverse('customer-book-class')
        data = {
            'class_id': self.class_instance.id,
            'booking_datetime': timezone.now().isoformat()
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertTrue(Booking.objects.filter(customer=self.customer, class_id=self.class_instance).exists())

    def test_duplicate_booking(self):
        # Create an initial booking
        Booking.objects.create(
            customer=self.customer,
            class_id=self.class_instance,
            booking_datetime=timezone.now()
        )

        url = reverse('customer-book-class')
        data = {
            'class_id': self.class_instance.id,
            'booking_datetime': timezone.now().isoformat()
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()['error'], 'You have already booked this class.')

    def test_class_not_found(self):
        # Test booking of non existent class
        url = reverse('customer-book-class')
        data = {
            'class_id': 9999,  # Non-existent class ID
            'booking_datetime': timezone.now().isoformat()
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json()['detail'], 'Class not found.')

    def test_customer_not_found(self):
        # Create a new user without a customer instance
        new_user = fitopiaUser.objects.create_user(
            username='newuser@example.com', 
            password='newpassword',
            email='newuser@example.com',
            first_name='New',
            last_name='User'
        )
        
        refresh = RefreshToken.for_user(new_user)
        self.client.cookies[settings.SIMPLE_JWT['AUTH_COOKIE']] = str(refresh.access_token)

        url = reverse('customer-book-class')
        data = {
            'class_id': self.class_instance.id,
            'booking_datetime': timezone.now().isoformat()
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json()['detail'], 'Permission denied.')

    def test_unauthenticated_request(self):
        # Test unauthenticated access
        self.client.cookies.clear()  # Clear the cookies to simulate unauthenticated request
        url = reverse('customer-book-class')
        data = {
            'class_id': self.class_instance.id,
            'booking_datetime': timezone.now().isoformat()
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json()['detail'], 'Authentication credentials were not provided.')


# ----- Working CustomerClassDetailViewTestCase ----------
class CustomerClassDetailViewTest(TestCase):

    def setUp(self):
        self.client = APIClient()

        # Create an administrator user and instance
        self.admin_user = fitopiaUser.objects.create_user(
            username='adminuser@example.com', 
            password='adminpassword',
            email='adminuser@example.com',
            first_name='Admin',
            last_name='User'
        )
        self.administrator = Administrator.objects.create(user=self.admin_user)
        
        # Create a normal user and instance
        self.user = fitopiaUser.objects.create_user(
            username='testuser@example.com', 
            password='testpassword',
            email='testuser@example.com',
            first_name='Test',
            last_name='User'
        )
        
        # Create a Customer instance
        self.customer = Customer.objects.create(user=self.user)

        # Create a staff instance
        self.staff = Staff.objects.create(user=self.admin_user, created_by=self.administrator)

        # Create a class instance
        self.class_instance = Class.objects.create(
            created_by=self.staff,
            class_name='Yoga Class',
            description='A relaxing yoga session',
            start_datetime=timezone.now() + timezone.timedelta(days=1),
            deleted=False
        )

        # Authenticate the client
        refresh = RefreshToken.for_user(self.user)
        self.client.cookies[settings.SIMPLE_JWT['AUTH_COOKIE']] = str(refresh.access_token)

    def test_get_class_detail_success(self):
        # Test retrieving the class details successfully
        url = reverse('customer-class-detail', kwargs={'pk': self.class_instance.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['class_name'], self.class_instance.class_name)
        self.assertEqual(response.json()['description'], self.class_instance.description)

    def test_get_class_detail_not_found(self):
        # Test retrieving a class that does not exist
        url = reverse('customer-class-detail', kwargs={'pk': 9999})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json()['detail'], 'Class not found.')

    def test_get_class_detail_unauthenticated(self):
        # Test retrieving a class detail without authentication
        self.client.cookies.clear()  # Clear the cookies to simulate unauthenticated request
        url = reverse('customer-class-detail', kwargs={'pk': self.class_instance.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json()['detail'], 'Authentication credentials were not provided.')
