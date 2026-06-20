from django.db import migrations


class Migration(migrations.Migration):
    """
    Drop the orphan 'reviews_review' and 'reviews_reviewresponse' tables
    that were left behind when the 'reviews' app was merged into 'marketplace'.
    These ghost tables serve no purpose and can cause confusion.
    """

    dependencies = [
        ('marketplace', '0005_review_reviewresponse'),
    ]

    operations = [
        migrations.RunSQL(
            sql="DROP TABLE IF EXISTS reviews_reviewresponse;",
            reverse_sql="",  # No going back — table was empty anyway
        ),
        migrations.RunSQL(
            sql="DROP TABLE IF EXISTS reviews_review;",
            reverse_sql="",
        ),
    ]
