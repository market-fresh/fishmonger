"""fishmongerapi URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from django.contrib.auth import views as auth_views

from core.views import home, signup, change_password
from fish.views import fish, delete_fish, update_fish
from stall.views import stall, delete_stall, update_stall
from order.views import order_all, order_by_id, order_summary, cancel_order, add_fish_from_order
from purchase_order.views import purchasing, purchasing_report, print_purchasing_report, add_fish_from_po
from invoice.views import invoice

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^login/$', auth_views.login, name='login'),
    url(r'^logout/$', auth_views.logout, {'next_page': '/home/'}, name='logout'),
    url(r'^change_password/$', change_password, name='change_password'),
    url(r'^password_reset/$', auth_views.password_reset, name='password_reset'),
    url(r'^password_reset/done/$', auth_views.logout, {'next_page': '/home/'}, name='password_reset_done'),
    url(r'^signup/$', signup, name='signup'),

    url(r'^s$', home),
    url(r'^home/$', home),
    url(r'^fish/$', fish),
    url(r'^fish/delete/(?P<fish_id>\d+)/$', delete_fish),
    url(r'^fish/update/(?P<fish_id>\d+)/$', update_fish),
    url(r'^search_fish/$', fish),
    url(r'^stall/$', stall),
    url(r'^stall/delete/(?P<stall_id>\d+)/$', delete_stall),
    url(r'^stall/(?P<stall_id>\d+)/$', update_stall),
    url(r'^search_stall/$', stall),

    url(r'^order/(?P<user_id>\d+)/$', order_all),
    url(r'^order/(?P<user_id>\d+)/stall/$', order_by_id),
    url(r'^order/(?P<user_id>\d+)/stall/(?P<stall_id>\d+)/$', order_all),
    url(r'^order/(?P<user_id>\d+)/summary/stall/$', order_all),
    url(r'^order/(?P<user_id>\d+)/summary/$', order_summary),
    url(r'^order/cancel/$', cancel_order),
    url(r'^order/(?P<user_id>\d+)/order/(?P<order_id>\d+)/$', order_by_id),
    url(r'^order/(?P<user_id>\d+)/add_fish/$', add_fish_from_order),

    url(r'^purchasing/(?P<user_id>\d+)/summary/$', purchasing),
    url(r'^purchasing/(?P<user_id>\d+)/fish/$', purchasing),
    url(r'^purchasing/(?P<user_id>\d+)/stall/$', purchasing),
    url(r'^purchasing/(?P<user_id>\d+)/purchasing/$', purchasing_report),
    url(r'^purchasing/(?P<user_id>\d+)/purchasing/(?P<fish_id>\d+)/$', purchasing),
    url(r'^purchasing/(?P<user_id>\d+)/add_fish/(?P<purchase_order_id>\d+)/$', add_fish_from_po),
    url(r'^purchasing/(?P<user_id>\d+)/print_purchasing/$', print_purchasing_report),

    url(r'^invoice/(?P<user_id>\d+)/$', invoice),
    url(r'^invoice/(?P<user_id>\d+)/stall/$', invoice),
]
