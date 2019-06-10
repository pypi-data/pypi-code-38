# coding: utf-8

# flake8: noqa
# -----------------------------------------------------------------------------------
# <copyright company="Aspose">
#   Copyright (c) 2018 Aspose.Slides for Cloud
# </copyright>
# <summary>
#   Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software"), to deal
#  in the Software without restriction, including without limitation the rights
#  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#  copies of the Software, and to permit persons to whom the Software is
#  furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in all
#  copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#  OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#  SOFTWARE.
# </summary>
# -----------------------------------------------------------------------------------

from __future__ import absolute_import


from asposeslidescloud.models.requests.slides_api_requests import CopyFileRequest
from asposeslidescloud.models.requests.slides_api_requests import CopyFolderRequest
from asposeslidescloud.models.requests.slides_api_requests import CreateFolderRequest
from asposeslidescloud.models.requests.slides_api_requests import DeleteFileRequest
from asposeslidescloud.models.requests.slides_api_requests import DeleteFolderRequest
from asposeslidescloud.models.requests.slides_api_requests import DeleteNotesSlideRequest
from asposeslidescloud.models.requests.slides_api_requests import DeleteNotesSlideParagraphRequest
from asposeslidescloud.models.requests.slides_api_requests import DeleteNotesSlideParagraphsRequest
from asposeslidescloud.models.requests.slides_api_requests import DeleteNotesSlidePortionRequest
from asposeslidescloud.models.requests.slides_api_requests import DeleteNotesSlidePortionsRequest
from asposeslidescloud.models.requests.slides_api_requests import DeleteNotesSlideShapeRequest
from asposeslidescloud.models.requests.slides_api_requests import DeleteNotesSlideShapesRequest
from asposeslidescloud.models.requests.slides_api_requests import DeleteParagraphRequest
from asposeslidescloud.models.requests.slides_api_requests import DeleteParagraphsRequest
from asposeslidescloud.models.requests.slides_api_requests import DeletePortionRequest
from asposeslidescloud.models.requests.slides_api_requests import DeletePortionsRequest
from asposeslidescloud.models.requests.slides_api_requests import DeleteSlideAnimationRequest
from asposeslidescloud.models.requests.slides_api_requests import DeleteSlideAnimationEffectRequest
from asposeslidescloud.models.requests.slides_api_requests import DeleteSlideAnimationInteractiveSequenceRequest
from asposeslidescloud.models.requests.slides_api_requests import DeleteSlideAnimationInteractiveSequenceEffectRequest
from asposeslidescloud.models.requests.slides_api_requests import DeleteSlideAnimationInteractiveSequencesRequest
from asposeslidescloud.models.requests.slides_api_requests import DeleteSlideAnimationMainSequenceRequest
from asposeslidescloud.models.requests.slides_api_requests import DeleteSlideByIndexRequest
from asposeslidescloud.models.requests.slides_api_requests import DeleteSlideShapeRequest
from asposeslidescloud.models.requests.slides_api_requests import DeleteSlideShapesRequest
from asposeslidescloud.models.requests.slides_api_requests import DeleteSlidesCleanSlidesListRequest
from asposeslidescloud.models.requests.slides_api_requests import DeleteSlidesDocumentPropertiesRequest
from asposeslidescloud.models.requests.slides_api_requests import DeleteSlidesDocumentPropertyRequest
from asposeslidescloud.models.requests.slides_api_requests import DeleteSlidesSlideBackgroundRequest
from asposeslidescloud.models.requests.slides_api_requests import DownloadFileRequest
from asposeslidescloud.models.requests.slides_api_requests import GetDiscUsageRequest
from asposeslidescloud.models.requests.slides_api_requests import GetFileVersionsRequest
from asposeslidescloud.models.requests.slides_api_requests import GetFilesListRequest
from asposeslidescloud.models.requests.slides_api_requests import GetLayoutSlideRequest
from asposeslidescloud.models.requests.slides_api_requests import GetLayoutSlidesListRequest
from asposeslidescloud.models.requests.slides_api_requests import GetMasterSlideRequest
from asposeslidescloud.models.requests.slides_api_requests import GetMasterSlidesListRequest
from asposeslidescloud.models.requests.slides_api_requests import GetNotesSlideRequest
from asposeslidescloud.models.requests.slides_api_requests import GetNotesSlideShapeRequest
from asposeslidescloud.models.requests.slides_api_requests import GetNotesSlideShapeParagraphRequest
from asposeslidescloud.models.requests.slides_api_requests import GetNotesSlideShapeParagraphsRequest
from asposeslidescloud.models.requests.slides_api_requests import GetNotesSlideShapePortionRequest
from asposeslidescloud.models.requests.slides_api_requests import GetNotesSlideShapePortionsRequest
from asposeslidescloud.models.requests.slides_api_requests import GetNotesSlideShapesRequest
from asposeslidescloud.models.requests.slides_api_requests import GetNotesSlideWithFormatRequest
from asposeslidescloud.models.requests.slides_api_requests import GetParagraphPortionRequest
from asposeslidescloud.models.requests.slides_api_requests import GetParagraphPortionsRequest
from asposeslidescloud.models.requests.slides_api_requests import GetSlideAnimationRequest
from asposeslidescloud.models.requests.slides_api_requests import GetSlideShapeRequest
from asposeslidescloud.models.requests.slides_api_requests import GetSlideShapeParagraphRequest
from asposeslidescloud.models.requests.slides_api_requests import GetSlideShapeParagraphsRequest
from asposeslidescloud.models.requests.slides_api_requests import GetSlideShapesRequest
from asposeslidescloud.models.requests.slides_api_requests import GetSlidesDocumentRequest
from asposeslidescloud.models.requests.slides_api_requests import GetSlidesDocumentPropertiesRequest
from asposeslidescloud.models.requests.slides_api_requests import GetSlidesDocumentPropertyRequest
from asposeslidescloud.models.requests.slides_api_requests import GetSlidesImageWithDefaultFormatRequest
from asposeslidescloud.models.requests.slides_api_requests import GetSlidesImageWithFormatRequest
from asposeslidescloud.models.requests.slides_api_requests import GetSlidesImagesRequest
from asposeslidescloud.models.requests.slides_api_requests import GetSlidesPlaceholderRequest
from asposeslidescloud.models.requests.slides_api_requests import GetSlidesPlaceholdersRequest
from asposeslidescloud.models.requests.slides_api_requests import GetSlidesPresentationTextItemsRequest
from asposeslidescloud.models.requests.slides_api_requests import GetSlidesSlideRequest
from asposeslidescloud.models.requests.slides_api_requests import GetSlidesSlideBackgroundRequest
from asposeslidescloud.models.requests.slides_api_requests import GetSlidesSlideCommentsRequest
from asposeslidescloud.models.requests.slides_api_requests import GetSlidesSlideImagesRequest
from asposeslidescloud.models.requests.slides_api_requests import GetSlidesSlideTextItemsRequest
from asposeslidescloud.models.requests.slides_api_requests import GetSlidesSlidesListRequest
from asposeslidescloud.models.requests.slides_api_requests import GetSlidesThemeRequest
from asposeslidescloud.models.requests.slides_api_requests import GetSlidesThemeColorSchemeRequest
from asposeslidescloud.models.requests.slides_api_requests import GetSlidesThemeFontSchemeRequest
from asposeslidescloud.models.requests.slides_api_requests import GetSlidesThemeFormatSchemeRequest
from asposeslidescloud.models.requests.slides_api_requests import MoveFileRequest
from asposeslidescloud.models.requests.slides_api_requests import MoveFolderRequest
from asposeslidescloud.models.requests.slides_api_requests import ObjectExistsRequest
from asposeslidescloud.models.requests.slides_api_requests import PostAddNewParagraphRequest
from asposeslidescloud.models.requests.slides_api_requests import PostAddNewPortionRequest
from asposeslidescloud.models.requests.slides_api_requests import PostAddNewShapeRequest
from asposeslidescloud.models.requests.slides_api_requests import PostAddNotesSlideRequest
from asposeslidescloud.models.requests.slides_api_requests import PostCopyLayoutSlideFromSourcePresentationRequest
from asposeslidescloud.models.requests.slides_api_requests import PostCopyMasterSlideFromSourcePresentationRequest
from asposeslidescloud.models.requests.slides_api_requests import PostNotesSlideAddNewParagraphRequest
from asposeslidescloud.models.requests.slides_api_requests import PostNotesSlideAddNewPortionRequest
from asposeslidescloud.models.requests.slides_api_requests import PostNotesSlideAddNewShapeRequest
from asposeslidescloud.models.requests.slides_api_requests import PostNotesSlideShapeSaveAsRequest
from asposeslidescloud.models.requests.slides_api_requests import PostPresentationMergeRequest
from asposeslidescloud.models.requests.slides_api_requests import PostShapeSaveAsRequest
from asposeslidescloud.models.requests.slides_api_requests import PostSlideAnimationEffectRequest
from asposeslidescloud.models.requests.slides_api_requests import PostSlideAnimationInteractiveSequenceRequest
from asposeslidescloud.models.requests.slides_api_requests import PostSlideAnimationInteractiveSequenceEffectRequest
from asposeslidescloud.models.requests.slides_api_requests import PostSlideSaveAsRequest
from asposeslidescloud.models.requests.slides_api_requests import PostSlidesAddRequest
from asposeslidescloud.models.requests.slides_api_requests import PostSlidesConvertRequest
from asposeslidescloud.models.requests.slides_api_requests import PostSlidesCopyRequest
from asposeslidescloud.models.requests.slides_api_requests import PostSlidesDocumentRequest
from asposeslidescloud.models.requests.slides_api_requests import PostSlidesDocumentFromHtmlRequest
from asposeslidescloud.models.requests.slides_api_requests import PostSlidesDocumentFromSourceRequest
from asposeslidescloud.models.requests.slides_api_requests import PostSlidesDocumentFromTemplateRequest
from asposeslidescloud.models.requests.slides_api_requests import PostSlidesPipelineRequest
from asposeslidescloud.models.requests.slides_api_requests import PostSlidesPresentationReplaceTextRequest
from asposeslidescloud.models.requests.slides_api_requests import PostSlidesReorderRequest
from asposeslidescloud.models.requests.slides_api_requests import PostSlidesReorderManyRequest
from asposeslidescloud.models.requests.slides_api_requests import PostSlidesSaveAsRequest
from asposeslidescloud.models.requests.slides_api_requests import PostSlidesSetDocumentPropertiesRequest
from asposeslidescloud.models.requests.slides_api_requests import PostSlidesSlideReplaceTextRequest
from asposeslidescloud.models.requests.slides_api_requests import PostSlidesSplitRequest
from asposeslidescloud.models.requests.slides_api_requests import PutLayoutSlideRequest
from asposeslidescloud.models.requests.slides_api_requests import PutNotesSlideShapeSaveAsRequest
from asposeslidescloud.models.requests.slides_api_requests import PutPresentationMergeRequest
from asposeslidescloud.models.requests.slides_api_requests import PutSetParagraphPortionPropertiesRequest
from asposeslidescloud.models.requests.slides_api_requests import PutSetParagraphPropertiesRequest
from asposeslidescloud.models.requests.slides_api_requests import PutShapeSaveAsRequest
from asposeslidescloud.models.requests.slides_api_requests import PutSlideAnimationRequest
from asposeslidescloud.models.requests.slides_api_requests import PutSlideAnimationEffectRequest
from asposeslidescloud.models.requests.slides_api_requests import PutSlideAnimationInteractiveSequenceEffectRequest
from asposeslidescloud.models.requests.slides_api_requests import PutSlideSaveAsRequest
from asposeslidescloud.models.requests.slides_api_requests import PutSlideShapeInfoRequest
from asposeslidescloud.models.requests.slides_api_requests import PutSlidesConvertRequest
from asposeslidescloud.models.requests.slides_api_requests import PutSlidesDocumentFromHtmlRequest
from asposeslidescloud.models.requests.slides_api_requests import PutSlidesSaveAsRequest
from asposeslidescloud.models.requests.slides_api_requests import PutSlidesSetDocumentPropertyRequest
from asposeslidescloud.models.requests.slides_api_requests import PutSlidesSlideRequest
from asposeslidescloud.models.requests.slides_api_requests import PutSlidesSlideBackgroundRequest
from asposeslidescloud.models.requests.slides_api_requests import PutSlidesSlideBackgroundColorRequest
from asposeslidescloud.models.requests.slides_api_requests import PutSlidesSlideSizeRequest
from asposeslidescloud.models.requests.slides_api_requests import PutUpdateNotesSlideRequest
from asposeslidescloud.models.requests.slides_api_requests import PutUpdateNotesSlideShapeRequest
from asposeslidescloud.models.requests.slides_api_requests import PutUpdateNotesSlideShapeParagraphRequest
from asposeslidescloud.models.requests.slides_api_requests import PutUpdateNotesSlideShapePortionRequest
from asposeslidescloud.models.requests.slides_api_requests import StorageExistsRequest
from asposeslidescloud.models.requests.slides_api_requests import UploadFileRequest
