from collective.quickupload.browser import uploadcapable


ALLOWED_IMAGETYPES = ['image/png',
                      'image/jpeg',
                      'image/gif',
                      'image/pjpeg',
                      'image/x-png'
                      ]


class SliderBlockQuickUploadCapableFileFactory(
        uploadcapable.QuickUploadCapableFileFactory):
    """ Quickupload file factory for sliderblocks.
    Make sure slider panes are created in this container."""

    def __call__(self, filename, title, description, content_type,
                 data, portal_type):

        portal_type = "ftw.slider.Pane"

        # Simple validator since the field validator is not triggered
        # TODO This should happen on the image field.
        if content_type not in ALLOWED_IMAGETYPES:
            raise ValueError('Invalid image type: Supported types '
                             'are: {0}'.format(', '.join(ALLOWED_IMAGETYPES)))

        return super(SliderBlockQuickUploadCapableFileFactory, self).__call__(
            filename, title, description, content_type, data, portal_type)
