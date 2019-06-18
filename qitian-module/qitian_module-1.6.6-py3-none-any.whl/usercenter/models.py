from django.db import models
from django.contrib.auth.models import User, Group
from django.db.models.signals import post_save
from django.core.exceptions import ObjectDoesNotExist
import time, random, pytz, datetime, logging
from django.contrib.sites.models import Site
from ueditor import UEditorField


class QtUser(models.Model):
    user = models.OneToOneField(User, related_name='qtuser', on_delete=models.CASCADE, null=True, default=None)
    site = models.ForeignKey(Site, on_delete=models.DO_NOTHING, blank=True, null=True)
    phone = models.CharField('手机号', max_length=32)
    qq = models.CharField('QQ', max_length=16, blank=True)
    nickname = models.CharField('昵称', max_length=128, blank=True, null=True)
    real_name = models.CharField('真实姓名', max_length=32, blank=True)
    alipay = models.CharField('支付宝', max_length=64, blank=True)
    email = models.EmailField('邮箱', blank=True)
    idcard = models.CharField('身份证', max_length=64, blank=True, null=True)
    type = models.IntegerField('类别', choices=((1, '广告主'), (2, '媒体主')), default=1)
    avatar = models.ImageField('头像', upload_to='avatar', blank=True, null=True)
    vip_expire = models.DateTimeField('VIP过期时间', blank=True, null=True)
    recommend = models.ForeignKey(User, related_name='recommend_user', verbose_name='推荐人', blank=True, null=True,
                                  on_delete=models.DO_NOTHING)
    created = models.DateTimeField('注册时间', auto_now_add=True)
    updated = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        db_table = 'qt_user'
        verbose_name = '用户'
        verbose_name_plural = verbose_name + '管理'

    def __str__(self):
        return self.phone

    @staticmethod
    def real_login_name(username, site):
        if username == 'navyhan':
            return username
        return '%s_%d' % (username, site.id)

    @staticmethod
    def user_available(phone, site):
        return QtUser.objects.filter(phone=phone).filter(site=site).exists()


def create_user_profile(sender, instance, created, **kwargs):
    if created:
        profile = QtUser()
        profile.phone = instance.username
        profile.nickname = instance.username
        profile.user = instance
        profile.save()
        # 初始化钱包
        wallet = Wallet()
        wallet.user = instance
        wallet.save()


post_save.connect(create_user_profile, sender=User)


class Wallet(models.Model):
    """
    用户钱包
    """
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name='wallet')
    money = models.FloatField('余额', default=0.00)
    pay_password = models.CharField('支付密码', max_length=128, blank=True, null=True)
    name = models.CharField('真实名称', max_length=64, blank=True, null=True)
    idcard = models.CharField('身份证', max_length=64, blank=True, null=True)
    created = models.DateTimeField('注册时间', auto_now_add=True)
    updated = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        db_table = 'wallet'
        verbose_name = '用户钱包'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.user.username


class WalletLog(models.Model):
    ORDER_TYPE = (
        (1, '预充值'),
        (2, '购买会员'),
        (3, '预定外围'),
        (4, '提现'),
    )

    record_sn = models.CharField('交易流水号', max_length=62)
    order_sn = models.CharField('订单号', max_length=63, blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name='wallet_log')
    change_money = models.FloatField('金额变动', default=0.00)
    remain = models.FloatField('余额', default=0.00)
    remark = models.CharField('备注', max_length=128, blank=True, null=True)
    type = models.IntegerField('变更类别', choices=ORDER_TYPE, default=1)
    pay_type = models.CharField('支付类别', max_length=32, blank=True, default='', null=True)
    created = models.DateTimeField('注册时间', auto_now_add=True)
    updated = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        db_table = 'wallet_log'
        verbose_name = '钱包记录'
        verbose_name_plural = verbose_name
        ordering = ['-id']

    def __str__(self):
        return self.record_sn

    @classmethod
    def create(cls, user, change_money, order_sn='', change_type=1, pay_type='', remark=''):
        # 检查订单号是不是被用过
        if WalletLog.objects.filter(order_sn=order_sn).filter(type=change_type).exists():
            return False
        wallet_log = cls(user=user, type=change_type, order_sn=order_sn, change_money=change_money, pay_type=pay_type,
                         remark=remark)
        wallet_log.record_sn = time.strftime('%Y%m%d%H%M%S') + str(random.randint(100, 999))
        wallet_log.save()
        return wallet_log


