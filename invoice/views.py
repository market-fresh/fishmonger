from django.contrib.auth import get_user_model
from django.shortcuts import render

from order.services import generate_stall_orders_list, check_exists_order_list
from invoice.services import generate_invoice_list, generate_invoice_of_stall, check_exists_invoice_list
from invoice.services import save_invoice, close_invoice, calculate_total_cost

# Create your views here.
def invoice(request, user_id):
    User = get_user_model()
    user = User.objects.get(id=user_id)

    if request.method == 'POST':
        template, context = post_invoice(request, user)
    else:
        template, context = get_invoice(request, user)

    return render(request, template, context)

def get_invoice(request, user):
    stall_id = request.GET['stall_id'] if request.GET else None
    stall_id = None if stall_id == 'All' else stall_id
    invoices = generate_invoice_of_stall(request, user, stall_id) if stall_id else generate_invoice_list(request, user)

    if check_exists_invoice_list(invoices):
        template = 'invoice/invoice.html'
        context = { 'invoices': invoices,
                    'parent_template': 'invoice/list_invoice.html',
                    'user_id': user.id
                    }
    else:
        error = 'No invoices generated for this purchase order.'
        if user.is_superuser:
            template = 'purchasing/show_summary.html'
            orders_list = generate_stall_orders_list(request, user.id, status__in=['New','Submitted', 'Purchasing'])
            context = { 'purchase_order': orders_list,
                        'user_id': user.id,
                        'error': error,
                        'generated': check_exists_order_list(orders_list)
                        }
        else:
            template = 'invoice/invoice.html'
            context = { 'invoices': invoices,
                        'parent_template': 'invoice/list_invoice.html',
                        'user_id': user.id,
                        'error': error
                        }

    return template, context

def post_invoice(request, user):
    context = dict()
    invoice_id = request.POST['invoice_id']

    if request.POST['save'] == 'Save':
        save_invoice(request, invoice_id)

        template = 'invoice/invoice.html'
        context = { 'invoices': generate_invoice_list(request, user),
                    'parent_template': 'invoice/list_invoice.html',
                    'user_id': user.id
                    }

    elif request.POST['save'] == 'Print':
        stall_id = request.POST['stall_id']
        template = 'invoice/invoice.html'
        context = { 'invoices': generate_invoice_of_stall(request, user, stall_id),
                    'parent_template': 'invoice/print_invoice.html',
                    'user_id': user.id,
                    'print': True
                    }

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
