from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from fish.forms import FishForm

from order.models import Order
from stall.models import Stall

from core.services import get_orders
from invoice.services import generate_invoice, generate_invoice_list
from order.services import generate_stall_orders_list, check_exists_order_list
from purchase_order.services import generate_purchase_order
from purchase_order.services import generate_po_by_stall, generate_po_by_fish, generate_purchasing_list
from purchase_order.services import save_stall, save_purchased_fish, save_distributed_fish, create_new_fish

# Create your views here.
@login_required(login_url="/login/")
def purchasing(request, user_id, fish_id=None):
    if request.method == 'POST':
        template, context = post_purchase_order(request, user_id, fish_id)
    else:
        template, context = get_purchase_order(request, user_id)

    return render(request, template, context)

def get_purchase_order(request, user_id):
    User = get_user_model()
    user = User.objects.get(id=user_id)
    request_type = request.path.split('/')[3]
    purchase_order = get_orders(Order, day=None, status__in=['Purchasing']).values('purchase_order').distinct()

    if purchase_order:
        if request_type == 'summary':
            orders_list = generate_stall_orders_list(request, user_id, status__in=['New','Submitted', 'Purchasing'])
            error = None if check_exists_order_list(orders_list) else 'No orders have been created.'
            template = 'purchasing/show_summary.html'
            context = { 'purchase_order': orders_list,
                    'purchase_order_id': purchase_order[0]['purchase_order'],
                    'user_id': user_id,
                    'generated': True,
                    'error': error
                    }

        elif request_type == 'stall':
            stall_name = request.GET['stall_name'] if request.GET else None

            if stall_name:
                if stall_name == 'All':
                    template = 'purchasing/list_stall.html'
                    context = { 'purchase_order': generate_po_by_stall(purchase_order),
                                'user_id': user_id,
                                'generated': True
                                }
                else:
                    stall = Stall.objects.get(description=stall_name)
                    template = 'purchasing/get_stall.html'
                    context = { 'purchase_order': generate_po_by_stall(purchase_order, stall),
                                'user_id': user_id,
                                'generated': True
                                }
            else:
                template = 'purchasing/list_stall.html'
                context = { 'purchase_order': generate_po_by_stall(purchase_order),
                            'user_id': user_id,
                            'generated': True
                            }

        elif request_type == 'fish':
            template = 'purchasing/list_fish.html'
            context = { 'purchase_order': generate_po_by_fish(purchase_order),
                        'user_id': user_id,
                        'generated': True
                        }

        elif request_type == 'add':
            template = 'purchasing/list_fish.html'
            context = { 'purchase_order': generate_po_by_fish(purchase_order),
                        'user_id': user_id,
                        'generated': True
                        }

    else:
        orders_list = generate_stall_orders_list(request, user_id, status__in=['New','Submitted', 'Purchasing'])
        error = None if check_exists_order_list(orders_list) else 'No orders have been created.'
        template = 'purchasing/show_summary.html'
        context = { 'purchase_order': orders_list,
                'user_id': user_id,
                'generated': False,
                'error': error
                }

    return template, context

def post_purchase_order(request, user_id, fish_id=None):
    User = get_user_model()
    user = User.objects.get(id=user_id)

    if request.POST['save'] == 'Generate Purchase Order':
        generate_purchase_order(request, user_id)
        template = 'purchasing/show_summary.html'
        context = { 'purchase_order': generate_stall_orders_list(request, user_id, status__in=['New','Submitted', 'Purchasing']),
                    'user_id': user_id,
                    'generated': True
                    }

    elif request.POST['save'] == 'Generate Invoice':
        #purchase_order = get_orders(Order, day=None, status__in=['Purchasing']).values('purchase_order').distinct()
        order_id = request.POST['order_id']
        stall_id = request.POST['stall_id']
        generate_invoice(order_id=order_id)
        template = 'invoice/invoice.html'
        context = { 'invoices': generate_invoice_list(request, stall_id=stall_id),
                    'parent_template': 'invoice/list_invoice.html',
                    'user_id': user.id
                    }

    elif request.POST['save'] == 'Save':
        request_type = request.path.split('/')[3]
        purchase_order = get_orders(Order, day=None, status__in=['Purchasing']).values('purchase_order').distinct()
        template, context = save(request, user_id, request_type, purchase_order)

    elif request.POST['save'] == 'Add':
        request_type = request.path.split('/')[3]
        purchase_order = get_orders(Order, day=None, status__in=['Purchasing']).values('purchase_order').distinct()
        template, context = save(request, user_id, request_type, purchase_order)

    else:
        template = 'purchasing/show_summary.html'
        context = { 'purchase_order': generate_stall_orders_list(request, user_id, status__in=['New','Submitted', 'Purchasing']),
                    'user_id': user_id,
                    'generated': False
                    }

    return template, context

