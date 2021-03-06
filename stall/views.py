from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from stall.forms import StallForm
from stall.models import Stall

# Create your views here.
@login_required(login_url="/login/")
def stall(request):
    """
    View to handle stall related user requests
    """

    if request.method == 'POST':
        form = StallForm(request.POST)
        stall = Stall.objects.all()
        if form.is_valid():
            cd = form.save()
        return render(request, 'stall/stall.html', {'form': form, 'stall': stall, 'save': True})
    else:
        form = StallForm()
        if 'q' in request.GET:
            q = request.GET['q']
            stall = Stall.objects.filter(description__icontains=q)
        else:
            q = 'all'
            stall = Stall.objects.all()
        return render(request, 'stall/stall.html', {'form': form, 'stall': stall, 'query': q})

@login_required(login_url="/login/")
def update_stall(request, stall_id):
    """
    View to handle user request to update stall details
    """

    stall = Stall.objects.get(id=stall_id)
    stall.description = request.POST['description']
    stall.save()
    return render(request, 'stall/stall.html', {'status': 'success'})

@login_required(login_url="/login/")
def delete_stall(request, stall_id):
    """
    View to handle user request to delete stall
    """

    form = StallForm()
    stall = Stall.objects.get(id=stall_id)
    stall.delete()
    stall = Stall.objects.all()
    return render(request, 'stall/stall.html', {'form': form, 'stall': stall})

@login_required(login_url="/login/")
def create_stall(request):
    """
    View to handle user request to create stall
    """

    if request.method == 'POST':
        form = StallForm(request.POST)
        if form.is_valid():
            cd = form.save()
        return render(request, 'stall/create_stall.html', {'form': form, 'save': True})
    else:
        form = StallForm()
        return render(request, 'stall/create_stall.html', {'form': form})

@login_required(login_url="/login/")
def search_stall(request):
    """
    View to handle search stall
    """

    if request.method == 'GET':
        if 'q' in request.GET:
            q = request.GET['q']
            stall = Stall.objects.filter(description__icontains=q)
        else:
            q = 'all'
            stall = Stall.objects.all()
        return render(request, 'stall/search_stall.html', {'stall': stall, 'query': q})
    else:
        return render(request, 'stall/search_stall.html', {'error': True})
