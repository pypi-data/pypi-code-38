import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Chart',
            fields=[
                ('id', models.AutoField(
                    auto_created=True, primary_key=True, serialize=False,
                    verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('chart_type', models.CharField(
                    choices=[('line', 'Line'), ('bar', 'Bar'), ('pie', 'Pie'),
                             ('area-spline', 'Area'), ('scatter', 'Scatter'),
                             ('donut', 'Donut')],
                    default='line', max_length=10)),
                ('until_type', models.CharField(
                    choices=[('t', 'This day/week/month/year'),
                             ('y', 'Last day/week/month/year'),
                             ('s', 'Specific Date')],
                    default='t', max_length=1)),
                ('until_date', models.DateField(
                    default=django.utils.timezone.now)),
                ('period_count', models.IntegerField()),
                ('period_step', models.CharField(
                    choices=[('d', 'Days'), ('m', 'Months'),
                             ('y', 'Years')], default='d', max_length=1)),
            ],
        ),
        migrations.CreateModel(
            name='Criteria',
            fields=[
                ('id', models.AutoField(
                    auto_created=True, primary_key=True, serialize=False,
                    verbose_name='ID')),
                ('stats_key', models.CharField(max_length=200)),
                ('side', models.CharField(
                    choices=[('l', 'Left'), ('r', 'Right')],
                    default='l', max_length=1)),
                ('chart', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='criteria',
                    to='django_adminstats.Chart')),
            ],
        ),
    ]
