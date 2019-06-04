# Generated by Django 2.2 on 2019-05-01 16:09

from django.db import migrations
import django_fsm
import subscriptions.states


class Migration(migrations.Migration):

    dependencies = [("subscriptions", "0001_init")]

    operations = [
        migrations.AlterField(
            model_name="subscription",
            name="state",
            field=django_fsm.FSMIntegerField(
                choices=[
                    (1, "ACTIVE"),
                    (2, "EXPIRING"),
                    (3, "RENEWING"),
                    (4, "SUSPENDED"),
                    (5, "ENDED"),
                    (-1, "ERROR"),
                ],
                default=subscriptions.states.SubscriptionState(1),
                help_text="The current status of the subscription. May not be modified directly.",
                protected=True,
            ),
        )
    ]