# 更新用户钱包余额
def update_wallet(sender, instance, created, **kwargs):
    if created:
        try:
            wallet = Wallet.objects.filter(user=instance.user).get()
        except ObjectDoesNotExist:
            wallet = Wallet()
            wallet.user = instance.user
        wallet.money = wallet.money + float(instance.change_money)
        wallet.save()
        instance.remain = wallet.money
        instance.save()


post_save.connect(update_wallet, sender=WalletLog)


class GroupProperty(models.Model):
    group = models.OneToOneField(Group, on_delete=models.CASCADE)
    summery = models.TextField('简介', blank=True, null=True)
    duration = models.IntegerField('会员时长', help_text='单位为天', default=30)
    price = models.IntegerField('价格', help_text='单位为元', blank=True, default=98)
    content = UEditorField('内容', blank=True, null=True)
    recommend = models.BooleanField('推荐', default=False)
    created = models.DateTimeField('注册时间', auto_now_add=True)
    updated = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        db_table = 'group_property'
        verbose_name = '会员属性'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.group.name


class VipLogs(models.Model):
    """
    用户VIP购买记录
    """
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    group = models.ForeignKey(Group, on_delete=models.DO_NOTHING)
    site = models.ForeignKey(Site, on_delete=models.DO_NOTHING)
    order = models.ForeignKey('Orders', on_delete=models.DO_NOTHING, blank=True, null=True)
    paid = models.FloatField('购买金额')
    buy_type = models.IntegerField('购买类型', choices=((1, '充值'), (2, '余额'), (3, '积分')))
    created = models.DateTimeField('购买时间', auto_now_add=True)
    updated = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        db_table = 'vip_logs'
        verbose_name = 'VIP记录'
        verbose_name_plural = verbose_name
        ordering = ['-id']

    def __str__(self):
        return self.user.username

    @staticmethod
    def add_log(order_sn, buy_type):
        logger = logging.getLogger('django')
        order = Orders.objects.get(order_sn=order_sn)
        if VipLogs.objects.filter(order=order).exists():
            logger.info('订单已存在.')
            return False
        vip_log = VipLogs()
        user_group = Group.objects.get(id=order.goods)
        vip_log.user = order.user
        vip_log.group = user_group
        vip_log.order = order
        vip_log.site = order.site
        vip_log.paid = order.amount
        vip_log.buy_type = buy_type
        return vip_log.save()


def update_vip_expire(sender, instance, created, **kwargs):
    if not created:
        return False
    user = instance.user.qtuser
    duration = instance.group.groupproperty.duration
    if not user.vip_expire or pytz.UTC.localize(datetime.datetime.now()) > user.vip_expire:
        user.vip_expire = pytz.UTC.localize(datetime.datetime.now()) + datetime.timedelta(
            days=duration)
    else:
        user.vip_expire += datetime.timedelta(days=duration)
    # 扣除用户余额
    user.save()
    # 用户先退出所有组
    instance.user.groups.clear()
    instance.user.groups.add(instance.group)
    WalletLog.create(instance.user, -instance.order.amount, instance.order.order_sn, 2, '余额', instance.group.name)
    return True


# 购买VIP卡的时候,同步更新用户VIP过期时间
post_save.connect(update_vip_expire, sender=VipLogs)


class Orders(models.Model):
    order_sn = models.CharField('订单号', unique=True, max_length=128)
    site = models.ForeignKey(Site, verbose_name='所属站点', on_delete=models.DO_NOTHING, blank=True, null=True)
    goods = models.IntegerField('商品ID')
    type = models.IntegerField('购买类别', choices=((1, '会员'), (2, '楼凤'), (3, '预定'), (4, '充值')))
    amount = models.FloatField('金额')
    status = models.IntegerField('状态', choices=((1, '待付款'), (2, '已付款'), (3, '已作废')), default=1)
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING, blank=True, null=True)
    pay_type = models.CharField('支付方式', max_length=32, default='支付宝')
    created = models.DateTimeField('购买时间', auto_now_add=True)
    updated = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        db_table = 'orders'
        verbose_name = '订单'
        verbose_name_plural = verbose_name + '管理'
        ordering = ['-id']

    def __str__(self):
        return self.order_sn

    @property
    def gen_sn(self):
        return time.strftime('%Y%m%d%H%M%S') + str(random.randint(100, 999))

    @classmethod
    def create(cls):
        order = cls()
        order.order_sn = order.gen_sn
        return order
