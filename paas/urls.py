from django.urls import path
from paas.views import ListCreateUsersView
from paas.views import ListCreateResourceView
from paas.views import ManageResource
from paas.views import login_view

urlpatterns = [
    path('login/', login_view, name='user-login'),
    path('users/', ListCreateUsersView.as_view(), name="list-users"),
    path('resources/', ListCreateResourceView.as_view(), name="list-resources"),

    path('resources/<uuid:pk>', ManageResource.as_view(), name="get-resource")
]
