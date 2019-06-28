# -*- coding: utf-8 -*-
from django import forms
from django.contrib.contenttypes.models import ContentType
from django.core import exceptions
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models.fields.related import resolve_relation, lazy_related_operation
from django.db.models.fields.related_descriptors import ManyToManyDescriptor
from django.db.models.utils import make_model_tuple
from django.forms.boundfield import BoundField
from django.utils import timezone
from django.utils.functional import curry
from polymorphic.base import PolymorphicModelBase

from .widgets import PolymorphicWidget, FormSetWidget


def validateDateLTEToday(value):
    today = timezone.now().date()
    if value > today:
        raise ValidationError('Data não pode ser futura.')


class AutoCreatedAtField(models.DateTimeField):
    """ Campo de data e hora automáticos. Para campos modified_at """

    def __init__(self, *args, **kwargs):
        # kwargs.setdefault('editable', False)
        kwargs.setdefault('default', timezone.now)
        super().__init__(*args, **kwargs)


class AutoModifiedAtField(AutoCreatedAtField):
    """ Campo de data e hora automáticos. Para campos modified_at """

    def pre_save(self, model_instance, add):
        value = timezone.now()
        if not model_instance.pk:
            for field in model_instance._meta.get_fields():
                if isinstance(field, AutoCreatedAtField):
                    value = getattr(model_instance, field.name)
                    break
        setattr(model_instance, self.attname, value)
        return value


class AnnotateBoundField(BoundField):
    """
    Retorna o valor de um campo da instância corrente, mesmo que seja um campo annotate do queryset.
    Usado quando há necessidade de ter um campo duas vezes no mesmo form ou se for um campo via annotate.
    """

    def value(self):
        """
        Returns the value for this BoundField, using the initial value if
        the form is not bound or the data otherwise.
        """
        try:
            # Retorna um campo da instância corrente se houver, senão usar o padrão de BoundField
            return getattr(self.form.instance, self.name)
        except:
            return super().value()


class AnnotateField(forms.Field):
    """
    Usado quando há necessidade de mostrar um campo via annotate da queryset e o Crispy não faz o tratamento correto.
    Ex.: Campo de seguro de incêndio no popup de dados do contrato de locação SKW
    """

    def get_bound_field(self, form, field_name):
        """
        Return a BoundField instance that will be used when accessing the form
        field in a template.
        """
        return AnnotateBoundField(form, self, field_name)


def create_many_to_many_protected_intermediary_model(field, klass):
    """ Gera o Meta: para criação de ManyToManyField """

    def set_managed(model, related, through):
        through._meta.managed = model._meta.managed or related._meta.managed

    to_model = resolve_relation(klass, field.remote_field.model)
    name = '%s_%s' % (klass._meta.object_name, field.name)
    lazy_related_operation(set_managed, klass, to_model, name)

    to = make_model_tuple(to_model)[1]
    from_ = klass._meta.model_name
    if to == from_:
        to = 'to_%s' % to
        from_ = 'from_%s' % from_

    meta = type(str('Meta'), (object,), {
        'db_table': field._get_m2m_db_table(klass._meta),
        'auto_created': klass,
        'app_label': klass._meta.app_label,
        'db_tablespace': klass._meta.db_tablespace,
        'unique_together': (from_, to),
        'verbose_name': '%(from)s-%(to)s relationship' % {'from': from_, 'to': to},
        'verbose_name_plural': '%(from)s-%(to)s relationships' % {'from': from_, 'to': to},
        'apps': field.model._meta.apps,
    })
    # Construct and return the new class.
    return type(str(name), (models.Model,), {
        'Meta': meta,
        '__module__': klass.__module__,
        from_: models.ForeignKey(
            klass,
            related_name='%s+' % name,
            db_tablespace=field.db_tablespace,
            db_constraint=field.remote_field.db_constraint,
            on_delete=models.CASCADE,
        ),
        to: models.ForeignKey(
            to_model,
            related_name='%s+' % name,
            db_tablespace=field.db_tablespace,
            db_constraint=field.remote_field.db_constraint,
            on_delete=models.PROTECT,
        )
    })


