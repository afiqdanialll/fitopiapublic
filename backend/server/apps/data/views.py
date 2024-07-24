from datetime import datetime
from rest_framework import generics, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.exceptions import NotFound
from .models import Class, Booking, Membership, PurchaseHistory
from apps.authentication.models import Administrator, Customer, Staff, fitopiaUser
from django.http import Http404
from django.utils import timezone
from apps.authentication.serializers import CustomerSerializer
from .serializers import (
    ClassSerializer,
    BookingSerializer,
    CustomerProfileSerializer,
    UserProfileSerializer,
    PurchaseHistorySerializer,
)
from apps.authentication.serializers import CustomerSerializer
from django.views.decorators.csrf import ensure_csrf_cookie, csrf_protect
from django.utils.decorators import method_decorator
from dateutil.relativedelta import relativedelta


# Class CRUD for staff
@method_decorator(csrf_protect, name='dispatch') 
class ClassListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try: 
            # RBAC
            staff_user = Staff.objects.get(user_id=request.user.id)
            
            classes = Class.objects.filter(deleted=False)
            serializer = ClassSerializer(classes, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        except Staff.DoesNotExist:
            return Response({"detail": "Permission denied."}, status=status.HTTP_403_FORBIDDEN)
        
        except Exception:
            return Response(
                {"detail": "Internal Server Error"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def post(self, request):
        try:
            # Check if the user is a staff member
            user = fitopiaUser.objects.get(id=request.user.id)

            # RBAC
            staff_user = Staff.objects.get(user_id=request.user.id)

            # Ensure staff entry exists
            staff = Staff.objects.get(user=user)

            data = request.data.copy()
            data["created_by"] = staff.id

            serializer = ClassSerializer(data=data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        except Staff.DoesNotExist:
            return Response({"detail": "Permission denied."}, status=status.HTTP_403_FORBIDDEN)
        
        except Staff.DoesNotExist:
            return Response(
                {"detail": "Staff record not found for the user."},
                status=status.HTTP_404_NOT_FOUND,
            )
        
        except Exception:
            return Response(
                {"detail": "Internal Server Error"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

@method_decorator(csrf_protect, name='dispatch') 
class ClassDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        try:
            return Class.objects.get(pk=pk, deleted=False)
        except Class.DoesNotExist:
            raise Http404

    def get(self, request, pk):
        try:
            # RBAC
            staff_user = Staff.objects.get(user_id=request.user.id)

            class_instance = self.get_object(pk)
            serializer = ClassSerializer(class_instance)
            return Response(serializer.data)
        
        except Staff.DoesNotExist:
            return Response({"detail": "Permission denied."}, status=status.HTTP_403_FORBIDDEN)

    def put(self, request, pk):
        try:
            # Check if the user is a staff member --- YISAN TO CFM !!!!!!!!!!
            # user = fitopiaUser.objects.get(id=request.user.id)

            # RBAC
            staff_user = Staff.objects.get(user_id=request.user.id)

            class_instance = self.get_object(pk)
            serializer = ClassSerializer(class_instance, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        except Staff.DoesNotExist:
            return Response({"detail": "Permission denied."}, status=status.HTTP_403_FORBIDDEN)
        
        except Exception:
            return Response(
                {"detail": "Internal Server Error"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def delete(self, request, pk):
        try:
            # Check if the user is a staff member --- YISAN TO CFM !!!!!!!!!!
            # user = fitopiaUser.objects.get(id=request.user.id)

            #RBAC
            staff_user = Staff.objects.get(user_id=request.user.id)

            class_instance = self.get_object(pk)
            class_instance.deleted = True
            class_instance.save()
            return Response(status=status.HTTP_204_NO_CONTENT)
            
        except Staff.DoesNotExist:
            return Response({"detail": "Permission denied."}, status=status.HTTP_403_FORBIDDEN)
        
        except Exception:
            return Response(
                {"detail": "Internal Server Error"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

# Retrive attending customers of each class for Staff
class ClassCustomersView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        try:
            # RBAC
            staff_user = Staff.objects.get(user_id=request.user.id)

            class_instance = Class.objects.get(pk=pk, deleted=False)
            bookings = Booking.objects.filter(class_id=class_instance.id, cancellation=False).select_related('customer')
            customer_firstname = [booking.customer.user.first_name for booking in bookings]
            return Response(customer_firstname, status=status.HTTP_200_OK)
        
        except Staff.DoesNotExist:
            return Response({"detail": "Permission denied."}, status=status.HTTP_403_FORBIDDEN)

        except Class.DoesNotExist:
            return Response(
                {"detail": "Class not found."}, status=status.HTTP_404_NOT_FOUND
            )
        
        except Exception:
            return Response(
                {"detail": "Internal Server Error"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


# Customer
class CustomerClassListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            # RBAC
            cust_user = Customer.objects.get(user_id=request.user.id)

            search_name = request.query_params.get("name", "").lower()
            search_start_datetime = request.query_params.get("start_datetime", "")

            classes = Class.objects.filter(deleted=False)

            if search_name:
                classes = classes.filter(class_name__icontains=search_name)

            if search_start_datetime:
                try:
                    start_datetime = datetime.strptime(search_start_datetime, "%Y-%m-%d")
                    classes = classes.filter(start_datetime__date=start_datetime.date())
                except ValueError:
                    return Response(
                        {"error": "Invalid date format"}, status=status.HTTP_400_BAD_REQUEST
                    )

            serializer = ClassSerializer(classes, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        except Customer.DoesNotExist:     
            return Response({"detail": "Permission denied."}, status=status.HTTP_403_FORBIDDEN)

        except Exception:
            return Response(
                {"detail": "Internal Server Error"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

class CustomerClassDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        try:
            # RBAC
            cust_user = Customer.objects.get(user_id=request.user.id)
            
            class_instance = Class.objects.get(pk=pk, deleted=False)
            serializer = ClassSerializer(class_instance)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Customer.DoesNotExist:     
            return Response({"detail": "Permission denied."}, status=status.HTTP_403_FORBIDDEN)
                
        except Class.DoesNotExist:
            return Response({"detail": "Class not found."}, status=status.HTTP_404_NOT_FOUND)
        
        except Exception:
            return Response(
                {"detail": "Internal Server Error"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

@method_decorator(csrf_protect, name='dispatch')
class CustomerBookClassView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            # RBAC
            cust_user = Customer.objects.get(user_id=request.user.id)
            
            customer = Customer.objects.get(user=request.user)
            class_id = request.data.get("class_id")
            class_instance = Class.objects.get(id=class_id, deleted=False)

            # Check if the user has already booked this class
            existing_booking = Booking.objects.filter(
                customer=customer, class_id=class_instance, cancellation=False
            )
            if existing_booking.exists():
                return Response(
                    {"error": "You have already booked this class."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Use current timezone-aware datetime
            booking_datetime = (
                request.data.get("booking_datetime") or timezone.now().isoformat()
            )

            booking = Booking.objects.create(
                customer=customer,
                class_id=class_instance,
                booking_datetime=booking_datetime,
            )
            return Response(
                BookingSerializer(booking).data, status=status.HTTP_201_CREATED
            )
        
        except Customer.DoesNotExist:
            return Response({"detail": "Permission denied."}, status=status.HTTP_403_FORBIDDEN)
        
        except Class.DoesNotExist:
            return Response({"detail": "Class not found."}, status=status.HTTP_404_NOT_FOUND)
        
        except Exception:
            return Response(
                {"detail": "Internal Server Error"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

@method_decorator(csrf_protect, name='dispatch')
class CustomerCancelBookingView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            # RBAC
            cust_user = Customer.objects.get(user_id=request.user.id)
            
            booking_id = request.data.get("booking_id")
            booking = Booking.objects.get(id=booking_id, customer__user=request.user)
            booking.cancellation = True
            booking.save()
            return Response(status=status.HTTP_205_RESET_CONTENT)
        
        except Customer.DoesNotExist:
            return Response({"detail": "Permission denied."}, status=status.HTTP_403_FORBIDDEN)
        
        except Booking.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        
        except Exception:
            return Response(
                {"detail": "Internal Server Error"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

class CustomerBookingHistoryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            # RBAC
            cust_user = Customer.objects.get(user_id=request.user.id)
            
            customer = Customer.objects.get(user=request.user)
            current_datetime = datetime.now()

            upcoming = Booking.objects.filter(
                customer=customer,
                class_id__start_datetime__gte=current_datetime,
                cancellation=False,
            )
            past = Booking.objects.filter(
                customer=customer,
                class_id__start_datetime__lt=current_datetime,
                cancellation=False,
            )
            cancelled = Booking.objects.filter(customer=customer, cancellation=True)

            upcoming_data = BookingSerializer(upcoming, many=True).data
            past_data = BookingSerializer(past, many=True).data
            cancelled_data = BookingSerializer(cancelled, many=True).data

            # Adding class details to the response
            for booking in upcoming_data:
                class_instance = Class.objects.get(id=booking["class_id"])
                booking["class_name"] = class_instance.class_name
                booking["class_description"] = class_instance.description
                booking["start_datetime"] = class_instance.start_datetime.isoformat()

            for booking in past_data:
                class_instance = Class.objects.get(id=booking["class_id"])
                booking["class_name"] = class_instance.class_name
                booking["class_description"] = class_instance.description
                booking["start_datetime"] = class_instance.start_datetime.isoformat()

            for booking in cancelled_data:
                class_instance = Class.objects.get(id=booking["class_id"])
                booking["class_name"] = class_instance.class_name
                booking["class_description"] = class_instance.description
                booking["start_datetime"] = class_instance.start_datetime.isoformat()

            return Response(
                {
                    "upcoming": upcoming_data,
                    "past": past_data,
                    "cancelled": cancelled_data,
                },
                status=status.HTTP_200_OK,
            )
        
        except Customer.DoesNotExist:
            return Response({"detail": "Permission denied."}, status=status.HTTP_403_FORBIDDEN)
        
        except Exception:
            return Response(
                {"detail": "Internal Server Error"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

@method_decorator(csrf_protect, name='dispatch')
class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:

            user = request.user
            data = {}
            if Customer.objects.filter(user=user).exists():
                customer = Customer.objects.get(user=user)

                # Fetch the latest purchase
                latest_purchase = PurchaseHistory.objects.filter(customer=customer).order_by('-purchase_datetime').first()

                if latest_purchase:
                    latest_membership = latest_purchase.membership

                    if latest_membership:
                        membership_status = 'Active' if latest_membership.end_date >= timezone.now().date() else 'Inactive'
                        data['membership'] = {
                            'id': latest_membership.id,
                            'status': membership_status,
                            'duration': f'{latest_membership.duration} Months',
                            'start_date': latest_membership.start_date,
                            'end_date': latest_membership.end_date
                        }
                    else:
                        data['membership'] = {
                            'status': 'Inactive',
                            'start_date': '-',
                            'end_date': '-',
                            'duration': '-'
                        }
                else:
                    data['membership'] = {
                        'status': 'Inactive',
                        'start_date': '-',
                        'end_date': '-',
                        'duration': '-'
                    }

                profile_data = CustomerProfileSerializer(customer).data
                profile_data['membership'] = data['membership']

                data.update(profile_data)

            elif Staff.objects.filter(user=user).exists():
                staff = Staff.objects.get(user=user)
                data.update(UserProfileSerializer(staff.user).data)
            elif Administrator.objects.filter(user=user).exists():
                admin = Administrator.objects.get(user=user)
                data.update(UserProfileSerializer(admin.user).data)
            else:
                return Response(status=status.HTTP_404_NOT_FOUND)

            return Response(data, status=status.HTTP_200_OK)
        
        except Exception:
            return Response(
                {"detail": "Internal Server Error"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def put(self, request):
        try:
            
            user = request.user
            data = request.data
            user.first_name = data.get('first_name', user.first_name)
            user.last_name = data.get('last_name', user.last_name)
            user.save()

            if Customer.objects.filter(user=user).exists():
                customer = Customer.objects.get(user=user)
                serializer = CustomerProfileSerializer(customer)
            elif Staff.objects.filter(user=user).exists():
                staff = Staff.objects.get(user=user)
                serializer = UserProfileSerializer(staff.user)
            elif Administrator.objects.filter(user=user).exists():
                admin = Administrator.objects.get(user=user)
                serializer = UserProfileSerializer(admin.user)
            else:
                return Response(status=status.HTTP_404_NOT_FOUND)

            updated_profile_data = serializer.data
            return Response(updated_profile_data, status=status.HTTP_200_OK)

        except Exception:
            return Response(
                {"detail": "Internal Server Error"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

# Membership
@method_decorator(csrf_protect, name='dispatch')
class PurchaseMembershipView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):

        
        # Mapping from string to number of months
        duration_mapping = {
            '1 Month': 1,
            '6 Months': 6,
            '12 Months': 12
        }

        try:
            # RBAC
            cust_user = Customer.objects.get(user_id=request.user.id)
            
            # Retrieve the duration string from the request
            duration_str = request.data.get('duration')
            # Convert the duration string to an integer
            duration = duration_mapping.get(duration_str)
            # Validate the duration
            if duration is None:
                return Response({"error": "Invalid membership duration. Choose from '1 Month', '6 Months', or '12 Months'."}, status=400)

            # Retrieve or create the customer associated with the user
            customer = Customer.objects.get(user=request.user)

            # Calculate the start and end dates for the membership
            start_date = timezone.now()
            end_date = start_date + relativedelta(months=duration)

            # Check if there is already an active membership
            if Membership.objects.filter(customer=customer, end_date__gte=timezone.now()).exists():
                return Response({"error": "Active membership already exists."}, status=400)

            # Create a new membership record
            membership = Membership(customer=customer, start_date=start_date, end_date=end_date, duration=duration)
            membership.save()

            if duration == 1:
                membership_price = 29.99  # Price for 1 month
            elif duration == 6:
                membership_price = 159.99  # Price for 6 months
            elif duration == 12:
                membership_price = 299.99  # Price for 12 months
            
            # Create a new purchase history record
            purchase_history = PurchaseHistory(customer=customer, membership=membership,amount=membership_price, purchase_datetime=timezone.now() )
            purchase_history.save()

            # Return a successful response with membership details
            return Response({
                "message": "Membership purchased successfully!",
                "membership_id": membership.id,
                "end_date": membership.end_date
            }, status=201)

        except Customer.DoesNotExist:
            return Response({"detail": "Permission denied."}, status=status.HTTP_403_FORBIDDEN)
        
        except ValueError as e:
            # Log and handle any ValueError that occurs during data processing
            return Response({"error": "Invalid input data."}, status=400)
        
        except Exception:
            return Response(
                {"detail": "Internal Server Error"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


def check_active_membership(user):
    return Membership.objects.filter(customer__user=user, end_date__gte=timezone.now()).exists()


class CheckMembershipView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
       
        try:
            # RBAC
            cust_user = Customer.objects.get(user_id=request.user.id)
            
            user = request.user
            if check_active_membership(user):
                return Response({"has_active_membership": True})
            else:
                return Response({"has_active_membership": False})
            
        except Customer.DoesNotExist:
            return Response({"detail": "Permission denied."}, status=status.HTTP_403_FORBIDDEN)
        
        except Exception:
            return Response(
                {"detail": "Internal Server Error"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        
class PurchaseHistoryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        
        try:
            # RBAC
            cust_user = Customer.objects.get(user_id=request.user.id)
            
            user = request.user
            purchases = PurchaseHistory.objects.filter(customer__user=request.user).select_related('membership')
            serializer = PurchaseHistorySerializer(purchases, many=True)
            return Response(serializer.data)
        
        except Customer.DoesNotExist:
            return Response({"detail": "Permission denied."}, status=status.HTTP_403_FORBIDDEN)
        
        except Exception:
            return Response(
                {"detail": "Internal Server Error"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        