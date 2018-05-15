from django.db import models
from django.utils import timezone
import django.contrib.auth.models as user_model
from django.conf import settings
from django.contrib.auth.models import User
from django.db.models.signals import post_save


# 学院
class Collage(models.Model):
    name = models.CharField(max_length=150, verbose_name="学院名称")
    desc = models.CharField(max_length=150, verbose_name="学院介绍")

    class Meta:
        verbose_name = "学院"
        verbose_name_plural = '学院'

    def __str__(self):
        return self.name


# 课程
# class Class(models.Model):
#     name = models.CharField(max_length=150, verbose_name="课程名称")
#     desc = models.CharField(max_length=150, verbose_name="课程介绍")
#     cash = models.IntegerField(verbose_name="课程金额")
#     is_math = models.BooleanField(default=False, verbose_name="是否为数学类课程")
#
#     class Meta:
#         verbose_name = "课程"
#         verbose_name_plural = '课程'
#
#     def ___unicode__(self):
#         return self.name
#

# 专业
class Major(models.Model):
    name = models.CharField(max_length=150, verbose_name="专业名称")
    desc = models.TextField(verbose_name="专业介绍")
    # classes = models.ManyToManyField('Class', blank=True, verbose_name="课程")
    type = models.CharField(max_length=50, verbose_name="学制", default="两年")
    collage = models.ForeignKey("Collage", verbose_name="申请学院", on_delete=models.DO_NOTHING,default="")
    studentcount = models.CharField(max_length=50, verbose_name="专业接纳人数", default="0")
    # is_double = models.BooleanField(default=True, verbose_name="是否双专业")
    class Meta:
        verbose_name = "专业"
        verbose_name_plural = '专业'

    def __str__(self):
        return self.name


# 用户信息
class Profile(models.Model):
    SHIRT_SEX = (
        ('M', '男'),
        ('W', '女'),
    )
    user = models.OneToOneField(User, on_delete=models.DO_NOTHING)
    major = models.ForeignKey("Major", null=True, blank=True, verbose_name="专业", on_delete=models.DO_NOTHING,default="")
    collage = models.ManyToManyField("Collage", blank=True, verbose_name="学院")
    number = models.CharField(max_length=150, verbose_name="学号/工号", default="", blank=True, null=True)
    name = models.CharField(max_length=150, verbose_name="姓名", default="", blank=True, null=True)
    sex = models.CharField(max_length=3, verbose_name="性别", choices=SHIRT_SEX)
    session = models.CharField(max_length=150, verbose_name="年级", default="", blank=True, null=True)
    phone = models.CharField(max_length=150, verbose_name="联系电话", default="", blank=True, null=True)
    homeaddr = models.CharField(max_length=150, verbose_name="家庭住址", default="", blank=True, null=True)

    class Meta:
        verbose_name = "学生/员工资料"
        verbose_name_plural = '学生/员工资料'

    def __str__(self):
        return  "%s's profile" % self.user


def create_user_profile(sender, instance, created, **kwargs):
    if created:
        profile, created = Profile.objects.get_or_create(user=instance)


post_save.connect(create_user_profile, sender=User)


# 第二专业申请表
class Approve(models.Model):
    # 默认为当前用户
    user = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, null=True, verbose_name="申请人",
                             on_delete=models.DO_NOTHING,default="")
    # is_cashed = models.BooleanField(default=False, verbose_name="是否缴费")
    submit_time = models.DateTimeField(auto_now_add=True, verbose_name="提交时间")
    # submit_time = models.DateTimeField(default=timezone.now, verbose_name="提交时间")
    major = models.ForeignKey("Major", verbose_name="申请专业", on_delete=models.DO_NOTHING,default="")
    # status = models.IntegerField(default=0, verbose_name="状态")
    has_math = models.BooleanField(verbose_name="是否有数学类课程")
    detail = models.TextField(verbose_name="数学具体课程", default="",null=True,blank=True)
    is_first = models.BooleanField(verbose_name="是否第一次修读")
    is_approved = models.NullBooleanField(blank=True, null=True, default=None, verbose_name="是否通过审核")
    is_interviewed = models.NullBooleanField(blank=True, default=None, verbose_name="是否通过面试")
    is_changed = models.NullBooleanField(blank=True, default=None, verbose_name="是否调剂")
    is_cashed = models.NullBooleanField(blank=True, default=None, verbose_name="是否扣款")
    suggest = models.TextField(verbose_name="审核意见", null=True,blank=True,default="")
   # studentcount = models.ForeignKey(Major.studentcount, blank=True, verbose_name="专业接纳能力",on_delete=models.DO_NOTHING)
    class Meta:
        verbose_name = "申请表"
        verbose_name_plural = '申请表'

    def __str__(self):
        return str(self.submit_time)


# 扣款记录 双专业或双学位学生交费情况记录表
# class CashFlow(models.Model):
#     user = models.CharField(max_length=150, verbose_name="学生名称")  # 换成user的外键
#     cash_time = models.DateTimeField(default=timezone.now, verbose_name="扣款时间")
#     cash_amount = models.DecimalField(default=0.0, max_digits=6, decimal_places=2, verbose_name="课程金额")
#     cash_free_amount = models.DecimalField(default=0.0, max_digits=6, decimal_places=2, verbose_name="减免金额")
#     cash_platform_id = models.CharField(max_length=50, verbose_name="支付平台流水号")
#     cash_platform_type = models.CharField(max_length=50, verbose_name="支付平台类型")
#     approve = models.ForeignKey("Approve", blank=True, null=True, verbose_name="申请表", on_delete=models.CASCADE)
#     cash_remark = models.CharField(max_length=50, verbose_name="备注", null=True, blank=True)
#
#     class Meta:
#         verbose_name = "扣款记录"
#         verbose_name_plural = '扣款记录'
#
#     def __str__(self):
#         return str(self.cash_time)


# 双专业或双学位学生信息记录表
class Record(models.Model):
    # 扣费成功的学生要生成到“双专业或双学位学生信息记录表”中，这个记录表会记录每个学生的基本情况
    user = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, null=True, verbose_name="申请人",
                             on_delete=models.DO_NOTHING,default="")
    major = models.ForeignKey("Major", verbose_name="申请专业", on_delete=models.DO_NOTHING,default="")
    time = models.DateTimeField(default=timezone.now, verbose_name="提交时间")
    collage = models.ForeignKey("Collage", verbose_name="申请学院", on_delete=models.DO_NOTHING, default="")

    class Meta:
        verbose_name = "双学位学生信息记录表"
        verbose_name_plural = '双学位学生信息记录表'

    def __str__(self):
        return str(self.time)


class UploadFile(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, null=True, verbose_name="通知人",
                             on_delete=models.DO_NOTHING,default="")
    upload_file = models.FileField(upload_to='upload_dir', verbose_name="专业培养方案")
    desc = models.TextField(verbose_name="通知内容", default="")

    class Meta:
        verbose_name = "通知栏"
        verbose_name_plural = '通知栏'

    def __str__(self):
        return str(self.user) + str(self.upload_file) + str(self.desc)
