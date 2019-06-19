from .models import Domain, Ping, PingSummary
from django_cron import CronJobBase, Schedule
# https://django-cron.readthedocs.io

import libaloha.network
import datetime
import logging
import pytz

logger = logging.getLogger(__name__)


class PingMeCronJob(CronJobBase):
    RUN_EVERY_MINS = 1
    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'ping_me.cron'

    def do(self):
        """Fonction principale d'exécution du cron"""

        all_domains = Domain.objects.order_by('url')
        logger.debug("Mise à jour des domaines PingMe! {} domaine(s) trouvé(s) !"
              .format(len(all_domains)))

        for domain in all_domains:
            self.update_domain(domain)

    def update_domain(self, domain):
        """Met à jour un domaine"""

        try:
            last_ping = Ping.objects.filter(domain=domain).latest('date')
        except Ping.DoesNotExist:
            last_ping = None

        ping = self.create_ping(domain)

        if last_ping:

            # Si le domaine ne répond plus au ping
            if last_ping.success and not ping.success:
                logger.error("Le domaine {} vient de tomber! :-o".format(domain.url))

            # Si le dernier ping date du mois dernier
            if last_ping.date.month != ping.date.month:
                self.clean_pings(domain, last_ping)

    def create_ping(self, domain):
        """Exécute un nouveau ping et l'enregistre en base de données"""

        ip_address = aloha.network.resolve_hostname(domain.url)
        ping = Ping(address=ip_address, domain=domain)

        if aloha.network.is_http_alive(domain.url, timeout=5):
            ping.success = True
            logger.debug("Site {} fonctionnel !".format(domain.url))
        else:
            ping.success = False
            logger.warning("Site {} cassé ! :-(".format(domain.url))

        ping.save()
        return ping

    def clean_pings(self, domain, last_ping):
        """Nettoie les pings du mois précédent et crée un résumé en base de données"""

        start_date = datetime.datetime(
            year=last_ping.date.year,
            month=last_ping.date.month,
            day=1,
            tzinfo=pytz.UTC
        )
        end_date = start_date + datetime.timedelta(days=32)
        end_date = end_date.replace(day=1)

        all_pings = Ping.objects.filter(domain=domain,
                                        date__range=(start_date, end_date))
        logger.info("clean_pings: {} pings trouvés pour le mois {}"
                    .format(len(all_pings), start_date.strftime('%m/%Y')))

        summary = PingSummary(domain=domain, date=start_date.date())
        for ping in all_pings:
            if ping.success:
                summary.nb_success += 1
            else:
                summary.nb_errors += 1

        summary.save()
        all_pings.delete()