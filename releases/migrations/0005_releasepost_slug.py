from django.db import migrations, models
from django.utils.text import slugify


def populate_slugs(apps, schema_editor):
    ReleasePost = apps.get_model('releases', 'ReleasePost')
    for post in ReleasePost.objects.all():
        base = slugify(post.title)
        slug = base
        n = 1
        while ReleasePost.objects.filter(slug=slug).exclude(pk=post.pk).exists():
            slug = f"{base}-{n}"
            n += 1
        post.slug = slug
        post.save(update_fields=['slug'])


class Migration(migrations.Migration):

    dependencies = [
        ('releases', '0004_releasepost_youtube_url'),
    ]

    operations = [
        # Step 1: add column without unique constraint, allowing blanks
        migrations.AddField(
            model_name='releasepost',
            name='slug',
            field=models.SlugField(max_length=120, blank=True, default=''),
        ),
        # Step 2: populate slugs for all existing rows
        migrations.RunPython(populate_slugs, migrations.RunPython.noop),
        # Step 3: now add the unique constraint safely
        migrations.AlterField(
            model_name='releasepost',
            name='slug',