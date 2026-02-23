# Generated manually for plan: Ayuda, Media, Galería y Draft

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
        ('catalog', '0027_alter_product_stock'),
    ]

    operations = [
        migrations.CreateModel(
            name='FAQ',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('question', models.CharField(max_length=500, verbose_name='Pregunta')),
                ('answer', models.TextField(verbose_name='Respuesta')),
                ('order', models.PositiveIntegerField(default=0, verbose_name='Orden')),
                ('is_active', models.BooleanField(default=True, verbose_name='Activa')),
                ('store', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='faqs', to='core.store', verbose_name='Tienda')),
            ],
            options={
                'verbose_name': 'Pregunta frecuente',
                'verbose_name_plural': 'Preguntas frecuentes',
                'ordering': ['order'],
            },
        ),
        migrations.CreateModel(
            name='Tutorial',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200, verbose_name='Título')),
                ('description', models.TextField(blank=True, verbose_name='Descripción')),
                ('video_url', models.URLField(blank=True, verbose_name='URL del video (YouTube, Vimeo, etc.)')),
                ('video_file', models.FileField(blank=True, null=True, upload_to='tutorials/videos/', verbose_name='Archivo de video')),
                ('order', models.PositiveIntegerField(default=0, verbose_name='Orden')),
                ('is_active', models.BooleanField(default=True, verbose_name='Activo')),
            ],
            options={
                'verbose_name': 'Tutorial',
                'verbose_name_plural': 'Tutoriales',
                'ordering': ['order'],
            },
        ),
        migrations.CreateModel(
            name='StoreFeedback',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('author_name', models.CharField(blank=True, max_length=150, verbose_name='Nombre')),
                ('author_email', models.EmailField(blank=True, max_length=254, verbose_name='Email')),
                ('message', models.TextField(verbose_name='Mensaje')),
                ('feedback_type', models.CharField(choices=[('queja', 'Queja'), ('propuesta', 'Propuesta')], max_length=20, verbose_name='Tipo')),
                ('is_read', models.BooleanField(default=False, verbose_name='Leído')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('store', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='feedbacks', to='core.store', verbose_name='Tienda')),
            ],
            options={
                'verbose_name': 'Queja / Propuesta',
                'verbose_name_plural': 'Quejas y propuestas',
                'ordering': ['-created_at'],
            },
        ),
    ]
