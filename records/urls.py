from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path

from . import views
from .forms import LoginForm

urlpatterns = [
    path("", views.TopView.as_view(), name="top"),
    path("signup/", views.SignUpView.as_view(), name="signup"),
    path("login/", LoginView.as_view(authentication_form=LoginForm), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("records/", views.RecordListView.as_view(), name="record_list"),
]
