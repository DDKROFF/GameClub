from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from .forms import RegisterForm, MultiFieldLoginForm


def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('signin')
    else:
        form = RegisterForm()

    return render(request, 'glob/register.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        form = MultiFieldLoginForm(data=request.POST)
        if form.is_valid():
            identity = form.cleaned_data.get('identity')
            password = form.cleaned_data.get('password')
            user = authenticate(request, identity=identity, password=password)
            if user is not None:
                login(request, user)
                return redirect('home')
    else:
        form = MultiFieldLoginForm()
    return render(request, 'glob/login.html', {'form': form})