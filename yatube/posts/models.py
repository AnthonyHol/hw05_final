from core.models import CreatedModel
from django.contrib.auth import get_user_model
from django.db import models

from .validators import validate_not_empty

User = get_user_model()


class Group(models.Model):
    title = models.CharField(
        verbose_name='Названние группы',
        max_length=200,
        help_text='Максимальная длина – 200 символов',
    )
    slug = models.SlugField(
        verbose_name='Уникальный адрес',
        max_length=200,
        unique=True,
        help_text='Уникальное значение. Максимальная длина – 200 символов',
    )
    description = models.TextField(verbose_name='Описание группы')

    def __str__(self):
        return self.title


class Post(CreatedModel):
    text = models.TextField(
        verbose_name='Текст поста',
        validators=[validate_not_empty],
        help_text='Введите текст поста',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name='Автор',
    )
    group = models.ForeignKey(
        Group,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='posts',
        verbose_name='Группа',
        help_text='Группа, к которой будет относиться пост',
    )
    image = models.ImageField('Картинка', upload_to='posts/', blank=True)

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'Пост'
        verbose_name_plural = 'Посты'

    def __str__(self):
        return self.text[:15]

    # def get_absolute_url(self):
    #     return reverse(
    #         'posts:post_detail',
    #         kwargs={
    #             'post_id': self.pk,
    #         },
    #     )


class Comment(CreatedModel):
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name='comments',
        verbose_name='Комментарии',
        help_text='Комментарии к посту',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Автор',
    )
    text = models.TextField(
        verbose_name='Текст комментария',
        validators=[validate_not_empty],
        help_text='Введите текст комментария',
    )

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'


class Follow(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='Автор',
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Подписчик',
    )
