from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm as _UserCreationForm
from web.models import Team, User, Page, Challenge, Category
from yactff.widgets import CodeMirrorWidget


class LoginForm(AuthenticationForm):
    AuthenticationForm.error_messages["inactive"] = "This account is inactive. Click the activation link sent to your email"


class TeamCreateForm(forms.ModelForm):
    class Meta:
        model = Team
        fields = ["name"]


class UserCreationForm(_UserCreationForm):
    class Meta(_UserCreationForm.Meta):
        model = User
        fields = ("email", "nickname", "first_name", "last_name")


class UserChangeForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ("email", "nickname", "first_name", "last_name")


class UserRequestPasswordResetForm(forms.Form):
    email = forms.EmailField()


class UserPasswordResetForm(_UserCreationForm):
    class Meta(_UserCreationForm.Meta):
        model = User
        fields = ()


class AdminUserChangeForm(UserChangeForm):
    class Meta(UserChangeForm.Meta):
        UserChangeForm.Meta.fields += ("team", "is_active")


class AdminPageForm(forms.ModelForm):
    class Meta:
        model = Page
        fields = ("name", "type", "in_menu", "content")
        widgets = {
            "content": CodeMirrorWidget(attrs={'style': 'width: 90%; height: 100%;'}),
        }


class AdminChallengeForm(forms.ModelForm):
    files = forms.FileField(widget=forms.FileInput(attrs={'multiple': True}), required=False)

    class Meta:
        model = Challenge
        exclude = ["file"]
        widgets = {
            "description": CodeMirrorWidget(attrs={'style': 'width: 90%; height: 100%;'}),
        }


class AdminCategoryForm(forms.ModelForm):
    name = forms.CharField(required=False)
    delete = forms.BooleanField(
        initial=False,
        required=False,
        help_text=('Check this to delete this object')
    )

    class Meta:
        model = Category
        fields = ("name",)
