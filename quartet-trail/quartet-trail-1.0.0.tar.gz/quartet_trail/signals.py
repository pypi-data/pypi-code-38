from django.db.models.signals import post_save, pre_delete, pre_save
from django.dispatch import receiver
from quartet_masterdata import models as masterdata_models
from quartet_trail.middleware import LoggedInUser

# this receiver is executed every-time some data is saved in any table
@receiver(pre_save,  sender=masterdata_models.TradeItem)
def audit_log(sender, instance, **kwargs):
    # get the request.user
    try:
        import pudb; pudb.set_trace()        
        model_fields = sender._meta.get_all_field_names()
        model_name = str(sender)
        logged_in = LoggedInUser()
        user = logged_in.user

        table_pk = instance._meta.pk.name
        table_pk_value = instance.__dict__[table_pk]
        query_kwargs = dict()
        query_kwargs[table_pk] = table_pk_value
        prev_instance = sender.objects.get(**query_kwargs) # for dynamic column name
        changed = filter(lambda field: getattr(instance, field, None)!=getattr(prev_instance, field, None), my_model_fields)
    except:
        # this instance is being created and not updated. ignore and return
        #logging.getLogger("info_logger").info("Signals: creating new instance of "+str(sender))
        return

