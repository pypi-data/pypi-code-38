# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json, os, random
from django.forms.models import model_to_dict
from django.shortcuts import render
from dss.Serializer import serializer
from django.core.urlresolvers import reverse_lazy
from django.utils.decorators import method_decorator
from django.shortcuts import get_object_or_404, reverse, redirect, render, HttpResponse
from .decorators import cls_decorator, func_decorator
from django.views.generic import ListView, DetailView, TemplateView, RedirectView
from django.db.models import Q, Sum, Count
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.conf import settings
from .models import Course, Section, CourseSectionMid, Video, UserLive, UserCourse, UserCourseSection, \
    Preference, UserSectionNote, SectionVideo, SectionQuestion, SectionQuestionOption, UserQuestionAnswerRecord, \
    UserLiveComment
from .forms import CourseForm, SectionForm, CourseSectionForm, CourseSectionOrderForm, VideoForm, UploadImageForm, \
    UserCourseForm, UserAssignmentForm, UserAssignmentImageForm, SectionVideoForm, PreferenceForm, \
    section_attach_form, UserSectionNoteForm, SectionVideoOrderForm, LivePlayLogsForm, UserLiveCommentForm, \
    CourseSectionQuestionSearchForm
from .utils import JSONResponse, page_it
from .cc import create_video_info, get_video_str, get_play_logs
from django.http import JsonResponse, HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction
from django.utils import timezone
from bee_django_course import signals
from django.apps import apps
from .exports import get_teach_users, get_user_course_section_list
import cc
from dss.Serializer import serializer
from django.core.exceptions import PermissionDenied

from qiniu import Auth
from qiniu import BucketManager

User = get_user_model()


def test(request):
    form = LivePlayLogsForm()
    # print('a', form)
    return render(request, 'bee_django_course/live/play_logs.html', context={'form': form})


class CourseRedirectView(RedirectView):
    # if 0:
    #     pattern_name = 'bee_django_course:section_list'
    # else:
    #     pattern_name = 'bee_django_course:section_list'
    query_string = True

    def get_redirect_url(self, *args, **kwargs):
        if self.request.user.has_perm('bee_django_course.view_all_courses'):
            # 跳转课程列表 CourseList
            self.pattern_name = 'bee_django_course:course_list'
        if self.request.user.has_perm('bee_django_course.view_teach_usercoursessection') or self.request.user.has_perm(
                'bee_django_course.view_all_usercoursesection'):
            # 跳转录播列表
            self.url = reverse('bee_django_course:live_list', kwargs={"user_id": 0})
        else:
            raise PermissionDenied
        return super(CourseRedirectView, self).get_redirect_url(*args, **kwargs)


# Create your views here.
# =======course=======
@method_decorator(cls_decorator(cls_name='CourseList'), name='dispatch')
class CourseList(ListView):
    template_name = 'bee_django_course/course/course_list.html'
    context_object_name = 'course_list'
    paginate_by = 20
    queryset = Course.objects.all()

    def get(self, request, *args, **kwargs):
        if request.user.has_perm('bee_django_course.view_all_courses'):
            return super(CourseList, self).get(request, *args, **kwargs)
        elif request.user.has_perm('bee_django_course.view_teach_usercoursessection'):
            return redirect(reverse('bee_django_course:live_list', kwargs={"user_id": 0}))
        else:
            raise PermissionDenied


@method_decorator(cls_decorator(cls_name='CourseDetail'), name='dispatch')
class CourseDetail(DetailView):
    model = Course
    template_name = 'bee_django_course/course/course_detail.html'
    context_object_name = 'course'

    def get_context_data(self, **kwargs):
        context = super(CourseDetail, self).get_context_data(**kwargs)
        course = Course.objects.get(id=self.kwargs["pk"])
        context["form"] = CourseSectionForm(course=course)
        mid_list = CourseSectionMid.objects.filter(course=course)
        context["mid_list"] = mid_list
        return context


@method_decorator(cls_decorator(cls_name='CourseCreate'), name='dispatch')
class CourseCreate(CreateView):
    model = Course
    form_class = CourseForm
    template_name = 'bee_django_course/course/course_form.html'


@method_decorator(cls_decorator(cls_name='CourseUpdate'), name='dispatch')
class CourseUpdate(UpdateView):
    model = Course
    form_class = CourseForm
    template_name = 'bee_django_course/course/course_form.html'


@method_decorator(cls_decorator(cls_name='CourseDelete'), name='dispatch')
class CourseDelete(DeleteView):
    model = Course
    success_url = reverse_lazy('bee_django_course:course_list')

    def get(self, request, *args, **kwargs):
        return self.http_method_not_allowed(request, *args, **kwargs)


@method_decorator(cls_decorator(cls_name='SectionList'), name='dispatch')
class SectionList(ListView):
    template_name = 'bee_django_course/section/section_list.html'
    context_object_name = 'section_list'
    paginate_by = 20
    queryset = Section.objects.all()

    def get(self, request, *args, **kwargs):
        if request.user.has_perm("bee_django_course.view_all_sections"):
            return super(SectionList, self).get(request, *args, **kwargs)
        else:
            raise PermissionDenied

    def get_queryset(self):
        section_name = self.request.GET.get('section_name')
        if section_name:
            return self.queryset.filter(name__contains=section_name)
        else:
            return self.queryset


@method_decorator(cls_decorator(cls_name='SectionDetail'), name='dispatch')
class SectionDetail(DetailView):
    model = Section
    template_name = 'bee_django_course/section/section_detail.html'
    context_object_name = 'section'

    def get_context_data(self, **kwargs):
        context = super(SectionDetail, self).get_context_data(**kwargs)
        context['section_video_form'] = SectionVideoForm(section=self.object)
        context['attachs'] = self.object.sectionattach_set.all()

        return context


# 关联课件视频
def create_section_video(request, section_id):
    section = get_object_or_404(Section, pk=section_id)

    if request.method == "POST":
        form = SectionVideoForm(data=request.POST)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.section = section
            obj.save()
            messages.success(request, '添加成功')
        else:
            messages.error(request, '表单错误')

        return redirect(reverse('bee_django_course:section_detail', kwargs={'pk': section.id}))


# 解除课件和视频对的关联
def remove_section_video(request, section_video_id):
    section_video = get_object_or_404(SectionVideo, pk=section_video_id)
    if request.method == "POST":
        section = section_video.section
        section_video.delete()

        return JsonResponse(data={
            'message': '移除成功',
            'section_video_id': section_video_id,
        })


@method_decorator(cls_decorator(cls_name='SectionCreate'), name='dispatch')
class SectionCreate(CreateView):
    model = Section
    form_class = SectionForm
    template_name = 'bee_django_course/section/section_form.html'

    def get_context_data(self, **kwargs):
        context = super(SectionCreate, self).get_context_data(**kwargs)
        context['formset'] = section_attach_form()

        return context

    @transaction.atomic
    def form_valid(self, form):
        if form.is_valid():
            section = form.save()
            formset = section_attach_form(data=self.request.POST, files=self.request.FILES)
            if formset.is_valid():
                attachs = formset.save(commit=False)
                for attach in attachs:
                    attach.section = section
                    attach.save()

        return super(SectionCreate, self).form_valid(form)


@method_decorator(cls_decorator(cls_name='SectionUpdate'), name='dispatch')
class SectionUpdate(UpdateView):
    model = Section
    form_class = SectionForm
    template_name = 'bee_django_course/section/section_form.html'

    def get_context_data(self, **kwargs):
        context = super(SectionUpdate, self).get_context_data(**kwargs)
        context['formset'] = section_attach_form(instance=self.object)

        return context

    def form_valid(self, form):
        formset = section_attach_form(data=self.request.POST, files=self.request.FILES, instance=self.object)
        if formset.is_valid():
            formset.save()

        return super(SectionUpdate, self).form_valid(form)


