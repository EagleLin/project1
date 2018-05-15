from collections import OrderedDict

from django.contrib import admin
from django.contrib import messages
from django.http import FileResponse
from django.utils.encoding import escape_uri_path
from django.utils.http import urlquote

from major.models import *
from django.core.exceptions import ValidationError
from django.http import HttpResponse
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from django import forms
from .models import Profile
from django.shortcuts import redirect

# Register your models here.
admin.site.site_title = "第二专业报名系统"
admin.site.site_header = '第二专业报名系统'
def delete_user(modeladmin, request, queryset):
    # 插入流水表
    # 插入显示结果表
   # a= Profile.objects.get(id=queryset[0].user_id.i)
    Profile.objects.filter(id=str(queryset[0].id)).delete()
    User.objects.filter(id=str(queryset[0].id)).delete()

# 用户模型扩展
class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'Profile'
    fk_name = 'user'


class CustomUserAdmin(UserAdmin):
    inlines = (ProfileInline,)
    list_display = ('username', 'is_staff')

    def get_actions(self, request):
        # 根据用户角色来获取动作
        actions = super(CustomUserAdmin, self).get_actions(request)
        if request.user.groups.filter(name__in=['student']).exists():
            actions = []
        else:
            actions.update(delete_user=(delete_user, 'delete_user', '删除用户信息'))
        return actions
    def get_inline_instances(self, request, obj=None):
        if not obj:
            return list()
        return super(CustomUserAdmin, self).get_inline_instances(request, obj)


admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)

# 注册数据模型  以供后台进行编辑操作
admin.site.register(Collage)
# admin.site.register(Class)

class MajorAdmin(admin.ModelAdmin):
    list_display = ('name', 'desc','studentcount')
admin.site.register(Major,MajorAdmin)


# casher 扣款流水表 
# 改动的地方为 自动根据请求的参数（approve_id）来初始化值
# class CashFlowAdminForm(forms.ModelForm):
#     class Meta:
#         model = CashFlow
#         fields = '__all__'


# class CashFlowAdmin(admin.ModelAdmin):
#     def get_form(self, request, obj=None, *args, **kwargs):
#         form = super(CashFlowAdmin, self).get_form(request, *args, **kwargs)
#         approve_id = request.GET.get('approve_id')
#         if approve_id is not None:
#             approve = Approve.objects.get(id=approve_id)
#             form.base_fields['approve'].initial = approve
#             form.base_fields['user'].initial = approve.user.profile.name
#             cash = 0
#             # 添加课程金额
#             for i in approve.major.classes.all():
#                 cash += i.cash
#             form.base_fields['cash_amount'].initial = cash
#         return form
#
#     def save_model(self, request, obj, form, change):
#         # 申请表 改为已扣款
#         obj.approve.is_cashed = True
#         obj.approve.save()
#         # 在添加扣款记录的同时  添加双学位信息记录表  同步
#         record = Record(
#             user=obj.approve.user,
#             major=obj.approve.major,
#             collage=obj.approve.major.collage
#         )
#         record.save()
#         super(CashFlowAdmin, self).save_model(request, obj, form, change)
#
#
# admin.site.register(CashFlow, CashFlowAdmin)


# 抽象动作 批量生成：审批、面试、调剂等动作
def make_process(desc, field, status=True, group='collage'):
    def f(modeladmin, request, queryset):
        queryset.update(**{str(field): status})

    f.short_description = str(desc)
    f.__name__ = "f" + str(field) + str(status)
    return f


def make_cash(modeladmin, request, queryset):
    # 插入流水表
    # 插入显示结果表
    queryset.update(**{"is_cashed": True})

make_cash.short_description = "扣款"

def make_cashdd(modeladmin, request, queryset):
    # 插入流水表
    # 插入显示结果表
    for i in queryset:
        print(i)
   # a= Profile.objects.get(id=queryset[0].user_id.i)
    profile= Profile.objects.filter(id=str(queryset[0].user_id))
    if not profile:
        messages.error(request, '请完善员工资料')
        return
    major = Major.objects.filter(id=profile[0].major_id)
    f  = open('扣费信息.txt', 'w+')
    f.write(str(profile[0].name) + " " + str(profile[0].number)  + " " + str(profile[0].phone) + " "+ str(profile[0].homeaddr) + " "+str( major[0].name))
    f.close()



