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
    """
    View to handle purchase order related user requests
    """

    if request.method == 'POST':
        template, context = post_purchase_order(request, user_id, fish_id)
    else:
        template, context = get_purchase_order(request, user_id)

    return render(request, template, context)

def get_purchase_order(request, user_id):
    """
    View to handle purchase order related user GET requests
    """

    User = get_user_model()
    user = User.objects.get(id=user_id)
    request_type = request.path.split('/')[3]
    purchase_order = get_orders(Order, day=None, status__in=['Purchasing']).values('purchase_order').distinct()

    if purchase_order:
        #Return purchase order summary report
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
                #Return purchase order report by stall for all stalls
                if stall_name == 'All':
                    template = 'purchasing/list_stall.html'
                    context = { 'purchase_order': generate_po_by_stall(purchase_order),
                                'user_id': user_id,
                                'generated': True
                                }
                #Return purchase order report by stall for specific stall
                else:
                    stall = Stall.objects.get(description=stall_name)
                    template = 'purchasing/get_stall.html'
                    context = { 'purchase_order': generate_po_by_stall(purchase_order, stall),
                                'user_id': user_id,
                                'generated': True
                                }
            #Return purchase order report by stall for all stalls
            else:
                template = 'purchasing/list_stall.html'
                context = { 'purchase_order': generate_po_by_stall(purchase_order),
                            'user_id': user_id,
                            'generated': True
                            }

        #Return purchase order report by fish
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

    #Show purchase order summary if there is no purchase orders. Reflect error message if there are no open orders.
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
    """
    View to handle purchase order related user POST requests
    """

    User = get_user_model()
    user = User.objects.get(id=user_id)

    #Call generate purchase order service and return corresponding template and context
    if request.POST['save'] == 'Generate Purchase Order':
        generate_purchase_order(request, user_id)
        template = 'purchasing/show_summary.html'
        context = { 'purchase_order': generate_stall_orders_list(request, user_id, status__in=['New','Submitted', 'Purchasing']),
                    'user_id': user_id,
                    'generated': True
                    }

    #Call generate invoice service and return corresponding template and context
    elif request.POST['save'] == 'Generate Invoice':
        #Code below is remove as generate invoice will be done by order instead of by bulk
        #purchase_order = get_orders(Order, day=None, status__in=['Purchasing']).values('purchase_order').distinct()
        order_id = request.POST['order_id']
        stall_id = request.POST['stall_id']
        generate_invoice(order_id=order_id)
        template = 'invoice/invoice.html'
        context = { 'invoices': generate_invoice_list(request, stall_id=stall_id),
                    'parent_template': 'invoice/list_invoice.html',
                    'user_id': user.id
                    }

    #Call save purchase order method and return corresponding template and context
    elif request.POST['save'] == 'Save':
        request_type = request.path.split('/')[3]
        purchase_order = get_orders(Order, day=None, status__in=['Purchasing']).values('purchase_order').distinct()
        template, context = save(request, user_id, request_type, purchase_order)

    #Call save purchase order method and return corresponding template and context. Request Type should be 'Add'
    elif request.POST['save'] == 'Add':
        request_type = request.path.split('/')[3]
        purchase_order = get_orders(Order, day=None, status__in=['Purchasing']).values('purchase_order').distinct()
        template, context = save(request, user_id, request_type, purchase_order)

    #Show purchase order summary if there is no purchase orders
    else:
        template = 'purchasing/show_summary.html'
        context = { 'purchase_order': generate_stall_orders_list(request, user_id, status__in=['New','Submitted', 'Purchasing']),
                    'user_id': user_id,
                    'generated': False
                    }

    return template, context

def save(request, user_id, request_type, purchase_order):
    """
    Method to handle the save purchase order requests
    """

    #Call save purchase order by fish service
    if request_type == 'fish':
        template = 'purchasing/list_fish.html'
        purchase_order_item_id = request.POST['purchase_order_item_id']
        weight = request.POST['weight']
        cost = request.POST['cost']
        save_purchased_fish(purchase_order, purchase_order_item_id, weight, cost)
        purchase_order = generate_po_by_fish(purchase_order)

    #Call save purchase order by stall service
    elif request_type == 'stall':
        stall_name = request.POST['stall_name'] if 'stall_name' in request.POST else None
        order_item_id = request.POST['order_item_id']
        weight = request.POST['weight']
        cost = request.POST['cost']
        save_stall(purchase_order, order_item_id, weight, cost)

        if stall_name:
            #Return template and context for purchase order for all stalls
            if stall_name == 'All':
                template = 'purchasing/list_stall.html'
                purchase_order = generate_po_by_stall(purchase_order)
            #Return template and context for purchase order for specific stalls
            else:
                stall = Stall.objects.get(description=stall_name)
                template = 'purchasing/get_stall.html'
                purchase_order = generate_po_by_stall(purchase_order, stall)
        #Return template and context for purchase order for all stalls
        else:
            template = 'purchasing/list_stall.html'
            purchase_order = generate_po_by_stall(purchase_order)

    #Call save purchase order using the purchasing report
    elif request_type == 'purchasing':
        purchase_order = get_orders(Order, day=None, status__in=['Purchasing']).values('purchase_order').distinct()
        fish_id  = request.path.split('/')[4]
        save_distributed_fish(request, purchase_order[0]['purchase_order'], fish_id)

        stall, purchase_order = generate_purchasing_list(purchase_order)
        template = 'purchasing/purchasing.html'
        context = {'status': 'success'}
        return template, context

    #Return purchase order summary by default
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
    """
    View to handle user request for the purchasing report.

    Returns the template and context for the report
    """

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
    """
    View to handle user request to print the purchasing report.

    Returns the print template and context
    """

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
    """
    View to handle the creation of new line items for open orders due to an adhoc creation of new fish
    """

    fish_name = request.POST['fish_name']
    create_new_fish(fish_name, purchase_order_id)
    return render(request, 'fish/create_fish.html', {'status': 'success'})
