import uuid

from django.db import models

from glossary.queryset import GlossaryManager


class GlossaryModel(models.Model):
    """
    Набор полей и методов для всех данных, которые
    нужно синхронизировать между основной копией и репликами.

    'uuid' - уникальный идентификатор, не зависящий от конкретной БД.
    'deleted' - метка "удален". Модели-наследники не удаляются
    насовсем, а скрываются при обычных запросах.
    """
    uuid = models.UUIDField(
        editable=False, default=uuid.uuid4, unique=True
    )
    deleted = models.BooleanField(default=False)

    objects = GlossaryManager()
    deleted_objects = GlossaryManager(show_deleted=True)
    all_objects = models.Manager()

    class Meta:
        abstract = True

    def delete(self):
        self.deleted = True
        self.save()

    def force_delete(self):
        return super().delete()

    def dump(self):
        data = {}
        for field in self._meta.fields:
            if isinstance(field, models.AutoField):
                continue
            elif isinstance(field, models.ForeignKey):
                related = getattr(self, field.name)
                if related:
                    related_uuid = str(related.uuid)
                    data[field.name] = related_uuid
            elif isinstance(field, models.UUIDField):
                data[field.name] = str(getattr(self, field.name))
            else:
                data[field.name] = getattr(self, field.name)
        return data

    @classmethod
    def clean_dump_data(cls, data):
        for field in cls._meta.fields:
            if isinstance(field, models.AutoField):
                continue
            elif isinstance(field, models.ForeignKey):
                related_model = field.related_model
                if field.name in data:
                    related_uuid = data[field.name]
                    related = related_model.all_objects.get(uuid=related_uuid)
                    data[field.name] = related
        return data

    @classmethod
    def get_foreign_key_count(cls):
        fk_count = 0
        for field in cls._meta.fields:
            if isinstance(field, models.ForeignKey):
                fk_count += 1
        return fk_count


class Faculty(GlossaryModel):
    name = models.CharField(verbose_name="Название", max_length=127)

    class Meta:
        verbose_name = "Факультет"
        verbose_name_plural = "Факультеты"

    def __str__(self):
        return self.name


class Department(GlossaryModel):
    name = models.CharField(verbose_name="Название", max_length=127)
    faculty = models.ForeignKey(Faculty, verbose_name="Факультет", on_delete=models.CASCADE)

    class Meta:
        verbose_name = "Кафедра"
        verbose_name_plural = "Кафедры"

    def __str__(self):
        return "{} - {}".format(self.faculty, self.name)


class AcademicGroup(GlossaryModel):
    FIRST = 1
    SECOND = 2
    THIRD = 3
    FOURTH = 4
    FIFTH = 5
    SIXTH = 6
    YEAR_CHOICES = (
        (FIRST, "Первый"),
        (SECOND, "Второй"),
        (THIRD, "Третий"),
        (FOURTH, "Четвертый"),
        (FIFTH, "Пятый"),
        (SIXTH, "Шестой"),
    )
    name = models.CharField(verbose_name="Название", max_length=127)
    faculty = models.ForeignKey(Faculty, verbose_name="Факультет", on_delete=models.CASCADE)
    year = models.SmallIntegerField(
        verbose_name="Курс", default=FIRST, choices=YEAR_CHOICES
    )
    dekid = models.IntegerField(verbose_name="ID в Деканате", default=0)

    class Meta:
        verbose_name = "Академическая группа"
        verbose_name_plural = "Академические группы"

    def __str__(self):
        return "{} - {}".format(self.faculty, self.name)
