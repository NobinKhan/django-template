


from django import views
from django.urls import include, path

from apps.emails.views import (
    EmailCreateView,
    EmailListView,

)
from apps.emails.api import SendEmail
from apps.emails import views





urlpatterns = [
    path("",include(([
        path("create/", EmailCreateView.as_view(), name="create_EmailCreate"),
        path("list/",EmailListView.as_view(),name='EmailListView'),
        path('EmailDeatilsApiView/<str:pk>/',views.EmailDeleteView.as_view(),name='emaildetails'),
        #path('EmailDeatilsApiView/<str:pk>/',views.email_detail,name='emaildetails'),
        path('send/',SendEmail.as_view(),name='send_emails'),
    ],"Email",)),),

]