from django.urls import path
from paas.views import ListCreateUsersView

urlpatterns = [
    path('users/', ListCreateUsersView.as_view(), name="list-users"),
]