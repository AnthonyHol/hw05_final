from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

User = get_user_model()


class UsersPagesTests(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        return super().setUpClass()

    def setUp(self) -> None:
        self.guest_client = Client()
        self.user = User.objects.create_user(
            username='TestUser', password='df3vfGFsf1', email='efd@gmail.com'
        )
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_pages_uses_correct_template_by_guest_client(self):
        """Страницы использует соответствующий шаблон."""

        templates_url_names = {
            reverse('users:password_reset'): 'users/password_reset_form.html',
            reverse(
                'users:password_reset_done'
            ): 'users/password_reset_done.html',
            # reverse(
            #     'users:password_reset_confirm',
            #     kwargs={'uid64': uid64, 'token': token},
            # ): 'users/password_reset_confirm.html',
            reverse(
                'users:password_reset_complete'
            ): 'users/password_reset_complete.html',
            reverse('users:signup'): 'users/signup.html',
            reverse('users:login'): 'users/login.html',
        }

        for address, template in templates_url_names.items():
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertTemplateUsed(
                    response, template, 'URL-адрес использует неверный шаблон'
                )
