from django.contrib import messages
from django.contrib.auth import login, authenticate, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm
from django.shortcuts import render

# Create your views here.
def home(request):
    return render(request, 'home.html')

@login_required(login_url="/login/")
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

@login_required(login_url="/login/")
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important!
            message = 'Your password was successfully updated!'
            return render(request, 'registration/change-password.html', {'form': form, 'message': message})
        else:
            return render(request, 'registration/change-password.html', {'form': form})
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'registration/change-password.html', {'form': form})
