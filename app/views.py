from django.conf import settings
from django.shortcuts import render, redirect
from django.views import View
from .  models import CustomUser
from . import models
from rest_framework import generics
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import RegistrationSerializer
from django.contrib.auth import authenticate
from rest_framework import generics, status
from . import serializers
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework import generics, permissions, status
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.utils import timezone
from django.core.mail import send_mail

from rest_framework.exceptions import ValidationError

from django.db.models import Avg, F, FloatField
from django.db.models.functions import Coalesce
from django.utils import timezone
from rest_framework.exceptions import ValidationError
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie
from rest_framework import generics
from rest_framework.exceptions import ValidationError
from django.shortcuts import get_object_or_404
from . import serializers, models
from django.utils import timezone

from django.utils import timezone
from rest_framework.exceptions import ValidationError

from django.db import transaction


class RegistrationView(generics.CreateAPIView):
    serializer_class = RegistrationSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        refresh = RefreshToken.for_user(user)

        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'username': user.username,
            'email': user.email,
            'first_name':user.first_name,
            'last_name':user.last_name,
            'id':user.id,
            'normal_user':user.is_User,
            'superuser':user.is_superuser,
            'service_provider':user.is_service,
            
      })


class LoginView(generics.GenericAPIView):
    serializer_class = serializers.LoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        username = serializer.validated_data.get('username')
        password = serializer.validated_data.get('password')

        user = authenticate(request, username=username, password=password)

        if user:
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'id':user.id,
                'normal_user':user.is_User,
                'superuser':user.is_superuser,
                'service_provider':user.is_service,

               'profile_pic':user.profile_picture.url if user.profile_picture else None

    
            })
        else:
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
        
from rest_framework.exceptions import PermissionDenied
class CreateService(generics.CreateAPIView):
    serializer_class = serializers.CreateServiceSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        profile = models.ServiceProviderprofile.objects.filter(user=self.request.user).first()
 
        if profile and profile.is_ok:
            serializer.save(user=self.request.user)
        else:
            raise PermissionDenied("You are not authorized to create a service.")



# class ListService(generics.ListAPIView):
#     serializer_class = serializers.ListServiceSerializer
#     permission_classes = [IsAuthenticated]

#     def get_queryset(self):
#         user = self.request.user
        
#         queryset = models.ServiceProvider.objects.filter(user=user)
#         return queryset
class ServiceProviderListView(generics.ListAPIView):
    queryset = models.ServiceProvider.objects.all()
    serializer_class = serializers.ServiceProviderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return models.ServiceProvider.objects.filter(user=user)
        
class UpdateService(generics.UpdateAPIView):
    serializer_class = serializers.CreateServiceSerializer
    permission_classes = [IsAuthenticated]
    queryset= models.ServiceProvider.objects.all()

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class DeleteService(generics.RetrieveDestroyAPIView):
    serializer_class = serializers.DeleteServiceSerializer
    permission_classes = [IsAuthenticated]
    queryset = models.ServiceProvider.objects.all()
    
    def destroy(self, request, *args, **kwargs):  
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({"message": "Service deleted successfully."}, status=status.HTTP_204_NO_CONTENT)

        
class ListRequests(generics.ListAPIView):
    serializer_class = serializers.RequestViewSerializer
    queryset = models.Booking.objects.all()
    
    def get_queryset(self):
        service_provider_id = self.kwargs.get('service_provider_id')
        service_provider = get_object_or_404(models.ServiceProvider, id=service_provider_id)
        return models.Booking.objects.filter(service=service_provider)
    
# class UpdateRequest(generics.RetrieveUpdateAPIView):
#     serializer_class = serializers.RequestUpdateSerializer
#     permission_classes = [IsAuthenticated]
#     queryset= models.Booking.objects.all()



class ProfileView(generics.RetrieveAPIView):
    serializer_class = serializers.profileSerializer
    permission_classes=[IsAuthenticated]

    def get_object(self):
        profile_instance=get_object_or_404(models.CustomUser,username=self.request.user.username)
        return profile_instance


