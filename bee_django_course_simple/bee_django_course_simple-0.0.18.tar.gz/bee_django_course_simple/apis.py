# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render

import json, os, random

from django.shortcuts import get_object_or_404, reverse, redirect, render, HttpResponse
from django.contrib.auth import get_user_model
from django.http import JsonResponse, HttpResponseRedirect
from django.views.generic import ListView, DetailView, TemplateView, RedirectView
from django.db import transaction
from django.conf import settings
from dss.Serializer import serializer
from .models import Course, Section, Part, Video, Question, Option, UserCourse, UserSection, \
    UserPart, UserVideo, UserQuestion

from .signals import add_prize_coin

User = get_user_model()



class UserPartUpdate(TemplateView):
    @transaction.atomic
    def post(self, request, *args, **kwargs):
        user_part_id = self.kwargs["user_part_id"]
        question_data = self.request.POST.get("question_data")
        video_id = self.request.POST.get("video_id")

        next_user_part_id = None
        # next_user_section_id = None
        # next_user_section_url = None
        next_user_part_btn = False  # 下一节按钮
        user_part = UserPart.objects.get(id=user_part_id)
        # question_count = 0  # 小节中题目数量
        question_correct_count = 0  # 小节中答对题目数量
        prize_coin = 0  # 奖励积分
        if not user_part.is_open():
            return JsonResponse(data={
                'error': 1,
                'message': '失败，原因：该小节已通过',
            })

        # 保存记录,更新part内question或video状态
        if question_data:
            question_data = json.loads(question_data)
            for q in question_data:
                # 记录过则不记录
                question = Question.objects.get(id=q["question_id"])
                u_q = UserQuestion.objects.filter(user_part=user_part, question=question)
                if u_q.exists():
                    continue
                user_question = UserQuestion()
                user_question.user_part = user_part
                user_question.question_id = q["question_id"]
                user_question.answer_option_id = q["option_id"]
                user_question.save()

                # # 该小节问题的数量
                # question_count = Question.objects.filter(part=user_part.part).count()
                # 检查答案
                if question.part.has_answer:
                    corrent_option = Option.objects.filter(question=question, id=q["option_id"],
                                                           is_correct=True)
                    # 答对时，记分及更新答对题目数量
                    if corrent_option.exists():
                        question_correct_count += 1
                        if question.score:
                            prize_coin += question.score

            user_part.prize_coin = prize_coin
            user_part.question_correct_count = question_correct_count
            user_part.save()
            # 发送信号
            if prize_coin > 0:
                reason = "答对题目奖励"
                add_prize_coin.send(sender=UserPart, user=user_part.user_section.user_course.user, coin=prize_coin,
                                    reason=reason)

        if video_id:
            video = Video.objects.get(id=video_id)
            # 记录过则不记录
            u_v = UserVideo.objects.filter(user_part=user_part, video=video)
            if not u_v.exists():
                video = Video.objects.get(id=video_id)
                user_video = UserVideo()
                user_video.user_part = user_part
                user_video.video = video
                user_video.save()

        # 判断当前user part是否可以通过，更新user part 状态
        user_part_can_pass = user_part.can_pass()
        if user_part_can_pass:
            user_part._pass()

        # 查找下一个user part
        next_user_part = user_part.next_user_part(status=1)
        if next_user_part:
            next_user_part_id = next_user_part.id
            next_user_part_btn = True

        # 判断当前user section是否可以通过
        user_section_can_pass = user_part.user_section.can_pass()
        if user_section_can_pass:
            user_part.user_section._pass()

        # 查找下一个user section，检查自动开启
        # next_user_section = user_part.user_section.next_user_section(status=0)
        # if next_user_section and user_section_can_pass:
        #     next_user_section._open()
        #     next_user_section_id = next_user_section.id
        #     next_user_section_url = reverse('bee_django_course_simple:custom_user_section_detail',
        #                                     kwargs={'pk': next_user_section_id})

        return JsonResponse(data={
            'error': 0,
            'message': '成功',
            'user_part_status': user_part.status,
            'next_user_part_id': next_user_part_id,
            'next_user_part_btn': next_user_part_btn,
            # 'next_user_section_id': next_user_section_id,
            # 'next_user_section_url': next_user_section_url,
            # 'user_part_can_pass': user_part_can_pass,
            "user_section_can_pass": user_section_can_pass,
            # "question_count": question_count,
            # "question_correct_count": question_correct_count,
        })


# VueJS 拉取数据用
class VueUserSection(TemplateView):
    def get(self, request, *args, **kwargs):
        user_section_id = self.kwargs['user_section_id']
        user_section = get_object_or_404(UserSection, pk=user_section_id)
        user_parts = user_section.userpart_set.all()

        for user_part in user_parts:
            user_part.part_type = user_part.part.type
            user_part.part_title = user_part.part.title
            user_part.extra_title = user_part.part.extra_title

            if user_part.part_type == 1:
                videos = []
                for v in user_part.part.video_set.all():
                    videos.append({
                        'id': v.id,
                        'content': v.content,
                        'url': "http://" + settings.QINIU_DOMAIN + "/" + v.file_name
                    })
                user_part.videos = videos
            elif user_part.part_type == 2:
                questions = []
                for q in user_part.part.question_set.all():
                    options = []
                    for o in q.option_set.all():
                        options.append({
                            'id': o.id,
                            'title': o.title
                        })
                    questions.append({
                        'id': q.id,
                        'title': q.title,
                        'options': options
                    })
                user_part.questions = questions

        data = serializer(user_parts, output_type='json', datetime_format='string')

        return JsonResponse(data={
            'user_parts': data,
            'status': user_section.status,
        })
