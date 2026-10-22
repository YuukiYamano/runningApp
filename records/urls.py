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
    path("records/new/", views.RecordCreateView.as_view(), name="record_new"),
    path("records/<int:pk>/", views.RecordDetailView.as_view(), name="record_detail"),
    path("records/<int:pk>/edit/", views.RecordUpdateView.as_view(), name="record_edit"),
    path("records/<int:pk>/delete/", views.RecordDeleteView.as_view(), name="record_delete"),
    path("profile/", views.ProfileUpdateView.as_view(), name="profile"),
]
