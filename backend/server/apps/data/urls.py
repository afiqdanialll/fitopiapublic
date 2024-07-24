from django.urls import path
from . import views

urlpatterns = [
    # Staff routes
    path('classes/', views.ClassListView.as_view(), name='classList'),
    path('classes/<int:pk>/', views.ClassDetailView.as_view(), name='classDetail'),
    path('classes/<int:pk>/customers/', views.ClassCustomersView.as_view(), name='classCustomers'),

    # Customer routes
    path('customer-classes/', views.CustomerClassListView.as_view(), name='customer-class-list'),
    path('customer-classes/<int:pk>/', views.CustomerClassDetailView.as_view(), name='customer-class-detail'),
    path('customer-book-class/', views.CustomerBookClassView.as_view(), name='customer-book-class'),
    path('bookings/', views.CustomerBookingHistoryView.as_view(), name='customer-booking-history'),
    path('cancel-booking/', views.CustomerCancelBookingView.as_view(), name='cancel_booking'),
    path('profile/', views.UserProfileView.as_view(), name='profile'),
    path('purchase-membership/', views.PurchaseMembershipView.as_view(), name='purchase-membership'),
    path('check-membership/', views.CheckMembershipView.as_view(), name='check-membership'),
    path('purchase-history/', views.PurchaseHistoryView.as_view(), name='purchase-history'),
]
