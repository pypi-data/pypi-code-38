from libaloha.django import AlohaView
from django.core.exceptions import ObjectDoesNotExist
from django.forms import ModelForm, TextInput
from django.urls import reverse
from django.http import HttpResponseRedirect
from django_ping_me.models import Domain

import datetime
import logging

logger = logging.getLogger(__name__)


class DomainForm(ModelForm):
    class Meta:
        model = Domain
        fields = ['url', 'description']
        widgets = {
            'description': TextInput(attrs={'style': 'width: 100%;'})
        }


class PingMeView(AlohaView):
    def get_domain(self, domain_pk):
        """Récupère le domaine dont la clé est passée en paramètre"""

        try:
            domain = Domain.objects.get(id=domain_pk)
            return domain
        except Domain.DoesNotExist:
            return None

    def get_domain_list(self):
        """Récupère la liste des domaines affectés à l'utilisateur courant"""

        if not self.request.user or not self.request.user.is_authenticated:
            return []

        if self.request.user.is_staff:
            domains = Domain.objects.all()
        else:
            domains = Domain.objects.filter(user=self.request.user)

        return domains.order_by('url')

    def get_edit_form(self, domain_pk):
        """Récupère le formulaire d'édition de domaine"""

        if domain_pk:
            domain = self.get_domain(domain_pk)
            if domain:
                return DomainForm(self.request.POST or None, instance=domain)

        return DomainForm(self.request.POST or None)


class ListDomainView(PingMeView):
    title = 'Liste des domaines'
    template_name = 'ping_me/domain_list.html'

    def get(self, request, *args, **kwargs):
        """Retourne la liste des domaines enregistrés"""

        context = self.get_context_data()
        context['domain_list'] = self.get_domain_list()
        context['current_month'] = datetime.date.today().replace(day=1)

        last_month = datetime.date.today().replace(day=1)
        last_month = last_month - datetime.timedelta(days=1)
        last_month = last_month.replace(day=1)
        context['last_month'] = last_month

        return self.render_to_response(context)

    def post(self, request, *args, **kwargs):
        """Traitement des différentes actions"""

        # Traitement de l'enregistrement de domaine
        if request.POST.get('btnSaveDomain') is not None:
            self.edit_domain()
            return HttpResponseRedirect(reverse('ping_me:index'))

        # Traitement de la suppression de domaine
        if request.POST.get('btnDeleteDomain', None) is not None:
            self.delete_domain()
            return HttpResponseRedirect(reverse('ping_me:index'))

        # Traitement global du parent si aucun traitement n'a été réalisé
        return super().post(request, *args, **kwargs)

    def edit_domain(self):
        """Édite un domaine à partir des données POST"""

        domain_pk = self.request.POST.get('hdnDomainId', 0)
        form = self.get_edit_form(domain_pk)
        if form.is_valid():
            try:
                if not form.instance.user:
                    form.instance.user = self.request.user
            except ObjectDoesNotExist:
                form.instance.user = self.request.user

            form.save()
            return True

        return False

    def delete_domain(self):
        """Supprime un domaine à partir des données POST"""

        domain_pk = int(self.request.POST.get('hdnDomainId', 0))
        domain = self.get_domain(domain_pk)
        if not domain:
            return False

        logger.info("Suppression du domaine {}".format(domain.url))
        domain.delete()
        return True


class PartialEditView(PingMeView):
    template_name = 'ping_me/partials/edit_form.html'

    def get(self, request, *args, **kwargs):
        """Retourne le formulaire d'édition d'un domaine"""

        domain_pk = kwargs.get('domain_pk', 0)
        form = self.get_edit_form(domain_pk)

        context = self.get_context_data()
        context['form'] = form
        context['is_edit'] = form.instance.id is not None
        return self.render_to_response(context)


class PartialDeleteView(PingMeView):
    template_name = 'ping_me/partials/delete_form.html'

    def get(self, request, *args, **kwargs):
        """Retourne le formulaire de suppression d'un domaine"""

        domain_pk = kwargs.get('domain_pk', 0)
        domain = self.get_domain(domain_pk)
        if not domain:
            raise ValueError("Impossible de trouver le domaine")

        context = self.get_context_data()
        context['domain'] = domain
        return self.render_to_response(context)
