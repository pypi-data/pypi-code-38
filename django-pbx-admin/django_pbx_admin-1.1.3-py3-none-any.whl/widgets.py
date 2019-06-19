import base64
import json
import logging
import mimetypes
import os

from django.core.files.uploadedfile import UploadedFile
from django.db.models.fields.files import FieldFile
from django.forms.widgets import FileInput, Textarea, CheckboxInput, HiddenInput


log = logging.getLogger(__name__)


class ImageInput(FileInput):
    """
    Widget providing a input element for file uploads based on the
    Django ``FileInput`` element. It hides the actual browser-specific
    input element and shows the available image for images that have
    been previously uploaded. Selecting the image will open the file
    dialog and allow for selecting a new or replacing image file.
    """

    template_name = "pbx_admin/forms/widgets/image_input_widget.html"

    def get_image_context(self, name, value, attrs):
        image = {}
        if isinstance(value, FieldFile) and value.name:
            image["filename"] = os.path.basename(value.name)
            image["url"] = image["thumb_url"] = value.url

        elif isinstance(value, UploadedFile) and not value.closed:
            image["filename"] = value.name
            mimetype = (
                value.content_type
                or mimetypes.guess_type(value.name)[0]
                or "application/octet-stream"
            )
            image["url"] = image["thumb_url"] = b"data:%s;base64,%s" % (
                mimetype.encode(),
                base64.b64encode(value.file.read()),
            )
            value.file.seek(0)

        elif isinstance(value, dict):
            image = value
        return image

    def get_context(self, name, value, attrs):
        """
        The image URL is take from *value* and is provided to the template as
        ``image_url`` context variable relative to ``MEDIA_URL``. Further
        attributes for the ``input`` element are provide in ``input_attrs`` and
        contain parameters specified in *attrs* and *name*.
        If *value* contains no valid image URL an empty string will be provided
        in the context.
        """
        if value is None:
            value = ""

        context = super().get_context(name, value, attrs)

        context["widget"]["attrs"].update(
            {
                # Escaping dots for jquery selector
                "id": context["widget"]["attrs"]["id"].replace(".", r"\."),
                "accept": "image/*",
                "class": "hidden",
            }
        )

        context["widget"]["image"] = self.get_image_context(name, value, attrs)

        return context


class RemovableImageInput(ImageInput):
    remove_input_cls = CheckboxInput

    def remove_input_name(self, name):
        """
        Given the name of the file input, return the name of the remove
        checkbox input.
        """
        return name + "-remove"

    def remove_input_id(self, name):
        """
        Given the name of the remove checkbox input, return the HTML id for it.
        """
        return name + "_id"

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        input_name = self.remove_input_name(name)
        input_id = self.remove_input_id(input_name)
        remove_input_context = self.remove_input_cls().get_context(
            input_name, None, attrs={"id": input_id}
        )
        remove_input_context["widget"]["attrs"]["id"] = input_id
        context["widget"]["remove_input"] = remove_input_context
        return context

    def value_from_datadict(self, data, files, name):
        upload = super().value_from_datadict(data, files, name)

        remove_input_value = self.remove_input_cls().value_from_datadict(
            data, files, self.remove_input_name(name)
        )
        if not self.is_required and remove_input_value:
            # False signals to remove any existing value,
            # as opposed to just None
            return False

        return upload


class PrettyRemovableImageInput(RemovableImageInput):
    template_name = "pbx_admin/forms/widgets/pretty_image_input_widget.html"
    remove_input_cls = HiddenInput


class JSONTextarea(Textarea):
    def __init__(self, attrs=None):
        default_attrs = {"data-type": "code", "data-mode": "javascript"}
        if attrs:
            default_attrs.update(attrs)
        super().__init__(default_attrs)

    def build_attrs(self, base_attrs, extra_attrs=None):
        attrs = super().build_attrs(base_attrs, extra_attrs)
        # rm required attr from textarea
        # browsers will throw an error when trying to validate required attr
        # on textarea hidden by codemirror
        if "required" in attrs:
            del attrs["required"]
        return attrs

    def format_value(self, value):
        if isinstance(value, str):
            try:
                value = json.loads(value)
            except json.JSONDecodeError:
                log.info("Incorrect JSON saved %s", value)
                return super().format_value(value)
        if value is None:
            return ""
        return json.dumps(value, indent=4, sort_keys=True, ensure_ascii=False)


class MultiplicableHiddenWidget(HiddenInput):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.attrs = {"class": "multiplicable-hidden"}

    def value_from_datadict(self, data, files, name):
        return {}