make_cashdd.short_description = "扣费信息"

def make_change(modeladmin, request, queryset):
    queryset.update(**{
        "is_changed": True,
        "is_approved": None,
        "is_interviewed": None
    })


make_change.short_description = "调剂"

def student_removeapprove(modeladmin, request, queryset):
    if  queryset[0].is_approved==None:
        Approve.objects.filter(id=str(queryset[0].id)).delete()
        return
    messages.error(request, "当前学生未审核不能删除")



student_removeapprove.short_description = "学生删除未审核专业"

def major_change(modeladmin, request, queryset):
    majorobect =  Major.objects.filter(id=str(queryset[0].major.id))
    count =majorobect[0].studentcount
    hascount=Approve.objects.filter(major=str(queryset[0].major.id)).count()
    messages.info(request, str("当前专业：")+str(majorobect[0].name) + "接纳人数："+str(majorobect[0].studentcount) )
    messages.info(request, str("当前用户专业申请人数：") + str(hascount))
    if hascount>int(majorobect[0].studentcount):
        return redirect("/admin/major/approve/" + str(queryset[0].id)+"/change")
    else:
        messages.error(request,"当前学生足以申请该专业不用调剂")


major_change.short_description = "学生专业调剂"

class ApproveAdmin(admin.ModelAdmin):
    list_display = (
        'user', 'submit_time', 'major', 'is_first', 'detail','is_approved', 'is_interviewed', 'is_changed', 'is_cashed','suggest')
    # 分页，每页显示条数
    list_per_page = 20
    # 分页，显示全部（真实数据<该值时，才会有显示全部）
    list_max_show_all = 200
    actions = (
        # todo 按权限分
        make_process("审核通过", "is_approved"),
        make_process("审核不通过", "is_approved", False),
        make_process("面试通过", "is_interviewed"),
        make_process("面试不通过", "is_interviewed", False),
       make_cash,
        make_change
    )

    def get_fields(self, request, obj=None):
        fields = super(ApproveAdmin, self).get_fields(request)
        if request.user.groups.filter(name__in=['student']).exists():
            fields = ['user', 'major','has_math', 'is_first','detail']
        return fields

    def get_actions(self, request):
        # 根据用户角色来获取动作
        actions = super(ApproveAdmin, self).get_actions(request)
        if request.user.groups.filter(name__in=['student']).exists():
            actions.clear()
            actions.update(major_change=(major_change, 'major_change', '学生专业调剂'))
            actions.update(student_removeapprove=(student_removeapprove, 'student_removeapprove', '学生删除未审核专业'))
        elif  request.user.username == 'root':
            a = actions.update(make_cashdd=(make_cashdd, 'make_cashdd','扣费信息'))
        return actions

    def save_model(self, request, obj, form, change):
        # 这写成判断学生的权限
        # 同一时间/年度？只能一次
        # 已有在读的 再只能提交一次
        if request.user.profile.name is None or request.user.profile.major is None:
            messages.set_level(request, messages.ERROR)
            messages.error(request, '未能提交申请 请完善资料')
            return

        if obj.is_first:
            cnt_first = Approve.objects.filter(is_first=True, user=request.user).count()
            if cnt_first > 0:
                messages.set_level(request, messages.ERROR)
                messages.error(request, '已存在首次提交申请 请勿重复提交')
                return
        # 已有的其他的 拒绝
        # “双专业或双学位学生信息记录表”存在的学生不能新申请双学位或双专业。
        cnt_other = Approve.objects.exclude(major=obj.major).filter(user=request.user).count()
        if cnt_other > 0:
            messages.set_level(request, messages.ERROR)
            messages.error(request, '已存在其他专业的提交申请 请勿重复提交')
            return
        # 同专业不行
        if obj.major == request.user.profile.major:
            messages.set_level(request, messages.ERROR)
            messages.error(request, '与本专业相同 请勿重复提交')
            return

        if obj is not None and obj.user is None:
            obj.user = request.user
            obj.save()
            super(ApproveAdmin, self).save_model(request, obj, form, change)
            return
        else:

            # 已提交的不能改， 调剂的能改
            if obj.is_changed is True:
                obj.is_changed = None
                obj.save()
                super(ApproveAdmin, self).save_model(request, obj, form, change)
                return
        # messages.error()
     #   messages.set_level(request, messages.ERROR)
      #  messages.error(request, '申请已经提交 暂时无法修改')
        super(ApproveAdmin, self).save_model(request, obj, form, change)
        return
      #  return False

    def get_queryset(self, request):
        # 学生只能看到自己的
        qs = super(ApproveAdmin, self).get_queryset(request)
        if request.user.groups.filter(name__in=['student']).exists():
            return qs.filter(user=request.user)
        return qs


