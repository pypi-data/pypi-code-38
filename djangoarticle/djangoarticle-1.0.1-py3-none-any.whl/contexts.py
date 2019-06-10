from .models import CategoryModelScheme


# this context returns all the category associated to apptwo.
def get_category_context(request):
    category_context = CategoryModelScheme.objects.all()
    return { 'category_context': category_context }
