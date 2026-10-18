# Generated manually to preserve existing project history.
import uuid

from django.db import migrations, models
import django.db.models.deletion
from django.core.validators import MaxValueValidator, MinValueValidator


class Migration(migrations.Migration):
    dependencies = [
        ('app', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='atencion',
            name='id',
            field=models.CharField(default=uuid.uuid4, editable=False, max_length=50, primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='atencion',
            name='fechaInicio',
            field=models.DateTimeField(auto_now_add=True),
        ),
        migrations.AlterField(
            model_name='atencion',
            name='fechaTermino',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='atencion',
            name='sbp',
            field=models.IntegerField(validators=[MinValueValidator(50), MaxValueValidator(250)]),
        ),
        migrations.AlterField(
            model_name='atencion',
            name='dbp',
            field=models.IntegerField(validators=[MinValueValidator(30), MaxValueValidator(150)]),
        ),
        migrations.AlterField(
            model_name='atencion',
            name='pulso',
            field=models.IntegerField(validators=[MinValueValidator(20), MaxValueValidator(250)]),
        ),
        migrations.AlterField(
            model_name='atencion',
            name='temperatura',
            field=models.IntegerField(validators=[MinValueValidator(25), MaxValueValidator(45)]),
        ),
        migrations.AlterField(
            model_name='atencion',
            name='saturacion',
            field=models.IntegerField(validators=[MinValueValidator(50), MaxValueValidator(100)]),
        ),
        migrations.AlterField(
            model_name='atencion',
            name='paciente',
            field=models.ForeignKey(max_length=50, on_delete=django.db.models.deletion.PROTECT, to='app.paciente'),
        ),
        migrations.AlterField(
            model_name='atencion',
            name='practicante',
            field=models.ForeignKey(max_length=50, on_delete=django.db.models.deletion.PROTECT, to='app.user'),
        ),
        migrations.AlterField(
            model_name='user',
            name='perfil',
            field=models.ForeignKey(max_length=50, on_delete=django.db.models.deletion.PROTECT, to='app.perfil'),
        ),
    ]