def save(request, user_id, request_type, purchase_order):

    if request_type == 'fish':
        template = 'purchasing/list_fish.html'
        purchase_order_item_id = request.POST['purchase_order_item_id']
        weight = request.POST['weight']
        cost = request.POST['cost']
        save_purchased_fish(purchase_order, purchase_order_item_id, weight, cost)
        purchase_order = generate_po_by_fish(purchase_order)

    elif request_type == 'stall':
        stall_name = request.POST['stall_name'] if 'stall_name' in request.POST else None
        order_item_id = request.POST['order_item_id']
        weight = request.POST['weight']
        cost = request.POST['cost']
        save_stall(purchase_order, order_item_id, weight, cost)

        if stall_name:
            if stall_name == 'All':
                template = 'purchasing/list_stall.html'
                purchase_order = generate_po_by_stall(purchase_order)
            else:
                stall = Stall.objects.get(description=stall_name)
                template = 'purchasing/get_stall.html'
                purchase_order = generate_po_by_stall(purchase_order, stall)
        else:
            template = 'purchasing/list_stall.html'
            purchase_order = generate_po_by_stall(purchase_order)

    elif request_type == 'purchasing':
        purchase_order = get_orders(Order, day=None, status__in=['Purchasing']).values('purchase_order').distinct()
        fish_id  = request.path.split('/')[4]
        save_distributed_fish(request, purchase_order[0]['purchase_order'], fish_id)

        stall, purchase_order = generate_purchasing_list(purchase_order)
        template = 'purchasing/purchasing.html'
        context = {'status': 'success'}
        return template, context

    else:
        template = 'purchasing/summary.html'
        purchase_order = generate_stall_orders_list(request, user_id, 'today')

    context = { 'purchase_order': purchase_order,
                'user_id': user_id,
                'generated': True
                }
    return template, context

@login_required(login_url="/login/")
def purchasing_report(request, user_id):
    User = get_user_model()
    user = User.objects.get(id=user_id)
    purchase_order = get_orders(Order, day=None, status__in=['Purchasing']).values('purchase_order').distinct()
    purchase_order_id = purchase_order[0]['purchase_order']
    stall, purchase_order = generate_purchasing_list(purchase_order)

    template = 'purchasing/purchasing.html'
    context = { 'purchase_order': purchase_order,
                'purchase_order_id': purchase_order_id,
                'stall' : stall,
                'user_id': user_id,
                'generated': 'True'
                }

    return render(request, template, context)

@login_required(login_url="/login/")
def print_purchasing_report(request, user_id):
    User = get_user_model()
    user = User.objects.get(id=user_id)
    purchase_order = get_orders(Order, day=None, status__in=['Purchasing']).values('purchase_order').distinct()
    purchase_order_id = purchase_order[0]['purchase_order']
    stall, purchase_order = generate_purchasing_list(purchase_order)

    template = 'purchasing/print_purchasing.html'
    context = { 'purchase_order': purchase_order,
                'purchase_order_id': purchase_order_id,
                'stall' : stall,
                'user_id': user_id,
                'generated': 'True'
                }

    return render(request, template, context)

@login_required(login_url="/login/")
def add_fish_from_po(request, user_id, purchase_order_id):
    fish_name = request.POST['fish_name']
    create_new_fish(fish_name, purchase_order_id)
    return render(request, 'fish/create_fish.html', {'status': 'success'})
