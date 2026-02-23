from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('releases', '0006_affiliatelink_favicon'),
    ]

    operations = [
        migrations.AddField(
            model_name='chatusername',
            name='email',
            field=models.EmailField(blank=True, help_text='Optional email for password reset and newsletter', max_length=254, null=True),
        ),
    ]
