from django.db import migrations
from django.utils.text import slugify


def populate_slugs(apps, schema_editor):
    db = schema_editor.connection
    with db.cursor() as cursor:
        cursor.execute("SELECT id, title FROM releases_releasepost")
        rows = cursor.fetchall()
        seen = set()
        for pk, title in rows:
            base = slugify(title)
            slug = base
            n = 1
            while slug in seen:
                slug = f"{base}-{n}"
                n += 1
            seen.add(slug)
            cursor.execute(
                "UPDATE releases_releasepost SET slug = %s WHERE id = %s",
                [slug, pk]
            )


class Migration(migrations.Migration):

    dependencies = [
        ('releases', '0004_releasepost_youtube_url'),
    ]

    operations = [
        migrations.RunSQL(
            "ALTER TABLE releases_releasepost ADD COLUMN IF NOT EXISTS slug VARCHAR(120) NOT NULL DEFAULT ''",
            "ALTER TABLE releases_releasepost DROP COLUMN IF EXISTS slug",
        ),
        migrations.RunPython(populate_slugs, migrations.RunPython.noop),
        migrations.RunSQL(
            "ALTER TABLE releases_releasepost ALTER COLUMN slug DROP DEFAULT",
            migrations.RunSQL.noop,
        ),
        migrations.RunSQL(
            "CREATE UNIQUE INDEX IF NOT EXISTS releases_releasepost_slug_key ON releases_releasepost (slug)",
            "DROP INDEX IF EXISTS releases_releasepost_slug_key",
        ),
    ]