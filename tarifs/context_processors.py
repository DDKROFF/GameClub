from .models import Tariff

def tariffs_context(request):
    return {'tariffs': Tariff.objects.filter(is_active=True)}