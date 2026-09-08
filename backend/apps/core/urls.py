from django.urls import path

from . import views

urlpatterns = [
    path("", views.HomePageView.as_view(), name="homepage"),
    path("dashboard", views.DashboardView.as_view(), name="dashboard"),
    path("about", views.AboutPageView.as_view(), name="about"),
    path("contact", views.ContactPageView.as_view(), name="contact"),
    path("questions", views.QuestionPageView.as_view(), name="questions"),
]
