from django.db import migrations, models
import fliphouserecords.storage_backends


class Migration(migrations.Migration):

    dependencies = [
        ('releases', '0005_releasepost_slug'),
    ]

    operations = [
        migrations.AddField(
            model_name='affiliatelink',
            name='favicon',
            field=models.ImageField(blank=True, help_text='Small logo or icon for this link (optional)', null=True, storage=fliphouserecords.storage_backends.MediaStorage(), upload_to='link_favicons/'),
        ),
    ]