@method_decorator(cls_decorator(cls_name='SectionDelete'), name='dispatch')
class SectionDelete(DeleteView):
    model = Section
    success_url = reverse_lazy('bee_django_course:section_list')

    def get(self, request, *args, **kwargs):
        return self.http_method_not_allowed(request, *args, **kwargs)


@method_decorator(cls_decorator(cls_name='CourseSectionMidCreate'), name='dispatch')
class CourseSectionMidCreate(TemplateView):
    @transaction.atomic
    def post(self, request, *args, **kwargs):
        form = CourseSectionForm(data=request.POST)
        course = get_object_or_404(Course, pk=self.kwargs["course_id"])
        mid_list = course.coursesectionmid_set.order_by('order_by')

        if form.is_valid():
            mid = form.save(commit=False)
            mid.course = course
            mid.save()

            # 追加已经学了此课程的用户的UCS
            for user_course in course.usercourse_set.all():
                user_course.usercoursesection_set.create(section=mid.section)

            messages.success(self.request, "添加成功")
            return redirect(reverse('bee_django_course:course_detail', kwargs={'pk': kwargs['course_id']}))
        else:
            messages.error(self.request, '表单错误')
            return render(self.request, 'bee_django_course/course/course_detail.html', context={
                'course': course,
                'form': form,
                'mid_list': mid_list,
            })


# 修改课程里课件的排序
def update_coursesectionmid(request, csm_id):
    course_section_mid = get_object_or_404(CourseSectionMid, pk=csm_id)

    if request.method == "POST":
        form = CourseSectionOrderForm(data=request.POST, instance=course_section_mid)
        if form.is_valid():
            form.save()
            messages.success(request, '修改成功')
        else:
            messages.error(request, '表单错误')

        return redirect(reverse('bee_django_course:course_detail', kwargs={'pk': course_section_mid.course.id}))
    else:
        form = CourseSectionOrderForm(instance=course_section_mid)

    return render(request, 'bee_django_course/course/course_section_mid_form.html', context={
        'form': form,
        'mid': course_section_mid,
    })


# 删除课程里的课件
@transaction.atomic
def delete_courseectionmid(request, csm_id):
    course_section_mid = get_object_or_404(CourseSectionMid, pk=csm_id)

    if request.method == "POST":
        course = course_section_mid.course
        section = course_section_mid.section
        course_section_mid.delete()

        # 同时删除用户对应课程的 UserCourseSection
        ucs_list = UserCourseSection.objects.filter(user_course__course=course,
                                                    section=section)
        ucs_list.delete()

        return JsonResponse(data={
            'rc': 0,
        })


@method_decorator(cls_decorator(cls_name='VideoList'), name='dispatch')
class VideoList(ListView):
    template_name = 'bee_django_course/video/video_list.html'
    context_object_name = 'video_list'
    paginate_by = 20

    def get(self, request, *args, **kwargs):
        if request.user.has_perm("bee_django_course.view_all_videos"):
            return super(VideoList, self).get(request, *args, **kwargs)
        else:
            raise PermissionDenied

    def get_context_data(self, **kwargs):
        context = super(VideoList, self).get_context_data(**kwargs)
        context["video_provider_name"] = settings.COURSE_VIDEO_PROVIDER_NAME
        return context

    def get_queryset(self):
        video_name_params = self.request.GET.get('video_name')
        if video_name_params:
            queryset = Video.objects.filter(title__contains=video_name_params)
        else:
            queryset = Video.objects.all()
        return queryset


@method_decorator(cls_decorator(cls_name='VideoDetail'), name='dispatch')
class VideoDetail(DetailView):
    model = Video
    template_name = 'bee_django_course/video/video_detail.html'
    context_object_name = 'video'

    def get_context_data(self, **kwargs):
        video = Video.objects.get(id=self.kwargs["pk"])
        context = super(VideoDetail, self).get_context_data(**kwargs)
        video_src = None
        if settings.COURSE_VIDEO_PROVIDER_NAME == 'cc':
            video_src = get_video_str(video.video_id)
        elif settings.COURSE_VIDEO_PROVIDER_NAME == 'qiniu':
            video_src = "http://" + settings.QINIU_DOMAIN + "/" + video.file_name
        context["video_src"] = video_src
        context["video_provider_name"] = settings.COURSE_VIDEO_PROVIDER_NAME
        return context


def update_section_video_order(request, section_video_id):
    section_video = get_object_or_404(SectionVideo, pk=section_video_id)
    if request.method == "POST":
        sv = SectionVideoOrderForm(request.POST, instance=section_video)
        if sv.is_valid():
            sv.save()
            return redirect(reverse('bee_django_course:section_detail', kwargs={'pk': section_video.section.id}))
    else:
        sv = SectionVideoOrderForm()
        return render(request, 'bee_django_course/section/section_video_order_form.html', context={
            'form': sv,
            'section_video': section_video,
        })


def prepare_live_video_page_data(live_video_id):
    try:
        user_live = UserLive.objects.get(record_video_id=live_video_id)

        user_live_comments = user_live.userlivecomment_set.order_by('-submit_date')

        return user_live_comments

    except UserLive.DoesNotExist:
        return


def live_video_detail(request, live_video_id):
    user_live = UserLive.objects.get(record_video_id=live_video_id)
    comments = user_live.userlivecomment_set.order_by('-submit_date')

    if request.method == "POST":
        comment_form = UserLiveCommentForm(data=request.POST)
        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.user = request.user
            comment.user_live = user_live
            comment.save()
            signals.user_live_comment.send(sender=UserLiveComment, user_live=user_live, comment_user=request.user)
            return redirect(reverse('bee_django_course:live_video_detail', kwargs={'live_video_id': live_video_id}))
    else:
        comment_form = UserLiveCommentForm()

    return render(request, 'bee_django_course/live/live_video_detail.html', context={
        'record_video_id': live_video_id,
        'user_live': user_live,
        'comments': comments,
        'comment_form': comment_form,
    })


def user_live_video_detail(request, live_video_id):
    user_live = UserLive.objects.get(record_video_id=live_video_id)
    comments = user_live.userlivecomment_set.order_by('-submit_date')

    if request.method == "POST":
        comment_form = UserLiveCommentForm(data=request.POST)
        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.user = request.user
            comment.user_live = user_live
            comment.save()
            signals.user_live_comment.send(sender=UserLiveComment, user_live=user_live, comment_user=request.user)
            return redirect(
                reverse('bee_django_course:user_live_video_detail', kwargs={'live_video_id': live_video_id}))
    else:
        comment_form = UserLiveCommentForm()

    return render(request, 'bee_django_course/user/live_video_detail.html', context={
        'record_video_id': live_video_id,
        'user_live': user_live,
        'comments': comments,
        'comment_form': comment_form,
    })


def edit_user_live_comment(request, user_live_comment_id):
    comment = get_object_or_404(UserLiveComment, pk=user_live_comment_id)

    if request.method == "POST":
        next = reverse('bee_django_course:user_live_video_detail',
                       kwargs={'live_video_id': comment.user_live.record_video_id})
        comment_form = UserLiveCommentForm(data=request.POST, instance=comment)
        if comment_form.is_valid():
            comment_form.save()
            return HttpResponseRedirect(next)
    else:
        comment_form = UserLiveCommentForm(instance=comment)

    return render(request, 'bee_django_course/live/edit_user_live_comment.html', context={
        'comment_form': comment_form,
    })


