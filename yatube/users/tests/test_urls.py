from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.test import Client, TestCase
from django.utils.http import urlsafe_base64_encode

User = get_user_model()


class UsersURLTests(TestCase):
    def setUp(self) -> None:
        self.guest_client = Client()
        self.user = User.objects.create_user(
            username='TestUser', password='df3vfGFsf1', email='efd@gmail.com'
        )
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_urls_uses_correct_template_by_guest_client(self):
        """URL-адрес использует соответствующий шаблон."""
        uid64 = urlsafe_base64_encode(str(self.user.pk).encode())

        templates_url_names = {
            '/auth/password_reset/': 'users/password_reset_form.html',
            '/auth/password_reset/done/': 'users/password_reset_done.html',
            f'/auth/reset/{uid64}/set-password/': (
                'users/password_reset_confirm.html'
            ),
            '/auth/reset/done/': 'users/password_reset_complete.html',
            '/auth/signup/': 'users/signup.html',
            '/auth/login/': 'users/login.html',
        }

        for address, template in templates_url_names.items():
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertTemplateUsed(
                    response, template, 'URL-адрес использует неверный шаблон'
                )

    def test_urls_uses_correct_template_by_authorized_client(self):
        """URL-адрес использует соответствующий шаблон
        для страниц, требующих авторизацию."""

        templates_url_names = {
            '/auth/password_change/': 'users/password_change_form.html',
            '/auth/password_change/done/': 'users/password_change_done.html',
            '/auth/logout/': 'users/logged_out.html',
        }

        for address, template in templates_url_names.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(
                    response, template, 'URL-адрес использует неверный шаблон'
                )

    def test_urls_exists_at_desired_location(self):
        """Страницы доступны неавторизированному пользователю."""
        uid64 = urlsafe_base64_encode(str(self.user.pk).encode())

        urls = (
            '/auth/password_reset/',
            '/auth/password_reset/done/',
            f'/auth/reset/{uid64}/set-password/',
            '/auth/reset/done/',
            '/auth/signup/',
            '/auth/login/',
            '/auth/logout/',
        )

        for address in urls:
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_urls_redirect_guest_client(self):
        """URL для смена пароля перенаправляют
        неавторизованного пользователя."""

        urls = (
            '/auth/password_change/',
            '/auth/password_change/done/',
        )

        for address in urls:
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_url_reset_password_redirect(self):
        """Редирект URL при смене пароля."""
        token = default_token_generator.make_token(self.user)
        uid64 = urlsafe_base64_encode(str(self.user.pk).encode())

        response = self.guest_client.get(f'/auth/reset/{uid64}/{token}/')
        self.assertRedirects(
            response,
            f'/auth/reset/{uid64}/set-password/',
            status_code=302,
            target_status_code=200,
            fetch_redirect_response=True,
        )

    def test_urls_is_available_to_the_authorized_client(self):
        """URL для смена пароля и выхода из аккаунта доступен
        только авторизированному пользователю."""

        urls = (
            '/auth/password_change/',
            '/auth/password_change/done/',
        )

        for address in urls:
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_unexisting_url(self):
        """Несуществующая страница выдает ошибку 404."""
        response = self.guest_client.get('/auth/unexisting_page/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
