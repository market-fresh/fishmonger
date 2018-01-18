from django.forms import ModelForm
from stall.models import Stall

class StallForm(ModelForm):
    """
    Class definition for Stall form
    """

    class Meta:
        model = Stall
        fields = ('name', 'description')
        
        #Removed since address definition is not part of requirement
        #fields = ('name', 'description', 'address_1', 'address_2', 'country', 'city', 'unit_no', 'postal_code', 'contact_no')
