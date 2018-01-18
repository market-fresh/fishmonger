from datetime import datetime, timedelta, time
from django.db import models

from order.models import Order, Order_Item
from purchase_order.models import Purchase_Order, Purchase_Order_Item
from invoice.models import Invoice, Invoice_Item

def get_or_none(model, action, *args, **kwargs):
    """
    Service to abstract the get and filter method call on model objects, and handle DoesNotExist error by returning None instead
    """
    try:
        if action == 'get':
            return model.objects.get(*args, **kwargs)
        else:
            return model.objects.filter(*args, **kwargs).order_by('-id')
    except model.DoesNotExist:
        return None

def get_orders(model, day, *args, **kwargs):
    """
    Service to handle the get and filter method calls on model objects based on day
    """

    if day == 'today':
        today = datetime.now().date()
        tomorrow = today + timedelta(1)
        today_start = datetime.combine(today, time())
        today_end = datetime.combine(tomorrow, time())
        return get_or_none(model, 'filter', *args, **kwargs, created_date__lte=today_end, created_date__gte=today_start)
        #return = get_or_none(Order, 'filter', stall=stall)
    else:
        return get_or_none(model, 'filter', *args, **kwargs)

def create_fish_in_items(fish):
    """
    Service to handle creation of new order line items, purchase order line items, and invoice line items during the adhoc creation of new fish
    """

    #Update orders with new fish
    order_set = Order.objects.filter(status__in=['New','Submitted', 'Purchasing', 'Invoiced'])
    for order in order_set:
        Order_Item.objects.create(order=order, fish=fish, status=order.status, quantity=0)

    #Update purchase orders with new fish
    purchase_order_set = order_set.values('purchase_order').distinct()
    for purchase_order in purchase_order_set:
        purchase_order_id = purchase_order['purchase_order']
        if purchase_order_id:
            purchase_order = Purchase_Order.objects.get(id=purchase_order_id)
            Purchase_Order_Item.objects.create(purchase_order=purchase_order, fish=fish)

    #Update invoices with new fish
    orders = Order.objects.filter(status__in=['Invoiced'])
    for order in orders:
        invoice = Invoice.objects.get(order=order)
        Invoice_Item.objects.create(invoice=invoice, fish=fish, total=0)