class ManyToManyProtectedField(models.ManyToManyField):
    """ Equivalente ao ManyToManyField exceto que não permite a exclusão de um registro que
        tem relacionamento many to many. """

    def contribute_to_class(self, cls, name, **kwargs):
        # To support multiple relations to self, it's useful to have a non-None
        # related name on symmetrical relations for internal reasons. The
        # concept doesn't make a lot of sense externally ("you want me to
        # specify *what* on my non-reversible relation?!"), so we set it up
        # automatically. The funky name reduces the chance of an accidental
        # clash.
        if self.remote_field.symmetrical and (
                self.remote_field.model == "self" or self.remote_field.model == cls._meta.object_name):
            self.remote_field.related_name = "%s_rel_+" % name
        elif self.remote_field.is_hidden():
            # If the backwards relation is disabled, replace the original
            # related_name with one generated from the m2m field name. Django
            # still uses backwards relations internally and we need to avoid
            # clashes between multiple m2m fields with related_name == '+'.
            self.remote_field.related_name = "_%s_%s_+" % (cls.__name__.lower(), name)

        super(models.ManyToManyField, self).contribute_to_class(cls, name, **kwargs)

        # The intermediate m2m model is not auto created if:
        #  1) There is a manually specified intermediate, or
        #  2) The class owning the m2m field is abstract.
        #  3) The class owning the m2m field has been swapped out.
        if not cls._meta.abstract:
            if self.remote_field.through:
                def resolve_through_model(_, model, field):
                    field.remote_field.through = model

                lazy_related_operation(resolve_through_model, cls, self.remote_field.through, field=self)
            elif not cls._meta.swapped:
                self.remote_field.through = create_many_to_many_protected_intermediary_model(self, cls)

        # Add the descriptor for the m2m relation.
        setattr(cls, self.name, ManyToManyDescriptor(self.remote_field, reverse=False))

        # Set up the accessor for the m2m table name for the relation.
        self.m2m_db_table = curry(self._get_m2m_db_table, cls._meta)


class FormSetBoundField(BoundField):
    def __init__(self, form, field, name):
        super().__init__(form, field, name)
        field.widget.form = form
        # field.widget.field = field
        if not form.is_bound:
            self.formset = field.widget.get_formset(
                instance=form.instance,
                prefix=form.add_prefix(name),
                initial=form.initial.get(name, field.initial),
            )
        else:
            self.formset = field.widget.get_formset(
                data=form.data,
                files=form.files,
                instance=form.instance,
                prefix=form.add_prefix(name),
            )

    def value(self):
        """
        Returns the value for this BoundField, using the initial value if
        the form is not bound or the data otherwise.

        Só é mostrado no GET

        Se self.form.is_bound então o form foi preenchido através de data,
        senão ele será preenchido através do initial

        Se entendi bem, então se form.instance está preenchido, mas is_bound = false, o initial vem com os dados
        originais do BD
        """
        # if not hasattr(self.form.instance._meta.get_field(self.name), 'related') and
        if not hasattr(self.form.instance._meta.get_field(self.name), 'remote_field') and not (
                self.form.instance._meta.get_field(self.name).many_to_many or
                self.form.instance._meta.get_field(self.name).many_to_one or
                self.form.instance._meta.get_field(self.name).one_to_many):
            raise exceptions.ImproperlyConfigured('Campo não é FK ou M2M ou M2O')

        data = self.formset

        return self.field.prepare_value(data)

    # def label_tag(self, contents=None, attrs=None):
    #     raise NotImplementedError

    # def css_classes(self, extra_classes=None):
    #     raise NotImplementedError

    def __iter__(self):
        return self.formset.__iter__()


