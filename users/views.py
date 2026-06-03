from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from .forms import LoginForm, RegisterForm

def login_view(request):
    if request.user.is_authenticated:
        return redirect('main:home')   # или другая главная

    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            identity = form.cleaned_data['identity']
            password = form.cleaned_data['password']
            # Используем наш MultiFieldAuthBackend
            user = authenticate(request, identity=identity, password=password)
            if user is not None:
                login(request, user)
                next_url = request.GET.get('next', 'main:home')
                return redirect(next_url)
            else:
                messages.error(request, 'Неверный логин/email/телефон или пароль.')
        # Если форма невалидна или пользователь не найден – покажем ошибки
        return render(request, 'users/signin.html', {'form': form})
    else:
        form = LoginForm()
    return render(request, 'users/signin.html', {'form': form})

def register_view(request):
    if request.user.is_authenticated:
        return redirect('main:home')

    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Явно указываем бэкенд, который использовался бы для входа
            user.backend = 'users.backends.MultiFieldAuthBackend'
            login(request, user)
            messages.success(request, 'Регистрация прошла успешно! Добро пожаловать.')
            return redirect('main:home')
        return render(request, 'users/signup.html', {'form': form})
    else:
        form = RegisterForm()
    return render(request, 'users/signup.html', {'form': form})

def logout_view(request):
    logout(request)
    messages.info(request, 'Вы вышли из аккаунта.')
    return redirect('main:home')