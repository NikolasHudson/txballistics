from django.urls import path

from . import views

app_name = "catalog"

urlpatterns = [
    path("search/", views.search, name="search"),
    path("c/<slug:slug>/", views.category, name="category"),
    path("p/<slug:slug>/", views.product_detail, name="product_detail"),
]
