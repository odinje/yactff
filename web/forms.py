from django.forms  import ModelForm
from web.models import Team

class TeamCreateForm(ModelForm):
    class Meta:
        model = Team
        fields = ["name", "logo"]
