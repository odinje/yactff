from django.shortcuts import render, redirect, get_object_or_404
from django.http import Http404, HttpResponse, JsonResponse
from django.contrib.auth import login
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.decorators import login_required
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib.sites.shortcuts import get_current_site
from django.contrib import messages
from django.utils.encoding import force_bytes, force_text
from web.tokens import account_token
from django.core.files.uploadedfile import InMemoryUploadedFile
import sys
import hashlib
from web.models import (
        Page,
        Category,
        Challenge,
        Submission,
        Team,
        get_scoreboard,
        email_user,
        User
        )
from django.conf import settings
from web.forms import (
        TeamCreateForm,
        UserCreationForm,
        UserChangeForm,
        UserRequestPasswordResetForm,
        UserPasswordResetForm,
        AdminPageForm,
        AdminChallengeForm,
        AdminCategoryForm,
        AdminUserChangeForm
        )
from web.decorator import (
        team_required,
        not_in_team,
        anonymous_required,
        admin_required,
        game_active,
        )
from web.utils import (
        random_string,
        delete_page_file,
        create_zip,
        pause_game as _pause_game,
        )


def _generate_user_token_message(user, domain, https, template):
    print(https)
    message = render_to_string(template,
        {
            "user": user,
            "domain": domain,
            "protocol": "https" if https else "http",
            "uid": urlsafe_base64_encode(force_bytes(user.pk)).decode("utf-8"),
            "token": account_token.make_token(user),
        })
    return message


def _verify_user_token(uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and account_token.check_token(user, token):
        return user
    return None


@anonymous_required
def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()
            mail_subject = "Activate your account for {}".format(settings.CTF_NAME)
            message = _generate_user_token_message(user, get_current_site(request), request.is_secure(), "web/user_activate_account_email.html")
            email_user(user.id, mail_subject, message)
            messages.info(request, "Please confirm your email address to complete the registration")
            return redirect("index")
    else:
        form = UserCreationForm()
    return render(request, 'web/signup.html', {'form': form})


def user_activate(request, uidb64, token):
    user = _verify_user_token(uidb64, token)
    if user:
        user.is_active = True
        user.save()
        login(request, user)
        messages.success(request, "Email is verifed")
    else:
        messages.error(request, "Activation link is invalid!")
    return redirect("user_profile")


def page(request, path=None):
    user = request.user
    name = path.split("/")[-1] if path else "index"
    page = get_object_or_404(Page, name=name)
    context = {}
    if user.is_superuser:
        if request.method == "POST":
            old_name = page.name
            old_type = page.type
            form = AdminPageForm(request.POST, instance=page)
            if form.is_valid():
                page = form.save()
                if old_name != page.name:
                    delete_page_file(old_name, old_type)
                    return redirect("page", path=page.name)
        else:
            form = AdminPageForm(instance=page)
        pages = Page.objects.all()
        template = "web/admin_page.html"
        context["form"] = form
        context["pages"] = pages
    else:
        template = "web/page.html"

    context["page"] = page
    return render(request, template, context)


@admin_required
def page_add(request):
    page_name = random_string()
    try:
        Page.objects.create(name=page_name, content="Text Here")
        return redirect("page", path=page_name)
    except:
        raise Http404  # Change to more useful return code


@admin_required
def page_remove(request, id):
    page = get_object_or_404(Page, id=id)
    if page.name != "index":  # Cannot delete index, maybe give value error?
        page.delete()
    return redirect("index")


@login_required
@game_active
def challenges(request):
    user = request.user
    categories = Category.objects.all()
    challenges = Challenge.objects.with_solves(team=user.team_id)
    context = {}
    if user.is_superuser:
        template = "web/admin_challenges.html"
        if request.method == "POST":
            form = [AdminCategoryForm(request.POST, instance=category, prefix=category.name) for category in categories]
            form.append(AdminCategoryForm(request.POST, prefix="new_category"))
            for pos, f in enumerate(form):
                if f.is_valid():
                    print(pos)
                    if pos == len(form)-1 and f.cleaned_data["name"] == "":
                        break
                    elif f.cleaned_data["delete"]:
                        f.instance.delete()
                    else:
                        f.save()
            return redirect("challenges")
        else:
            form = [AdminCategoryForm(instance=category, prefix=category.name) for category in categories]
            form.append(AdminCategoryForm(prefix="new_category"))
        context["form"] = form
    else:
        template = "web/challenges.html"
    context["challenges"] = challenges
    context["categories"] = categories

    return render(request, template, context)


@login_required
@game_active
def challenge(request, id):
    user = request.user
    team_id = user.team_id
    challenge = Challenge.objects.with_solves(team=team_id, challenge=id)
    context = {}
    if user.is_superuser:
        template = "web/admin_challenge.html"
        if request.method == "POST":
            form = AdminChallengeForm(request.POST,  instance=challenge)
            files = request.FILES.getlist("files")
            print(files)
            if form.is_valid():
                new_challenge = form.save(commit=False)
                if files:
                    files_zip = create_zip(files)
                    files_zip.seek(0)
                    new_challenge.file = InMemoryUploadedFile(files_zip, None, "{}.zip".format(hashlib.sha256(files_zip.read()).hexdigest()), "application/zip", sys.getsizeof(files_zip), charset=None)
                new_challenge.save()
        else:
            form = AdminChallengeForm(instance=challenge)
        context["form"] = form
        context["submissions"] = Submission.objects.filter(challenge_id=challenge.id)
    else:
        template = "web/challenge.html"
        if not challenge.active:  # TODO: Rename active => is_active
            raise Http404
    context["challenge"] = challenge
    context["flag_format"] = settings.CTF_FLAG_FORMAT
    if request.method == "POST" and team_id:
        if "flag" in request.POST:
            flag = request.POST["flag"]
            if challenge.is_flag(flag):
                solved = Submission(team_id=team_id, challenge=challenge, solved_by=user)
                solved.save()
                challenge.is_solved = True

    return render(request, template, context)


@admin_required
def challenge_add(request):
    challenge_name = random_string()
    try:
        first_category = Category.objects.filter()[:1].get()
        challenge = Challenge.objects.create(title=challenge_name, category=first_category, author=request.user, key=settings.CTF_FLAG_FORMAT)
        return redirect("challenge", id=challenge.id)
    except:
        raise Http404  # Change to more useful return code


@admin_required
def submission_remove(request, id):
    submission = get_object_or_404(Submission, id=id)
    challenge_id = submission.challenge_id
    submission.delete()
    return redirect("challenge", id=challenge_id)


def scoreboard(request):
    return render(request, "web/scoreboard.html")


def scoreboard_json(request):
    scores = get_scoreboard()
    return JsonResponse(scores, safe=False)


def user_password_reset(request):
    if request.method == "POST":
        form = UserRequestPasswordResetForm(request.POST)
        if form.is_valid():
            user = get_object_or_404(User, email=form.cleaned_data["email"])
            if user.is_active:
                email_subject = "Password reset for {}".format(settings.CTF_NAME)
                message = _generate_user_token_message(user, get_current_site(request), request.is_secure(), "web/password_reset_email.html")
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
    user = _verify_user_token(uidb64, token)
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
            "challenges": challenges,
            "password_form": password_form,
            "userdata_form": userdata_form,
        })


