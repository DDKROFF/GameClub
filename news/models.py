from django.db import models
from django.utils import timezone
from django.utils.text import slugify

class Tag(models.Model):
    name = models.CharField("Название", max_length=50, unique=True)
    slug = models.SlugField("Слаг", max_length=50, unique=True, blank=True)

    class Meta:
        verbose_name = "Тег"
        verbose_name_plural = "Теги"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class News(models.Model):
    title = models.CharField("Заголовок", max_length=255)
    excerpt = models.TextField("Анонс", blank=True)
    publication_date = models.DateTimeField("Дата публикации", default=timezone.now)
    tags = models.ManyToManyField(Tag, blank=True, verbose_name="Теги",
                                  related_name="news_items")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Новость"
        verbose_name_plural = "Новости"
        ordering = ['-publication_date']
        indexes = [
            models.Index(fields=['publication_date']),
        ]

    def __str__(self):
        return self.title


class NewsStats(models.Model):
    news = models.OneToOneField(
        News,
        on_delete=models.CASCADE,
        primary_key=True,
        related_name="stats"
    )
    views = models.PositiveIntegerField("Просмотры", default=0)
    likes = models.PositiveIntegerField("Лайки", default=0)
    dislikes = models.PositiveIntegerField("Дизлайки", default=0)

    class Meta:
        verbose_name = "Статистика новости"
        verbose_name_plural = "Статистика новостей"

    def __str__(self):
        return f"Статистика: {self.news.title}"