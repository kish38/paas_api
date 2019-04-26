from django.urls import path
from paas.views import ListCreateUsersView
from paas.views import ListCreateResourceView

urlpatterns = [
    path('users/', ListCreateUsersView.as_view(), name="list-users"),
    path('resources/', ListCreateResourceView.as_view(), name="list-resources"),
]