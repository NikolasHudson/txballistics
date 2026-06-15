from django.urls import path

from . import views

app_name = "cart"

urlpatterns = [
    path("", views.detail, name="detail"),
    path("add/", views.add, name="add"),
    path("update/", views.update, name="update"),
    path("remove/", views.remove, name="remove"),
    path("promo/", views.apply_promo, name="apply_promo"),
]
