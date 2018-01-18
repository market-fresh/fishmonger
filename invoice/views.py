from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from order.services import generate_stall_orders_list, check_exists_order_list
from invoice.services import generate_invoice_list, generate_invoice_of_stall, check_exists_invoice_list
from invoice.services import save_invoice, close_invoice, calculate_total_cost

# Create your views here.
@login_required(login_url="/login/")
def invoice(request, user_id):
    """
    View to handle invoice related user requests
    """

    User = get_user_model()
    user = User.objects.get(id=user_id)

    if request.method == 'POST':
        template, context = post_invoice(request, user)
    else:
        template, context = get_invoice(request, user)

    return render(request, template, context)

def get_invoice(request, user):
    """
    View to handle invoice related GET requests
    """

    stall_id = request.GET['stall_id'] if request.GET else None
    stall_id = None if stall_id == 'All' else stall_id
    invoices = generate_invoice_of_stall(request, user, stall_id) if stall_id else generate_invoice_list(request, user)

    #If there exists an open invoice, return list of invoices
    if check_exists_invoice_list(invoices):
        template = 'invoice/invoice.html'
        context = { 'invoices': invoices,
                    'parent_template': 'invoice/list_invoice.html',
                    'user_id': user.id
                    }
    else:
        error = 'No invoices generated for this purchase order.'
        #If there does not exist any open invoice and user is a superuser, return list of orders
        if user.is_superuser:
            template = 'purchasing/show_summary.html'
            orders_list = generate_stall_orders_list(request, user.id, status__in=['New','Submitted', 'Purchasing'])
            context = { 'purchase_order': orders_list,
                        'user_id': user.id,
                        'error': error,
                        'generated': check_exists_order_list(orders_list)
                        }
        #If there does not exist any open invoice and user is not a superuser, return error page in invoice page
        else:

            template = 'invoice/invoice.html'
            context = { 'invoices': invoices,
                        'parent_template': 'invoice/list_invoice.html',
                        'user_id': user.id,
                        'error': error
                        }

    return template, context

def post_invoice(request, user):
    """
    View to handle invoice related POST requests
    """

    context = dict()
    invoice_id = request.POST['invoice_id']

    #Call save invoice service and return corresponding template and context
    if request.POST['save'] == 'Save':
        save_invoice(request, invoice_id)

        template = 'invoice/invoice.html'
        context = { 'invoices': generate_invoice_list(request, user),
                    'parent_template': 'invoice/list_invoice.html',
                    'user_id': user.id
                    }

    #Return corresponding template and context
    elif request.POST['save'] == 'Print':
        stall_id = request.POST['stall_id']
        template = 'invoice/invoice.html'
        context = { 'invoices': generate_invoice_of_stall(request, user, stall_id),
                    'parent_template': 'invoice/print_invoice.html',
                    'user_id': user.id,
                    'print': True
                    }

    #Call close invoice service and return corresponding template and context
    elif request.POST['save'] == 'Close':
        invoices = generate_invoice_list(request, user)
        if check_exists_invoice_list(invoices):
            error = close_invoice(request, invoice_id)
            template = 'invoice/invoice.html'
            context = { 'invoices': generate_invoice_list(request, user),
                        'parent_template': 'invoice/list_invoice.html',
                        'user_id': user.id,
                        'error': error
                        }
        else:
            error = 'No invoices generated for this purchase order.'
            template = 'purchasing/show_summary.html'
            orders_list = generate_stall_orders_list(request, user.id, status__in=['New','Submitted', 'Purchasing'])
            context = { 'purchase_order': orders_list,
                        'user_id': user.id,
                        'error': error,
                        'generated': check_exists_order_list(orders_list)
                        }

    return template, context