def delete_user_live_comment(request, user_live_comment_id):
    comment = get_object_or_404(UserLiveComment, pk=user_live_comment_id)

    if request.method == "POST":
        next = reverse('bee_django_course:user_live_video_detail',
                       kwargs={'live_video_id': comment.user_live.record_video_id})
        comment.delete()
        return JsonResponse(data={
            'message': '操作成功',
            'next': next,
        })


@method_decorator(cls_decorator(cls_name='VideoUpload'), name='dispatch')
class VideoUpload(TemplateView):
    def get(self, request, *args, **kwargs):
        return render(request, 'bee_django_course/video/video_upload.html')


@method_decorator(cls_decorator(cls_name='VideoUpload'), name='dispatch')
class VideoUploadToQiniu(TemplateView):
    def get(self, request, *args, **kwargs):
        return render(request, 'bee_django_course/video/video_upload_to_qiniu.html')


# 将七牛云的视频，添加至Video
def add_qiniu_video_to_video(request):
    if request.method == "POST":
        file_name = request.POST.get('file_name')
        try:
            video = Video.objects.create(title=file_name, file_name=file_name)
            return JsonResponse(data={
                'rc': 0,
                'message': '创建成功'
            })
        except:
            return JsonResponse(data={
                'rc': -1,
                'message': '添加失败'
            })


# ======上传视频=====
# 1 创建点播信息
@method_decorator(cls_decorator(cls_name='CCVideoInfoCreate'), name='dispatch')
class CCVideoInfoCreate(TemplateView):
    def post(self, request, *args, **kwargs):
        title = request.POST.get("title")
        tag = request.POST.get("tag")
        description = request.POST.get("description")
        filename = request.POST.get("filename")
        filesize = request.POST.get("filesize")
        res = create_video_info(title, filename, filesize, settings.COURSE_CC_CATEGORYID)
        return JSONResponse(json.dumps(res, ensure_ascii=False))


# 2 上传成功后记录用户video对应关系
def cc_video_upload_done(request):
    # uid = request.POST.get("uid")
    # sid = request.POST.get("sid")
    title = request.POST.get("title")
    if title:
        title = os.path.splitext(title)[0]
    videoid = request.POST.get("videoid")
    if videoid:
        ccvideo = Video()
        ccvideo.title = title
        ccvideo.created_by = request.user
        ccvideo.video_id = videoid
        ccvideo.save()
    res = {"error": 0}
    return JSONResponse(json.dumps(res, ensure_ascii=False))


# 转码完成后cc的回调
@func_decorator('cc_video_callback')
def cc_video_callback(request):
    return


# 上传视频到七牛，需要先获取的token
def get_qiniu_token(key):
    access_key = settings.QINIU_AK
    secret_key = settings.QINIU_SK
    # 构建鉴权对象
    q = Auth(access_key, secret_key)
    # 要上传的空间
    bucket_name = settings.QINIU_BUCKET_NAME
    # key 上传后保存的文件名

    # 生成上传 Token，可以指定过期时间等
    # 上传策略示例
    # https://developer.qiniu.com/kodo/manual/1206/put-policy
    policy = {
        # 'callbackUrl':'https://requestb.in/1c7q2d31',
        # 'callbackBody':'filename=$(fname)&filesize=$(fsize)'
        # 'persistentOps':'imageView2/1/w/200/h/200'
    }
    # 3600为token过期时间，秒为单位。3600等于一小时
    token = q.upload_token(bucket_name, key=key.encode('utf-8'), expires=3600, policy=policy)
    return token


def uptoken(request):
    key = request.GET.get('key')
    token = get_qiniu_token(key)
    return JsonResponse(data={
        'uptoken': token,
        'domain': settings.QINIU_DOMAIN,
    })


def add_video_to_part(request, part_id):
    if request.method == "POST":
        file_name = request.POST.get('file_name')
        try:
            part = get_object_or_404(Part, pk=part_id)
            video_count = part.video_set.all().count() + 1
            part.video_set.create(file_name=file_name, number=video_count)

            return JsonResponse(data={
                'rc': 0,
                'message': '创建成功'
            })
        except Part.DoesNotExist:
            return JsonResponse(data={
                'rc': -1,
                'message': '未找到对应小节'
            })



# 查看所有的学生录播
@method_decorator(cls_decorator(cls_name='LiveList'), name='dispatch')
class LiveList(ListView):
    template_name = 'bee_django_course/live/live_list.html'
    context_object_name = 'live_list'
    paginate_by = 20
    queryset = None

    def get_user(self):
        user_id = self.kwargs["user_id"]
        if not user_id in [None, '0']:
            user = User.objects.get(id=user_id)
            return user
        return None

    def get_queryset(self):
        if self.request.user.has_perm("bee_django_course.view_all_userlives"):
            self.queryset = UserLive.objects.filter(status=1)
        elif self.request.user.has_perm("bee_django_course.view_teach_userlives"):
            users = get_teach_users(self.request.user)
            self.queryset = UserLive.objects.filter(user__in=users, status=1).order_by('-created_at')
        else:
            return []
        user = self.get_user()
        if user:
            self.queryset = self.queryset.filter(user=user)
        return self.queryset

    def get_context_data(self, **kwargs):
        context = super(LiveList, self).get_context_data(**kwargs)
        # context["vdieo_provider_name"] = settings.COURSE_VIDEO_PROVIDER_NAME
        context["live_url"] = None
        context["user"] = self.get_user()
        return context


# # 查看单个学生的所有录播
# @method_decorator(cls_decorator(cls_name='UserLiveList'), name='dispatch')
# class UserLiveList(ListView):
#     template_name = 'bee_django_course/live/user_live_list.html'
#     context_object_name = 'user_live_list'
#     paginate_by = 20
#     queryset = UserLive.objects.filter(status__in=[1, 2]).order_by('-created_at')
#
#     def get_queryset(self):
#         return UserLive.objects.filter(user_id=self.kwargs["user_id"], status__in=[1, 2]).order_by('-created_at')
#
#     def get_context_data(self, **kwargs):
#         context = super(UserLiveList, self).get_context_data(**kwargs)
#         # TODO
#         user = get_object_or_404(User, pk=self.kwargs["user_id"])
#         # context["vdieo_provider_name"] = settings.COURSE_VIDEO_PROVIDER_NAME
#         context["live_url"] = None
#         context["user"] = user
#         return context


# @func_decorator('play_video')
# class VideoPlay(DetailView):
#     model = Video
#     template_name = 'bee_django_course/video/video_admin_play.html'
#     context_object_name = 'video'
#
#     a="<script src="https://p.bokecc.com/player?vid=E23A9847AA05EBC49C33DC5901307461&siteid=0AB85AD887FFBEEA&autoStart=false&width=600&height=490&playerid=9A64817BAA03E452&playertype=1" type="text/javascript"></script>"
#         try:
#             video = CCLive.objects.get(id=video_id)
#             src = "https://p.bokecc.com/playhtml.bo?vid=" + video.record_video_id + "&siteid=" + cc.userid + "&autoStart=false&playerid=9A64817BAA03E452&playertype=1"
#
#         except:
#             video = None
#         comments = Comment.objects.filter(live=video).order_by('created_at')
#     elif type_str == 'video':
#         try:
#             video = CCVideo.objects.get(id=video_id)
#             src = "https://p.bokecc.com/playhtml.bo?vid=" + video.videoid + "&siteid=" + cc.userid + "&autoStart=false&playerid=9A64817BAA03E452&playertype=1"
#         except:
#             video = None
#     return render(request, 'course/templates/playVideo.html', locals())


