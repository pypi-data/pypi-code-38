from ftw.simplelayout.images.limits.validators import ImageLimitValidator
from ftw.slider.contents.pane import IPaneSchema
from z3c.form import validator


class SliderPaneImageLimitValidator(ImageLimitValidator):

    identifier = 'ftw.slider.Pane'


validator.WidgetValidatorDiscriminators(
    SliderPaneImageLimitValidator,
    field=IPaneSchema['image']
)
