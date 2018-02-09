from django import forms
from web.models import Team, User, Page, Challenge, Category
from yactff.widgets import CodeMirrorWidget


class TeamCreateForm(forms.ModelForm):
    class Meta:
        model = Team
        fields = ["name", "logo"]


class UserCreationForm(forms.ModelForm):
    """A form for creating new users. Includes all the required
    fields, plus a repeated password."""
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Password confirmation', widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ("email", "nickname")

    def clean_password2(self):
        # Check that the two password entries match
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class UserChangeForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ("email", "nickname",)


class AdminPageForm(forms.ModelForm):
    class Meta:
        model = Page
        fields = ("name", "type", "in_menu", "content")
        widgets = {
            "content": CodeMirrorWidget(attrs={'style': 'width: 90%; height: 100%;'}),
        }


class AdminChallengeForm(forms.ModelForm):
    class Meta:
        model = Challenge
        fields = ("__all__")
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
