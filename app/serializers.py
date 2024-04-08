
from . import models 
from rest_framework import serializers
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from .models import ServiceProvider,Feedback,Category,CustomUser,Locations, ServiceProviderprofile
class RegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = models.CustomUser
        fields = ['username', 'email', 'password','first_name','last_name','is_User','is_service']

    def create(self, validated_data):
        user = models.CustomUser.objects.create_user(**validated_data)
        return user

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')

        if username and password:
            user = authenticate(username=username, password=password)

            if not user:
                msg = 'Unable to log in with provided credentials.'
                raise serializers.ValidationError(msg, code='authorization')
        else:
            msg = 'Must include "username" and "password".'
            raise serializers.ValidationError(msg, code='authorization')

        attrs['user'] = user
        return attrs
    

class CreateServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceProvider
        fields=['category','shop_name','location','description'] 
        read_only_fields = ['user']  

class ServiceProviderSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = ServiceProvider
        fields = '__all__'


class DeleteServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model=ServiceProvider
        fields=[]
        

class CreateRequestSerializer(serializers.ModelSerializer):
    class Meta: 
        model = models.Booking
        fields = ['datetime']

        
class RequestViewSerializer(serializers.ModelSerializer):
    username=serializers.CharField(source='user.username')
    locationname=serializers.CharField(source='service.location.location')
    categoryname=serializers.CharField(source='service.category.name')
    shope=serializers.CharField(source='service.shop_name')
    class Meta:
        model = models.Booking
        fields = ['user','datetime','username','locationname','categoryname','shope','id',]




class MyRequests(serializers.ModelSerializer):
    service_provider = ServiceProviderSerializer(source='service', read_only=True)
    category = serializers.CharField(source='service.category.name', read_only=True)
    locationname=serializers.CharField(source='service.location.location')

    class Meta:
        model = models.Booking
        fields = ['datetime', 'service_provider', 'category','locationname','id']

class DeleteRequestserializer(serializers.ModelSerializer):
    class Meta:
        model=models.Booking
        fields=[]


    
class ListService_Providersserializer(serializers.ModelSerializer):
    class Meta:
        model=ServiceProvider
        fields='__all__'

class Feedbackserializer(serializers.ModelSerializer):
    class Meta:
        model=Feedback
        fields=['feedback','rating']

class ListFeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feedback
        fields = ['feedback','rating','user']


class Deletefeedbackserializer(serializers.ModelSerializer):
    class Meta:
        model=Feedback
        fields=[]
class ServiceProviderSerializer(serializers.ModelSerializer):
    locationname=serializers.CharField(source='location.location')
    categoryname=serializers.CharField(source='category.name')
    username=serializers.CharField(source='user.username')
    
    class Meta:
        model=ServiceProvider
        fields=['user','category','shop_name','location','description','id','username','categoryname','locationname','avg_rating']

class profileSerializer(serializers.ModelSerializer):
    class Meta:
        model=CustomUser
        fields=["username","email","first_name","last_name"]


class Locationserializer(serializers.ModelSerializer):
    locationname = serializers.CharField(source='location')  

    class Meta:
        model = Locations
        fields = ['id', 'locationname']

class CategorySerializer(serializers.ModelSerializer):
    categoryname=serializers.CharField(source='name')
    class Meta:
        model=Category
        fields=['id','categoryname']

class CreateProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model=ServiceProviderprofile
        fields=["document","ph","is_ok"]

class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Message
        fields = ['message']

class MessageListSerializer(serializers.ModelSerializer):
    sender_username = serializers.ReadOnlyField(source='sender.username')
    receiver_username = serializers.ReadOnlyField(source='receiver.username')
    class Meta:
        model = models.Message
        fields = ['sender_username','receiver_username','timestamp','message']

class Reportserializer(serializers.ModelSerializer):
    class Meta:
        model=models.Report
        fields=['reason']

class RespondSerializer(serializers.ModelSerializer):
    class Meta:
        model=models.FeedbackRespond
        fields=['respond']

class ListRespond(serializers.ModelSerializer):
    shope_name=serializers.CharField(source="feedback.service.shop_name")
    class Meta:
        model=models.FeedbackRespond
        fields=['shope_name','respond']