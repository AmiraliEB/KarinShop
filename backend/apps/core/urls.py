from django.urls import path

from . import views

urlpatterns = [
    path("", views.HomePageView.as_view(), name="homepage"),
    path("dashboard/", views.DashboardView.as_view(), name="dashboard"),
    path("dashboard/address/", views.DashboardAddressView.as_view(), name="dashboard-address"),
    path("dashboard/messages/", views.DashboardMessagesView.as_view(), name="dashboard-messages"),
    path("about/", views.AboutPageView.as_view(), name="about"),
    path("contact/", views.ContactPageView.as_view(), name="contact"),
    path("questions/", views.QuestionPageView.as_view(), name="questions"),
]
