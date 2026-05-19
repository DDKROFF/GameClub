from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.shortcuts import get_object_or_404
from .models import News, NewsStats

def news_list(request):
    news_qs = News.objects.prefetch_related('tags').select_related('stats').all()
    return render(request, 'news/news_list.html', {'news_list': news_qs})



@require_POST
def news_like(request, news_id):
    news = get_object_or_404(News, pk=news_id)
    stats, _ = NewsStats.objects.get_or_create(news=news)

    session_key = f'voted_news_{news_id}'
    if session_key in request.session:
        return JsonResponse({'success': False, 'message': 'Вы уже голосовали'}, status=400)

    stats.likes += 1
    stats.save(update_fields=['likes'])
    request.session[session_key] = 'like'
    return JsonResponse({'success': True, 'likes': stats.likes, 'dislikes': stats.dislikes})

@require_POST
def news_dislike(request, news_id):
    news = get_object_or_404(News, pk=news_id)
    stats, _ = NewsStats.objects.get_or_create(news=news)

    session_key = f'voted_news_{news_id}'
    if session_key in request.session:
        return JsonResponse({'success': False, 'message': 'Вы уже голосовали'}, status=400)

    stats.dislikes += 1
    stats.save(update_fields=['dislikes'])
    request.session[session_key] = 'dislike'
    return JsonResponse({'success': True, 'likes': stats.likes, 'dislikes': stats.dislikes})

@require_POST
def news_view(request, news_id):
    news = get_object_or_404(News, pk=news_id)
    stats, _ = NewsStats.objects.get_or_create(news=news)

    session_key = f'viewed_news_{news_id}'
    if session_key in request.session:
        return JsonResponse({'success': False, 'message': 'Уже засчитан'}, status=400)

    stats.views += 1
    stats.save(update_fields=['views'])
    request.session[session_key] = True
    return JsonResponse({'success': True, 'views': stats.views})