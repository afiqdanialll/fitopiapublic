from datetime import timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.password_validation import validate_password
from rest_framework import status
from django.contrib.auth.hashers import check_password
from .serializers import (
    UserSerializer,
    CustomerSerializer,
    StaffSerializer,
)
from .logger import (
    auth_log,
    two_fa_log,
    disable_account_log,
    reset_password_log,
)
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken, OutstandingToken
from rest_framework_simplejwt.views import TokenRefreshView
from .models import fitopiaUser, Customer, Staff, Administrator, Otp
from django.core.mail import send_mail
from django.conf import settings
from django.forms import ValidationError
from django.utils import timezone
import secrets
import string
import bcrypt
from django.contrib.auth import authenticate
from datetime import timedelta
import random
from django.views.decorators.csrf import ensure_csrf_cookie, csrf_protect
from django.utils.decorators import method_decorator
from axes.decorators import axes_dispatch
from django.contrib.auth import signals
from datetime import datetime

@method_decorator(csrf_protect, name="dispatch")
class SignupView(APIView):
    def post(self, request):
        user_data = request.data.copy()
        user_data["email"] = user_data["username"]
        serializer = UserSerializer(data=user_data)
        if serializer.is_valid():
            user = serializer.save()
            # Saves customer data with foreign key referencing to the fitopiauser table
            customer = Customer.objects.create(user=user)

            return Response(status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:

            # Get refresh token from cookies
            refresh_token = request.COOKIES.get('refresh_token')
            if refresh_token:
                # Blacklist the refresh token
                token = RefreshToken(refresh_token)
                token.blacklist()
            
            token_str = request.COOKIES.get('access_token')
            if token_str:
                access_token = AccessToken(token_str)
            
            # Create an OutstandingToken entry for the access token
            outstanding_token, created = OutstandingToken.objects.get_or_create(
                jti=access_token['jti'],
                defaults={
                    'token': token_str,
                    'expires_at': datetime.fromtimestamp(access_token['exp'])
                }
            )
            
            # Blacklist the access token
            BlacklistedToken.objects.create(token=outstanding_token)
            
            response = Response(
                {"message": "Logged out successfully"}, status=status.HTTP_200_OK
            )
            response.delete_cookie("access_token")
            response.delete_cookie("csrftoken")
            response.delete_cookie('refresh_token')
           
            return response
        except Exception as e:
            print(e)
            response = Response(
                {"message": "Logged out successfully"}, status=status.HTTP_200_OK
            )
            response.delete_cookie("access_token")
            response.delete_cookie("csrftoken")
            response.delete_cookie('refresh_token')

            return response
           

# CRUD for Customer
class GetCustomerDataView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            # RBAC
            a_user = Administrator.objects.get(user_id=request.user.id)
            
            # Use select_related to fetch related user data
            data = Customer.objects.select_related("user").all()
            serializer = CustomerSerializer(data, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        except Administrator.DoesNotExist:
            return Response({"detail": "Permission denied."}, status=status.HTTP_403_FORBIDDEN)
        
        except Exception as e:
            print(e)
            return Response(status=status.HTTP_400_BAD_REQUEST)


class GetStaffDataView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            # RBAC
            a_user = Administrator.objects.get(user_id=request.user.id)
            
            # Use select_related to fetch related user data
            data = Staff.objects.select_related("user").all()
            serializer = StaffSerializer(data, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        except Administrator.DoesNotExist:
            return Response({"detail": "Permission denied."}, status=status.HTTP_403_FORBIDDEN)
        except Exception as e:
            print(e)
            return Response(status=status.HTTP_400_BAD_REQUEST)


@method_decorator(csrf_protect, name="dispatch")
class AddStaffView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # RBAC
        try:
            a_user = Administrator.objects.get(user_id=request.user.id)
        except Administrator.DoesNotExist:
            return Response({"detail": "Permission denied."}, status=status.HTTP_403_FORBIDDEN)

        user_data = request.data.copy()
        temp_password = generate_temp_password()
        user_data["password"] = temp_password
        serializer = UserSerializer(data=user_data)
        if serializer.is_valid():
            user = serializer.save()
            admin_user = Administrator.objects.get(user_id=request.user.id)
            staff = Staff.objects.create(user=user, created_by=admin_user)

            # Email content
            subject = "Welcome to the Team"
            message = f"""
            <html>
            <body>
                <p>Dear Staff Member,</p>
                <p> Welcome to the team! Here is your account's password:</p>
                <h2>{temp_password}</h2>
                <p>For security reasons, please change your password immediately after logging in.</p>
                <p>Thank you,</p>
                <p>Fitopia</p>
            </body>
            </html>
            """
            recipient_list = [user_data["email"]]
            send_mail(
                subject,
                "",
                settings.EMAIL_HOST_USER,
                recipient_list,
                fail_silently=True,
                html_message=message,
            )
            return Response(status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Account Activiation/Deactivation
@method_decorator(csrf_protect, name="dispatch")
class ToggleAccountStatusView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            # RBAC
            a_user = Administrator.objects.get(user_id=request.user.id)
            
            admin_user = Administrator.objects.select_related("user").get(
                user_id=request.user.id
            )
            admin_user = Administrator.objects.select_related("user").get(user_id=request.user.id)
            if request.data["type"] == "staff":
                user = Staff.objects.select_related("user").get(id=request.data["id"])
            elif request.data["type"] == "customer":
                user = Customer.objects.select_related("user").get(
                    id=request.data["id"]
                )
            user.user.is_active = not user.user.is_active
            user.user.save()

            disable_account_log(
                request.data["id"],
                request,
                user.user.is_active,
                admin_user.user.username,
                True,
            )
            return Response(user.user.is_active, status=status.HTTP_200_OK)
        
        except Administrator.DoesNotExist:
            return Response({"detail": "Permission denied."}, status=status.HTTP_403_FORBIDDEN)
        
        except Exception as e:
            print(e)
            disable_account_log(
                request.data["id"], request, False, admin_user.user.username, False
            )
            return Response(status=status.HTTP_400_BAD_REQUEST)


@method_decorator(csrf_protect, name="dispatch")
class ResetPasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            # RBAC
            a_user = Administrator.objects.get(user_id=request.user.id)
            
            admin_user = Administrator.objects.select_related("user").get(
                user_id=request.user.id
            )

            if request.data["type"] == "staff":
                user = Staff.objects.select_related("user").get(id=request.data["id"])
            elif request.data["type"] == "customer":
                user = Customer.objects.select_related("user").get(
                    id=request.data["id"]
                )

            user_email = user.user.email
            temp_password = generate_temp_password()

            # set temp password as new password
            user.user.set_password(temp_password)
            user.user.save()
            # set password_reset to true
            user.password_reset = True
            user.save()

            reset_password_log(
                request.data["id"], request, admin_user.user.username, True
            )

            # Email content
            subject = "Password Reset"
            message = f"""
            <html>
            <body>
                <p>Dear user,</p>
                <p>You have requested a temporary password. Please use the temporary password below to log in to your account:</p>
                <h2>{temp_password}</h2>
                <p>For security reasons, please change your password immediately after logging in.</p>
                <p>If you did not request this password reset, please ignore this email or contact support immediately.</p>
                <p>Thank you,</p>
                <p>Fitopia</p>
            </body>
            </html>
            """
            recipient_list = [user_email]
            send_mail(
                subject,
                "",
                settings.EMAIL_HOST_USER,
                recipient_list,
                fail_silently=True,
                html_message=message,
            )

            return Response(status=status.HTTP_205_RESET_CONTENT)
                
        except Administrator.DoesNotExist:
            return Response({"detail": "Permission denied."}, status=status.HTTP_403_FORBIDDEN)

        except Exception as e:
            print(e)
            reset_password_log(
                request.data["id"], request, admin_user.user.username, False
            )
            return Response(status=status.HTTP_400_BAD_REQUEST)
@method_decorator(csrf_protect, name='dispatch')
class CurrentPasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        current_password = request.data.get('current_password')
        new_password = request.data.get('new_password')
        user = request.user

        if check_password(current_password, user.password):
            if not check_password(new_password, user.password):
                return Response({'match': True}, status=200)
            return Response({'error': 'New password cannot be the same as the current password'}, status=400)
        return Response({'error': 'Current password is incorrect'}, status=400)


@method_decorator(csrf_protect, name="dispatch")
class UserFirstLoginResetPasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            user = request.user
            new_password = request.data.get("new_password")
            if not new_password:
                return Response(
                    {"error": "New password is required"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Validate the new password
            try:
                validate_password(new_password, user)
            except ValidationError as e:
                return Response(
                    {"error": e.messages}, status=status.HTTP_400_BAD_REQUEST
                )

            # Check if the user is a staff or customer and needs password reset
            staff = Staff.objects.filter(user=user).first()
            customer = Customer.objects.filter(user=user).first()

            if staff:
                if not staff.password_reset:
                    return Response(
                        {"error": "Password reset not required"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
                staff.password_reset = False
                staff.save()
            elif customer:
                if not customer.password_reset:
                    return Response(
                        {"error": "Password reset not required"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
                customer.password_reset = False
                customer.save()
            else:
                return Response(
                    {"error": "User not found"}, status=status.HTTP_404_NOT_FOUND
                )

            user.set_password(new_password)
            user.save()

            return Response(
                {"success": "Password reset successfully"}, status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


def generate_temp_password(length=12):
    characters = string.ascii_letters + string.digits + string.punctuation
    temp_password = "".join(secrets.choice(characters) for i in range(length))
    return temp_password


def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        "refresh": str(refresh),
        "access": str(refresh.access_token),
    }


def generate_otp(length=6):
    characters = string.ascii_uppercase + string.digits
    while True:
        otp = "".join(random.choice(characters) for _ in range(length))
        if any(c.isdigit() for c in otp) and any(c.isalpha() for c in otp):
            return otp


def generate_and_store_otp(user):
    try:
        Otp.objects.filter(user=user, is_used=False).update(is_used=True)
        expires_at = timezone.now() + timedelta(minutes=1)
        otp = generate_otp()
        hashed_otp = bcrypt.hashpw(otp.encode(), bcrypt.gensalt()).decode()
        otp_entry = Otp.objects.create(
            user=user, otp=hashed_otp, created_at=timezone.now(), expires_at=expires_at
        )
        return otp
    except Exception as e:
        print("Error creating OTP:", str(e))


@method_decorator(axes_dispatch, name='dispatch')
@method_decorator(csrf_protect, name="dispatch")
class LoginView(APIView):
    
    def post(self, request):
        data = request.data
        username = data.get("username", None)
        password = data.get("password", None)

        try:
            user = fitopiaUser.objects.get(username=username)
            if not user.is_active:
                auth_log(username, request, False)
                return Response(
                    {"error": "Invalid credentials"},
                    status=status.HTTP_403_FORBIDDEN,
                )
        except fitopiaUser.DoesNotExist:
            auth_log(username, request, False)
            return Response(
                {"error": "Invalid credentials"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        # Authenticate the user
        authenticated_user = authenticate(request,username=username, password=password)
        if authenticated_user is not None:
            signals.user_logged_in.send(
                sender=fitopiaUser,
                request=request,
                user=authenticated_user,
            )

            request.session["pre_2fa_user_id"] = authenticated_user.id
            response_data = {"Success": "Login successfully"}

            otp = generate_and_store_otp(authenticated_user)

            subject = "Your One-Time Password (OTP)"
            message = f"""
            Dear user,

            You have requested a One-Time Password (OTP) for authentication. Please use the OTP below to complete your login:

            {otp}

            For security reasons, this OTP is valid for 1 minute and can be used only once.

            If you did not request this OTP, please ignore this email or contact support immediately.

            Thank you,
            Fitopia
            """

            recipient_list = [authenticated_user.email]
            try:
                send_mail(
                    subject,
                    message,  # Ensure message is passed here
                    settings.EMAIL_HOST_USER,
                    recipient_list,
                    fail_silently=False,
                )
            except Exception as e:
                print("Error sending email:", str(e))

            return Response(response_data, status=status.HTTP_200_OK)
        else:
            auth_log(username, request, False)
            return Response(
                {"error": "Invalid credentials"},
                status=status.HTTP_401_UNAUTHORIZED,
            )


class CheckPre2FAView(APIView):
    def get(self, request):
        if "pre_2fa_user_id" in request.session:
            return Response(
                {"message": "User is authenticated for 2FA"}, status=status.HTTP_200_OK
            )
        return Response(
            {"error": "User not authenticated for 2FA"},
            status=status.HTTP_403_FORBIDDEN,
        )

@method_decorator(csrf_protect, name="dispatch")   
class verifyOTP(APIView):
    def post(self, request):
        response = Response()
        pre_2fa_user_id = request.session.get("pre_2fa_user_id")
        otp_received = request.data.get("otp")

        if not pre_2fa_user_id:
            response.data = {'error': 'Session expired. Please login again.'}
            response.status_code = status.HTTP_400_BAD_REQUEST
            return response

        try:
            user = fitopiaUser.objects.get(id=pre_2fa_user_id)
        except fitopiaUser.DoesNotExist:
            response.data = {'error': 'Invalid user.'}
            response.status_code = status.HTTP_400_BAD_REQUEST
            return response
        try:
            now = timezone.now()
            otp_entry = Otp.objects.filter(user=user, is_used=False).first()

            if not otp_entry:
                request.session.flush()
                response.data = {"error": "OTP has expired and is now invalidated."}
                response.status_code = status.HTTP_400_BAD_REQUEST
                return response

            if otp_entry.expires_at < now:
                otp_entry.is_used = True
                otp_entry.save()
                request.session.flush()
                response.data = {'error': 'OTP has expired and is now invalidated.'}
                response.status_code = status.HTTP_400_BAD_REQUEST
                return response

            if otp_entry.attempts >= 4 and now - otp_entry.last_attempt_at < timedelta(minutes=1):
                otp_entry.is_used = True
                otp_entry.save()
                request.session.flush()
                response.data = {'error': 'Too many attempts. Try again later.'}
                response.status_code = status.HTTP_400_BAD_REQUEST
                return response
            
            if bcrypt.checkpw(otp_received.encode(), otp_entry.otp.encode()):
                    otp_entry.is_used = True
                    otp_entry.save()
                    request.session.flush()
                    data = get_tokens_for_user(user)
                    response.set_cookie(
                        key=settings.SIMPLE_JWT["AUTH_COOKIE"],
                        value=data["access"],
                        max_age=settings.SIMPLE_JWT["ACCESS_TOKEN_LIFETIME"].total_seconds(),
                        secure=settings.SIMPLE_JWT["AUTH_COOKIE_SECURE"],
                        httponly=settings.SIMPLE_JWT["AUTH_COOKIE_HTTP_ONLY"],
                        samesite=settings.SIMPLE_JWT["AUTH_COOKIE_SAMESITE"],
                    )
                    response.set_cookie(
                        key='refresh_token',
                        value=data["refresh"],
                        max_age=settings.SIMPLE_JWT["REFRESH_TOKEN_LIFETIME"].total_seconds(),
                        secure=settings.SIMPLE_JWT["AUTH_COOKIE_SECURE"],
                        httponly=settings.SIMPLE_JWT["AUTH_COOKIE_HTTP_ONLY"],
                        samesite=settings.SIMPLE_JWT["AUTH_COOKIE_SAMESITE"],
                        path='/',
                    )
                    two_fa_log(pre_2fa_user_id, request, True)
                    response.data = {'message': 'OTP verified successfully'}
                    return response
            
            else:
                otp_entry.attempts += 1
                otp_entry.last_attempt_at = now
                otp_entry.save()
                response.data = {'error': 'Invalid OTP'}
                response.status_code = status.HTTP_400_BAD_REQUEST
                return response
        except Exception as e:
            print(f"Error during OTP verification: {str(e)}")  # Print error to logs
            response.data = {'error': 'An error occurred during OTP verification.'}
            response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
            return response

class CheckAuthView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        
        user = request.user
        is_admin = Administrator.is_admin(user)  # Call the is_admin function
        is_customer = Customer.is_customer(user)  # Call the is_customer function
        is_staff = Staff.is_staff(user)  # Call the is_customer function
        if is_admin:
            user_role = "admin"
            return Response({"detail": "Authenticated", "role": user_role}, status=200)
        elif is_customer:
            cust_user = Customer.objects.get(user_id=user.id)
            user_role = "customer"
            pass_reset = cust_user.password_reset
            return Response(
                {
                    "detail": "Authenticated",
                    "role": user_role,
                    "password_reset": pass_reset,
                },
                status=200,
            )
        elif is_staff:
            staff_user = Staff.objects.get(user_id=user.id)
            user_role = "staff"
            pass_reset = staff_user.password_reset
            return Response(
                {
                    "detail": "Authenticated",
                    "role": user_role,
                    "password_reset": pass_reset,
                },
                status=200,
            )
        else:
            return Response({"detail": "Authenticated"}, status=200)
        
class CustomTokenRefreshView(TokenRefreshView):
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        if response.status_code == status.HTTP_200_OK:
            data = response.data
            response.set_cookie(
                key=settings.SIMPLE_JWT["AUTH_COOKIE"],
                value=data["access"],
                max_age=settings.SIMPLE_JWT["ACCESS_TOKEN_LIFETIME"].total_seconds(),
                secure=settings.SIMPLE_JWT["AUTH_COOKIE_SECURE"],
                httponly=settings.SIMPLE_JWT["AUTH_COOKIE_HTTP_ONLY"],
                samesite=settings.SIMPLE_JWT["AUTH_COOKIE_SAMESITE"],
            )
        return response


@method_decorator(ensure_csrf_cookie, name="dispatch")
class GetCSRFToken(APIView):

    def get(self, request, format=None):
        return Response({"success": "CSRF cookie set"})
