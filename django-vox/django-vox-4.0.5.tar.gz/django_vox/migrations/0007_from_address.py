from django.db import migrations, models


def set_not_bulk(apps, _schema_editor):
    template_cls = apps.get_model("django_vox", "Template")
    template_cls.objects.update(bulk=False)


class Migration(migrations.Migration):

    dependencies = [("django_vox", "0006_activity_read_at")]

    operations = [
        migrations.RemoveField(model_name="failedmessage", name="contact_name"),
        migrations.RenameField(
            model_name="failedmessage", old_name="address", new_name="to_addresses"
        ),
        migrations.AddField(
            model_name="failedmessage",
            name="from_address",
            field=models.CharField(
                blank=True, max_length=500, verbose_name="from address"
            ),
        ),
        migrations.AlterField(
            model_name="failedmessage",
            name="to_addresses",
            field=models.TextField(verbose_name="to addresses"),
        ),
        migrations.RenameField(
            model_name="template", old_name="recipient", new_name="recipients"
        ),
        migrations.AddField(
            model_name="template",
            name="from_address",
            field=models.CharField(
                blank=True, max_length=500, verbose_name="from address"
            ),
        ),
        migrations.AddField(
            model_name="template",
            name="bulk",
            field=models.BooleanField(
                default=True,
                verbose_name="bulk",
                help_text="Send the same message to all recipients",
            ),
        ),
        migrations.AlterField(
            model_name="template",
            name="recipients",
            field=models.TextField(
                default="re",
                verbose_name="recipients",
                blank=True,
                help_text="Who this message actually gets sent to.",
            ),
        ),
        migrations.RunPython(set_not_bulk, migrations.RunPython.noop),
    ]