@method_decorator(cls_decorator(cls_name='SectionUpdate'), name='dispatch')
class VideoUpdate(UpdateView):
    model = Video
    form_class = VideoForm
    template_name = 'bee_django_course/video/video_form.html'

    # def get_success_url(self):
    #     return


# @func_decorator('create_cc_video_info')
# def create_cc_video_info(request):
#     return


@csrf_exempt
@func_decorator('upload_image')
def upload_image(request):
    max_size = settings.COURSE_UPLOAD_MAXSIZE
    if request.method == "POST":
        file = request.FILES.get(settings.COURSE_ATTACH_FILENAME)
        if file.size > max_size:
            return HttpResponse("error|图片大小超过5M!")

        # 保存图片。用户上传的图片，与用户的对应关系也保存到数据库中
        form = UploadImageForm(request.POST, request.FILES)
        if form.is_valid():
            user_image = form.save(commit=False)
            if request.user.is_authenticated:
                user_image.user = request.user
            user_image.save()
            return HttpResponse(user_image.image.url)
        else:
            print form.errors
            return HttpResponse("error|文件存储错误")
    else:
        return HttpResponse("error|请求错误")


# 弃用，改为UserCourseSectionList
@func_decorator('user_course')
def user_course(request, user_id):
    user = get_object_or_404(User, pk=user_id)

    user_course = user.usercourse_set.order_by('created_at')

    # TODO：1 默认正在学习的全部课程，没有就显示最近学过的 给出其他学过课程的链接
    # 2 列表显示课件里的视频 已学/所需时间 是否完成
    # 3 显示课件评论链接，没学过的不可点
    return render(request, template_name='bee_django_course/user/user_course.html', context={
        'user': user,
        'user_course': user_course,
    })


# 查看指定用户user的课件列表
class UserCourseSectionList(ListView):
    template_name = "bee_django_course/user/user_course_section_list.html"
    model = UserCourseSection
    queryset = None
    paginate_by = 30
    context_object_name = 'user_course_section_list'
    user_course = None
    user_course_list = []

    def get_queryset(self):
        user_id = self.kwargs["user_id"]
        self.user_course_list = UserCourse.objects.filter(user__id=user_id).order_by('status', '-created_at')

        if self.user_course_list.exists():
            self.user_course = self.user_course_list.first()
            self.section_list = get_user_course_section_list(self.user_course)
            return self.section_list
        return []

    def get_context_data(self, **kwargs):
        context = super(UserCourseSectionList, self).get_context_data(**kwargs)
        context["user_course"] = self.user_course
        context["user_course_list"] = self.user_course_list
        return context


# 用户查看指定课程的课件列表
# 弃用 改用UserCourseDetail
def user_course_section_list(request, user_course_id):
    user_course = get_object_or_404(UserCourse, pk=user_course_id)

    section_list = get_user_course_section_list(user_course=user_course)

    return render(request, 'bee_django_course/user/user_course_section_list.html', context={
        'user_course': user_course,
        'section_list': section_list,
    })


# 查看指定用户课程user_course的课件列表
class UserCourseDetail(ListView):
    template_name = "bee_django_course/user/user_course_section_list.html"
    model = UserCourseSection
    queryset = None
    paginate_by = 30
    context_object_name = 'user_course_section_list'
    user_course = None
    user_course_list = []

    def get_queryset(self):
        user_course_id = self.kwargs["user_course_id"]
        self.user_course = UserCourse.objects.get(id=user_course_id)
        user = self.user_course.user
        self.user_course_list = UserCourse.objects.filter(user=user).order_by('status', '-created_at')
        self.section_list = get_user_course_section_list(self.user_course)
        return self.section_list

    def get_context_data(self, **kwargs):
        context = super(UserCourseDetail, self).get_context_data(**kwargs)
        context["user_course"] = self.user_course
        context["user_course_list"] = self.user_course_list
        return context


# 用户课程列表的管理页面
def manage_user_course_section_list(request, user_course_id):
    user_course = get_object_or_404(UserCourse, pk=user_course_id)

    section_list = get_user_course_section_list(user_course=user_course)

    return render(request, 'bee_django_course/manage/user_course_section_list.html', context={
        'user_course': user_course,
        'section_list': section_list,
    })


# 查看用户所学课程的课件 依据课件作业方式的设置，添加不同的提交作业按钮
# !!! 似乎弃用了
def user_course_section_detail(request, ucs_id):
    ucs = get_object_or_404(UserCourseSection, pk=ucs_id)
    section = ucs.section
    user = request.user

    if request.method == "POST":
        # 创建学习笔记
        note_form = UserSectionNoteForm(data=request.POST)
        if note_form.is_valid():
            note = note_form.save(commit=False)
            note.user = user
            note.section = section
            note.save()

            signals.section_note_created.send(sender=UserSectionNote, user_section_note_id=note.id)

            return redirect(reverse('bee_django_course:user_course_section_detail', kwargs={'pk': ucs_id}))
    else:
        note_form = UserSectionNoteForm()

    all_notes_list = section.usersectionnote_set.filter(is_open=True).order_by('-created_at')
    all_notes = page_it(request, query_set=all_notes_list)
    my_notes_list = section.usersectionnote_set.filter(user=request.user).order_by('-created_at')
    my_notes = page_it(request, query_set=my_notes_list)

    return render(request, 'bee_django_course/user/user_course_section_detail.html', context={
        'ucs': ucs,
        'note_form': note_form,
        'my_notes': my_notes,
        'all_notes': all_notes,
    })


class UserCourseSectionDetail(DetailView):
    model = UserCourseSection
    template_name = 'bee_django_course/user/user_course_section_detail.html'

    def get_success_url(self):
        return reverse('bee_django_course:user_course_section_detail', kwargs={'pk': self.kwargs["pk"]})

    def get_context_data(self, **kwargs):
        context = super(UserCourseSectionDetail, self).get_context_data(**kwargs)
        ucs = UserCourseSection.objects.get(id=self.kwargs["pk"])
        section = ucs.section
        all_notes = section.usersectionnote_set.all().order_by('-created_at')
        open_notes = all_notes.filter(is_open=True).order_by('-created_at')
        my_notes = section.usersectionnote_set.filter(user=self.request.user).order_by('-created_at')
        note_form = UserSectionNoteForm()
        context["all_notes"] = page_it(self.request, query_set=all_notes)
        context["open_notes"] = open_notes
        context["my_notes"] = page_it(self.request, query_set=my_notes)
        context["note_form"] = note_form
        context["questions"] = section.get_questions()
        context['video_provider_name'] = settings.COURSE_VIDEO_PROVIDER_NAME
        return context

    def post(self, request, *args, **kwargs):
        # This method is called when valid form data has been POSTed.
        # It should return an HttpResponse.
        note_form = UserSectionNoteForm(data=request.POST)
        if note_form.is_valid():
            ucs = UserCourseSection.objects.get(id=self.kwargs["pk"])
            section = ucs.section
            note = note_form.save(commit=False)
            note.user = request.user
            note.section = section
            note.save()

            signals.section_note_created.send(sender=UserSectionNote, user_section_note_id=note.id)

            return redirect(self.get_success_url())


# 用户查看作业
def user_assignment(request, ucs_id):
    user_course_section = get_object_or_404(UserCourseSection, pk=ucs_id)
    text_form = UserAssignmentForm()
    image_form = UserAssignmentImageForm()
    image_name = settings.COURSE_ATTACH_FILENAME

    assignments = user_course_section.userassignment_set.order_by('created_at')
    assignment_images = user_course_section.userassignmentimage_set.order_by('upload_at')

    if assignments.exists():  # 有作业
        user_assignment = assignments.first()
        text_form = UserAssignmentForm(instance=user_assignment)

    return render(request, 'bee_django_course/user/user_assignment.html', context={
        'ucs': user_course_section,
        'text_form': text_form,
        'image_form': image_form,
        'image_name': image_name,
        'assignments': assignments,
        'assignment_images': assignment_images,
    })