class FormSetField(forms.Field):
    widget = FormSetWidget

    def __init__(self, formset_class, *args, **kwargs):
        self.formset_class = formset_class
        # self.related = kwargs.pop('related', None)
        self.show_add_button = kwargs.pop('show_add_button', True)
        self.template_name = kwargs.pop('template_name', 'formsetfield/formsetfield.html')
        # self.btnbutton = kwargs.pop('btnbutton', 'success')
        widget = kwargs.pop('widget',
                            self.widget(
                                attrs={'formset_class': self.formset_class,
                                       # 'related': self.related,
                                       'show_add_button': self.show_add_button,
                                       'template_name': self.template_name,
                                       }))

        super().__init__(formset_class, widget=widget, *args, **kwargs)
        self.widget.formset_class = formset_class

    def clean(self, formset):
        if formset.is_valid():
            self.validate(formset)
            self.run_validators(formset)
            return formset.cleaned_data
        raise forms.ValidationError(formset.errors)

    def validate(self, value):
        if not value.is_valid():
            if self.error_messages and 'invalid' in self.error_messages:
                raise ValidationError(self.error_messages['invalid'])
            else:
                raise ValidationError(code='invalid', message='Invalid input')

    def get_bound_field(self, form, field_name):
        return FormSetBoundField(form, self, field_name)
        # equivalente a super(FormSetField, self).get_bound_field(form, field_name)

    def widget_attrs(self, widget):
        attrs = super().widget_attrs(widget)
        # attrs.update({'formset_class': self.formset_class, 'template_name': self.template_name, 'btnbutton': self.btnbutton})
        attrs.update({'formset_class': self.formset_class, 'template_name': self.template_name})
        return attrs

    def save(self, instance, formset, attname):
        formset.related_name = self.related_name or attname
        formset.related_instance = instance
        formset.save()

    # Baseado em dal_gm2m para dal.forms.FutureModelForm que é a base do CommonModelForm
    def value_from_object(self, instance, name):
        """Return the list of related objects."""
        try:
            if getattr(instance, name):
                return [x.id for x in getattr(instance, name).all()]
        except Exception:
            try:
                return [getattr(instance, name).id]
            except Exception:
                pass
        return []

    def save_relation_data(self, instance, name, value):
        """Update the relation to be ``value``."""
        # instance_field = getattr(instance, name)
        keys = ['id', 'DELETE']
        instance_field = instance._meta.get_field(name)

        # if hasattr(instance_field, 'through'):
        if instance_field.many_to_many:
            # instance_field = proprietarios
            # Delete all relations - Deleta todas as relações associadas a instancia
            source_field = instance_field.remote_field.name
            if hasattr(instance, name):
                instance_field = getattr(instance, name)
            instance_field.clear()  # Delete all instance of relation m2m
            # Re-Cria relação uma a uma
            for dic in value:
                if not dic.get('DELETE', False):
                    dic_ok = {key: val for key, val in dic.items()
                              if (key not in keys and
                                  not (instance_field.through._meta.get_field(key).many_to_many
                                       # or instance_field.through._meta.get_field(key).many_to_one
                                       # or instance_field.through._meta.get_field(key).one_to_many
                                       ))}
                    dic_nok = {key: value for key, value in dic.items() if key not in dic_ok and key not in keys}
                    obj = self.formset_class.model(**dic_ok)
                    setattr(obj, source_field, instance)
                    obj.save()
                    for key, val in dic_nok.items():
                        for n in val:
                            if not n.get('DELETE', False):
                                # Ajusta through object para a nova instância, pois a antiga foi excluida em
                                # instance_field.clear()
                                n[instance_field.through._meta.get_field(key).m2m_field_name()] = obj
                                # self.formset_class.form.base_fields['beneficiarios'].formset_class ==> pega formclass
                                # do campo para o qual foi feito o ajuste do key
                                dic_nok_ok = {k: v for k, v in n.items()
                                              if (k not in keys
                                                  and not getattr(obj, key).through._meta.get_field(k).many_to_many)}
                                obj_f = self.formset_class.form.base_fields[key].formset_class.model(**dic_nok_ok)
                                obj_f.save()
        elif instance_field.one_to_many:
            source_field = instance_field.remote_field.name
            instance_field = getattr(instance, instance_field.get_accessor_name(), None)
            # if hasattr(instance, name):
            #     instance_field = getattr(instance, name)
            updt = False
            try:
                instance_field.clear()
            except Exception:
                # Possivelmente campo de FormSetField em classe.
                # Ex.: a classe Municipio tem uma FK para Estado, seria um update do campo municipio de objeto de Estado
                updt = True
            cls = instance_field.model
            # cls = self.formset_class.model

            for dic in value:
                if dic.get('DELETE', False):
                    obj = dic.get(cls._meta.pk.name)
                    # Se não for herança da PolymorphicModelBase, então prossegue conforme original do FormSetField
                    # Senão obj já tem o objeto a ser excluído
                    if not isinstance(cls, PolymorphicModelBase):
                        obj = cls.objects.get(pk=obj.pk if isinstance(obj, models.Model) else obj)
                    if obj:
                        obj.delete()
                else:
                    cls = self.formset_class.model
                    if dic.get('polymorphic_ctype', None) and not isinstance(dic['polymorphic_ctype'], ContentType):
                        dic['polymorphic_ctype'] = ContentType.objects.get_for_id(dic['polymorphic_ctype'])
                        cls = dic['polymorphic_ctype'].model_class()

                    dic_ok = {key: val for key, val in dic.items()
                              if (key not in keys and
                                   not (cls._meta.get_field(key).many_to_many
                                       # instance_field.through._meta.get_field(key).many_to_many
                                       # or instance_field.through._meta.get_field(key).many_to_one
                                       # or instance_field.through._meta.get_field(key).one_to_many
                                       ))}
                    dic_nok = {key: value for key, value in dic.items() if key not in dic_ok and key not in keys}

                    obj = dic.get(cls._meta.pk.name, None)
                    # Tentativa de incluir id quando for primary key,
                    # pois está fazendo insert no lugar de update quando id é primary key, pois está em "keys"
                    if not updt and obj:
                        try:
                            updt = cls._meta.get_field('id').primary_key
                        except:
                            pass

                    if updt and isinstance(obj, models.Model):
                        # info = cls._meta.get_field_info(obj)
                        for attr, v in dic_ok.items():
                            # if attr in info.relations and info.relations[attr].to_many:
                            #     field = getattr(obj, attr)
                            #     field.set(v)
                            # else:
                            #     setattr(obj, attr, v)
                            setattr(obj, attr, v)
                    else:
                        # obj = self.formset_class.model(**dic_ok)
                        obj = cls(**dic_ok)
                        setattr(obj, source_field, instance)
                    obj.save()
                    for key, val in dic_nok.items():
                        for n in val:
                            if len(n) and not n.get('DELETE', False):
                                # Ajusta through object para a nova instância, pois a antiga foi excluida em
                                # instance_field.clear()
                                n[cls._meta.get_field(key).m2m_field_name()] = obj
                                # n[instance_field.through._meta.get_field(key).m2m_field_name()] = obj
                                # self.formset_class.form.base_fields['beneficiarios'].formset_class ==> pega formclass
                                # do campo para o qual foi feito o ajuste do key
                                dic_nok_ok = {k: v for k, v in n.items()
                                              if (k not in keys
                                                  and not getattr(obj, key).through._meta.get_field(k).many_to_many)}
                                obj_f = cls._meta.get_field(key).rel.through(**dic_nok_ok)
                                # obj_f = self.formset_class.form.base_fields[key].formset_class.model(**dic_nok_ok)
                                obj_f.save()
        elif instance_field.one_to_one:
            # pass
            cls = self.formset_class.model
            for related in value:
                if related.get('DELETE', False):
                    obj = cls.objects.get(pk=related.get('id'))
                    obj.delete()
                else:
                    d = {k: v for k, v in related.items() if k not in keys}
                    try:
                        pk_name = cls._meta.pk.name
                        pk = getattr(related.get(pk_name), pk_name)  # só o id, não o objeto
                        cls.objects.filter(pk=pk).update(**d)  # faz o update com os dados do form
                    except Exception as e:
                        # se deu erro então tenta inclusão
                        obj = cls(**d)
                        obj.save()
        else:
            for related in instance_field.all():
                if related.object not in value:
                    instance_field.remove(related)

            for related in value:
                instance_field.connect(related)

    def save_form_data(self, instance, data):
        setattr(instance, self.name, data)
        raise NotImplementedError


class PolymorphicBoundField(FormSetBoundField):
    def __init__(self, form, field, name):
        # super().__init__(form, field, name)
        BoundField.__init__(self, form, field, name)
        field.widget.form = form
        # field.widget.field = field
        if not form.is_bound:
            self.formset = field.widget.get_formset(
                instance=form.instance,
                prefix=form.add_prefix(name),
                # prefix=name,
                initial=form.initial.get(name, field.initial),
            )
        else:
            self.formset = field.widget.get_formset(
                data=form.data,
                files=form.files,
                instance=form.instance,
                prefix=form.add_prefix(name),
                # prefix=name,
            )


class PolymorphicField(FormSetField):
    """
    Layout object, mostra um formset associado a uma FK, M2M ou O2O para Polymorphic Models.
    """

    widget = PolymorphicWidget

    def get_bound_field(self, form, field_name):
        return PolymorphicBoundField(form, self, field_name)
