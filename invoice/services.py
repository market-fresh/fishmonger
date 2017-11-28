from django.db.models import Sum, F

from core.services import get_orders

from invoice.models import Invoice, Invoice_Item
from order.models import Order, Order_Item
from stall.models import Stall

def generate_invoice_item_list(invoice):
    invoice_item = Invoice_Item.objects.filter(invoice=invoice)
    invoice_item_list = list()

    for item in invoice_item:
        item_dict = dict()
        item_dict['id'] = item.id
        item_dict['name'] = item.fish.name + ' (' + item.fish.chinese_name + ')'
        item_dict['weight'] =  item.weight
        item_dict['cost'] =  item.cost
        item_dict['total'] =  item.total
        invoice_item_list.append(item_dict)

    return invoice_item_list


def generate_invoice_list(request, user=None, stall_id=None):
    stall_invoice_list = list()
    if stall_id:
        stalls = Stall.objects.filter(id=stall_id)
    else:
        if user:
            stalls = Stall.objects.filter(name=user)
            if user.is_superuser:
                stalls = Stall.objects.all()
        else:
            stalls = Stall.objects.all()

    for stall in stalls:
        stall_invoice = dict()
        stall_invoice['stall'] = stall
        order = get_orders(Order, day=None, stall=stall, status='Invoiced')
        invoice = Invoice.objects.filter(stall=stall, order=order)
        stall_invoice['status'] = order[0].status if order else None
        stall_invoice['invoice'] = invoice[0] if invoice else None
        stall_invoice['invoice_item'] = generate_invoice_item_list(invoice=invoice)
        stall_invoice_list.append(stall_invoice)

    return stall_invoice_list

def generate_invoice_of_stall(request, user, stall_id):
    stall_invoice_list = list()
    stalls = Stall.objects.filter(id=stall_id)

    for stall in stalls:
        stall_invoice = dict()
        stall_invoice['stall'] = stall
        order = get_orders(Order, day=None, stall=stall, status='Invoiced')
        invoice = Invoice.objects.filter(stall=stall, order=order)
        stall_invoice['status'] = order[0].status if order else None
        stall_invoice['invoice'] = invoice[0] if invoice else None
        stall_invoice['invoice_item'] = generate_invoice_item_list(invoice=invoice)
        stall_invoice_list.append(stall_invoice)

    return stall_invoice_list

def generate_invoice(order_id=None, purchase_order=None):
    order_list = Order.objects.filter(id=order_id) if order_id else Order.objects.filter(purchase_order=purchase_order)
    for order in order_list:
        if order.status == 'Purchasing':
            total_cost = calculate_total_cost(Order, order)
            invoice = Invoice.objects.create(stall=order.stall, total_cost=total_cost, order=order)
            order_obj = Order.objects.filter(id=order.id)
            order_obj.update(status='Invoiced')
            order_item = Order_Item.objects.filter(order=order_obj)
            order_item.update(status='Invoiced')
            generate_invoice_items(order, invoice)

def calculate_total_cost(model, item):
    if model == Order:
        total_cost = Order_Item.objects.filter(order=item).aggregate(total=Sum(F('weight') * F('cost')))['total']
    elif model == Invoice:
        total_cost = Invoice_Item.objects.filter(invoice=item).aggregate(total=Sum(F('weight') * F('cost')))['total']
    return total_cost

def generate_invoice_items(order, invoice):
    order_item = Order_Item.objects.filter(order=order)
    for oi in order_item:
        Invoice_Item.objects.create(invoice=invoice,
                                    fish=oi.fish,
                                    weight=oi.weight,
                                    cost=oi.cost,
                                    total=oi.weight*oi.cost)

def save_invoice(request, invoice_id):
    if request.POST['key'] == 'total':
        ice = request.POST['ice'] if request.POST['ice'] else None
        cash_float = request.POST['cash_float'] if request.POST['cash_float'] else None
        sales = request.POST['sales'] if request.POST['sales'] else None
        invoice = Invoice.objects.filter(id=invoice_id)
        invoice.update(ice=ice, cash_float=cash_float, sales=sales)

    elif request.POST['key'] == 'item':
        weight = float(request.POST['weight']) if request.POST['weight'] else 0
        cost = float(request.POST['cost']) if request.POST['cost'] else 0
        invoice_item_id = request.POST['invoice_item_id']
        invoice_item = Invoice_Item.objects.filter(id=invoice_item_id)
        invoice_item.update(weight=weight,cost=cost,total=weight*cost)
        invoice = Invoice.objects.filter(id=invoice_id)
        total_cost = calculate_total_cost(Invoice, invoice)
        invoice.update(total_cost=total_cost)


def close_invoice(request, invoice_id):
    ice = request.POST['ice_'+invoice_id] if request.POST['ice_'+invoice_id] else None
    cash_float = request.POST['cash_float_'+invoice_id] if request.POST['cash_float_'+invoice_id] else None
    sales = request.POST['sales_'+invoice_id] if request.POST['sales_'+invoice_id] else None

    if ice and cash_float and sales:
        invoice = Invoice.objects.get(id=invoice_id)
        #save_invoice(request, invoice_id)
        invoice = Invoice.objects.filter(id=invoice_id)
        invoice.update(ice=ice, cash_float=cash_float, sales=sales)
        order = Order.objects.filter(invoice=invoice)
        order.update(status='Closed')
        order_item = Order_Item.objects.filter(order=order)
        order_item.update(status='Closed')
        return None

    else:
        return 'Ice, Float, or Sales is missing'

def check_exists_invoice_list(invoices):
    for invoice in invoices:
        if invoice['status']:
            return True
    return False
