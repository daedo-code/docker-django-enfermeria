from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ('app', '0002_secure_clinical_records'),
    ]

    operations = [
        migrations.AddField(
            model_name='atencion',
            name='anulada',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='atencion',
            name='fechaAnulacion',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='atencion',
            name='anuladoPor',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='atenciones_anuladas', to=settings.AUTH_USER_MODEL),
        ),
    ]
