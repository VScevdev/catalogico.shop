# Generated manually: Tutorial video_url max_length 200 -> 600

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0028_add_faq_tutorial_storefeedback'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tutorial',
            name='video_url',
            field=models.URLField(blank=True, max_length=600, verbose_name='URL del video (YouTube, Vimeo, etc.)'),
        ),
    ]
