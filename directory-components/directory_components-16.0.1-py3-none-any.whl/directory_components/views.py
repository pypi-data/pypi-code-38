from django.views.generic import TemplateView


class RobotsView(TemplateView):
    template_name = 'robots.txt'
    content_type = 'text/plain'
