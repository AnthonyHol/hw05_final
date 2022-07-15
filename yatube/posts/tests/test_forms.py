from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Comment, Group, Post

User = get_user_model()


class PostsFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')

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

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(PostsFormTests.user)

    def test_edit_post(self):
        """Тест формы изменения поста."""
        post = Post.objects.create(
            author=self.user,
            text='Тестовый пост 3',
            group=PostsFormTests.group,
            image=self.uploaded,
        )

        form_data = {
            'text': 'Это тест изменения поста 3:)',
            'group': PostsFormTests.group_2.pk,
        }

        response = self.authorized_client.post(
            reverse('posts:post_edit', kwargs={'post_id': post.pk}),
            data=form_data,
            follow=True,
        )

        post.refresh_from_db()

        self.assertEqual(
            post.text,
            form_data['text'],
            'Текст поста не был изменен.',
        )
        self.assertEqual(
            response.status_code, HTTPStatus.OK, 'Запрос не вернул код 200.'
        )
        self.assertRedirects(
            response,
            reverse('posts:post_detail', kwargs={'post_id': post.pk}),
        )

    def test_add_comment(self):
        """Тест формы добавления комментария."""
        comment_count = Comment.objects.count()

        post = Post.objects.create(
            author=self.user,
            text='Тестовый пост 3',
            group=PostsFormTests.group,
            image=self.uploaded,
        )

        form_data = {
            'post': post,
            'author': self.user,
            'text': 'teeeeeeeeeeext',
        }

        response = self.authorized_client.post(
            reverse('posts:add_comment', kwargs={'post_id': post.pk}),
            data=form_data,
            follow=True,
        )

        self.assertEqual(
            Comment.objects.count(),
            comment_count + 1,
            'После отправки формы количество постов не изменилось.',
        )
        self.assertEqual(
            response.status_code, HTTPStatus.OK, 'Запрос не вернул код 200.'
        )


class PostCreateViewTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')

        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
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

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(PostCreateViewTest.user)

    def test_create_post_with_group(self):
        """Тест формы создания поста с группой."""
        post_count = Post.objects.count()

        form_data = {
            'text': 'Это тест создания нового поста - 2 :)',
            'group': PostCreateViewTest.group.pk,
            'image': self.uploaded,
        }

        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True,
        )
        self.assertEqual(
            Post.objects.count(),
            post_count + 1,
            'После отправки формы количество постов не изменилось.',
        )
        self.assertEqual(
            response.status_code, HTTPStatus.OK, 'Запрос не вернул код 200.'
        )

    def test_create_post_without_group(self):
        """Тест формы создания поста без группы."""
        post_count = Post.objects.count()

        form_data = {
            'text': 'Это тест создания нового поста :)',
        }

        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True,
            image=self.uploaded,
        )

        self.assertEqual(
            Post.objects.count(),
            post_count + 1,
            'После отправки формы количество постов не изменилось.',
        )
        self.assertEqual(
            Post.objects.last().text,
            form_data['text'],
            'Последний добавленный пост отличается от созданного.',
        )
        self.assertEqual(
            response.status_code, HTTPStatus.OK, 'Запрос не вернул код 200.'
        )
