# -*- coding: utf-8 -*-
import click

from spell.cli.exceptions import api_client_exception_handler
from spell.cli.utils import HiddenOption


@click.command(name="status",
               short_help="Display account and billing information")
@click.option("--raw", help="Display output in raw format.", is_flag=True, default=False, cls=HiddenOption)
@click.pass_context
def status(ctx, raw):
    """
    Display account and billing information

    Display account and billing information, such as current plan, total run time,
    and free credit usage.
    """
    client = ctx.obj["client"]

    with api_client_exception_handler():
        billing_info = client.get_billing_info()

        click.echo("Current Plan: {}".format(billing_info.plan_name))
        if billing_info.previous_stripe_billing_date is not None:
            click.echo("Previous invoice date: {}".format(billing_info.previous_stripe_billing_date))
        if billing_info.next_stripe_billing_date is not None:
            click.echo("Next invoice date: {}".format(billing_info.next_stripe_billing_date))
        if len(billing_info.period_machine_stats) > 0:
            click.echo("Upcoming charges for usage:")
            for row in billing_info.period_machine_stats:
                click.echo("\t- {}: {} (${:,.2f})".format(
                    row.machine_type_name,
                    row.total.time_used,
                    row.total.cost_used_usd
                ))
            if billing_info.used_credits_usd > 0.0:
                click.echo("\t- {}: {} ($-{:,.2f})".format("Credits", "", billing_info.used_credits_usd))
            click.echo("\t= {}: {} (${:,.2f})".format("Total", "", billing_info.total_charge_usd))
        click.echo("Remaining free credit: ${:,.2f}".format(billing_info.remaining_credits_usd))
        if len(billing_info.total_machine_stats) > 0:
            click.echo("Total usage:")
            for row in billing_info.total_machine_stats:
                click.echo("\t- {}: {}".format(row.machine_type_name, row.total.time_used))
        click.echo("Run history:")
        click.echo("\t- total: {} runs".format(billing_info.total_runs))
        click.echo("\t- currently queued due to concurrency: {} runs".format(billing_info.concurrent_queued_runs))
        click.echo("\t- plan concurrency limit: {} runs".format(billing_info.concurrent_run_limit))