# User------------------- 
    

class ListServiceProviders(APIView):
    def get(self, request, category_id, location_id):  
        category = get_object_or_404(models.Category, pk=category_id)
        location = get_object_or_404(models.Locations, pk=location_id)
        
        # Annotate each service provider with their average rating, ensuring to handle null values
        service_providers = models.ServiceProvider.objects.filter(
            category=category, location=location, approve=True
        ).annotate(
            average_rating=Coalesce(Avg('feedback__rating'), F('avg_rating'), output_field=FloatField())
        ).order_by('-average_rating')
        
        serializer = serializers.ServiceProviderSerializer(service_providers, many=True)
        return Response(serializer.data)
    


class CreateRequest(generics.CreateAPIView):
    serializer_class = serializers.CreateRequestSerializer
    queryset = models.Booking.objects.all()
    permission_classes = [IsAuthenticated]

    @method_decorator(ensure_csrf_cookie)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def perform_create(self, serializer):
        service_id = self.kwargs.get("sr_id")
        service = get_object_or_404(models.ServiceProvider, id=service_id)
        user = self.request.user
        booking_time = serializer.validated_data.get('datetime')

        if booking_time is None:
            raise ValidationError("Booking time is required.")

        # Get all bookings for the service
        service_bookings = models.Booking.objects.filter(service=service)

        if service_bookings.exists():
            # Iterate through all existing bookings
            for booking in service_bookings:
                # Ensure booking time is at least 60 minutes after the existing booking time
                if booking_time <= booking.datetime + timezone.timedelta(minutes=60):
                    raise ValidationError("Booking time must be at least 60 minutes after any existing booking time for this service.")
                # If booking date is different, allow booking without restriction
                if booking_time.date() != booking.datetime.date():
                    break
        
        end_time = booking_time + timezone.timedelta(hours=1)

        conflicting_bookings = models.Booking.objects.filter(
            service=service,
            datetime__gte=booking_time,
            datetime__lt=end_time
        )

        if conflicting_bookings.exists():
            raise ValidationError("Another booking for this service is already scheduled during the requested time.")
        
        booking = serializer.save(service=service, user=user)




        # Send confirmation email to user
        # subject = 'Booking Confirmation'
        # message = f"Dear {user.username}, Your booking has been confirmed at {booking_time}."
        # from_email = 'your-email@example.com'  # Update with your email
        # to_email = user.email
        # send_mail(subject, message, from_email, [to_email])

        # provider_subject = 'New Booking Notification'
        # provider_message = f"Dear {service.user.username}, A new booking has been placed for your {service.shop_name} service at {booking_time}."
        # provider_from_email = 'demotest640@gmail.com'  # Update with your email
        # provider_to_email = service.user.email
        # send_mail(provider_subject, provider_message, provider_from_email, [provider_to_email])

        


class CreateFeedback(generics.CreateAPIView):
    serializer_class=serializers.Feedbackserializer
    queryset = models.Feedback.objects.all()
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        user=self.request.user
        sr_id=self.kwargs.get('sr_id')
        instance=get_object_or_404(models.ServiceProvider,id=sr_id)
        serializer.save(user=user,service=instance)
        return super().perform_create(serializer)

class ListFeedback(generics.ListAPIView):
    serializer_class = serializers.ListFeedbackSerializer
    queryset = models.Feedback.objects.all()
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        service_id = self.kwargs.get('service_id')
        return models.Feedback.objects.filter(service=service_id)

class Deletefeedback(generics.RetrieveDestroyAPIView):
    serializer_class=serializers.Deletefeedbackserializer
    permission_classes = [IsAuthenticated]
    queryset=models.Feedback.objects.all()

class ListmyRequests(generics.ListAPIView):
    serializer_class=serializers.MyRequests
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user=self.request.user
        queryset=models.Booking.objects.filter(user=user)
        return queryset
    