# 助教查看作业
def manage_user_assignment(request, ucs_id):
    user_course_section = get_object_or_404(UserCourseSection, pk=ucs_id)
    text_form = UserAssignmentForm()
    image_form = UserAssignmentImageForm()
    image_name = settings.COURSE_ATTACH_FILENAME

    assignments = user_course_section.userassignment_set.order_by('created_at')
    assignment_images = user_course_section.userassignmentimage_set.order_by('upload_at')

    if assignments.exists():  # 有作业
        user_assignment = assignments.first()
        text_form = UserAssignmentForm(instance=user_assignment)

    return render(request, 'bee_django_course/manage/user_assignment.html', context={
        'ucs': user_course_section,
        'text_form': text_form,
        'image_form': image_form,
        'image_name': image_name,
        'assignments': assignments,
        'assignment_images': assignment_images,
    })


# 保存作业
def save_user_assignment(request, ucs_id):
    ucs = get_object_or_404(UserCourseSection, pk=ucs_id)
    rc = 0
    message = '已保存'
    if request.method == "POST":
        if ucs.userassignment_set.exists():
            # 已经有保存过的草稿
            saved_assignment = ucs.userassignment_set.order_by('created_at').first()
            form = UserAssignmentForm(data=request.POST, instance=saved_assignment)
            if form.is_valid():
                form.save()
            else:
                rc = -1
                message = '表单错误'
        else:
            # 新创建作业的草稿
            form = UserAssignmentForm(data=request.POST)
            if form.is_valid():
                user_assignment = form.save(commit=False)
                user_assignment.user_course_section = ucs
                user_assignment.save()

        return JsonResponse(data={
            'rc': rc,
            'message': message,
        })


# 提交用户作业。改变 UserCourseSection 的状态
def submit_user_assignment(request, ucs_id):
    ucs = get_object_or_404(UserCourseSection, pk=ucs_id)

    if request.method == "POST":
        if request.user == ucs.user_course.user:
            ucs.be_submit()
            message = '提交成功'
        else:
            message = '错误的用户'

        next_url = reverse('bee_django_course:user_assignment', kwargs={'ucs_id': ucs.id})

        return JsonResponse(data={
            'message': message,
            'next_url': next_url,
        })


@transaction.atomic
def user_assignment_image_upload(request, ucs_id):
    ucs = get_object_or_404(UserCourseSection, pk=ucs_id)

    if request.method == "POST":
        form = UserAssignmentImageForm(request.POST, request.FILES)

        if form.is_valid():
            print form.cleaned_data
            if not form.cleaned_data['image']:
                messages.error(request, '请先选择要上传的图片')
                return redirect(reverse('bee_django_course:user_assignment', kwargs={'ucs_id': ucs.id}))

            assignment = form.save(commit=False)
            assignment.user_course_section = ucs
            assignment.save()
            # 上传图片后，也要更新UCS的更新时间
            ucs.updated_at = timezone.now()
            ucs.save()

            rc = ucs.auto_pass_check()
            if rc:
                ucs.get_pass()

            messages.success(request, '上传成功')
            return redirect(reverse('bee_django_course:user_assignment', kwargs={'ucs_id': ucs.id}))
        else:
            return render(request, template_name="bee_django_course/user/user_assignment.html", context={
                'ucs': ucs,
                'image_form': form,
            })


# 用户查看课程
def view_courses(request):
    courses = Course.objects.order_by('created_at')

    return render(request, 'bee_django_course/user/view_courses.html', context={
        'courses': courses,
    })


