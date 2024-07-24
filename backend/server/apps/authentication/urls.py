from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.LoginView.as_view(), name="login"),
    path('check-pre-2fa/', views.CheckPre2FAView.as_view(), name="check-pre-2fa"),
    path('verify-otp/', views.verifyOTP.as_view(), name ='verify-otp'),
    path('check-session/', views.CheckAuthView.as_view(), name='check-session'),
    path('csrf_cookie/', views.GetCSRFToken.as_view(), name='csrf_cookie'),
    path('token_refresh/', views.CustomTokenRefreshView.as_view(), name='token_refresh'),

    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('signup/', views.SignupView.as_view(), name='signup'),
    path('current-password/', views.CurrentPasswordView.as_view(), name='current-password'),
    path('user-reset-password/', views.UserFirstLoginResetPasswordView.as_view(), name='userResetPassword'),

    # Admin Routes
    path('getCustomerData/', views.GetCustomerDataView.as_view(), name='GetCustomerData'),
    path('getStaffData/', views.GetStaffDataView.as_view(), name='getStaffData'),
    path('addStaff/', views.AddStaffView.as_view(), name='addStaff'),
    path('toggleAccountStatus/', views.ToggleAccountStatusView.as_view(), name='toggleAccountStatus'),
    path('resetPassword/', views.ResetPasswordView.as_view(), name='resetPassword'),

]
