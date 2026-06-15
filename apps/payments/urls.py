from django.urls import path

from . import views

app_name = "payments"

urlpatterns = [
    path("webhook/<str:provider>/", views.webhook, name="webhook"),
]
