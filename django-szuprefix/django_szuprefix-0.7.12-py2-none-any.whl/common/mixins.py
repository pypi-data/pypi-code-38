# -*- coding:utf-8 -*- 
__author__ = 'denishuang'


class AttachmentFormMixin(object):
    attachments_field = "attachments"

    def get_context_data(self):
        ctx = super(AttachmentFormMixin, self).get_context_data()
        ctx["attachment_field"] = self.attachments_field
        ctx["config_attachments"] = True
        return ctx

    def get_form(self, form_class=None):
        form = super(AttachmentFormMixin, self).get_form(form_class)
        if self.request.method == "POST":
            fs = self.get_upload_attachments()
        else:
            fs = hasattr(form,"instance") and form.instance.attachments.all() or []
        self.common_config_attachments = fs
        return form


    def get_upload_attachments(self):
        ids = [int(id) for id in self.request.POST.getlist(self.attachments_field)]
        return self.request.user.common_config_attachments.filter(id__in=ids)

    def bind_attachments(self, obj):
        setattr(obj, self.attachments_field, self.common_config_attachments)

class ImageFormMixin(object):
    images_field = "images"

    def get_context_data(self):
        ctx = super(ImageFormMixin, self).get_context_data()
        ctx["images_field"] = self.images_field
        ctx["config_images"] = True
        return ctx

    def get_form(self, form_class=None):
        form = super(ImageFormMixin, self).get_form(form_class)
        if self.request.method == "POST":
            fs = self.get_upload_images()
        else:
            fs = hasattr(form,"instance") and form.instance.images.all() or []
        self.common_config_images = fs
        return form


    def get_upload_images(self):
        ids = [ int(id) for id in self.request.POST.getlist(self.images_field)]
        return self.request.user.common_config_images.filter(id__in=ids)

    def bind_images(self,obj):
        setattr(obj ,self.images_field, self.common_config_images)
