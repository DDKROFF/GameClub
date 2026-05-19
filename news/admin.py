from django.contrib import admin
from .models import News, NewsStats, Tag

class NewsStatsInline(admin.StackedInline):
    model = NewsStats
    can_delete = False

@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    list_display = ['title', 'publication_date', 'views_display']
    inlines = [NewsStatsInline]
    filter_horizontal = ['tags']

    def views_display(self, obj):
        return obj.stats.views if hasattr(obj, 'stats') else 0
    views_display.short_description = 'Просмотры'

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}
