# -*- coding: utf-8 -*-


from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('trosnoth', '0012_trosnotharena'),
    ]

    operations = [
        migrations.AddField(
            model_name='trosnothuser',
            name='ownsElephant',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterModelOptions(
            name='trosnothserversettings',
            options={'verbose_name_plural': 'Trosnoth server settings'},
        ),
    ]
