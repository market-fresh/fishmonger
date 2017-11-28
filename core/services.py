from datetime import datetime, timedelta, time
from django.db import models

def get_or_none(model, action, *args, **kwargs):
    try:
        if action == 'get':
            return model.objects.get(*args, **kwargs).order_by('-id')
        else:
            return model.objects.filter(*args, **kwargs).order_by('-id')
    except model.DoesNotExist:
        return None

def get_orders(model, day, *args, **kwargs):

    if day == 'today':
        today = datetime.now().date()
        tomorrow = today + timedelta(1)
        today_start = datetime.combine(today, time())
        today_end = datetime.combine(tomorrow, time())
        return get_or_none(model, 'filter', *args, **kwargs, created_date__lte=today_end, created_date__gte=today_start)
        #return = get_or_none(Order, 'filter', stall=stall)
    else:
        return get_or_none(model, 'filter', *args, **kwargs)
