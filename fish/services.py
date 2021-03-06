from django.db.models import Max

from fish.forms import FishForm
from fish.models import Fish

from core.services import create_fish_in_items

def create_fish(request):
    """
    Service to handle the creation of new fish inventory
    """

    form = FishForm(request.POST)
    if form.is_valid():
        cd = form.save(commit=False)
        max_sequence = Fish.objects.all().aggregate(Max('sequence'))['sequence__max']
        cd.sequence = max_sequence + 1 if max_sequence else 1
        cd.save()

        create_fish_in_items(cd)

    fish = Fish.objects.all().order_by('sequence')

    return {'form': form, 'fish': fish, 'save': True}

def search_fish(request):
    """
    Service to handle search of fish in inventory
    """

    form = FishForm()
    if 'q' in request.GET:
        q = request.GET['q']
        fish = Fish.objects.filter(name__icontains=q).order_by('sequence')
    else:
        q = 'all'
        fish = Fish.objects.all().order_by('sequence')

    return {'form': form, 'fish': fish, 'query': q}

def up_fish(request):
    """
    Service to handle moving up of the sequence of the fish in the inventory
    """

    form = FishForm()
    fish_id = request.POST['id']
    sequence = int(request.POST['sequence'])
    fish1 = Fish.objects.get(id=fish_id, sequence=sequence)
    fish1.sequence = 0
    fish1.save()
    fish2 = Fish.objects.get(sequence=sequence - 1)
    fish2.sequence = fish2.sequence + 1
    fish2.save()
    fish1.sequence = sequence - 1
    fish1.save()

    return {'form': form, 'fish': Fish.objects.all().order_by('sequence')}

def down_fish(request):
    """
    Service to handle moving down of the sequence of the fish in the inventory
    """
    
    form = FishForm()
    fish_id = request.POST['id']
    sequence = int(request.POST['sequence'])
    fish1 = Fish.objects.get(id=fish_id, sequence=sequence)
    fish1.sequence = 0
    fish1.save()
    fish2 = Fish.objects.get(sequence=sequence + 1)
    fish2.sequence = fish2.sequence - 1
    fish2.save()
    fish1.sequence = sequence + 1
    fish1.save()

    return {'form': form, 'fish': Fish.objects.all().order_by('sequence')}
