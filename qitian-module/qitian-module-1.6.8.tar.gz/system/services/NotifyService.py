from system.models import Notify


# 往Notify表中插入一条公告记录
def create_announce(title, content, sender=None):
    notify = Notify()
    notify.title = title
    notify.content = content
    if sender:
        notify.sender = sender
    notify.type = 1
    notify.save()


# 往Notify表中插入一条提醒记录
def create_remind(title, target, targetType, action, sender, content):
    pass


# 往Notify表中插入一条信息记录
# 往UserNotify表中插入一条记录，并关联新建的Notify
def create_message(title, content, sender, receiver):
    pass
