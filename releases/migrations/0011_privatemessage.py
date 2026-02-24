# Generated manually
from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('releases', '0010_chatusername_profile'),
    ]

    operations = [
        migrations.CreateModel(
            name='PrivateMessage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sender', models.CharField(max_length=50)),
                ('recipient', models.CharField(max_length=50)),
                ('message', models.TextField(max_length=500)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'ordering': ['timestamp'],
            },
        ),
    ]