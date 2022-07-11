# Generated by Django 2.2.16 on 2022-07-09 07:10

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0009_comment'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='comment',
            options={'ordering': ('-created',), 'verbose_name': 'Комментарий', 'verbose_name_plural': 'Комментарии'},
        ),
        migrations.AlterField(
            model_name='comment',
            name='post',
            field=models.ForeignKey(blank=True, help_text='Комментарии к посту', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='comments', to='posts.Post', verbose_name='Комментарии'),
        ),
    ]
