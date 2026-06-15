from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

from apps.cart.services import merge_session_into_user
from apps.catalog.models import Product

from .forms import EmailAuthenticationForm, ProfileForm, RegisterForm
from .models import SavedItem
from .utils import record_attestation


def login_view(request):
    if request.user.is_authenticated:
        return redirect("accounts:dashboard")
    form = EmailAuthenticationForm(request, data=request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.get_user()
        login(request, user)
        merge_session_into_user(request, user)
        if not request.POST.get("remember"):
            request.session.set_expiry(0)
        return redirect("accounts:dashboard")
    return render(request, "accounts/auth.html", {"login_form": form, "active_tab": "signin"})


def register_view(request):
    if request.user.is_authenticated:
        return redirect("accounts:dashboard")
    form = RegisterForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        record_attestation(request, email=user.email, context="register", user=user)
        login(request, user)
        merge_session_into_user(request, user)
        messages.success(request, "Welcome to TX Ballistics!")
        return redirect("accounts:dashboard")
    return render(request, "accounts/auth.html", {"register_form": form, "active_tab": "register"})


def logout_view(request):
    logout(request)
    return redirect("core:home")


@login_required
def dashboard(request):
    user = request.user
    orders = user.orders.all()[:10]
    saved = user.saved_items.select_related("product")
    ready_count = user.orders.filter(status="ready").count()
    lifetime = sum((o.total for o in user.orders.all()), 0)
    stats = {
        "orders": user.orders.count(),
        "ready": ready_count,
        "saved": saved.count(),
        "lifetime": lifetime,
    }
    return render(
        request,
        "accounts/dashboard.html",
        {
            "orders": orders,
            "saved": saved,
            "stats": stats,
            "active_tab": request.GET.get("tab", "dashboard"),
            "profile_form": ProfileForm(instance=user),
        },
    )


@login_required
def profile_update(request):
    form = ProfileForm(request.POST or None, instance=request.user)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Profile updated.")
    return redirect("/account/?tab=profile")


@login_required
def save_toggle(request):
    product = get_object_or_404(Product, pk=request.POST.get("product_id"))
    saved = SavedItem.objects.filter(user=request.user, product=product).first()
    if saved:
        saved.delete()
        state = "off"
    else:
        SavedItem.objects.create(user=request.user, product=product)
        state = "on"
    if request.htmx:
        return HttpResponse("♥" if state == "on" else "♡")
    return redirect(request.META.get("HTTP_REFERER", "core:home"))
