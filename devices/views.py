from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from .models import Hall, Device, Computer, Console


class HallListView(ListView):
    model = Hall
    template_name = 'halls/hall_list.html'
    context_object_name = 'halls'
    paginate_by = 10
    ordering = ['name']

    def get_queryset(self):
        queryset = super().get_queryset()
        q = self.request.GET.get('q')
        if q:
            queryset = queryset.filter(name__icontains=q)
        return queryset


class HallDetailView(DetailView):
    model = Hall
    template_name = 'halls/hall_detail.html'
    context_object_name = 'hall'


class HallCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = Hall
    fields = ['name', 'description', 'max_capacity']
    template_name = 'halls/hall_form.html'
    success_url = reverse_lazy('hall_list')
    permission_required = 'halls.add_hall'


class HallUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = Hall
    fields = ['name', 'description', 'max_capacity']
    template_name = 'halls/hall_form.html'
    success_url = reverse_lazy('hall_list')
    permission_required = 'halls.change_hall'


class HallDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = Hall
    template_name = 'halls/hall_confirm_delete.html'
    success_url = reverse_lazy('hall_list')
    permission_required = 'halls.delete_hall'


class DeviceListView(ListView):
    model = Device
    template_name = 'devices/device_list.html'
    context_object_name = 'devices'
    paginate_by = 20

    def get_queryset(self):
        queryset = super().get_queryset().select_related('hall')
        device_type = self.request.GET.get('type')
        if device_type:
            queryset = queryset.filter(device_type=device_type)
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)
        hall_id = self.request.GET.get('hall')
        if hall_id:
            queryset = queryset.filter(hall_id=hall_id)
        q = self.request.GET.get('q')
        if q:
            queryset = queryset.filter(inventory_number__icontains=q)
        return queryset

class DeviceDetailView(DetailView):
    model = Device
    template_name = 'devices/device_detail.html'
    context_object_name = 'device'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        device = self.object
        if device.device_type == Device.DeviceType.COMPUTER:
            context['computer'] = getattr(device, 'computer_details', None)
        elif device.device_type == Device.DeviceType.CONSOLE:
            context['console'] = getattr(device, 'console_details', None)
        return context

class ComputerListView(ListView):
    model = Computer
    template_name = 'computers/computer_list.html'
    context_object_name = 'computers'
    paginate_by = 20
    queryset = Computer.objects.select_related('device__hall')

    def get_queryset(self):
        queryset = super().get_queryset()
        min_ram = self.request.GET.get('min_ram')
        if min_ram:
            queryset = queryset.filter(ram_gb__gte=min_ram)
        cpu = self.request.GET.get('cpu')
        if cpu:
            queryset = queryset.filter(cpu__icontains=cpu)
        return queryset

class ComputerDetailView(DetailView):
    model = Computer
    template_name = 'computers/computer_detail.html'
    context_object_name = 'computer'

class ConsoleListView(ListView):
    model = Console
    template_name = 'consoles/console_list.html'
    context_object_name = 'consoles'
    paginate_by = 20
    queryset = Console.objects.select_related('device__hall')

class ConsoleDetailView(DetailView):
    model = Console
    template_name = 'consoles/console_detail.html'
    context_object_name = 'console'

class ClubMapView(TemplateView):
    template_name = 'hallsMap.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Общая статистика
        context['halls_count'] = Hall.objects.count()
        context['devices_count'] = Device.objects.count()
        context['computers_count'] = Computer.objects.count()
        context['consoles_count'] = Console.objects.count()

        # Получаем залы с предзагрузкой устройств
        halls = Hall.objects.prefetch_related('devices').all()
        halls_data = []
        for hall in halls:
            devices = hall.devices.all()
            # Группируем устройства по ряду и колонке
            grid = {}
            for device in devices:
                if device.row is not None and device.column is not None:
                    grid[(device.row, device.column)] = device
            # Определяем максимальные индексы для сетки
            max_row = max([r for r, _ in grid.keys()], default=0)
            max_col = max([c for _, c in grid.keys()], default=0)
            # Создаём матрицу rows x cols
            matrix = []
            for r in range(1, max_row+1):
                row_cells = []
                for c in range(1, max_col+1):
                    device = grid.get((r, c))
                    if device:
                        cell_type = 'pc' if device.device_type == Device.DeviceType.COMPUTER else 'con'
                        info = f"{device.inventory_number} – {device.get_device_type_display()}"
                        row_cells.append({
                            'type': cell_type,
                            'info': info,
                            'device': device
                        })
                    else:
                        row_cells.append({'type': 'spacer', 'info': ''})
                matrix.append(row_cells)
            halls_data.append({
                'name': hall.name,
                'matrix': matrix,
                'rows': max_row,
                'cols': max_col,
            })
        context['halls'] = halls_data
        return context