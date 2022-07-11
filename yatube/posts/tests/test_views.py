from http import HTTPStatus

from django import forms
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.urls import reverse
from posts.forms import PostForm
from posts.models import Follow, Group, Post

from yatube.settings import POSTS_PER_PAGE

User = get_user_model()


class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.user_2 = User.objects.create_user(username='auth_2')

        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.group_2 = Group.objects.create(
            title='Тестовая группа 2',
            slug='test-slug-2',
            description='Тестовое описание 2',
        )

        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )

        cls.uploaded = SimpleUploadedFile(
            name='small.gif', content=small_gif, content_type='image/gif'
        )

        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
            group=cls.group,
            image=cls.uploaded,
        )

        cls.posts_count = Post.objects.count()

    def setUp(self) -> None:
        self.authorized_user_client = Client()
        self.authorized_user_client.force_login(self.user_2)

        self.authorized_author_client = Client()
        self.authorized_author_client.force_login(self.user)

    def _test_post_attributes(self, post):
        self.assertEqual(
            post.text,
            self.post.text,
            'Ошибка в формировании контекста атрибута "text" для "post".',
        )
        self.assertEqual(
            post.author,
            self.post.author,
            'Ошибка в формировании контекста атрибута "author" для "post".',
        )
        self.assertEqual(
            post.group,
            self.post.group,
            'Ошибка в формировании контекста атрибута "group" для "post".',
        )
        self.assertEqual(
            post.image,
            self.post.image,
            'Ошибка в формировании контекста атрибута "image" для "post".',
        )

    def test_pages_uses_correct_template_by_guest_client(self):
        """Страницы использует соответствующий шаблон."""

        templates_url_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse(
                'posts:profile', kwargs={'username': self.user.username}
            ): 'posts/profile.html',
            reverse(
                'posts:group_list', kwargs={'slug': self.group.slug}
            ): 'posts/group_list.html',
            reverse(
                'posts:post_detail', kwargs={'post_id': self.post.id}
            ): 'posts/post_detail.html',
        }

        for address, template in templates_url_names.items():
            with self.subTest(address=address):
                response = self.client.get(address)
                self.assertTemplateUsed(
                    response, template, 'URL-адрес использует неверный шаблон'
                )

    def test_pages_uses_correct_template_by_authorized_client(self):
        """Страницам авторизованных пользователей
        использует соответствующий шаблон.
        """
        templates_url_names = {
            reverse(
                'posts:post_edit', kwargs={'post_id': self.post.id}
            ): 'posts/create_post.html',
            reverse('posts:post_create'): 'posts/create_post.html',
        }

        for address, template in templates_url_names.items():
            with self.subTest(address=address):
                response = self.authorized_author_client.get(address)
                self.assertTemplateUsed(
                    response, template, 'URL-адрес использует неверный шаблон'
                )

    def test_index_page_show_correct_context(self):
        """Проверка формирования шаблона index с правильным контекстом."""
        response = self.client.get(reverse('posts:index'))

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertIn(self.post, response.context['page_obj'])

    def test_group_list_page_show_correct_context(self):
        """Проверка формирования шаблона страницы
        group_list с верным контекстом"""

        response = self.client.get(
            reverse('posts:group_list', kwargs={'slug': self.group.slug})
        )

        self._test_post_attributes(response.context.get('post'))

    def test_profile_page_show_correct_context(self):
        """Проверка формирования шаблона страницы
        profile с верным контекстом
        """

        response = self.client.get(
            reverse(
                'posts:profile',
                kwargs={'username': self.user.username},
            )
        )

        self._test_post_attributes(response.context['page_obj'][0])

    def test_post_detail_page_show_correct_context(self):
        """Проверка формирования шаблона страницы
        post_detail с верным контекстом
        """
        response = self.client.get(
            reverse(
                'posts:post_detail',
                kwargs={'post_id': self.post.pk},
            )
        )

        self._test_post_attributes(response.context.get('post'))

    def test_create_post_page_show_correct_context(self):
        """Проверка формирования шаблона страницы
        post_create с верным контекстом
        """

        response = self.authorized_user_client.get(
            reverse('posts:post_create')
        )

        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.models.ModelChoiceField,
        }

        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)

                self.assertIsInstance(form_field, expected)

        self.assertEqual(
            response.context.get('is_edit'), False, 'Передан неверный is_edit.'
        )
        self.assertIsInstance(
            response.context.get('form'),
            PostForm,
            'Форма не является классом PostForm.',
        )

    def test_edit_post_page_show_correct_context(self):
        """Проверка формирования шаблона страницы
        post_create с верным контекстом
        """

        response = self.authorized_author_client.get(
            reverse('posts:post_edit', kwargs={'post_id': self.post.pk})
        )

        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.models.ModelChoiceField,
        }

        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)

                self.assertIsInstance(form_field, expected)

        self.assertEqual(
            response.context.get('is_edit'), True, 'Передан неверный is_edit.'
        )
        self.assertIsInstance(
            response.context.get('form'),
            PostForm,
            'Форма не является классом PostForm.',
        )

    def test_index_page_show_correct_context_after_create_post(self):
        """Проверка формирования шаблона главной страницы
        после создания поста с верным контекстом
        """
        new_post = Post.objects.create(
            author=self.user,
            text='Тестовый пост нового пользователя',
            group=self.group,
        )

        response = self.client.get(
            reverse('posts:group_list', kwargs={'slug': self.group.slug})
        )

        self.assertIn(new_post, response.context['page_obj'])

    def test_group_list_page_show_correct_context_after_create_post(self):
        """Проверка формирования шаблона страницы group_list
        после создания поста с верным контекстом
        """
        new_post = Post.objects.create(
            author=self.user,
            text='Тестовый пост нового пользователя',
            group=self.group,
        )

        response = self.client.get(
            reverse('posts:group_list', kwargs={'slug': self.group.slug})
        )

        self.assertIn(new_post, response.context['page_obj'])

    def test_profile_page_show_correct_context_after_create_post(self):
        """Проверка формирования шаблона страницы profile
        после создания поста с верным контекстом
        """
        new_post = Post.objects.create(
            author=self.user,
            text='Тестовый пост нового пользователя',
            group=self.group,
        )

        response = self.client.get(
            reverse(
                'posts:profile',
                kwargs={'username': self.user.username},
            )
        )

        self.assertIn(new_post, response.context['page_obj'])

    def test_group_page_correct_context_after_create_post_for_another_group(
        self,
    ):
        """Проверка формирования шаблона страницы группы
        после создания поста с верным контекстом для другой группы
        """
        new_post = Post.objects.create(
            author=self.user,
            text='Тестовый пост нового пользователя',
            group=self.group,
        )

        response = self.client.get(
            reverse(
                'posts:group_list',
                kwargs={'slug': self.group_2.slug},
            )
        )

        self.assertNotIn(new_post, response.context['page_obj'])

    def test_comment_on_post_by_guest_user(self):
        """Проверка невозможности создания комментария к посту
        неавторизованным пользователем
        """
        response = self.client.get(
            reverse(
                'posts:add_comment',
                kwargs={'post_id': self.post.pk},
            )
        )

        self.assertRedirects(
            response,
            reverse('users:login')
            + '?next='
            + reverse(
                'posts:add_comment',
                kwargs={'post_id': self.post.pk},
            ),
            status_code=302,
            target_status_code=200,
            fetch_redirect_response=True,
        )

    def test_comment_on_post_by_authorized_user(self):
        """Проверка создания комментария к посту"""
        response = self.authorized_user_client.get(
            reverse(
                'posts:add_comment',
                kwargs={'post_id': self.post.pk},
            )
        )

        self.assertRedirects(
            response,
            reverse('posts:post_detail', kwargs={'post_id': self.post.pk}),
            status_code=302,
            target_status_code=200,
            fetch_redirect_response=True,
        )


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )

        cls.posts_count = int(POSTS_PER_PAGE * 1.7)

        cls.posts = [
            Post(author=cls.user, text=f'Пост {i}', group=cls.group)
            for i in range(cls.posts_count)
        ]
        Post.objects.bulk_create(cls.posts)

    def test_pages_contains_ten_records(self):
        """Проверка, что страница index имеет правильное число постов"""
        urls = (
            reverse('posts:index'),
            reverse(
                'posts:group_list',
                kwargs={'slug': self.group.slug},
            ),
            reverse(
                'posts:profile',
                kwargs={'username': self.user.username},
            ),
        )

        for address in urls:
            with self.subTest(address=address):
                response_page_1 = self.client.get(address)
                response_page_2 = self.client.get(address + '?page=2')

                self.assertEqual(
                    len(response_page_1.context['page_obj']),
                    POSTS_PER_PAGE,
                    f'Страница "{address}" имеет неверное количество страниц.',
                )
                self.assertEqual(
                    len(response_page_2.context['page_obj']),
                    self.posts_count - POSTS_PER_PAGE,
                    f'Страница "{address}" имеет неверное количество страниц.',
                )


