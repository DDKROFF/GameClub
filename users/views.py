from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import AuthenticationForm
from .forms import RegisterForm

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('main:home')   # замените на ваш URL главной
        # Если форма невалидна или пользователь не найден
        return render(request, 'index.html', {
            'login_form': form,
            'register_form': RegisterForm(),
            'active_tab': 'login',
            'show_modal': True,
        })
    else:
        # GET-запрос — просто показываем главную с закрытым модальным окном
        return render(request, 'index.html', {
            'login_form': AuthenticationForm(),
            'register_form': RegisterForm(),
            'active_tab': 'login',
            'show_modal': False,
        })

def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('main:home')
        # Ошибки регистрации
        return render(request, 'index.html', {
            'login_form': AuthenticationForm(),
            'register_form': form,
            'active_tab': 'register',
            'show_modal': True,
        })
    else:
        return render(request, 'index.html', {
            'login_form': AuthenticationForm(),
            'register_form': RegisterForm(),
            'active_tab': 'register',
            'show_modal': False,
        })