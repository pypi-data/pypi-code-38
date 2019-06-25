try:
    from email import message_from_bytes
except ImportError:
    # For python 2.x compatibility
    from future.backports.email import message_from_bytes

from collections import OrderedDict

from django.db import models


class DevelopEmail(models.Model):
    created_datetime = models.DateTimeField(auto_now_add=True)
    subject = models.TextField(null=False, blank=True, default='')
    from_email = models.TextField(
        null=False, blank=True, default='',
        db_index=True)
    to_emails = models.TextField(null=False, blank=True, default='')
    raw_message = models.TextField(null=False, blank=True, default='')

    class Meta:
        ordering = ['-created_datetime']

    @property
    def subject_with_fallback(self):
        return self.subject.strip() or '(No subject)'

    @property
    def message(self):
        if not hasattr(self, '_message'):
            self._message = message_from_bytes(self.raw_message.encode('utf-8'))
        return self._message

    def _get_message(self, content_type, allow_not_multipart_fallback=False):
        if self.message.is_multipart():
            for part in self.message.walk():
                part_content_type = part.get_content_type()
                part_content_disposition = str(part.get('Content-Disposition'))

                if part_content_type == content_type and 'attachment' not in part_content_disposition:
                    return part.get_payload(decode=True).decode('utf-8')
            return None
        elif allow_not_multipart_fallback:
            return self.message.get_payload(decode=True).decode('utf-8')
        return None

    @property
    def plaintext_message(self):
        return self._get_message(content_type='text/plain', allow_not_multipart_fallback=True)

    @property
    def html_message(self):
        return self._get_message(content_type='text/html', allow_not_multipart_fallback=False)

    def iter_attachment_messages(self):
        if self.message.is_multipart():
            for part in self.message.walk():
                part_content_disposition = str(part.get('Content-Disposition'))

                if 'attachment' in part_content_disposition:
                    yield part

    def iter_attachment_data(self, include_payload=True):
        for attachment_message in self.iter_attachment_messages():
            data = {
                'filename': attachment_message.get_filename(),
                'content_type': attachment_message.get_content_type(),
                'payload': attachment_message.get_payload(decode=True)
            }
            if include_payload:
                data['payload'] = attachment_message.get_payload(decode=True)
            yield data

    def get_attachment_dict(self, include_payload=False):
        attachmentsdict = OrderedDict()
        for attachmentdata in self.iter_attachment_data(include_payload=include_payload):
            if attachmentdata['filename']:
                attachmentsdict[attachmentdata['filename']] = attachmentdata
        return attachmentsdict

    def __str__(self):
        return '#{} - {}'.format(self.id, self.subject_with_fallback)