class DeleteRequest(generics.DestroyAPIView):
    serializer_class = serializers.DeleteRequestserializer
    permission_classes = [IsAuthenticated]
    queryset = models.Booking.objects.all()
    s = [IsAuthenticated]
    queryset = models.Booking.objects.all()
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()  # Retrieve the booking instance
        user = instance.user  # Get the associated user
        
        # Refund the money to the user and deduct penalty
        refund_amount = 100 - 15  # Refund 100 and deduct 15 as penalty
        user.balance += refund_amount
        user.save()

        # Create a Payment object for the refund and penalty
        # penalty_description = "Penalty for cancellation"
        # refund_description = "Refund for cancelled booking"
        # # models.Payment.objects.create(
        #     user=user,
        #     payment=refund_amount,  # Deducted amount (refund - penalty)
        #     service=instance.service,
            
        # )
        
        # Call the superclass method to perform the deletion
        return super().destroy(request, *args, **kwargs)


class ListLocations(generics.ListAPIView):
    serializer_class=serializers.Locationserializer
    queryset=models.Locations.objects.all()

class ListCategories(generics.ListAPIView):
    serializer_class=serializers.CategorySerializer
    queryset=models.Category.objects.all()

class CreateServiceproviderProfile(generics.CreateAPIView):
    serializer_class=serializers.CreateProfileSerializer
    queryset=models.ServiceProviderprofile.objects.all()
    def perform_create(self, serializer):
        user=self.request.user
        serializer.save(user=user)
        return super().perform_create(serializer)
    

class MessageListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = serializers.MessageSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        receiver_id = self.kwargs['receiver']
        # Mark messages as read
        messages = models.Message.objects.filter(receiver_id=receiver_id)
        for message in messages:
            message.is_read = True
            message.save()
        return messages
    
    def perform_create(self, serializer):
        receiver_id = self.kwargs.get('receiver')
        receiver = get_object_or_404(models.CustomUser, id=receiver_id)
        serializer.save(sender=self.request.user, receiver=receiver)


class MessageListAPIView(generics.ListCreateAPIView):
    serializer_class =serializers.MessageListSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        user = self.request.user
        receiver_id = self.kwargs.get('receiver_id')
        return models.Message.objects.filter(sender=user, receiver_id=receiver_id) | \
               models.Message.objects.filter(sender_id=receiver_id, receiver=user)

class CreateReport(generics.CreateAPIView):
    serializer_class=serializers.Reportserializer
    permission_classes=(IsAuthenticated,)
    def perform_create(self, serializer):
        user = self.request.user
        service_id = self.kwargs.get('service_id')
        service = get_object_or_404(models.ServiceProvider, id=service_id)
        serializer.save(user=user, service=service)

     
        report_count = models.Report.objects.filter(service=service).count()
        
        if report_count > 7:
           
            service.approve = False
            service.save()
            # dlt=models.Report.objects.filter(service=service)
            # dlt.delete()
            provider_subject = 'Report Notifiaction'
            provider_message = f"Many reports have been submitted for your service named /{service.shop_name}/. Effective immediately, users cannot access your service. Please review and address this matter urgently. Thank you."
            provider_from_email = 'demotest640@gmail.com'  # Update with your email
            provider_to_email = service.user.email
            send_mail(provider_subject, provider_message, provider_from_email, [provider_to_email])


class RespondFeedback(generics.CreateAPIView):
    serializer_class=serializers.RespondSerializer
    permission_classes=[IsAuthenticated]

    def perform_create(self, serializer):
        user=self.request.user
        feedback_id=self.kwargs.get('feedback_id')
        feedback=get_object_or_404(models.Feedback, id=feedback_id)
        serializer.save(user=user,feedback=feedback)


class ListRespond(generics.ListAPIView):
    serializer_class=serializers.ListRespond
    permission_classes=[IsAuthenticated]
    def get_queryset(self):
        feedback_id=self.kwargs.get('feedback_id')
        feedback=get_object_or_404(models.Feedback, id=feedback_id)
        query=models.FeedbackRespond.objects.filter(feedback=feedback)
        return query
        