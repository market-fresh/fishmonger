from django.db.models import Max

from core.services import get_orders, create_fish_in_items

from fish.models import Fish
from stall.models import Stall
from order.models import Order, Order_Item
from purchase_order.models import Purchase_Order, Purchase_Order_Item

#Order item list for a specified order
def generate_order_item_list(model, *args, **kwargs):
    """
    Service to handle the generation of order item list.

    Returns a list of order items
    """

    order_item = model.objects.filter(*args, **kwargs)
    order_item_list = list()

    for oi in order_item:
        order_item_dict = dict()
        order_item_dict['id'] = oi.id
        order_item_dict['name'] = oi.fish.name + ' (' + oi.fish.chinese_name + ')'
        #Fix sequencing of the fish
        order_item_dict['sequence'] = oi.fish.sequence
        order_item_dict['value'] =  oi.quantity
        order_item_dict['weight'] = oi.weight
        if model == Purchase_Order_Item:
            order_item_dict['buying_cost'] =  oi.buying_cost
            order_item_dict['selling_cost'] =  oi.selling_cost
        else:
            order_item_dict['cost'] =  oi.cost
        if model == Order_Item:
            order_item_dict['status'] = oi.status

        order_item_list.append(order_item_dict)

        #Fix sequencing of the fish here
    return sorted(order_item_list, key=lambda k: k['sequence'])

#Order list for a specified stll
def generate_order_list(day=None, *args, **kwargs):
    """
    Service to handle the generation of order list.

    Returns a list of orders
    """

    #Get the list of orders from the stall
    order_list = list()
    order = get_orders(Order, day, *args, **kwargs)

    #If the stall has an order
    if order:
        for o in order:
            order_dict = dict()
            order_dict['order'] = o
            #Get the list of order items for an order
            order_dict['order_item'] = generate_order_item_list(Order_Item, order=o)
            order_list.append(order_dict)

        return order_list

#Order list from specified stalls based on user id
def generate_stall_orders_list(request, user, *args, **kwargs):
    """
    Service to handle the generation of order list for a list of stall.

    Returns a list of orders for a list of stalls
    """

    stall_orders_list = list()
    stalls = Stall.objects.all() if request.user.is_superuser else Stall.objects.filter(name=user)

    for stall in stalls:
        stall_orders = dict()
        stall_orders['stall'] = stall
        stall_orders['order_list'] = generate_order_list(stall=stall, *args, **kwargs)
        stall_orders_list.append(stall_orders)

    return stall_orders_list

#Order list  based on user stall_id
def generate_order_list_for_stall(request, stall_id, *args, **kwargs):
    """
    Service to handle the generation of order list for a specific stall.

    Returns a list of orders for the stall
    """

    stall_orders_list = list()
    stall =  Stall.objects.get(id=stall_id)

    stall_orders = dict()
    stall_orders['stall'] = stall
    stall_orders['order_list'] = generate_order_list(stall=stall, *args, **kwargs)
    stall_orders_list.append(stall_orders)

    return stall_orders_list

def create_order(request, user):
    """
    Service to handle the creation of new order
    """

    stall_id = request.POST['stall_id']
    stall = Stall.objects.get(id=stall_id)
    order = Order.objects.create(stall=stall, status='New')
    fishes = Fish.objects.all().order_by('sequence')
    for fish in fishes:
        Order_Item.objects.create(order=order, fish=fish, status= 'New', quantity=0)
    return order

def save_order(request, user):
    """
    Service to handle the updating of an order
    """

    if 'order_item_id' in request.POST:
        order_item_id = request.POST['order_item_id']
        value = request.POST['value']
        order_item = Order_Item.objects.filter(id=order_item_id)
        order_item.update(quantity=value)
    return

def post_order_submit_po(request, user):
    """
    Service to handle the submission of an order for purchasing
    """

    order_id = request.POST['order_id']
    order = Order.objects.filter(id=order_id)
    order_item = Order_Item.objects.filter(order=order)
    order_item.update(status='Submitted')
    order.update(status='Submitted')
    return

def check_exists_order_list(orders_list):
    """
    Service to check if order exists from a list of orders.
    """

    for order in orders_list:
        if order['order_list']:
            return True
    return False

def create_new_fish(fish_name):
    """
    Service to handle the creation of new line items for open orders due to an adhoc creation of new fish
    """

    sequence = Fish.objects.all().aggregate(Max('sequence'))['sequence__max'] + 1
    fish = Fish.objects.create(name=fish_name, sequence=sequence)

    create_fish_in_items(fish)
