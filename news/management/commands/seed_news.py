# news/management/commands/seed_news.py

import random
from datetime import timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.utils.text import slugify
from faker import Faker

from news.models import Tag, News, NewsStats


# Переиспользуемые теги (теперь slug генерируется в коде)
TAGS_DATA = [
    {"name": "Нововведение", "slug": slugify("Нововведение", allow_unicode=True)},
    {"name": "Обновление ПО", "slug": slugify("Обновление ПО", allow_unicode=True)},
    {"name": "Технические работы", "slug": slugify("Технические работы", allow_unicode=True)},
    {"name": "Игровые новости", "slug": slugify("Игровые новости", allow_unicode=True)},
    {"name": "Извинения", "slug": slugify("Извинения", allow_unicode=True)},
    {"name": "Апгрейд", "slug": slugify("Апгрейд", allow_unicode=True)},
    {"name": "Анонс", "slug": slugify("Анонс", allow_unicode=True)},
    {"name": "Киберспорт", "slug": slugify("Киберспорт", allow_unicode=True)},
]

# Шаблоны новостей (без изменений)
NEWS_TEMPLATES = [
    {
        'title': 'Обновили изношенную периферию в зале №{}',
        'excerpt': 'Заменили мышки, клавиатуры и коврики – играть стало комфортнее.',
        'content': 'Друзья, в зале №{} полностью обновлена периферия: механические клавиатуры, геймерские мыши с оптическими сенсорами, новые коврики. Приятной игры!',
        'tags': ['Апгрейд', 'Обновление ПО']
    },
    {
        'title': 'Игра {} получила крупное обновление',
        'excerpt': '{} выпустили патч. Обновление скоро появится на всех ПК.',
        'content': 'Разработчики {} выпустили масштабное обновление. Мы уже тестируем стабильность и установим его в ближайшие часы. Просим прощения за возможное ожидание во время установки.',
        'tags': ['Игровые новости', 'Обновление ПО']
    },
    {
        'title': 'Технические работы: плановая профилактика {}',
        'excerpt': '{} числа клуб будет недоступен несколько часов.',
        'content': 'Уважаемые гости! {} числа с {} до {} будут проводиться технические работы. Возможны перерывы в доступе к компьютерам. Приносим извинения за неудобства.',
        'tags': ['Технические работы', 'Извинения']
    },
    {
        'title': 'Нововведение: запустили систему лояльности',
        'excerpt': 'Каждое посещение приносит бонусы!',
        'content': 'Теперь за каждое посещение вы получаете бонусные баллы. Их можно обменять на бесплатные часы игры, напитки или скидки. Подробности у администратора.',
        'tags': ['Нововведение', 'Анонс']
    },
    {
        'title': 'Обновляем видеокарты до {}',
        'excerpt': 'Готовьтесь к максимальным настройкам графики!',
        'content': 'Меняем видеокарты на новые {} во всех залах. Апгрейд завершим в течение недели. Просим прощение за небольшие перерывы в работе.',
        'tags': ['Апгрейд', 'Нововведение']
    },
    {
        'title': 'Извинения за долгое обновление игр',
        'excerpt': 'По техническим причинам процесс затянулся.',
        'content': 'Приносим искренние извинения за долгое ожидание обновления игр на компьютерах. Делаем всё возможное, чтобы завершить обновления в ближайшее время. Спасибо за терпение!',
        'tags': ['Извинения', 'Технические работы']
    },
    {
        'title': 'Киберспортивный турнир по {}',
        'excerpt': 'Призовой фонд – {} рублей. Регистрация открыта!',
        'content': 'Турнир по {} состоится {}. Призовой фонд – {} рублей. Участие бесплатное. Регистрация у администратора до {}. Ждём всех!',
        'tags': ['Киберспорт', 'Анонс']
    },
    {
        'title': 'Новинки в баре: вкусняшки и энергетики',
        'excerpt': 'Расширили ассортимент – приходите пробовать!',
        'content': 'В нашем баре появились новые снеки, сэндвичи и линейка энергетических напитков. Загляните оценить обновлённый ассортимент!',
        'tags': ['Нововведение']
    },
]

GAMES = ['CS2', 'Dota 2', 'Valorant', 'Apex Legends', 'PUBG', 'Fortnite', 'Overwatch 2']
HARDWARE = ['RTX 4070', 'RTX 4080', 'RX 7800 XT', 'Ryzen 7000 series']


