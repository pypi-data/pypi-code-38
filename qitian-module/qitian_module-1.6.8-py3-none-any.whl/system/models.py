from django.db import models
from mptt.models import MPTTModel, TreeForeignKey
from django.contrib.sites.models import Site
from uuslug import slugify
from ueditor import UEditorField
from django.contrib.auth.models import User


class Menu(MPTTModel):
    site = models.ManyToManyField(Site, blank=True, verbose_name='所属站点')
    title = models.CharField('名称', max_length=128)
    alias = models.CharField('标签', max_length=32, blank=True)
    url = models.CharField('地址', max_length=255, blank=True)
    description = models.TextField('描述', blank=True, null=True)
    parent = TreeForeignKey('self', verbose_name='上级菜单', related_name='children', null=True, blank=True,
                            on_delete=models.SET_NULL)
    status = models.IntegerField('状态', choices={(1, '显示'), (2, '隐藏')}, default=1)
    sort = models.IntegerField('排序', default=1)
    type = models.IntegerField('类别', choices={(1, '店铺'), (2, '文章'), (3, '论坛')}, default=1)
    created = models.DateTimeField('创建时间', auto_now_add=True)
    updated = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        db_table = 'sys_menu'
        verbose_name = '菜单'
        verbose_name_plural = verbose_name + '管理'

    def __str__(self):
        return self.title


class Province(models.Model):
    name = models.CharField('省份', max_length=32)
    code = models.CharField('代码', max_length=32, blank=True)

    class Meta:
        verbose_name = '省份'
        verbose_name_plural = verbose_name + '管理'
        db_table = 'province'

    def __str__(self):
        return self.name


class City(models.Model):
    name = models.CharField('城市', max_length=32)
    province = models.ForeignKey('Province', verbose_name='所属省份', on_delete=models.CASCADE)

    class Meta:
        verbose_name = '城市'
        verbose_name_plural = verbose_name
        db_table = 'city'

    def __str__(self):
        return self.name


class Area(models.Model):
    name = models.CharField('区域', max_length=32)
    city = models.ForeignKey('City', on_delete=models.CASCADE)

    class Meta:
        verbose_name = '区域'
        verbose_name_plural = verbose_name + '管理'
        db_table = 'area'

    def __str__(self):
        return self.name


# 用户访问记录
class VisitLogs(models.Model):
    url = models.CharField('访问页面', max_length=128)
    ip = models.CharField('IP', max_length=32, blank=True)
    user_agent = models.CharField('User-Agent', max_length=255)
    plant_form = models.CharField('用户终端', max_length=255, blank=True)
    referrer = models.CharField('来源网站', max_length=255, blank=True)
    passport = models.CharField('用户地区', max_length=32, blank=True)
    created = models.DateTimeField('创建时间', auto_now_add=True)
    updated = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        db_table = 'sys_visit_log'
        verbose_name = '访问记录'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.url


class SmsCode(models.Model):
    mobile = models.CharField('手机', max_length=32)
    code = models.IntegerField('验证码')
    used = models.BooleanField('是否验证', default=False)
    ip = models.CharField('IP', max_length=32, blank=True)
    user_agent = models.CharField('User-Agent', max_length=255, blank=True)
    created = models.DateTimeField('创建时间', auto_now_add=True)
    updated = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        db_table = 'sys_sms_code'
        verbose_name = '验证码'
        verbose_name_plural = verbose_name + '管理'
        ordering = ['-id']

    def __str__(self):
        return self.mobile


class SiteProperty(models.Model):
    site = models.OneToOneField(Site, verbose_name='站点', on_delete=models.CASCADE)
    title = models.CharField('站点标题', max_length=128, blank=True)
    sub_title = models.CharField('副标题', max_length=128, blank=True)
    template = models.CharField('模板名称', max_length=64, blank=True)
    slug = models.SlugField('简称别名', help_text='图片、文件存储路径,为域名中间名称', max_length=64)
    meta_desc = models.TextField('描述', blank=True, null=True)
    meta_keywords = models.TextField('关键词', blank=True, null=True)
    scheme = models.BooleanField('HTTPS', default=True)
    logo = models.ImageField('LOGO', upload_to='upload/sites', blank=True, null=True)
    icon = models.ImageField('ICON', upload_to='upload/sites', blank=True, null=True)
    blocks = models.CharField('模块设定', max_length=255, help_text='使用英文,号分隔类别,:号后面为显示条数|分隔区块', blank=True, null=True)
    phone = models.CharField('联系电话', max_length=32, blank=True)
    email = models.CharField('Email', max_length=64, blank=True)
    qq = models.CharField('QQ', max_length=64, blank=True)
    address = models.CharField('地址', max_length=255, blank=True, null=True)
    beian = models.CharField('备案号', max_length=64, blank=True)
    baidu_verify = models.CharField('百度验证', max_length=64, blank=True)
    baidu_site_token = models.CharField('站点Token', max_length=64, blank=True, null=True)
    tongji = models.TextField('百度统计', blank=True)
    city = models.ForeignKey(City, on_delete=models.DO_NOTHING, verbose_name='所属城市', blank=True, null=True)
    notice = models.TextField('公告信息', blank=True, null=True)
    stand_mobile = models.BooleanField('独立移动站', choices=((True, '是'), (False, '否')), default=False)

    class Meta:
        db_table = 'sys_site_property'
        verbose_name = '站点信息'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.site.name

    @staticmethod
    def check_site_property(site):
        if not hasattr(site, 'siteproperty'):
            site_property = SiteProperty()
            site_property.site = site
            site_property.slug = slugify(site.name)
            site_property.title = site.name
            site_property.save()