@transaction.atomic
def choose_user_course(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    courses = Course.objects.exclude(usercourse__user=user).order_by('created_at')
    form = UserCourseForm(user=user)

    if request.method == "POST":
        form = UserCourseForm(data=request.POST, user=user)
        if form.is_valid():
            user_course = form.save(commit=False)
            user_course.user = user
            user_course.save()

            for e in user_course.course.coursesectionmid_set.all():
                user_course.usercoursesection_set.create(section=e.section)

            # 自动开启第一课
            setion_list = get_user_course_section_list(user_course)
            first_section = setion_list.first()
            if first_section:
                first_section.open_ucs()
                return redirect(reverse('bee_django_course:choose_user_course', kwargs={'user_id': user.id}))
        else:
            messages.error(request, '表单错误')

    return render(request, 'bee_django_course/manage/choose_user_course.html', context={
        'user': user,
        'courses': courses,
        'form': form,
    })


# 删除用户学习中的课程
def delete_user_course(request, user_course_id):
    if request.method == "POST":
        user_course = get_object_or_404(UserCourse, pk=user_course_id)
        user = user_course.user
        for e in user_course.usercoursesection_set.all():
            e.delete()

        user_course.delete()
        success_url = reverse('bee_django_course:choose_user_course', kwargs={'user_id': user.id})
        messages.success(request, "用户定制课程已删除")
        return JsonResponse(data={
            'success_url': success_url,
        })


# 助教查看用户课程
def manage_user_course(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    current_course = user.usercourse_set.filter(status=0).order_by('created_at')
    finished_course = user.usercourse_set.filter(status=1).order_by('created_at')

    return render(request, 'bee_django_course/manage/user_course.html', context={
        'user': user,
        'current_course': current_course,
        'finished_course': finished_course,
    })


# 管理查看用户待评分文字作业
def manage_user_assignments(request):
    student_name = request.GET.get('student_name')

    if request.user.has_perm("bee_django_course.view_all_usercoursesection"):
        data_list = UserCourseSection.objects.filter(status__in=[1, 4]) \
            .filter(Q(userassignment__isnull=False) | Q(userassignmentimage__isnull=False)) \
            .order_by('-updated_at').distinct()
    elif request.user.has_perm("bee_django_course.view_teach_usercoursessection"):
        users = get_teach_users(request.user)
        data_list = UserCourseSection.objects.filter(status__in=[1, 4]) \
            .filter(user_course__user__in=users) \
            .filter(Q(userassignment__isnull=False) | Q(userassignmentimage__isnull=False)) \
            .order_by('-updated_at').distinct()
    else:
        data_list = []

    if student_name:
        data_list = data_list.filter(Q(user_course__user__first_name__contains=student_name)
                                     | Q(user_course__user__username=student_name))

    data = page_it(request, query_set=data_list)

    return render(request, 'bee_django_course/manage/assignments.html', context={
        'assignments': data,
    })


# 查看用户所有作业
def manage_user_assignment_list(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    data_list = UserCourseSection.objects.filter(user_course__user=user). \
        filter(Q(userassignment__isnull=False) | Q(userassignmentimage__isnull=False)). \
        order_by('user_course__course__coursesectionmid__order_by')
    data = page_it(request, query_set=data_list)

    return render(request, 'bee_django_course/manage/user_assignments.html', context={
        'assignments': data,
        'user': user,
    })


# 查看用户所有直播视频
def manage_user_live_list(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    data_list = UserLive.objects.filter(user=user, status=1).order_by('-created_at')
    data = page_it(request, query_set=data_list)

    return render(request, 'bee_django_course/manage/user_lives.html', context={
        'lives': data,
        'user': user,
    })


LEVEL_1 = 10
LEVEL_2 = 20


# 给用户作业打分（依据文字作业，图片作业或者视频作业）
@transaction.atomic
def review_user_assignment(request, ucs_id, level):
    ucs = get_object_or_404(UserCourseSection, pk=ucs_id)

    if request.method == "POST":
        signals.assignment_will_be_scored.send(sender=ucs.__class__, user_course_section=ucs, request=request)

        level = request.POST.get('level')
        comment = request.POST.get('comment')
        message = '打分成功'

        if level == '1':
            ucs.get_pass(score=LEVEL_1, comment=comment)
            signals.assignment_was_scored.send(sender=ucs.__class__, user_course_section=ucs, request=request)
        elif level == '2':
            ucs.get_pass(score=LEVEL_2, comment=comment)
            signals.assignment_was_scored.send(sender=ucs.__class__, user_course_section=ucs, request=request)
        elif level == '0':
            ucs.reject()
            message = '退回成功'

        return JsonResponse(data={
            'rc': 0,
            'message': message,
            'new_url': reverse('bee_django_course:manage_user_assignment', kwargs={'ucs_id': ucs.id})
        })


# 开启用户课件
def open_user_course_section(request, ucs_id):
    ucs = get_object_or_404(UserCourseSection, pk=ucs_id)

    if request.method == "POST":
        ucs.open_ucs()
        message = '操作成功'
        return JsonResponse(data={
            'rc': 0,
            'message': message,
            'new_url': reverse('bee_django_course:user_course_detail',
                               kwargs={'user_course_id': ucs.user_course.id})
        })


# 通过用户课件（开启下一课）
def pass_user_course_section(request, ucs_id):
    ucs = get_object_or_404(UserCourseSection, pk=ucs_id)
    if request.method == "POST":
        ucs.get_pass(score=0)
        message = '操作成功'
        return JsonResponse(data={
            'rc': 0,
            'message': message,
            'new_url': reverse('bee_django_course:user_course_detail',
                               kwargs={'user_course_id': ucs.user_course.id})
        })


# 关闭学习中的课件
def close_user_course_section(request, ucs_id):
    ucs = get_object_or_404(UserCourseSection, pk=ucs_id)
    if request.method == "POST":
        ucs.close()
        message = '操作成功'
        return JsonResponse(data={
            'rc': 0,
            'message': message,
            'new_url': reverse('bee_django_course:user_course_detail',
                               kwargs={'user_course_id': ucs.user_course.id})
        })


# 手动通过时，用户提醒助教
def notify_mentor(request, user_id):
    try:
        user = User.objects.get(pk=user_id)
        rc = user.notify_mentor()

        if rc == 0:
            return JsonResponse(data={
                'rc': 0,
                'msg': '提醒成功'
            })
        elif rc == -1:
            return JsonResponse(data={
                'rc': -1,
                'msg': '用户还没有班级'
            })
        elif rc == -2:
            return JsonResponse(data={
                'rc': -1,
                'msg': '用户班级未分配助教'
            })
        else:
            return JsonResponse(data={
                'rc': -1,
                'msg': '未知错误'
            })
    except User.DoesNotExist:
        return JsonResponse(data={
            'rc': -1,
            'msg': '用户不存在'
        })


# 手动通过时，用户申请客服
def notify_agent(request, user_id):
    try:
        user = User.objects.get(pk=user_id)
        user.notify_agent()

        return JsonResponse(data={
            'rc': 0,
            'msg': '提醒成功'
        })
    except User.DoesNotExist:
        return JsonResponse(data={
            'rc': -1,
            'msg': '用户不存在'
        })


def user_list(request):
    # user_list = User.objects.filter(is_active=True).order_by('date_joined')
    if not request.user.has_perm('bee_django_course.assign_user_course'):
        raise PermissionDenied

    user_list = User.objects.order_by('date_joined')
    users = page_it(request, query_set=user_list)

    return render(request, 'bee_django_course/manage/user_list.html', context={
        'users': users,
    })


def save_cc_live(userId, roomId, liveId, stopStatus, recordStatus, recordVideoId, recordVideoDuration, replayUrl,
                 startTime, endTime):
    cclives = UserLive.objects.filter(live_id=liveId)
    if cclives.exists():
        cclive = cclives.first()
        if cclives.count() > 1:
            cclives.exclude(pk=cclive.id).delete()
    else:
        cclive = UserLive()
        cclive.status = 1
        cclive.stop_status = stopStatus

    cclive.cc_user_id = userId
    cclive.room_id = roomId
    cclive.live_id = liveId
    cclive.record_status = recordStatus
    cclive.record_video_id = recordVideoId
    cclive.replay_url = replayUrl

    if startTime:
        cclive.start_time = startTime + "+0800"
    if endTime:
        cclive.end_time = endTime + "+0800"

    cclive.duration = recordVideoDuration

    app_list = settings.COURSE_CC_ROOMID_MODEL_NAME.split("|")
    app = apps.get_app_config(app_list[0])
    model = app.get_model(app_list[1])

    kwargs = {}
    kwargs[app_list[2]] = roomId
    try:
        user_profile = model.objects.get(**kwargs)
        user = user_profile.user
    except:
        user = None

    if user:
        cclive.user = user
        cclive.save()
    else:
        print "user is None"

    return cclive


from bee_django_course.exports import get_user_last_course_section


# 录制完成
def cc_live_finished_callback(request):
    # http://doc.bokecc.com/live/dev/callback/
    user_id = request.GET.get("userId")  # CC账号ID
    room_id = request.GET.get("roomId")  # 直播间ID
    live_id = request.GET.get("liveId")  # 直播ID
    record_status = request.GET.get("recordStatus")  # 直播录制状态，10：录制成功，20：录制失败，30：直播过长
    record_video_id = request.GET.get("recordVideoId")  # 录制视频ID（如果录制成功，则返回该参数）
    record_video_duration = request.GET.get("recordVideoDuration")  # 录制视频时长，单位：秒（如果录制成功，则返回该参数）
    replay_url = request.GET.get("replayUrl")  # 直播回放地址（如果录制成功，则返回该参数）
    start_time = request.GET.get("startTime")  # 直播开始时间
    end_time = request.GET.get("endTime")  # 直播结束时间
    cc_type = request.GET.get('type')  # 回调类型
    if cc_type != '103':
        res = {"result": "OK"}
        return JsonResponse(json.dumps(res, ensure_ascii=False), safe=False)

    cc_lives = UserLive.objects.filter(live_id=live_id).filter(~Q(record_status='10')).order_by('-created_at')
    if cc_lives.exists():
        cc_live = save_cc_live(user_id, room_id, live_id, None, record_status, record_video_id,
                               record_video_duration,
                               replay_url,
                               start_time,
                               end_time)
        # 录制成功
        if cc_live.record_status == "10":
            user = cc_live.user
            refreshed_cc_live = UserLive.objects.get(pk=cc_live.pk)
            timedelta = (refreshed_cc_live.end_time - refreshed_cc_live.start_time).seconds
            coin_multiple = 0
            if timedelta >= 60 and user:
                # 更新课件学习时间
                user_course_section = get_user_last_course_section(user)
                if user_course_section:
                    user_course_section.update_work_time(timedelta / 60)

                coin_multiple = save_coin_multiple(cc_live)

                signals.live_callback_finished.send(sender=UserLive, user_live=cc_live, coin_multiple=coin_multiple)

            cc_live.call_count += 1
            cc_live.save()

        res = {"result": "OK"}
        return JsonResponse(json.dumps(res, ensure_ascii=False), safe=False)
    else:
        res = {"result": "ERROR"}
        return JsonResponse(json.dumps(res, ensure_ascii=False), safe=False)


# 直播结束
def cc_live_end_callback(request):
    user_id = request.GET.get("userId")  # CC账号ID
    room_id = request.GET.get("roomId")  # 直播间ID
    live_id = request.GET.get("liveId")  # 直播ID
    cc_type = request.GET.get('type')  # 回调类型
    start_time = request.GET.get("startTime")  # 直播开始时间
    end_time = request.GET.get("endTime")  # 直播结束时间
    stop_status = request.GET.get("stopStatus")  # 直播结束状态，10：正常结束，20：非正常结束

    if cc_type != '2':
        res = {"result": "OK"}
        return JsonResponse(json.dumps(res, ensure_ascii=False), safe=False)

    cc_lives = UserLive.objects.filter(live_id=live_id).order_by('-created_at')

    if cc_lives.exists():
        cc_live = cc_lives.first()
        cc_live.call_count += 1
        cc_live.save()
    else:
        cc_live = save_cc_live(user_id, room_id, live_id, stop_status, None, None,
                               None,
                               None,
                               start_time,
                               end_time)

    res = {"result": "OK"}
    return JsonResponse(json.dumps(res, ensure_ascii=False), safe=False)


class LivePlayLogs(TemplateView):
    template_name = 'bee_django_course/live/play_logs.html'

    def get_context_data(self, **kwargs):
        context = super(LivePlayLogs, self).get_context_data(**kwargs)
        context["form"] = LivePlayLogsForm()
        print('a', context["form"])
        return context

    def post(self, request, *args, **kwargs):
        form = LivePlayLogsForm(request.POST)
        if form.is_valid():
            video_id = form.cleaned_data['a']
            date = form.cleaned_data['date']
            total, play_log = get_play_logs(video_id=video_id, date=date)
            print(total, play_log)
            # return redirect(reverse_lazy('bee_django_crm:preuser_application_update_preuser', kwargs={'pk': preuser.id}))


def save_coin_multiple(cc_live):
    coin_multiple = 1
    r = random.randint(1, 1000)
    if r >= 980:
        coin_multiple = 3
    elif r >= 900:
        coin_multiple = 2
    cc_live.coin_multiple = coin_multiple
    cc_live.save()
    return coin_multiple


def set_preference(request):
    if Preference.objects.all().count() == 0:
        Preference.objects.create()

    preference = Preference.objects.first()

    if request.method == "POST":
        form = PreferenceForm(instance=preference, data=request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, '已保存')
            return redirect(reverse('bee_django_course:preference'))
        else:
            messages.error(request, '表单错误')
    else:
        form = PreferenceForm(instance=preference)

    return render(request, 'bee_django_course/preference.html', context={
        'form': form,
    })


# ========== 课件测试问卷==============
class SectionQuestionView(TemplateView):
    template_name = 'bee_django_course/question/question.html'

    def _get_section(self):
        section_id = self.kwargs["section_id"]
        section = Section.objects.get(id=section_id)
        return section

    # def _get_question_list(self):
    #     section = self._get_section()
    #     question_list = SectionQuestion.objects.filter(section=section).order_by('order_by')
    #     return question_list

    # def get(self, request, *args, **kwargs):
    #     return super(SectionQuestionView, self).get(request, *args, **kwargs)

    def get_ex_url(self):
        return settings.COURSE_EX_URL

    def get_context_data(self, **kwargs):
        context = super(SectionQuestionView, self).get_context_data(**kwargs)
        context["section"] = self._get_section()
        context["ex_url"] = self.get_ex_url()
        # context["question_list"] = self._get_question_list()
        return context


class SectionQuestionListJson(TemplateView):
    def _get_section(self):
        section_id = self.kwargs["section_id"]
        section = Section.objects.get(id=section_id)
        return section

    def _get_question_list(self):
        section = self._get_section()
        question_list = SectionQuestion.objects.filter(section=section).order_by('order_by')
        output_question_list = []
        for question in question_list:
            q = model_to_dict(question)
            q["options"] = question.options.order_by('order_by')
            output_question_list.append(q)
        return output_question_list

    def get(self, request, *args, **kwargs):
        question_list = self._get_question_list()
        question_list = serializer(question_list, output_type='json', datetime_format='string')
        return JsonResponse(data={
            'error': 0,
            'question_list': question_list
        })

        # res=serializers.serialize("json", {'question_list': question_list})
        # return HttpResponse(res, content_type='application/json')
        # return JSONResponse(json.dumps({"question_list": question_list}, ensure_ascii=False))


class SectionQuestionCreate(TemplateView):
    def post(self, request, *args, **kwargs):
        # This method is called when valid form data has been POSTed.
        # It should return an HttpResponse.
        section_id = request.POST.get("section_id")
        type_id = request.POST.get("type_id")
        section = Section.objects.get(id=section_id)
        question = section.add_question(type_id)
        new_question = model_to_dict(question)
        new_question["options"] = question.options.order_by('order_by')
        new_question = serializer(new_question, output_type='json', datetime_format='string')
        return JsonResponse(data={
            'error': 0,
            'message': '成功',
            'new_question': new_question
        })


class SectionQuestionSave(TemplateView):
    def post(self, request, *args, **kwargs):
        # This method is called when valid form data has been POSTed.
        # It should return an HttpResponse.
        question_id = request.POST.get("question_id")
        question_name = request.POST.get("question_name")
        question_order_by = request.POST.get("question_order_by")
        question_tip_correct = request.POST.get("question_tip_correct")
        question_tip_wrong = request.POST.get("question_tip_wrong")
        options_str = request.POST.get("options_str")
        option_list = json.loads(options_str)
        try:
            question = SectionQuestion.objects.get(id=question_id)
        except:
            return JsonResponse(data={
                'error': 1,
                'message': '参数错误'
            })
        question.question = question_name
        question.order_by = question_order_by
        question.tip_correct = question_tip_correct
        question.tip_wrong = question_tip_wrong
        question.save()
        for option_dict in option_list:
            try:
                option = SectionQuestionOption.objects.get(id=option_dict["id"])
            except:
                continue
            option.option = option_dict["option"]
            option.order_by = option_dict["order_by"]
            option.is_correct = option_dict["is_correct"]
            option.save()
        return JsonResponse(data={
            'error': 0,
            'message': '保存成功'
        })
        pass


class SectionQuestionDelete(TemplateView):
    def post(self, request, *args, **kwargs):
        question_id = request.POST.get("question_id")
        try:
            question = SectionQuestion.objects.get(id=question_id)
        except:
            return JsonResponse(data={
                'error': 1,
                'message': '参数错误'
            })
        question.delete()
        return JsonResponse(data={
            'error': 0,
            'message': '删除成功'
        })


class SectionQuestionOptionCreate(TemplateView):
    def post(self, request, *args, **kwargs):
        # This method is called when valid form data has been POSTed.
        # It should return an HttpResponse.
        question_id = request.POST.get("question_id")
        try:
            question = SectionQuestion.objects.get(id=question_id)
        except:
            return JsonResponse(data={
                'error': 1,
                'message': '参数错误'
            })
        new_options = question.add_options(count=1)
        new_option = serializer(new_options[0], output_type='json', datetime_format='string')
        return JsonResponse(data={
            'error': 0,
            'message': '添加成功',
            'new_option': new_option
        })


class SectionQuestionOptionDelete(TemplateView):
    def post(self, request, *args, **kwargs):
        # This method is called when valid form data has been POSTed.
        # It should return an HttpResponse.
        option_id = request.POST.get("option_id")
        try:
            option = SectionQuestionOption.objects.get(id=option_id)
        except:
            return JsonResponse(data={
                'error': 1,
                'message': '参数错误'
            })
        option.delete()
        return JsonResponse(data={
            'error': 0,
            'message': '删除成功'
        })


# 学生回答问题页
class SectionQuestionAnswer(TemplateView):
    template_name = 'bee_django_course/question/answer.html'

    # def _get_user_section(self):
    #     user_section_id = self.kwargs[""]
    #     ucs = UserCourseSection.objects.get(id=user_section_id)
    #     return ucs

    def get_ucs(self):
        user_section_id = self.kwargs["user_section_id"]
        ucs = UserCourseSection.objects.get(id=user_section_id)
        return ucs

    def get_context_data(self, **kwargs):
        context = super(SectionQuestionAnswer, self).get_context_data(**kwargs)
        ucs = self.get_ucs()
        context["ucs"] = ucs
        context["ex_url"] = settings.COURSE_EX_URL
        return context

        # def post(self, request, *args, **kwargs):
        #     ucs = self._get_user_section()
        #     print(ucs.section)
        #     return JsonResponse(data={
        #         'error': 0
        #     })


# 根据每个学生查看问卷调查
class UserQuestionAnswerRecordList(ListView):
    template_name = 'bee_django_course/question/user_question_answer_record_list.html'
    context_object_name = 'question_list'
    paginate_by = 20
    queryset = None

    def get_ucs(self):
        user_section_id = self.kwargs["user_section_id"]
        # print(user_section_id)
        if not user_section_id in ["0", None]:
            ucs = UserCourseSection.objects.get(id=user_section_id)
            return ucs
        else:
            return None

    def get_user(self):
        ucs = self.get_ucs()
        if ucs:
            return ucs.user_course.user
        return None

    def search(self):

        ucs = self.get_ucs()
        if ucs:
            self.queryset = ucs.section.get_questions()
        # 只有显示全部问题，即没有ucs时，才可搜索
        else:
            question_has_correct = self.request.GET.get("question_has_correct")
            question_name = self.request.GET.get("question_name")

            if question_has_correct in ["-1", None]:
                self.queryset = SectionQuestion.objects.all()
            else:
                if question_has_correct in ["1"]:
                    self.queryset = SectionQuestion.get_has_correct_questions(has_correct=True)
                elif question_has_correct in ["0"]:
                    self.queryset = SectionQuestion.get_has_correct_questions(has_correct=False)
            if question_name:
                self.queryset = self.queryset.filter(question__contains=question_name)

        return self.queryset

    def get_context_data(self, **kwargs):
        context = super(UserQuestionAnswerRecordList, self).get_context_data(**kwargs)
        question_has_correct = self.request.GET.get("question_has_correct")
        question_name = self.request.GET.get("question_name")
        ucs = self.get_ucs()
        if ucs:
            user = ucs.user_course.user
        else:
            user = None
        context["ucs"] = ucs
        context["user"] = user
        context["user_section_id"] = self.kwargs["user_section_id"]
        context["search_form"] = CourseSectionQuestionSearchForm(
            {"question_has_correct": question_has_correct, "question_name": question_name})
        return context

    def get(self, request, *args, **kwargs):
        self.queryset = self.search()
        if request.GET.get("export"):
            pass
            # rows = ([(i + 1).__str__()] + self.get_csv_info(fee) for i, fee in enumerate(self.queryset))
            # return export_csv('缴费信息'.encode('utf-8'), self.get_csv_headers(), rows)
        else:
            return super(UserQuestionAnswerRecordList, self).get(request, *args, **kwargs)


class UserQuestionAnswerRecordDetail(DetailView):
    model = SectionQuestion
    template_name = 'bee_django_course/question/question_reocrd_detail.html'
    context_object_name = 'question'

    def get_context_data(self, **kwargs):
        context = super(UserQuestionAnswerRecordDetail, self).get_context_data(**kwargs)
        question_id = self.kwargs["pk"]
        question = SectionQuestion.objects.get(id=question_id)
        option_list = question.options.all()
        res_queryset = UserQuestionAnswerRecord.objects.filter(question_id=question_id).values('answer',
                                                                                               'answer__option').annotate(
            answer_count=Count('answer')).order_by().order_by("-answer_count")

        res_list = []
        user_count = 0
        for o in option_list:
            d = {}
            found = False
            for i in res_queryset:
                if o.id == i["answer"]:
                    d["key"] = o.option
                    d["value"] = i["answer_count"]
                    user_count += i["answer_count"]
                    found = True
                    res_list.append(d)
            if found == False:
                d["key"] = o.option
                d["value"] = 0
                res_list.append(d)

        # for res_dict in res_queryset:
        #     # option_id = res_dict["answer"]
        #     count = res_dict["answer_count"]

        context["user_count"] = user_count
        context["res_list"] = res_list
        # context["res_queryset"]=res_queryset
        return context


# 用户答题正确，更新ucs状态，返回用户学习课程的列表
def ucs_question_passed(request, ucs_id):
    if request.method == "POST":
        ucs = get_object_or_404(UserCourseSection, pk=ucs_id)
        questions = request.POST.get("questions")
        questions = json.loads(questions)
        # 检查是否保存，如没有存过，则保存用户答案
        user = request.user
        for question in questions:
            answers = question["answers"]
            question_id = question["id"]
            records = UserQuestionAnswerRecord.objects.filter(user=user, question_id=question_id)
            if records.exists():
                continue
            for answer in answers:
                record = UserQuestionAnswerRecord()
                record.user = user
                record.answer_id = answer
                record.question_id = question_id
                record.save()

        ucs.question_passed = True
        ucs.question_passed_at = timezone.now()
        ucs.save()

        rc = ucs.auto_pass_check()
        if rc:
            ucs.get_pass()

        if settings.COURSE_QUESTION_RETURN_LINK:
            return_link = settings.COURSE_QUESTION_RETURN_LINK
        else:
            return_link = reverse('bee_django_course:user_course_detail', kwargs={
                'user_course_id': ucs.user_course_id,
            })

        return JsonResponse(data={
            'return_link': return_link,
        })


# 删除(隐藏）录播(UserLive)
def delete_user_live(request, user_live_id):
    if request.method == "POST":
        user_live = get_object_or_404(UserLive, pk=user_live_id)

        cc.delete_video(user_live.record_video_id)
        user_live.status = -2
        user_live.save()

        # 同时要删除获得的M币，但插件只能发送信号，让每个项目单独处理
        signals.user_live_delete.send(sender=UserLive, user_live=user_live)

        return JsonResponse(data={
            'rc': 0,
        })


# 微信小程序接口
# 课程页
def weixin_user_course_index(request):
    user = request.token_user
    if not user:
        return JsonResponse(data={
            'msg': '无效的用户',
        })

    ucs = get_user_last_course_section(user)
    if not ucs:
        return JsonResponse(data={
            'msg': '没有学习中的课程',
        })

    return JsonResponse(data={
        'user_name': user.first_name or user.username,
        'section_detail': serializer(ucs.section, output_type='json',
                                     datetime_format='string', exclude_attr=['image', 'info']),
        'ucs_detail': serializer(ucs, output_type='json', datetime_format='string'),
        'msg': 'OK',
    })


# 课程详情页
def weixin_ucs_detail(request, ucs_id):
    try:
        ucs = UserCourseSection.objects.get(pk=ucs_id)
        videos = []
        for e in ucs.section.sectionvideo_set.all():
            videos.append({'vid': e.video.video_id, 'titile': e.video.title})

        return JsonResponse(data={
            'rc': 0,
            'section_detail': serializer(ucs.section, output_type='json', datetime_format='string',
                                         exclude_attr=['image']),
            'section_videos': serializer(videos, output_type='json')
        })
    except UserCourseSection.DoesNotExist:
        return JsonResponse(data={
            'rc': -1,
            'msg': '用户课程(UCS)不存在',
        })


def test_video(request):
    return render(request, 'bee_django_course/test_video.html')
