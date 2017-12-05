from django.db.models import Max
from operator import itemgetter

from core.services import get_orders
from order.services import generate_order_item_list

from fish.models import Fish
from stall.models import Stall
from order.models import Order, Order_Item
from purchase_order.models import Purchase_Order, Purchase_Order_Item

from core.services import get_or_none
from order.services import generate_stall_orders_list

#Generate purchase order based on submitted orders
def generate_purchase_order(request, user_id):
    stall_orders = generate_stall_orders_list(request, user_id)
    purchase_order = Purchase_Order.objects.create()

    for stall in stall_orders:
        if stall['order_list']:
            for order in stall['order_list']:
                order_id = order['order'].id
                order_obj = Order.objects.filter(id=order_id, status='Submitted')

                for item in order['order_item']:
                    name = item['name'].split('(')[0].rstrip()
                    fish = Fish.objects.get(name=name)
                    quantity = item['value']
                    purchase_order_item = Purchase_Order_Item.objects.filter(purchase_order=purchase_order, fish=fish)

                    if purchase_order_item:
                        order_item = get_or_none(Order_Item, 'filter', order=order_obj, fish=fish)
                        if order_item:
                            if order_item[0].status == 'Submitted':
                                current_quantity = purchase_order_item[0].quantity
                                new_quantity = current_quantity + quantity
                                purchase_order_item.update(quantity=new_quantity)
                                order_item.update(status='Purchasing')
                    else:
                        order_item = get_or_none(Order_Item, 'filter', order=order_obj, fish=fish)
                        if order_item:
                            if order_item[0].status == 'Submitted':
                                purchase_order_item = Purchase_Order_Item.objects.create(purchase_order=purchase_order, fish=fish, quantity=quantity)
                                order_item.update(status='Purchasing')

                order_obj.update(purchase_order=purchase_order, status='Purchasing')

#Generate the fish report
def generate_po_by_fish(purchase_order):
    purchase_order_dict = dict()
    purchase_order_dict['purchase_order'] = Purchase_Order.objects.get(id=purchase_order)
    purchase_order_dict['order_item'] = generate_order_item_list(Purchase_Order_Item, purchase_order=purchase_order)
    return purchase_order_dict

#Generate the stall report
def generate_po_by_stall(purchase_order, stall=None):
    purchase_order_dict = dict()

    purchase_order_dict['purchase_order'] = Purchase_Order.objects.get(id=purchase_order)
    orders = Order.objects.filter(purchase_order=purchase_order, stall=stall, status__in=['Submitted', 'Purchasing']) if stall else Order.objects.filter(purchase_order=purchase_order, status__in=['Submitted', 'Purchasing'])
    order_stall_list = list()

    for order in orders:
        order_stall_dict = dict()
        order_stall_dict['stall'] = order.stall.description
        order_stall_dict['stall_id'] = order.stall.id
        order_stall_dict['order_item'] = generate_order_item_list(Order_Item, order=order)
        order_stall_list.append(order_stall_dict)

    purchase_order_dict['order'] = order_stall_list

    return purchase_order_dict

#Generate the purchasing report
def generate_purchasing_list(purchase_order):
    purchase_order_item = Purchase_Order_Item.objects.filter(purchase_order=purchase_order)
    stall = Stall.objects.all()

    fish_list = list()
    for poi in purchase_order_item:
        fish_dict = dict()
        fish_dict['id'] = poi.fish.id
        fish_dict['name'] = poi.fish.name
        fish_dict['chinese_name'] = poi.fish.chinese_name
        fish_dict['sequence'] = poi.fish.sequence
        values_list = list()
        quantity = 0
        weight = 0
        for s in stall:
            order = get_orders(Order, None, purchase_order=purchase_order, stall=s, status__in=['Purchasing'])
            values_dict = dict()
            values_dict['stall']  = s.id
            if order:
                order_item = Order_Item.objects.filter(order=order, fish=poi.fish)
                values_dict['order_item'] = order_item[0].id if order_item[0].id else None
                values_dict['quantity'] = order_item[0].quantity if order_item[0].quantity else 0
                values_dict['weight'] = order_item[0].weight if order_item[0].weight else 0
                values_dict['cost'] = order_item[0].cost if order_item[0].cost else 0
            else:
                values_dict['order_item'] = None
                values_dict['quantity'] = 0
                values_dict['weight'] = 0
                values_dict['cost'] = 0
            quantity = quantity + values_dict['quantity']
            weight = weight + values_dict['weight']
            values_list.append(values_dict)
        fish_dict['values'] = values_list
        total_dict = dict()
        total_dict['quantity'] = quantity
        total_dict['weight'] = weight
        total_dict['cost'] = poi.selling_cost if poi.selling_cost else 0
        fish_dict['total'] = total_dict

        fish_list.append(fish_dict)

        fish_list = sorted(fish_list, key=itemgetter('sequence'))

    return stall, fish_list

