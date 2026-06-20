import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('news', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='agrinews',
            name='status',
            field=models.CharField(
                choices=[
                    ('pending', 'Pending Approval'),
                    ('published', 'Published'),
                    ('rejected', 'Rejected'),
                ],
                default='published',
                max_length=20,
                db_index=True,
            ),
        ),
        migrations.AddField(
            model_name='agrinews',
            name='source_type',
            field=models.CharField(
                choices=[
                    ('external_feed', 'External Feed'),
                    ('user_submission', 'User Submission'),
                ],
                default='external_feed',
                max_length=20,
            ),
        ),
        migrations.AddField(
            model_name='agrinews',
            name='submitted_by',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='submitted_news',
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        # published_by already exists but without related_name — alter it
        migrations.AlterField(
            model_name='agrinews',
            name='published_by',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='published_news',
                to=settings.AUTH_USER_MODEL,
            ),
        ),
    ]