class CacheTest(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )

    def test_cache_index(self):
        """Проверка работы кэширования главной страницы."""
        Post.objects.create(
            author=self.user,
            text='Тестовый пост',
            group=self.group,
        )
        pre_cache_response = self.client.get('posts:index')
        pre_cache_page = pre_cache_response.content.decode('utf-8')
        Post.objects.all().delete()
        post_cache_response = self.client.get('posts:index')
        post_cache_page = post_cache_response.content.decode('utf-8')

        self.assertHTMLEqual(
            pre_cache_page,
            post_cache_page,
            'Кэнирование страницы index работает неправильно.',
        )

        cache.clear()
        after_clear_cache_response = self.client.get('posts:index')

        self.assertNotEqual(
            after_clear_cache_response,
            post_cache_response,
            'Кэнирование страницы index работает неправильно.',
        )


class FollowViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='user', password='pass')
        self.user.save()
        self.client.force_login(self.user)

    def test_follow_by_authorized_client(self):
        """Авторизованный пользователь может подписываться
        на других пользователей.
        """
        following = User.objects.create(username='auth1')
        self.client.get(
            reverse(
                'posts:profile_follow', kwargs={'username': following.username}
            ),
            follow=True,
        )

        self.assertIs(
            Follow.objects.filter(user=self.user, author=following).exists(),
            True,
        )

    def test_unfollow_by_authorized_client(self):
        """Авторизованный пользователь может отписываться
        от других пользователей.
        """
        following = User.objects.create(username='auth2')
        self.client.get(
            reverse(
                'posts:profile_follow', kwargs={'username': following.username}
            ),
            follow=True,
        )
        self.client.get(
            reverse(
                'posts:profile_unfollow',
                kwargs={'username': following.username},
            ),
            follow=True,
        )

        self.assertIs(
            Follow.objects.filter(user=self.user, author=following).exists(),
            False,
        )

    def test_new_post_by_subscriber(self):
        """Новая запись пользователя появляется в ленте тех,
        кто на него подписан.
        """
        following = User.objects.create(username='auth1')
        Follow.objects.create(user=self.user, author=following)
        post = Post.objects.create(author=following, text='test')
        response = self.client.get(
            reverse('posts:follow_index'),
            follow=True,
        )

        self.assertIn(post, response.context['page_obj'].object_list)

    def test_new_post_by_no_subscriber(self):
        """Новая запись пользователя не появляется
        в ленте тех, кто не подписан.
        """
        following = User.objects.create(username='auth1')
        post = Post.objects.create(author=following, text='test')

        temp_user = User.objects.create_user(username='temp_user')
        self.client.force_login(temp_user)

        response = self.client.get(
            reverse('posts:follow_index'),
            follow=True,
        )

        self.assertNotIn(post, response.context['page_obj'].object_list)
