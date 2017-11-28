from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect

# Create your views here.
def home(request):
    return render(request, 'home.html')

def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            #user = authenticate(username=username, password=raw_password)
            #login(request, user)
            message = "%s has been saved." % (username,)
            #request.session['message'] = message
            return render(request, 'registration/signup.html', {'form': form, 'message': message})
    else:
        form = UserCreationForm()
    return render(request, 'registration/signup.html', {'form': form})
