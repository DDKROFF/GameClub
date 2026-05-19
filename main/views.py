from django.views.generic import TemplateView
from devices.models import Hall, Device, Computer, Console
from news.models import News

class IndexView(TemplateView):
    template_name = 'index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['halls_count'] = Hall.objects.count()
        context['devices_count'] = Device.objects.count()
        context['computers_count'] = Computer.objects.count()
        context['consoles_count'] = Console.objects.count()
        context['news_list'] = News.objects.prefetch_related('tags') \
            .select_related('stats') \
            .all()
        return context

class HallView(TemplateView):
    template_name = 'devices/hallsMap.html'