admin.site.register(Approve, ApproveAdmin)


class ReordAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'major',
        'time',
        'collage',
    )
    actions = (
        make_change,
    )


admin.site.register(Record, ReordAdmin)


def test_action(modeladmin, request, queryset):
    print('test_action')


# class TestAction:
#     def __init__(self, short_description):
#         self.short_description = short_description
#         self.__name__ = '666'
#
#     def __call__(self, modeladmin, request, queryset):
#         print('test')
#         pass
#
#
# new666 = TestAction("新增操作666")


class ProfileAdmin(admin.ModelAdmin):
    list_display = ( 'name','id', 'number', 'major', 'session', 'sex', 'phone','homeaddr')


    # actions = (
    #     make_change,
    # )

    def get_actions(self, request):
        actions = super(ProfileAdmin, self).get_actions(request)
        if request.user.groups.filter(name='student').exists():
            return []
        return actions

    def get_readonly_fields(self, request, obj=None):
        actions = super(ProfileAdmin, self).get_readonly_fields(request)
        if  request.user.groups.filter(name='student').exists():
            return    (
        'user', 'major', 'collage', 'number', 'name', 'sex', 'session'
    )
        else:
            return actions

    def get_queryset(self, request):
        # 学生只能看到自己的
        qs = super(ProfileAdmin, self).get_queryset(request)
        if request.user.groups.filter(name='student').exists():
            return qs.filter(user=request.user)
        return qs


admin.site.register(Profile, ProfileAdmin)


# 下载
def download_file(modeladmin, request, queryset):
    print(modeladmin)
    print(request)
    print(queryset)
    import os
    response = FileResponse(queryset[0].upload_file.file)
    response['Content-Type'] = 'application/octet-stream'
    # response['Content-Disposition'] = 'attachment;filename={}'.format(urlquote(os.path.basename(queryset[0].upload_file.name)))
    # response['Content-Disposition'] = 'attachment;filename={}'.format(urlquote('asdf.jpg'))
    response['Content-Disposition'] = "attachment; filename*=utf-8''{}".format(os.path.basename(escape_uri_path(queryset[0].upload_file.name)))
    return response


download_file.short_description = "下载专业培养方案"

class UploadFileAdmin(admin.ModelAdmin):
    list_display = ('user', 'desc')


    def get_actions(self, request):
        # 根据用户角色来获取动作
        actions = super(UploadFileAdmin, self).get_actions(request)
        if request.user.groups.filter(name__in=['student']).exists():
            actions = OrderedDict(download_file=(download_file, 'download_file', '下载专业培养方案'))
        return actions

    def get_queryset(self, request):
        # 学生只能看到自己的
        qs = super(UploadFileAdmin, self).get_queryset(request)
        if request.user.groups.filter(name='student').exists():
            return qs.filter(user=request.user)
        return qs
    # def get_actions(self, request):
    #     # 根据用户角色来获取动作
    #     actions = super(UploadFileAdmin, self).get_actions(request)
    #     if request.user.groups.filter(name__in=['collage']).exists():
    #         actions = ['delete_selected']
    #     return actions

admin.site.register(UploadFile, UploadFileAdmin)

