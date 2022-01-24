# Generated by Django 3.2.4 on 2022-01-23 22:52

from django.db import migrations, models
import django.db.models.manager


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0060_merge_20220121_2030'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='grade',
            options={'default_manager_name': 'unfiltered'},
        ),
        migrations.AlterModelOptions(
            name='professor',
            options={'default_manager_name': 'unfiltered'},
        ),
        migrations.AlterModelOptions(
            name='review',
            options={'default_manager_name': 'unfiltered'},
        ),
        migrations.AlterModelManagers(
            name='grade',
            managers=[
                ('unfiltered', django.db.models.manager.Manager()),
            ],
        ),
        migrations.AlterModelManagers(
            name='professor',
            managers=[
                ('unfiltered', django.db.models.manager.Manager()),
            ],
        ),
        migrations.AlterModelManagers(
            name='review',
            managers=[
                ('unfiltered', django.db.models.manager.Manager()),
            ],
        ),
        migrations.AddIndex(
            model_name='review',
            index=models.Index(fields=['status'], name='home_review_status_358306_idx'),
        ),
        migrations.AddConstraint(
            model_name='grade',
            constraint=models.UniqueConstraint(fields=('course', 'semester', 'section'), name='unique_course_semester_section'),
        ),
    ]