from django.urls import reverse
from django.http import HttpResponseRedirect
from django.views.generic import TemplateView
from .models import Message

import logging


class AbstractMessageView(TemplateView):
    
    def __init__(self):
        super(AbstractMessageView, self).__init__()
        self.logger = logging.getLogger('messaging')

    def get(self, request, *args, **kwargs):
        """
        Django method to handle a message view.
        Take a slug as parameter and handle a message
        """

        if not 'slug' in kwargs:
            return super().get(request, *args, **kwargs)

        slug = str(kwargs.get('slug', ''))
        message = self.get_message(slug)

        if not message:
            request.session['unknown-slug'] = slug
            return HttpResponseRedirect(reverse('messaging:index'))
        
        return self.handle(request, message)

    def get_message(self, slug):
        """Get a message or return none"""
        
        try:
            message = Message.objects.get(slug=slug)
            
        except Message.DoesNotExist:
            self.logger.error("Try to get an unknown message: {}".format(slug))
            return None
        
        self.logger.info("Get message: {}".format(message.slug))
        return message
    
    def save_message(self, message):
        """Save a message"""
        
        message.save()
        self.logger.info("Save message: {}".format(message.slug))
    
    def delete_message(self, message):
        """Delete a message"""
        
        slug = message.slug
        message.delete()
        self.logger.info("Delete message: {}".format(slug))
    

class IndexView(TemplateView):
    """Index view"""
    template_name = 'messaging/index.html'
    
    def get(self, request):    
        """Handle get request"""
        
        context = {}
        
        # If we just add a new message
        if 'added-slug' in request.session:
            context['added_slug'] = request.session['added-slug']
            del request.session['added-slug']
            
        # If we just ask for an unknown message
        if 'unknown-slug' in request.session:
            context['unknown_slug'] = request.session['unknown-slug']
            del request.session['unknown-slug']

        return self.render_to_response(context)
    
    def post(self, request):
        """Handle post request"""
        
        value = request.POST.get('slug')
        if not value:
            return self.render_to_response({})
        
        return HttpResponseRedirect(reverse('messaging:message', args=[value]))


class NewMessageView(AbstractMessageView):
    """New message view"""
    template_name = 'messaging/edit-message.html'

    def post(self, request):
        """Handle post request"""
        
        value = request.POST.get('txtMessage', '')
        if not value:
            return self.render_to_response({})
        
        message = Message(message=value, 
            is_editable = request.POST.get('chkIsEditable', '') == 'on', 
            is_deletable = request.POST.get('chkIsDeletable', '') == 'on')
        self.save_message(message)
        
        request.session['added-slug'] = message.slug
        return HttpResponseRedirect(reverse('messaging:index'))


class MessageView(AbstractMessageView):
    """Message view"""
    template_name = 'messaging/message.html'
    
    def handle(self, request, message):
        context = { 'message': message }
        return self.render_to_response(context)
    

class EditMessageView(AbstractMessageView):
    """Edit message view"""
    template_name = 'messaging/edit-message.html'
    
    def handle(self, request, message):
        
        if not message.is_editable:
            return HttpResponseRedirect(reverse('messaging:message', args=[message.slug]))
        
        context = { 'message': message }
        return self.render_to_response(context)
    
    def post(self, request, slug):
        
        message = self.get_message(slug)
        if not message:
            request.session['unknown-slug'] = slug
            return HttpResponseRedirect(reverse('messaging:index'))
        
        value = request.POST.get('txtMessage', '')
        if not value:
            return self.render_to_response({'message': message})
        
        message.message = value
        self.save_message(message)
        
        request.session['added-slug'] = message.slug
        return HttpResponseRedirect(reverse('messaging:index'))
    

class DeleteMessageView(AbstractMessageView):
    """Delete message view"""
    
    def handle(self, request, message):
        
        if not message.is_deletable:
            return HttpResponseRedirect(reverse('messaging:message', args=[message.slug]))
        
        self.delete_message(message)    
        return HttpResponseRedirect(reverse('messaging:index'))