@team_required
def team_profile(request):
    team = request.user.team
    challenges = Submission.objects.get_solved(team=team)
    return render(request, "web/team_profile.html",
            {
                "team": team,
                "team_view": True,
                "max_team_size": settings.MAX_TEAM_SIZE,
                "challenges": challenges
            })


@login_required
def public_team_profile(request, id):
    team = get_object_or_404(Team, id=id)
    challenges = Submission.objects.get_solved(team=team)

    return render(request, "web/team_profile.html",
            {
                "team": team,
                "team_view": False,
                "max_team_size": None,
                "challenges": challenges,
            })


@not_in_team
def team_create(request):
    user = request.user
    if request.method == "POST":
        form = TeamCreateForm(request.POST)
        if form.is_valid():
            team = form.save()
            user.team = team
            user.save()

            return redirect("team_profile")
    else:
        form = TeamCreateForm()

    return render(request, "web/team_create.html",
            {
                "form": form,
                "max_team_size": settings.MAX_TEAM_SIZE
            })


@not_in_team  # TODO: Rethink or redo
def team_join(request):
    user = request.user
    if request.method == "POST":
        token = request.POST["token"]
        try:
            team = Team.objects.get(token=token)
            user.team = team
            user.save()
            messages.info(request, "Joined, {}".format(team.name))
            return redirect("team_profile")
        except:
            messages.error(request, "Team not found")
            return redirect("user_profile")
    else:
        return HttpResponse(status=405)


@admin_required
def user_all(request):
    users = User.objects.all()

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


@admin_required
def pause_game(request):
    _pause_game()
    return redirect("index")
