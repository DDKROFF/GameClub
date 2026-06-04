from django.shortcuts import render
from .models import Tariff

def home(request):
    tariffs = Tariff.objects.filter(is_active=True)
    return render(request, 'includes/tariffs_block.html', {'tariffs': tariffs})