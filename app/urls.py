
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from . import views
urlpatterns=[
    path('register/',views.RegistrationView.as_view(), name='register'),
    path('login/',views.LoginView.as_view(),name='login'),
    path('CreateService/', views.CreateService.as_view(), name='CreateService'),
    #serviceProvider------------------------------------------------------------------------------
    path('service-providers/', views.ServiceProviderListView.as_view(), name='service-provider-list'),
    path('UpdateService/<int:pk>/', views.UpdateService.as_view(), name='UpdateService'),
    path('DeleteService/<int:pk>/',views.DeleteService.as_view(),name='DeleteService'),
    path('ListRequests/<int:service_provider_id>/', views.ListRequests.as_view(), name='ListRequests'),
    path('respond/to/feedback/<int:feedback_id>/',views.RespondFeedback.as_view(),name='respond'),
    # user ---------------------------------------------------------------------------------------

    path('CreateRequest/<int:sr_id>/',views.CreateRequest.as_view(),name='CreateRequest'),
    path('ProfileView/', views.ProfileView.as_view(), name='ProfileView'),
    path('ListServiceProviders/<int:category_id>/<int:location_id>/', views.ListServiceProviders.as_view(), name='ListServiceProviders'),
    path('Createfeedback/<int:sr_id>/',views.CreateFeedback.as_view(),name='CreateFeedback'),
    path('ListFeedback/<int:service_id>/',views.ListFeedback.as_view(),name='ListFeedback'),
    path('Deletefeedback/<int:pk>/',views.Deletefeedback.as_view(),name='Deletefeedback'),
    path('ListmyRequests/',views.ListmyRequests.as_view(),name='ListmyRequests'),
    path('DeleteRequest/<int:pk>/',views.DeleteRequest.as_view(),name='DeleteRequest'),
    path('list-locations/',views.ListLocations.as_view(),name='list-locations'),
    path('list-categories/',views.ListCategories.as_view(),name='list-categories'),
    path('create/Serviceprovider/Profile/',views.CreateServiceproviderProfile.as_view(),name='CreateServiceproviderProfile'),
    path('report/service/<int:service_id>/', views.CreateReport.as_view(), name='Report'),
    path('list/response/feedback/<int:feedback_id>/',views.ListRespond.as_view(),name="List-feedback-respond"),
    #chat----------------------------------------------------------------------------------
    path('messages/<int:receiver>/', views.MessageListCreateAPIView.as_view(), name='message-list-create'),
    path('listmessages/<int:receiver_id>/', views.MessageListAPIView.as_view(), name='message-list-create'),
    
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

#check mail settings in booking