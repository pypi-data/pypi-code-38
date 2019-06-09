from django.conf.urls import url, include

urlpatterns = [
    url(r'^books/', include('aparnik.packages.educations.books.api.urls', namespace='books')),
    url(r'^publishers/', include('aparnik.packages.educations.books.api.urls-publishers', namespace='publishers')),
    url(r'^writers-translators/', include('aparnik.packages.educations.books.api.urls-writers-translators', namespace='writers-translators')),
    url(r'^teachers/', include('aparnik.packages.educations.teachers.api.urls', namespace='teachers')),
    url(r'^courses/', include('aparnik.packages.educations.courses.api.urls', namespace='courses')),
    url(r'^educations/', include('aparnik.packages.educations.educations.api.urls', namespace='educations')),
    url(r'^progresses/', include('aparnik.packages.educations.progresses.api.urls', namespace='progresses')),
]
