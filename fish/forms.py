from django.forms import ModelForm
from fish.models import Fish

class FishForm(ModelForm):
    """
    Class definition for Fish form
    """
    
    class Meta:
        model = Fish
        fields = ('name', 'chinese_name')
        #Below code is used to see the fish sequence. Used to debug implementation of sequencing of fish
        #fields = ('name', 'chinese_name','sequence')
