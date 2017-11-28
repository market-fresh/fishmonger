from django.forms import ModelForm
from fish.models import Fish

class FishForm(ModelForm):
    class Meta:
        model = Fish
        fields = ('name', 'chinese_name')
        #fields = ('name', 'chinese_name','sequence')
