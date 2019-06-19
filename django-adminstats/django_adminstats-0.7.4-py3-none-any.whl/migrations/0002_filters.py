from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('django_adminstats', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='criteria', name='axis_spec',
            field=models.TextField(blank=True, default='')),
        migrations.AddField(
            model_name='criteria', name='filter_spec',
            field=models.TextField(blank=True, default='')),
        migrations.AddField(
            model_name='criteria', name='group_spec',
            field=models.TextField(blank=True, default='')),
        migrations.AlterField(
            model_name='chart', name='chart_type',
            field=models.CharField(
                choices=[('line', 'Line'), ('bar', 'Bar'), ('pie', 'Pie'),
                         ('area-spline', 'Area'), ('scatter', 'Scatter'),
                         ('donut', 'Donut')],
                default='line', max_length=100),
        ),
        migrations.RemoveField(model_name='criteria', name='side'),
    ]
