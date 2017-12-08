from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from fish.models import Fish
from order.models import Order, Order_Item
from stall.models import Stall

from core.services import get_orders

from order.services import generate_stall_orders_list, generate_order_list_for_stall
from order.services import generate_order_list, generate_order_item_list
from order.services import create_order, save_order, post_order_submit_po, create_new_fish

# Create your views here.
@login_required(login_url="/login/")
def order_all(request, user_id, stall_id=None):
    if request.method == 'POST':
        template, context = post_order(request, user_id)
    else:
        if stall_id:
            template, context = get_order(request, user_id, True, stall_id=stall_id)
        else:
            stall_id = request.GET['stall_id'] if request.GET else None
            if stall_id == 'All':
                template, context = get_order(request, user_id, True, stall_id=None)
            else:
                template, context = get_order(request, user_id, True, stall_id=stall_id)

    #return render(request, 'order/order.html', context)
    return render(request, template, context)

@login_required(login_url="/login/")
def order_by_id(request, user_id, order_id=None):
    if request.method == 'POST':
        template, context = post_order(request, user_id, order_id)
    else:
        stall_id = request.GET['stall_id'] if request.GET else None
        if stall_id == 'All':
            template, context = get_order(request, user_id, False, order_id)
        else:
            template, context = get_order(request, user_id, False, order_id, stall_id=stall_id)

    #return render(request, 'order/order.html', context)
    return render(request, template, context)

@login_required(login_url="/login/")
def order_summary(request, user_id):
    template = 'order/order_summary.html'
    context = { 'purchase_order': generate_stall_orders_list(request, user_id, status__in=['New','Submitted', 'Purchasing','Invoiced','Closed', 'Cancelled']),
                'user_id': user_id,
                'summary': False
                }

    return render(request, template, context)

def get_order(request, user_id, isAll, order_id=None, stall_id=None):
    User = get_user_model()
    user = User.objects.get(id=user_id)
    isSuperuser = request.user.is_superuser

    if isSuperuser:
        if order_id:
            order = generate_order_list(id=order_id)[0]
            template = 'order/get_order.html'
            context = { 'stall': order['order'].stall,
                        'order': order,
                        'user_id': user_id}
        else:
            if stall_id:
                template = 'order/order_summary.html'
                context = { 'purchase_order': generate_order_list_for_stall(request, stall_id, status__in=['New','Submitted', 'Purchasing','Invoiced','Closed', 'Cancelled']),
                            'user_id': user_id,
                            'summary': True
                            }
            else:
                stall_orders = generate_stall_orders_list(request, user, status__in=['New','Submitted', 'Purchasing'])
                template = 'order/list_order_all.html'
                context = { 'stall_orders': stall_orders,
                            'fish': Fish.objects.all().order_by('sequence'),
                            'user_id': user_id}

    else:
        stall = Stall.objects.get(name=user)
        if isAll:
            orders = generate_order_list(stall=stall)
            template = 'order/list_order_by_stall.html'
            context = { 'stall': stall,
                        'orders': orders,
                        'user_id': user_id}

        else:
            order = generate_order_list(stall=stall, id=order_id)[0]
            if order:
                template = 'order/get_order.html'
                context = { 'stall': stall,
                            'order': order,
                            'user_id': user_id}
            else:
                template = 'order/new_order.html'
                context = { 'stall': stall,
                            'fish': Fish.objects.all().order_by('sequence'),
                            'user_id': user_id}

    return template, context

def post_order(request, user_id, order_id=None):
    User = get_user_model()
    user = User.objects.get(id=user_id)
    stall = Stall.objects.get(id=request.POST['stall_id']) if request.user.is_superuser else Stall.objects.get(name=user)
    save = False

    if request.POST['submit'] == 'Create Order':
        order = create_order(request, user)
        order_id = order.id

    elif request.POST['submit'] == 'Save':
        save_order(request, user)
        save = True

    elif request.POST['submit'] == 'Cancel':
        cancel_order(request, user)

    elif request.POST['submit'] == 'Submit for Purchasing':
        post_order_submit_po(request, user)
        save = True

    order = generate_order_list(stall=stall, id=order_id)[0]
    template = 'order/get_order.html'
    context = { 'stall': stall,
                'order': order,
                'save': save,
                'user_id': user_id}

    return template, context

@login_required(login_url="/login/")
def cancel_order(request, user=None):
    order_id = request.POST['order_id']
    user_id = user.id if user else request.POST['user_id']
    order = Order.objects.filter(id=order_id)
    order_item = Order_Item.objects.filter(order=order)
    order_item.update(status='Cancelled')
    order.update(status='Cancelled')

    template, context = get_order(request, user_id, True)
    return render(request, template, context)

@login_required(login_url="/login/")
def add_fish_from_order(request, user_id):
    fish_name = request.POST['fish_name']
    create_new_fish(fish_name)
    return render(request, 'fish/create_fish.html', {'status': 'success'})
