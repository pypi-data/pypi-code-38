from .base import Base


class Category(Base):
    template_name = "issuestracker/category.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["category"] = kwargs["category"]
        return context
