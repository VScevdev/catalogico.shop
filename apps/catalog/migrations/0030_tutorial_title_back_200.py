# Revert Tutorial title to max_length=200 (in case 0029 had changed it to 600)

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0029_alter_tutorial_title_max_length'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tutorial',
            name='title',
            field=models.CharField(max_length=200, verbose_name='Título'),
        ),
    ]