class Command(BaseCommand):
    help = 'Заполняет базу данных тестовыми новостями для кибер-клуба'

    def add_arguments(self, parser):
        parser.add_argument(
            '--count',
            type=int,
            default=12,
            help='Количество создаваемых новостей (по умолчанию 12)'
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Очистить все существующие новости перед заполнением'
        )

    def handle(self, *args, **options):
        count = options['count']
        clear = options['clear']

        if clear:
            self.stdout.write('🗑️ Удаление существующих новостей и статистики...')
            NewsStats.objects.all().delete()
            News.objects.all().delete()
            self.stdout.write('✅ Готово.')

        # Создаём теги
        self.create_tags()

        # Генерируем новости
        self.generate_news(count)

    def create_tags(self):
        # Удаляем все теги с пустым slug (ошибочные записи от предыдущих запусков)
        deleted, _ = Tag.objects.filter(slug='').delete()
        if deleted:
            self.stdout.write(f'🧹 Удалено {deleted} проблемных тегов с пустым slug')

        created_count = 0
        for tag_info in TAGS_DATA:
            tag, created = Tag.objects.get_or_create(
                name=tag_info['name'],
                defaults={'slug': tag_info['slug']}
            )
            if created:
                created_count += 1
        if created_count:
            self.stdout.write(self.style.SUCCESS(f'📌 Создано {created_count} новых тегов'))
        else:
            self.stdout.write('📌 Теги уже существуют')

    def generate_news(self, num_news):
        fake = Faker('ru_RU')
        tag_cache = {tag.name: tag for tag in Tag.objects.all()}
        created_titles = []

        for i in range(num_news):
            template = random.choice(NEWS_TEMPLATES)
            title, excerpt, content = self.render_template(template, fake)

            pub_date = timezone.now() - timedelta(days=random.randint(0, 30), hours=random.randint(0, 23))

            news = News.objects.create(
                title=title,
                excerpt=excerpt,
                publication_date=pub_date
            )
            if hasattr(news, 'content'):
                news.content = content
                news.save(update_fields=['content'])

            for tag_name in template['tags']:
                if tag_name in tag_cache:
                    news.tags.add(tag_cache[tag_name])

            NewsStats.objects.create(
                news=news,
                views=random.randint(0, 5000),
                likes=random.randint(0, 300),
                dislikes=random.randint(0, 50)
            )

            created_titles.append(title)

            if (i + 1) % 5 == 0:
                self.stdout.write(f'📰 Создано {i + 1} из {num_news} новостей...')

        self.stdout.write(self.style.SUCCESS(f'\n✅ Успешно создано {len(created_titles)} новостей:'))
        for t in created_titles[:5]:
            self.stdout.write(f'  • {t}')
        if len(created_titles) > 5:
            self.stdout.write(f'  • ... и {len(created_titles) - 5} других')

    def render_template(self, template, fake):
        title_tpl = template['title']
        excerpt_tpl = template['excerpt']
        content_tpl = template['content']

        if 'зале №{}' in title_tpl:
            room = random.randint(1, 5)
            return title_tpl.format(room), excerpt_tpl, content_tpl.format(room)

        if 'игра {}' in title_tpl or 'игру {}' in title_tpl:
            game = random.choice(GAMES)
            return title_tpl.format(game), excerpt_tpl.format(game), content_tpl.format(game)

        if 'видеокарты до {}' in title_tpl:
            hw = random.choice(HARDWARE)
            return title_tpl.format(hw), excerpt_tpl, content_tpl.format(hw)

        if 'плановая профилактика {}' in title_tpl:
            day = random.randint(5, 25)
            start_h = random.randint(8, 12)
            end_h = start_h + random.randint(2, 4)
            date_str = f'{day}.{random.randint(1,12)}'
            return (title_tpl.format(date_str),
                    excerpt_tpl.format(day),
                    content_tpl.format(day, start_h, end_h))

        if 'турнир по {}' in title_tpl:
            game = random.choice(GAMES)
            prize = random.choice([5000, 10000, 15000, 25000])
            date = fake.date_between(start_date='+1d', end_date='+30d')
            reg_deadline = date - timedelta(days=random.randint(1, 3))
            return (title_tpl.format(game),
                    excerpt_tpl.format(prize),
                    content_tpl.format(game, date.strftime('%d.%m.%Y'), prize, reg_deadline.strftime('%d.%m.%Y')))

        return title_tpl, excerpt_tpl, content_tpl