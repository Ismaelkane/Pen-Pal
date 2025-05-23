# Generated by Django 5.1.6 on 2025-02-21 10:07

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('translator', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserConversation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('conversation', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_conversations', to='translator.conversation')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_conversations', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'unique_together': {('user', 'conversation')},
            },
        ),
    ]
