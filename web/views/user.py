
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.decorators import login_required
from django.contrib.sites.shortcuts import get_current_site
from django.contrib import messages
from web.tokens import generate_user_token_message, verify_user_token
from web.models import (
        Submission,
        email_user,
        User
        )
from django.conf import settings
from web.forms import (
        UserCreationForm,
        UserChangeForm,
        UserRequestPasswordResetForm,
        UserPasswordResetForm,
        AdminUserChangeForm
        )
from web.decorator import (
        anonymous_required,
        admin_required,
        )


@anonymous_required
def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()
            mail_subject = "Activate your account for {}".format(settings.CTF_NAME)
            message = generate_user_token_message(user, get_current_site(request), request.is_secure(), "web/user_activate_account_email.html")
            email_user(user.id, mail_subject, message)
            messages.info(request, "Please confirm your email address to complete the registration")
            return redirect("index")
    else:
        form = UserCreationForm()
    return render(request, 'web/signup.html', {'form': form})


def user_activate(request, uidb64, token):
    user = verify_user_token(uidb64, token)
    if user:
        user.is_active = True
        user.save()
        login(request, user)
        messages.success(request, "Email is verifed")
    else:
        messages.error(request, "Activation link is invalid!")
    return redirect("user_profile")


def user_password_reset(request):
    if request.method == "POST":
        form = UserRequestPasswordResetForm(request.POST)
        if form.is_valid():
            user = get_object_or_404(User, email=form.cleaned_data["email"])
            if user.is_active:
                email_subject = "Password reset for {}".format(settings.CTF_NAME)
                message = generate_user_token_message(user, get_current_site(request), request.is_secure(), "web/password_reset_email.html")
                email_user(user.id, email_subject, message)
                messages.info(request, "Password reset link is sent to your email")
                return redirect("index")
            else:
                messages.warning(request, "User is not active. Contact the admin if you want to activate this account")
    else:
        form = UserRequestPasswordResetForm()
    return render(request, "web/password_reset_form.html", {"form": form})


def user_password_reset_confirm(request, uidb64, token):
    template = "web/password_reset_confirm.html"
    user = verify_user_token(uidb64, token)
    context = {}
    if user:
        context["validlink"] = True
        if request.method == "POST":
            form = UserPasswordResetForm(request.POST, instance=user)
            if form.is_valid():
                form.save()
                login(request, user)
                messages.success(request, "Password reset successful. You are now logged in")
                return redirect("index")
        else:
            form = UserPasswordResetForm()
        context["form"] = form
    else:
        context["validlink"] = False
    return render(request, template, context)


@login_required
def user_profile(request):
    user = request.user
    team = user.team
    challenges = Submission.objects.get_solved(team=team, user=user)
    if request.method == "POST":
        userdata_form = UserChangeForm(request.POST, instance=user)
        password_form = PasswordChangeForm(user, request.POST)
        if userdata_form.is_valid():
            userdata_form.save()
        if password_form.is_valid():
            password_form.save()
    else:
        userdata_form = UserChangeForm(instance=user)
        password_form = PasswordChangeForm(user)
    return render(request, "web/user_profile.html",
                  {
                       "password_form": password_form,
                       "userdata_form": userdata_form,
                       "challenges": challenges,
                  })


@admin_required
def user_all(request):
    users = User.objects.all().order_by("id")

    return render(request, "web/admin_users.html", {"users": users})


@admin_required
def user_show(request, id):
    user = User.objects.get(id=id)
    if request.method == "POST":
        form = AdminUserChangeForm(request.POST, instance=user)
        if form.is_valid():
            user = form.save()
    else:
        form = AdminUserChangeForm(instance=user)

    return render(request, "web/admin_user.html", {"target_user": user, "form": form})
