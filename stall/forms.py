from django.forms import ModelForm
from stall.models import Stall

class StallForm(ModelForm):
    class Meta:
        model = Stall
        fields = ('name', 'description', 'address_1', 'address_2', 'country', 'city', 'unit_no', 'postal_code', 'contact_no')
