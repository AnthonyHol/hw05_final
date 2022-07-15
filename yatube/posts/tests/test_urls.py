from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase

from posts.models import Group, Post

User = get_user_model()


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.author = User.objects.create_user(username='auth')
        cls.user = User.objects.create_user(username='HasNoName')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(author=cls.author, text='Тестовая пост')

    def setUp(self) -> None:
        self.authorized_user_client = Client()
        self.authorized_user_client.force_login(self.user)

        self.authorized_author_client = Client()
        self.authorized_author_client.force_login(PostURLTests.author)

    def test_urls_uses_correct_template_by_guest_client(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names = {
            '/': 'posts/index.html',
            f'/profile/{self.author.username}/': 'posts/profile.html',
            f'/group/{self.group.slug}/': 'posts/group_list.html',
            f'/posts/{self.post.id}/': 'posts/post_detail.html',
        }

        for address, template in templates_url_names.items():
            with self.subTest(address=address):
                response = self.client.get(address)
                self.assertTemplateUsed(
                    response, template, 'URL-адрес использует неверный шаблон.'
                )

    def test_urls_uses_correct_template_by_authorized_client(self):
        """URL-адрес страниц авторизованных пользователей
        использует соответствующий шаблон."""
        templates_url_names = {
            f'/posts/{self.post.id}/edit/': 'posts/create_post.html',
            '/create/': 'posts/create_post.html',
            '/follow/': 'posts/follow.html',
        }

        for address, template in templates_url_names.items():
            with self.subTest(address=address):
                response = self.authorized_author_client.get(address)
                self.assertTemplateUsed(
                    response, template, 'URL-адрес использует неверный шаблон.'
                )

    def test_urls_exists_at_desired_location(self):
        """Страницы доступны неавторизированному пользователю."""
        urls = (
            '/',
            f'/profile/{self.author.username}/',
            f'/group/{self.group.slug}/',
            f'/posts/{self.post.id}/',
        )

        for address in urls:
            with self.subTest(address=address):
                response = self.client.get(address)
                self.assertEqual(
                    response.status_code,
                    HTTPStatus.OK,
                    'Запрос не вернул код 200.',
                )

    def test_url_is_available_to_the_author(self):
        """URL с редактированием поста доступен только автору поста."""
        url = f'/posts/{self.post.id}/edit/'

        response_from_guest = self.client.get(url)
        response_from_author = self.authorized_author_client.get(url)
        response_from_other_user = self.authorized_user_client.get(url)

        res_responses = (
            response_from_author.status_code == HTTPStatus.OK
            and response_from_guest.status_code == HTTPStatus.FOUND
            and response_from_other_user.status_code == HTTPStatus.FOUND
        )
        self.assertTrue(
            res_responses, 'Ошибка доступа к странице редактирования поста.'
        )

    def test_unexisting_url(self):
        """Несуществующая страница выдает ошибку 404."""
        response = self.client.get('/unexisting_page/')
        self.assertEqual(
            response.status_code,
            HTTPStatus.NOT_FOUND,
            'Запрос вернул невеверный код.',
        )