#Save purchasing details done from the purchasing report
def save_distributed_fish(request, purchase_order_id, fish_id):
    key = request.POST['key']
    value = request.POST['value'] if request.POST['value'] != '' else 0

    #Update cost of all orders with the fish
    if key == 'total_cost':
        fish = Fish.objects.get(id=fish_id)
        purchase_order = Purchase_Order.objects.get(id=purchase_order_id)
        orders = Order.objects.filter(purchase_order=purchase_order)
        for order in orders:
            order_item = Order_Item.objects.filter(order=order, fish=fish, quantity__gt=0)
            order_item.update(cost=value)
            #if order_item:
            #    update_status(order_item)
        purchase_order_item = Purchase_Order_Item.objects.filter(purchase_order=purchase_order, fish=fish)
        purchase_order_item.update(selling_cost=value)

    #Update the quantity, weight and cost of individual fish
    else:
        stall_id = request.POST['stall_id']
        order_item_id = request.POST['order_item_id'] if request.POST['order_item_id'] != 'None' else None
        #Update with existing order
        if order_item_id:
            order_item = Order_Item.objects.filter(id=order_item_id)

            if key == 'quantity':
                order_item.update(quantity=value)
            elif key == 'weight':
                order_item.update(weight=value)
            elif key == 'cost':
                order_item.update(cost=value)

        #Update without existing order and add to current purchase order
        else:
            purchase_order = Purchase_Order.objects.get(id=purchase_order_id)
            stall = Stall.objects.get(id=stall_id)
            order = Order.objects.create(stall=stall, status='Purchasing', purchase_order=purchase_order)
            fishes = Fish.objects.all()

            for fish in fishes:
                if str(fish.id) == fish_id:
                    if key == 'quantity':
                        Order_Item.objects.create(order=order, fish=fish, status= 'Purchasing', quantity=value)
                    elif key == 'weight':
                        Order_Item.objects.create(order=order, fish=fish, status= 'Purchasing', weight=value)
                    elif key == 'cost':
                        Order_Item.objects.create(order=order, fish=fish, status= 'Purchasing', cost=value)
                else:
                    Order_Item.objects.create(order=order, fish=fish, status= 'Purchasing', quantity=0)

#Save purchasing details done from the fish report
def save_purchased_fish(purchase_order, purchase_order_item_id, weight, cost):
    weight = 0 if weight == '' else weight
    cost = 0 if cost == '' else cost
    purchase_order_item = Purchase_Order_Item.objects.filter(id=purchase_order_item_id)
    purchase_order_item.update(weight=weight, buying_cost=cost)
    fish = purchase_order_item[0].fish

#Save purchasing details done from the stall report
def save_stall(purchase_order, order_item_id, weight, cost):
    weight = 0 if weight == '' else weight
    cost = 0 if cost == '' else cost
    order_item = Order_Item.objects.filter(id=order_item_id)
    order_item.update(weight=weight, cost=cost)

#Perform status update of the order_items on based on purchasing information
def update_status(order_item):
    if order_item[0].quantity <= order_item[0].weight:
        if  order_item[0].cost and order_item[0].cost != 0.0:
            order_item.update(status='Purchased')
    else:
        order_item.update(status='Purchasing')

    if  not order_item[0].cost and order_item[0].cost == 0.0:
        order_item.update(status='Purchasing')

    if order_item[0].quantity == 0:
        order_item.update(status='Purchased')
    check_order_item_completion(order_item[0].order)

#Check order completion based on status of order items
def check_order_item_completion(order):
    order_item = Order_Item.objects.filter(order=order)
    done = True

    for oi in order_item:
        if oi.status == 'Purchasing':
            done = False

    order_obj = Order.objects.filter(id=order.id)
    if done:
        order_obj.update(status='Purchased')
    else:
        order_obj.update(status='Purchasing')

#Save new fish
def create_new_fish(fish_name, purchase_order_id):
    sequence = Fish.objects.all().aggregate(Max('sequence'))['sequence__max'] + 1
    fish = Fish.objects.create(name=fish_name, sequence=sequence)
    purchase_order = Purchase_Order.objects.get(id=purchase_order_id)
    Purchase_Order_Item.objects.create(purchase_order=purchase_order, fish=fish)
    orders = Order.objects.filter(purchase_order=purchase_order)
    for order in orders:
        Order_Item.objects.create(order=order, fish=fish, status='Purchasing', quantity=0)
