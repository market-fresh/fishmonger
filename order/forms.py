from django.forms import ModelForm, Form, formset_factory
from order.models import Order, Order_Item

#class OrderForm(ModelForm):
#    stall = models.ForeignKey('stall.Stall', on_delete=models.CASCADE)
#    status = models.CharField(max_length=50, blank=True, default='')

    #name = forms.CharField(required=True)
    #description = forms.CharField(required=False)
    #photo = forms.ImageField(required=False)

#class OrderItemForm(ModelForm):
#    class Meta:
#        model = Order_Item
#        fields = ('order', 'fish', 'quantity', 'status')

#OrderItemFormSet = formset_factory(OrderItemForm, can_order=True)

class OrderItemForm(ModelForm):
    class Meta:
        model = Order_Item
        fields = ('quantity', 'weight','cost')
