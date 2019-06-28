# conding=utf-8
"""
@project:edubalibs
@language:Python3
@create:2019/5/30
@author:qianyang<qianyang@aibayes.com>
@description:none
"""
from .person.face.face_detect import ApolloFaceDetector
from .person.face.face_recog import ApolloFaceRecognizer
from .person.face.face_register import face_register
from .person.age_gender.age_gender_recog import ApolloAgeGenderRecognizer
from .person.beauty.beauty_recog import ApolloBeautyRecognizer
from .person.emotion.emotion_recog import ApolloEmotionRecognizer
from .person.handpose.handpose_recog import ApolloHandPoseRecognizer
from .person.headpose.headpose_recog import ApolloHeadPoseRecognizer
from .person.skeleton.skeleton_recog import ApolloSkeletonRecognizer
from .object.color.color_recog import ApolloColorRecognizer
from .object.distance.distance_detect import ApolloDistanceDetector
from .object.object.object_detect import ApolloObjectDetector
