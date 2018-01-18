from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from fish.forms import FishForm
from fish.models import Fish

from fish.services import create_fish, search_fish, up_fish, down_fish

# Create your views here.
@login_required(login_url="/login/")
def fish(request):
    """
    View to handle fish related user requests
    """

    if request.method == 'POST':
        if request.POST['submit'] == 'Submit':
            context = create_fish(request)

        elif request.POST['submit'] == 'Up':
            context = up_fish(request)

        elif request.POST['submit'] == 'Down':
            context = down_fish(request)

    else:
        context = search_fish(request)

    return render(request, 'fish/fish.html', context)

@login_required(login_url="/login/")
def delete_fish(request, fish_id):
    """
    View to handle user request to delete fish from inventory
    """

    form = FishForm()
    sequence = int(request.POST['sequence'])
    fish = Fish.objects.filter(id=fish_id, sequence=sequence)
    fish.delete()

    fishes = Fish.objects.filter(sequence__gt=sequence)
    for fish in fishes:
        cd = Fish.objects.get(id=fish.id)
        cd.sequence = fish.sequence - 1
        cd.save()

    context = {'form': form, 'fish': Fish.objects.all().order_by('sequence')}
    return render(request, 'fish/fish.html', context)

@login_required(login_url="/login/")
def update_fish(request, fish_id):
    """
    View to handle user request to update fish details in inventory
    """

    form = FishForm(request.POST or None)
    if form.is_valid():
        fish = Fish.objects.get(id=fish_id)
        fish.name = request.POST['name']
        fish.chinese_name = request.POST['chinese_name']
        fish.save()
    return render(request, 'fish/fish.html', {'status': 'success'})
