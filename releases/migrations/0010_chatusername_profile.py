# Generated manually to prevent local python version mismatch issues
from django.db import migrations, models
import fliphouserecords.storage_backends


class Migration(migrations.Migration):

    dependencies = [
        ('releases', '0009_passwordresettoken'),
    ]

    operations = [
        migrations.AddField(
            model_name='chatusername',
            name='avatar',
            field=models.ImageField(
                blank=True, 
                null=True, 
                storage=fliphouserecords.storage_backends.MediaStorage(), 
                upload_to='chat_avatars/'
            ),
        ),
        migrations.AddField(
            model_name='chatusername',
            name='bio',
            field=models.TextField(blank=True, max_length=500, null=True),
        ),
        migrations.AddField(
            model_name='chatusername',
            name='last_login',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='chatusername',
            name='location',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]