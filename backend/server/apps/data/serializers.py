from datetime import date
from rest_framework import serializers
from .models import Class, Booking, Membership, PurchaseHistory
from ..authentication.models import Customer, fitopiaUser

class ClassSerializer(serializers.ModelSerializer):
    class Meta:
        model = Class
        fields = ['id', 'class_name', 'description', 'start_datetime', 'created_by', 'deleted']

class BookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = '__all__'

class MembershipSerializer(serializers.ModelSerializer):
    status = serializers.SerializerMethodField()

    class Meta:
        model = Membership
        fields = ['id', 'start_date', 'end_date', 'duration', 'status']

    def get_status(self, obj):
        return 'Active' if obj.end_date >= date.today() else 'Inactive'

class PurchaseHistorySerializer(serializers.ModelSerializer):
    expiry_date = serializers.DateField(source='membership.end_date', read_only=True)
    membership_type = serializers.CharField(source='membership.duration', read_only=True)
    class Meta:
        model = PurchaseHistory
        fields = ['id', 'amount', 'purchase_datetime', 'expiry_date', 'membership_type']

class CustomerProfileSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(source='user.first_name')
    last_name = serializers.CharField(source='user.last_name')
    email = serializers.EmailField(source='user.email')
    username = serializers.CharField(source='user.username')
    date_joined = serializers.DateTimeField(source='user.date_joined')
    membership = serializers.SerializerMethodField()
    is_customer = serializers.SerializerMethodField()

    class Meta:
        model = Customer
        fields = ['first_name', 'last_name', 'username', 'email', 'membership', 'date_joined', 'is_customer']

    def get_membership(self, obj):
        membership = Membership.objects.filter(customer=obj).first()
        return MembershipSerializer(membership).data if membership else None

    def get_is_customer(self, obj):
        return True

class UserProfileSerializer(serializers.ModelSerializer):
    email = serializers.EmailField()
    username = serializers.CharField()
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    date_joined = serializers.DateTimeField()
    is_customer = serializers.SerializerMethodField()

    class Meta:
        model = fitopiaUser
        fields = ['first_name', 'last_name', 'username', 'email', 'date_joined', 'is_customer']

    def get_is_customer(self, obj):
        return Customer.objects.filter(user=obj).exists()