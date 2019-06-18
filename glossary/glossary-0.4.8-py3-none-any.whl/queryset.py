from django.db import models


class GlossaryQuerySet(models.QuerySet):
    """
    QuerySet, который не позволяет удалять записи из БД
    пачками. Вместо этого устанавливается метка "удален".

    На записи 'GlossaryModel' так же переопределен метод
    'delete'.
    """

    def delete(self):
        return self.update(deleted=True)

    def force_delete(self):
        return super().delete()


class GlossaryManager(models.Manager):
    """
    Этот менеджер может показывать либо только записи
    без метки "удален", либо только записи с этой меткой.

    За это поведение отвечает параметр 'show_deleted'.
    По умолчанию показываются все записи без метки "удалено".
    """

    def __init__(self, *args, **kwargs):
        self.show_deleted = kwargs.pop("show_deleted", False)
        super().__init__(*args, **kwargs)

    def get_queryset(self):
        return GlossaryQuerySet(self.model, using=self._db)\
            .filter(deleted=self.show_deleted)