# 友情链接
class Links(models.Model):
    site = models.ManyToManyField(Site, verbose_name='所属站点', blank=True)
    title = models.CharField('站点名称', max_length=64)
    domain = models.CharField('域名', max_length=128)
    desc = models.TextField('备注', blank=True, null=True)
    status = models.BooleanField('状态', choices=((1, '启用'), (0, '禁用')), default=1)
    created = models.DateTimeField('创建时间', auto_now_add=True)
    updated = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        db_table = 'sys_links'
        verbose_name = '友情链接'
        verbose_name_plural = verbose_name
        ordering = ['-id']

    def __str__(self):
        return self.title


class Notify(models.Model):
    """
    基于 https://www.jianshu.com/p/6bf8166b291c 文章进行数据结构设计
    Save Remind
    消息表，我们需要target、targetType字段，来记录该条提醒所关联的对象。而action字段，则记录该条提醒所关联的动作。
    比如消息：「小明喜欢了文章」
    则：

    target = 123,  // 文章ID
    targetType = 'post',  // 指明target所属类型是文章
    sender = 123456  // 小明ID
    Save Announce and Message
    当然，Notify还支持存储公告和信息。它们会用到content字段，而不会用到target、targetType、action字段。

    作者：JC_Huang
    链接：https://www.jianshu.com/p/6bf8166b291c
    來源：简书
    简书著作权归作者所有，任何形式的转载都请联系作者获得授权并注明出处。
    """
    NOTIFY_TYPE = (
        (1, '公告'),
        (2, '提醒'),
        (3, '消息'),
    )
    title = models.CharField('标题', max_length=128, blank=True, null=True)
    content = UEditorField('内容', blank=True, null=True)
    type = models.IntegerField('类别', choices=NOTIFY_TYPE)
    target = models.IntegerField('目标ID', blank=True, null=True)
    target_type = models.CharField('目标类型', max_length=32, blank=True, null=True)
    action = models.CharField('动作类型', max_length=32, blank=True, null=True)
    sender = models.ForeignKey(User, on_delete=models.DO_NOTHING, blank=True, null=True)
    created = models.DateTimeField('创建时间', auto_now_add=True)
    updated = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        db_table = 'sys_notify'
        verbose_name = '系统通知'
        verbose_name_plural = verbose_name
        ordering = ['-id']

    def __str__(self):
        return self.title if self.title else '[{type}]{who}{action}{target}'.format(
            type=self.get_type_display(),
            who=self.sender,
            action=self.action,
            target=self.target
        )


class UserNotify(models.Model):
    is_read = models.BooleanField('已读', default=False)
    user = models.ForeignKey(User, verbose_name='用户', on_delete=models.DO_NOTHING)
    notify = models.ForeignKey('Notify', verbose_name='通知', on_delete=models.DO_NOTHING)
    created = models.DateTimeField('创建时间', auto_now_add=True)
    updated = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        db_table = 'sys_user_notify'
        verbose_name = '用户通知'
        verbose_name_plural = verbose_name
        ordering = ['-id']

    def __str__(self):
        return self.user


# 消息订阅
class Subscription(models.Model):
    """
    订阅，是从Notify表拉取消息到UserNotify的前提，用户首先订阅了某一个目标的某一个动作，在此之后产生这个目标的这个动作的消息，才会被通知到该用户。
    如：「小明关注了产品A的评论」，数据表现为：

    target: 123,  // 产品A的ID
    targetType: 'product',
    action: 'comment',
    user: 123  // 小明的ID
    这样，产品A下产生的每一条评论，都会产生通知给小明了。

    作者：JC_Huang
    链接：https://www.jianshu.com/p/6bf8166b291c
    來源：简书
    简书著作权归作者所有，任何形式的转载都请联系作者获得授权并注明出处。
    """
    target = models.IntegerField('目标ID')
    target_type = models.CharField('目标类型', max_length=32)
    action = models.CharField('订阅动作', max_length=128, blank=True, null=True,
                              help_text='如: comment/like/post/update etc.')
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING, blank=True, null=True)
    created = models.DateTimeField('创建时间', auto_now_add=True)
    updated = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        db_table = 'sys_subscription'
        verbose_name = '消息订阅'
        verbose_name_plural = verbose_name
        ordering = ['-id']

    def __str__(self):
        return self.action


class SubscriptionConfig(models.Model):
    """
    defaultSubscriptionConfig: {
      'comment'   : true,    // 评论
      'like'      : true,    // 喜欢
    }
    """
    action = models.TextField('动作')
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    created = models.DateTimeField('创建时间', auto_now_add=True)
    updated = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        db_table = 'sys_subscription_config'
        verbose_name = '订阅设置'
        verbose_name_plural = verbose_name
        ordering = ['-id']

    def __str__(self):
        return self.user.username


class BaiduPushLog(models.Model):
    site = models.ForeignKey(Site, on_delete=models.DO_NOTHING)
    title = models.CharField('文章标题', max_length=255, blank=True, null=True)
    url = models.CharField('推送URL', max_length=255, blank=True, null=True)
    status = models.BooleanField('状态', choices=((True, '成功'), (False, '失败')))
    created = models.DateTimeField('创建时间', auto_now_add=True)
    updated = models.DateTimeField('更新时间', auto_now=True)

    class Meta:
        db_table = 'sys_baidu_push_log'
        verbose_name = '百度推送记录'
        verbose_name_plural = verbose_name
        ordering = ['-id']

    def __str__(self):
        return self.title
