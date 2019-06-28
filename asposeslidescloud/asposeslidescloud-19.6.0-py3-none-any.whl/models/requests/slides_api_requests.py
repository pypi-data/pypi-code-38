# coding: utf-8

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

class CopyFileRequest(object):

    def __init__(self, src_path, dest_path, src_storage_name = None, dest_storage_name = None, version_id = None):
        self.src_path = src_path
        self.dest_path = dest_path
        self.src_storage_name = src_storage_name
        self.dest_storage_name = dest_storage_name
        self.version_id = version_id

class CopyFolderRequest(object):

    def __init__(self, src_path, dest_path, src_storage_name = None, dest_storage_name = None):
        self.src_path = src_path
        self.dest_path = dest_path
        self.src_storage_name = src_storage_name
        self.dest_storage_name = dest_storage_name

class CreateFolderRequest(object):

    def __init__(self, path = None, storage_name = None):
        self.path = path
        self.storage_name = storage_name

class DeleteFileRequest(object):

    def __init__(self, path = None, storage_name = None, version_id = None):
        self.path = path
        self.storage_name = storage_name
        self.version_id = version_id

class DeleteFolderRequest(object):

    def __init__(self, path = None, storage_name = None, recursive = None):
        self.path = path
        self.storage_name = storage_name
        self.recursive = recursive

class DeleteNotesSlideRequest(object):

    def __init__(self, name, slide_index, password = None, folder = None, storage = None):
        self.name = name
        self.slide_index = slide_index
        self.password = password
        self.folder = folder
        self.storage = storage

class DeleteNotesSlideParagraphRequest(object):

    def __init__(self, name, slide_index, shape_index, paragraph_index, path = None, password = None, folder = None, storage = None):
        self.name = name
        self.slide_index = slide_index
        self.shape_index = shape_index
        self.paragraph_index = paragraph_index
        self.path = path
        self.password = password
        self.folder = folder
        self.storage = storage

class DeleteNotesSlideParagraphsRequest(object):

    def __init__(self, name, slide_index, shape_index, path = None, paragraphs = None, password = None, folder = None, storage = None):
        self.name = name
        self.slide_index = slide_index
        self.shape_index = shape_index
        self.path = path
        self.paragraphs = paragraphs
        self.password = password
        self.folder = folder
        self.storage = storage

class DeleteNotesSlidePortionRequest(object):

    def __init__(self, name, slide_index, shape_index, paragraph_index, portion_index, path = None, password = None, folder = None, storage = None):
        self.name = name
        self.slide_index = slide_index
        self.shape_index = shape_index
        self.paragraph_index = paragraph_index
        self.portion_index = portion_index
        self.path = path
        self.password = password
        self.folder = folder
        self.storage = storage

class DeleteNotesSlidePortionsRequest(object):

    def __init__(self, name, slide_index, shape_index, paragraph_index, path = None, portions = None, password = None, folder = None, storage = None):
        self.name = name
        self.slide_index = slide_index
        self.shape_index = shape_index
        self.paragraph_index = paragraph_index
        self.path = path
        self.portions = portions
        self.password = password
        self.folder = folder
        self.storage = storage

class DeleteNotesSlideShapeRequest(object):

    def __init__(self, name, slide_index, shape_index, path = None, password = None, folder = None, storage = None):
        self.name = name
        self.slide_index = slide_index
        self.shape_index = shape_index
        self.path = path
        self.password = password
        self.folder = folder
        self.storage = storage

class DeleteNotesSlideShapesRequest(object):

    def __init__(self, name, slide_index, path = None, shapes = None, password = None, folder = None, storage = None):
        self.name = name
        self.slide_index = slide_index
        self.path = path
        self.shapes = shapes
        self.password = password
        self.folder = folder
        self.storage = storage

class DeleteParagraphRequest(object):

    def __init__(self, name, slide_index, shape_index, paragraph_index, path = None, password = None, folder = None, storage = None):
        self.name = name
        self.slide_index = slide_index
        self.shape_index = shape_index
        self.paragraph_index = paragraph_index
        self.path = path
        self.password = password
        self.folder = folder
        self.storage = storage

class DeleteParagraphsRequest(object):

    def __init__(self, name, slide_index, shape_index, path = None, paragraphs = None, password = None, folder = None, storage = None):
        self.name = name
        self.slide_index = slide_index
        self.shape_index = shape_index
        self.path = path
        self.paragraphs = paragraphs
        self.password = password
        self.folder = folder
        self.storage = storage

class DeletePortionRequest(object):

    def __init__(self, name, slide_index, shape_index, paragraph_index, portion_index, path = None, password = None, folder = None, storage = None):
        self.name = name
        self.slide_index = slide_index
        self.shape_index = shape_index
        self.paragraph_index = paragraph_index
        self.portion_index = portion_index
        self.path = path
        self.password = password
        self.folder = folder
        self.storage = storage

class DeletePortionsRequest(object):

    def __init__(self, name, slide_index, shape_index, paragraph_index, path = None, portions = None, password = None, folder = None, storage = None):
        self.name = name
        self.slide_index = slide_index
        self.shape_index = shape_index
        self.paragraph_index = paragraph_index
        self.path = path
        self.portions = portions
        self.password = password
        self.folder = folder
        self.storage = storage

class DeleteSlideAnimationRequest(object):

    def __init__(self, name, slide_index, password = None, folder = None, storage = None):
        self.name = name
        self.slide_index = slide_index
        self.password = password
        self.folder = folder
        self.storage = storage

class DeleteSlideAnimationEffectRequest(object):

    def __init__(self, name, slide_index, effect_index, password = None, folder = None, storage = None):
        self.name = name
        self.slide_index = slide_index
        self.effect_index = effect_index
        self.password = password
        self.folder = folder
        self.storage = storage

class DeleteSlideAnimationInteractiveSequenceRequest(object):

    def __init__(self, name, slide_index, sequence_index, password = None, folder = None, storage = None):
        self.name = name
        self.slide_index = slide_index
        self.sequence_index = sequence_index
        self.password = password
        self.folder = folder
        self.storage = storage

class DeleteSlideAnimationInteractiveSequenceEffectRequest(object):

    def __init__(self, name, slide_index, sequence_index, effect_index, password = None, folder = None, storage = None):
        self.name = name
        self.slide_index = slide_index
        self.sequence_index = sequence_index
        self.effect_index = effect_index
        self.password = password
        self.folder = folder
        self.storage = storage

class DeleteSlideAnimationInteractiveSequencesRequest(object):

    def __init__(self, name, slide_index, password = None, folder = None, storage = None):
        self.name = name
        self.slide_index = slide_index
        self.password = password
        self.folder = folder
        self.storage = storage

class DeleteSlideAnimationMainSequenceRequest(object):

    def __init__(self, name, slide_index, password = None, folder = None, storage = None):
        self.name = name
        self.slide_index = slide_index
        self.password = password
        self.folder = folder
        self.storage = storage

class DeleteSlideByIndexRequest(object):

    def __init__(self, name, slide_index, password = None, folder = None, storage = None):
        self.name = name
        self.slide_index = slide_index
        self.password = password
        self.folder = folder
        self.storage = storage

class DeleteSlideShapeRequest(object):

    def __init__(self, name, slide_index, shape_index, path = None, password = None, folder = None, storage = None):
        self.name = name
        self.slide_index = slide_index
        self.shape_index = shape_index
        self.path = path
        self.password = password
        self.folder = folder
        self.storage = storage

class DeleteSlideShapesRequest(object):

    def __init__(self, name, slide_index, path = None, shapes = None, password = None, folder = None, storage = None):
        self.name = name
        self.slide_index = slide_index
        self.path = path
        self.shapes = shapes
        self.password = password
        self.folder = folder
        self.storage = storage

class DeleteSlidesCleanSlidesListRequest(object):

    def __init__(self, name, slides = None, password = None, folder = None, storage = None):
        self.name = name
        self.slides = slides
        self.password = password
        self.folder = folder
        self.storage = storage

class DeleteSlidesDocumentPropertiesRequest(object):

    def __init__(self, name, password = None, folder = None, storage = None):
        self.name = name
        self.password = password
        self.folder = folder
        self.storage = storage

class DeleteSlidesDocumentPropertyRequest(object):

    def __init__(self, name, property_name, password = None, folder = None, storage = None):
        self.name = name
        self.property_name = property_name
        self.password = password
        self.folder = folder
        self.storage = storage

class DeleteSlidesSlideBackgroundRequest(object):

    def __init__(self, name, slide_index, password = None, folder = None, storage = None):
        self.name = name
        self.slide_index = slide_index
        self.password = password
        self.folder = folder
        self.storage = storage

class DownloadFileRequest(object):

    def __init__(self, path = None, storage_name = None, version_id = None):
        self.path = path
        self.storage_name = storage_name
        self.version_id = version_id

class GetDiscUsageRequest(object):

    def __init__(self, storage_name = None):
        self.storage_name = storage_name

class GetFileVersionsRequest(object):

    def __init__(self, path = None, storage_name = None):
        self.path = path
        self.storage_name = storage_name

class GetFilesListRequest(object):

    def __init__(self, path = None, storage_name = None):
        self.path = path
        self.storage_name = storage_name

class GetLayoutSlideRequest(object):

    def __init__(self, name, slide_index, password = None, folder = None, storage = None):
        self.name = name
        self.slide_index = slide_index
        self.password = password
        self.folder = folder
        self.storage = storage

class GetLayoutSlidesListRequest(object):

    def __init__(self, name, password = None, folder = None, storage = None):
        self.name = name
        self.password = password
        self.folder = folder
        self.storage = storage

class GetMasterSlideRequest(object):

    def __init__(self, name, slide_index, password = None, folder = None, storage = None):
        self.name = name
        self.slide_index = slide_index
        self.password = password
        self.folder = folder
        self.storage = storage

class GetMasterSlidesListRequest(object):

    def __init__(self, name, password = None, folder = None, storage = None):
        self.name = name
        self.password = password
        self.folder = folder
        self.storage = storage

class GetNotesSlideRequest(object):

    def __init__(self, name, slide_index, password = None, folder = None, storage = None):
        self.name = name
        self.slide_index = slide_index
        self.password = password
        self.folder = folder
        self.storage = storage

class GetNotesSlideShapeRequest(object):

    def __init__(self, name, slide_index, shape_index, path = None, password = None, folder = None, storage = None):
        self.name = name
        self.slide_index = slide_index
        self.shape_index = shape_index
        self.path = path
        self.password = password
        self.folder = folder
        self.storage = storage

class GetNotesSlideShapeParagraphRequest(object):

    def __init__(self, name, slide_index, shape_index, paragraph_index, path = None, password = None, folder = None, storage = None):
        self.name = name
        self.slide_index = slide_index
        self.shape_index = shape_index
        self.paragraph_index = paragraph_index
        self.path = path
        self.password = password
        self.folder = folder
        self.storage = storage

class GetNotesSlideShapeParagraphsRequest(object):

    def __init__(self, name, slide_index, shape_index, path = None, password = None, folder = None, storage = None):
        self.name = name
        self.slide_index = slide_index
        self.shape_index = shape_index
        self.path = path
        self.password = password
        self.folder = folder
        self.storage = storage

class GetNotesSlideShapePortionRequest(object):

    def __init__(self, name, slide_index, shape_index, paragraph_index, portion_index, path = None, password = None, folder = None, storage = None):
        self.name = name
        self.slide_index = slide_index
        self.shape_index = shape_index
        self.paragraph_index = paragraph_index
        self.portion_index = portion_index
        self.path = path
        self.password = password
        self.folder = folder
        self.storage = storage

class GetNotesSlideShapePortionsRequest(object):

    def __init__(self, name, slide_index, shape_index, paragraph_index, path = None, password = None, folder = None, storage = None):
        self.name = name
        self.slide_index = slide_index
        self.shape_index = shape_index
        self.paragraph_index = paragraph_index
        self.path = path
        self.password = password
        self.folder = folder
        self.storage = storage

class GetNotesSlideShapesRequest(object):

    def __init__(self, name, slide_index, path = None, password = None, folder = None, storage = None):
        self.name = name
        self.slide_index = slide_index
        self.path = path
        self.password = password
        self.folder = folder
        self.storage = storage

class GetNotesSlideWithFormatRequest(object):

    def __init__(self, name, slide_index, format, width = None, height = None, password = None, folder = None, storage = None, fonts_folder = None):
        self.name = name
        self.slide_index = slide_index
        self.format = format
        self.width = width
        self.height = height
        self.password = password
        self.folder = folder
        self.storage = storage
        self.fonts_folder = fonts_folder

class GetParagraphPortionRequest(object):

    def __init__(self, name, slide_index, shape_index, paragraph_index, portion_index, path = None, password = None, folder = None, storage = None):
        self.name = name
        self.slide_index = slide_index
        self.shape_index = shape_index
        self.paragraph_index = paragraph_index
        self.portion_index = portion_index
        self.path = path
        self.password = password
        self.folder = folder
        self.storage = storage

class GetParagraphPortionsRequest(object):

    def __init__(self, name, slide_index, shape_index, paragraph_index, path = None, password = None, folder = None, storage = None):
        self.name = name
        self.slide_index = slide_index
        self.shape_index = shape_index
        self.paragraph_index = paragraph_index
        self.path = path
        self.password = password
        self.folder = folder
        self.storage = storage

class GetSlideAnimationRequest(object):

    def __init__(self, name, slide_index, shape_index, password = None, folder = None, storage = None):
        self.name = name
        self.slide_index = slide_index
        self.shape_index = shape_index
        self.password = password
        self.folder = folder
        self.storage = storage

class GetSlideShapeRequest(object):

    def __init__(self, name, slide_index, shape_index, path = None, password = None, folder = None, storage = None):
        self.name = name
        self.slide_index = slide_index
        self.shape_index = shape_index
        self.path = path
        self.password = password
        self.folder = folder
        self.storage = storage

class GetSlideShapeParagraphRequest(object):

    def __init__(self, name, slide_index, shape_index, paragraph_index, path = None, password = None, folder = None, storage = None):
        self.name = name
        self.slide_index = slide_index
        self.shape_index = shape_index
        self.paragraph_index = paragraph_index
        self.path = path
        self.password = password
        self.folder = folder
        self.storage = storage

class GetSlideShapeParagraphsRequest(object):

    def __init__(self, name, slide_index, shape_index, path = None, password = None, folder = None, storage = None):
        self.name = name
        self.slide_index = slide_index
        self.shape_index = shape_index
        self.path = path
        self.password = password
        self.folder = folder
        self.storage = storage

class GetSlideShapesRequest(object):

    def __init__(self, name, slide_index, path = None, password = None, folder = None, storage = None):
        self.name = name
        self.slide_index = slide_index
        self.path = path
        self.password = password
        self.folder = folder
        self.storage = storage

class GetSlidesDocumentRequest(object):

    def __init__(self, name, password = None, storage = None, folder = None):
        self.name = name
        self.password = password
        self.storage = storage
        self.folder = folder

class GetSlidesDocumentPropertiesRequest(object):

    def __init__(self, name, password = None, folder = None, storage = None):
        self.name = name
        self.password = password
        self.folder = folder
        self.storage = storage

class GetSlidesDocumentPropertyRequest(object):

    def __init__(self, name, property_name, password = None, folder = None, storage = None):
        self.name = name
        self.property_name = property_name
        self.password = password
        self.folder = folder
        self.storage = storage

class GetSlidesImageWithDefaultFormatRequest(object):

    def __init__(self, name, index, password = None, folder = None, storage = None):
        self.name = name
        self.index = index
        self.password = password
        self.folder = folder
        self.storage = storage

class GetSlidesImageWithFormatRequest(object):

    def __init__(self, name, index, format, password = None, folder = None, storage = None):
        self.name = name
        self.index = index
        self.format = format
        self.password = password
        self.folder = folder
        self.storage = storage

class GetSlidesImagesRequest(object):

    def __init__(self, name, password = None, folder = None, storage = None):
        self.name = name
        self.password = password
        self.folder = folder
        self.storage = storage

class GetSlidesPlaceholderRequest(object):

    def __init__(self, name, slide_index, placeholder_index, password = None, folder = None, storage = None):
        self.name = name
        self.slide_index = slide_index
        self.placeholder_index = placeholder_index
        self.password = password
        self.folder = folder
        self.storage = storage

class GetSlidesPlaceholdersRequest(object):

    def __init__(self, name, slide_index, password = None, folder = None, storage = None):
        self.name = name
        self.slide_index = slide_index
        self.password = password
        self.folder = folder
        self.storage = storage

class GetSlidesPresentationTextItemsRequest(object):

    def __init__(self, name, with_empty = None, password = None, folder = None, storage = None):
        self.name = name
        self.with_empty = with_empty
        self.password = password
        self.folder = folder
        self.storage = storage

class GetSlidesSlideRequest(object):

    def __init__(self, name, slide_index, password = None, folder = None, storage = None):
        self.name = name
        self.slide_index = slide_index
        self.password = password
        self.folder = folder
        self.storage = storage

class GetSlidesSlideBackgroundRequest(object):

    def __init__(self, name, slide_index, password = None, folder = None, storage = None):
        self.name = name
        self.slide_index = slide_index
        self.password = password
        self.folder = folder
        self.storage = storage

class GetSlidesSlideCommentsRequest(object):

    def __init__(self, name, slide_index, password = None, folder = None, storage = None):
        self.name = name
        self.slide_index = slide_index
        self.password = password
        self.folder = folder
        self.storage = storage

class GetSlidesSlideImagesRequest(object):

    def __init__(self, name, slide_index, password = None, folder = None, storage = None):
        self.name = name
        self.slide_index = slide_index
        self.password = password
        self.folder = folder
        self.storage = storage

class GetSlidesSlideTextItemsRequest(object):

    def __init__(self, name, slide_index, with_empty = None, password = None, folder = None, storage = None):
        self.name = name
        self.slide_index = slide_index
        self.with_empty = with_empty
        self.password = password
        self.folder = folder
        self.storage = storage

class GetSlidesSlidesListRequest(object):

    def __init__(self, name, password = None, folder = None, storage = None):
        self.name = name
        self.password = password
        self.folder = folder
        self.storage = storage

class GetSlidesThemeRequest(object):

    def __init__(self, name, slide_index, password = None, folder = None, storage = None):
        self.name = name
        self.slide_index = slide_index
        self.password = password
        self.folder = folder
        self.storage = storage

class GetSlidesThemeColorSchemeRequest(object):

    def __init__(self, name, slide_index, password = None, folder = None, storage = None):
        self.name = name
        self.slide_index = slide_index
        self.password = password
        self.folder = folder
        self.storage = storage

class GetSlidesThemeFontSchemeRequest(object):

    def __init__(self, name, slide_index, password = None, folder = None, storage = None):
        self.name = name
        self.slide_index = slide_index
        self.password = password
        self.folder = folder
        self.storage = storage

class GetSlidesThemeFormatSchemeRequest(object):

    def __init__(self, name, slide_index, password = None, folder = None, storage = None):
        self.name = name
        self.slide_index = slide_index
        self.password = password
        self.folder = folder
        self.storage = storage

class MoveFileRequest(object):

    def __init__(self, src_path, dest_path, src_storage_name = None, dest_storage_name = None, version_id = None):
        self.src_path = src_path
        self.dest_path = dest_path
        self.src_storage_name = src_storage_name
        self.dest_storage_name = dest_storage_name
        self.version_id = version_id

class MoveFolderRequest(object):

    def __init__(self, src_path, dest_path, src_storage_name = None, dest_storage_name = None):
        self.src_path = src_path
        self.dest_path = dest_path
        self.src_storage_name = src_storage_name
        self.dest_storage_name = dest_storage_name

class ObjectExistsRequest(object):

    def __init__(self, path = None, storage_name = None, version_id = None):
        self.path = path
        self.storage_name = storage_name
        self.version_id = version_id

class PostAddNewParagraphRequest(object):

    def __init__(self, name, slide_index, shape_index, path = None, dto = None, password = None, folder = None, storage = None, position = None):
        self.name = name
        self.slide_index = slide_index
        self.shape_index = shape_index
        self.path = path
        self.dto = dto
        self.password = password
        self.folder = folder
        self.storage = storage
        self.position = position

class PostAddNewPortionRequest(object):

    def __init__(self, name, slide_index, shape_index, paragraph_index, path = None, dto = None, password = None, folder = None, storage = None, position = None):
        self.name = name
        self.slide_index = slide_index
        self.shape_index = shape_index
        self.paragraph_index = paragraph_index
        self.path = path
        self.dto = dto
        self.password = password
        self.folder = folder
        self.storage = storage
        self.position = position

class PostAddNewShapeRequest(object):

    def __init__(self, name, slide_index, path = None, dto = None, password = None, folder = None, storage = None, shape_to_clone = None, position = None):
        self.name = name
        self.slide_index = slide_index
        self.path = path
        self.dto = dto
        self.password = password
        self.folder = folder
        self.storage = storage
        self.shape_to_clone = shape_to_clone
        self.position = position

class PostAddNotesSlideRequest(object):

    def __init__(self, name, slide_index, dto = None, password = None, folder = None, storage = None):
        self.name = name
        self.slide_index = slide_index
        self.dto = dto
        self.password = password
        self.folder = folder
        self.storage = storage

class PostCopyLayoutSlideFromSourcePresentationRequest(object):

    def __init__(self, name, clone_from, clone_from_position, clone_from_password = None, clone_from_storage = None, password = None, folder = None, storage = None):
        self.name = name
        self.clone_from = clone_from
        self.clone_from_position = clone_from_position
        self.clone_from_password = clone_from_password
        self.clone_from_storage = clone_from_storage
        self.password = password
        self.folder = folder
        self.storage = storage

class PostCopyMasterSlideFromSourcePresentationRequest(object):

    def __init__(self, name, clone_from, clone_from_position, clone_from_password = None, clone_from_storage = None, apply_to_all = None, password = None, folder = None, storage = None):
        self.name = name
        self.clone_from = clone_from
        self.clone_from_position = clone_from_position
        self.clone_from_password = clone_from_password
        self.clone_from_storage = clone_from_storage
        self.apply_to_all = apply_to_all
        self.password = password
        self.folder = folder
        self.storage = storage

class PostNotesSlideAddNewParagraphRequest(object):

    def __init__(self, name, slide_index, shape_index, path = None, dto = None, password = None, folder = None, storage = None, position = None):
        self.name = name
        self.slide_index = slide_index
        self.shape_index = shape_index
        self.path = path
        self.dto = dto
        self.password = password
        self.folder = folder
        self.storage = storage
        self.position = position

class PostNotesSlideAddNewPortionRequest(object):

    def __init__(self, name, slide_index, shape_index, paragraph_index, path = None, dto = None, password = None, folder = None, storage = None, position = None):
        self.name = name
        self.slide_index = slide_index
        self.shape_index = shape_index
        self.paragraph_index = paragraph_index
        self.path = path
        self.dto = dto
        self.password = password
        self.folder = folder
        self.storage = storage
        self.position = position

class PostNotesSlideAddNewShapeRequest(object):

    def __init__(self, name, slide_index, path = None, dto = None, password = None, folder = None, storage = None, shape_to_clone = None, position = None):
        self.name = name
        self.slide_index = slide_index
        self.path = path
        self.dto = dto
        self.password = password
        self.folder = folder
        self.storage = storage
        self.shape_to_clone = shape_to_clone
        self.position = position

class PostNotesSlideShapeSaveAsRequest(object):

    def __init__(self, name, slide_index, shape_index, format, path = None, options = None, password = None, folder = None, storage = None, scale_x = None, scale_y = None, bounds = None, fonts_folder = None):
        self.name = name
        self.slide_index = slide_index
        self.shape_index = shape_index
        self.format = format
        self.path = path
        self.options = options
        self.password = password
        self.folder = folder
        self.storage = storage
        self.scale_x = scale_x
        self.scale_y = scale_y
        self.bounds = bounds
        self.fonts_folder = fonts_folder

class PostPresentationMergeRequest(object):

    def __init__(self, name, request = None, password = None, storage = None, folder = None):
        self.name = name
        self.request = request
        self.password = password
        self.storage = storage
        self.folder = folder

class PostShapeSaveAsRequest(object):

    def __init__(self, name, slide_index, shape_index, format, path = None, options = None, password = None, folder = None, storage = None, scale_x = None, scale_y = None, bounds = None, fonts_folder = None):
        self.name = name
        self.slide_index = slide_index
        self.shape_index = shape_index
        self.format = format
        self.path = path
        self.options = options
        self.password = password
        self.folder = folder
        self.storage = storage
        self.scale_x = scale_x
        self.scale_y = scale_y
        self.bounds = bounds
        self.fonts_folder = fonts_folder

class PostSlideAnimationEffectRequest(object):

    def __init__(self, name, slide_index, effect = None, password = None, folder = None, storage = None):
        self.name = name
        self.slide_index = slide_index
        self.effect = effect
        self.password = password
        self.folder = folder
        self.storage = storage

class PostSlideAnimationInteractiveSequenceRequest(object):

    def __init__(self, name, slide_index, sequence = None, password = None, folder = None, storage = None):
        self.name = name
        self.slide_index = slide_index
        self.sequence = sequence
        self.password = password
        self.folder = folder
        self.storage = storage

class PostSlideAnimationInteractiveSequenceEffectRequest(object):

    def __init__(self, name, slide_index, sequence_index, effect = None, password = None, folder = None, storage = None):
        self.name = name
        self.slide_index = slide_index
        self.sequence_index = sequence_index
        self.effect = effect
        self.password = password
        self.folder = folder
        self.storage = storage

class PostSlideSaveAsRequest(object):

    def __init__(self, name, slide_index, format, options = None, width = None, height = None, password = None, folder = None, storage = None, fonts_folder = None):
        self.name = name
        self.slide_index = slide_index
        self.format = format
        self.options = options
        self.width = width
        self.height = height
        self.password = password
        self.folder = folder
        self.storage = storage
        self.fonts_folder = fonts_folder

class PostSlidesAddRequest(object):

    def __init__(self, name, position = None, password = None, folder = None, storage = None, layout_alias = None):
        self.name = name
        self.position = position
        self.password = password
        self.folder = folder
        self.storage = storage
        self.layout_alias = layout_alias

class PostSlidesConvertRequest(object):

    def __init__(self, format, document = None, password = None, fonts_folder = None):
        self.format = format
        self.document = document
        self.password = password
        self.fonts_folder = fonts_folder

class PostSlidesCopyRequest(object):

    def __init__(self, name, slide_to_copy, position = None, source = None, source_password = None, source_storage = None, password = None, folder = None, storage = None):
        self.name = name
        self.slide_to_copy = slide_to_copy
        self.position = position
        self.source = source
        self.source_password = source_password
        self.source_storage = source_storage
        self.password = password
        self.folder = folder
        self.storage = storage

class PostSlidesDocumentRequest(object):

    def __init__(self, name, data = None, input_password = None, password = None, storage = None, folder = None):
        self.name = name
        self.data = data
        self.input_password = input_password
        self.password = password
        self.storage = storage
        self.folder = folder

class PostSlidesDocumentFromHtmlRequest(object):

    def __init__(self, name, html = None, password = None, storage = None, folder = None):
        self.name = name
        self.html = html
        self.password = password
        self.storage = storage
        self.folder = folder

class PostSlidesDocumentFromSourceRequest(object):

    def __init__(self, name, source_path = None, source_password = None, source_storage = None, password = None, storage = None, folder = None):
        self.name = name
        self.source_path = source_path
        self.source_password = source_password
        self.source_storage = source_storage
        self.password = password
        self.storage = storage
        self.folder = folder

class PostSlidesDocumentFromTemplateRequest(object):

    def __init__(self, name, template_path, data = None, template_password = None, template_storage = None, is_image_data_embedded = None, password = None, storage = None, folder = None):
        self.name = name
        self.template_path = template_path
        self.data = data
        self.template_password = template_password
        self.template_storage = template_storage
        self.is_image_data_embedded = is_image_data_embedded
        self.password = password
        self.storage = storage
        self.folder = folder

class PostSlidesPipelineRequest(object):

    def __init__(self, pipeline = None, files = None):
        self.pipeline = pipeline
        self.files = files

class PostSlidesPresentationReplaceTextRequest(object):

    def __init__(self, name, old_value, new_value, ignore_case = None, password = None, folder = None, storage = None):
        self.name = name
        self.old_value = old_value
        self.new_value = new_value
        self.ignore_case = ignore_case
        self.password = password
        self.folder = folder
        self.storage = storage

class PostSlidesReorderRequest(object):

    def __init__(self, name, slide_index, new_position, password = None, folder = None, storage = None):
        self.name = name
        self.slide_index = slide_index
        self.new_position = new_position
        self.password = password
        self.folder = folder
        self.storage = storage

class PostSlidesReorderManyRequest(object):

    def __init__(self, name, old_positions = None, new_positions = None, password = None, folder = None, storage = None):
        self.name = name
        self.old_positions = old_positions
        self.new_positions = new_positions
        self.password = password
        self.folder = folder
        self.storage = storage

class PostSlidesSaveAsRequest(object):

    def __init__(self, name, format, options = None, password = None, storage = None, folder = None, fonts_folder = None):
        self.name = name
        self.format = format
        self.options = options
        self.password = password
        self.storage = storage
        self.folder = folder
        self.fonts_folder = fonts_folder

class PostSlidesSetDocumentPropertiesRequest(object):

    def __init__(self, name, properties = None, password = None, folder = None, storage = None):
        self.name = name
        self.properties = properties
        self.password = password
        self.folder = folder
        self.storage = storage

class PostSlidesSlideReplaceTextRequest(object):

    def __init__(self, name, slide_index, old_value, new_value, ignore_case = None, password = None, folder = None, storage = None):
        self.name = name
        self.slide_index = slide_index
        self.old_value = old_value
        self.new_value = new_value
        self.ignore_case = ignore_case
        self.password = password
        self.folder = folder
        self.storage = storage

class PostSlidesSplitRequest(object):

    def __init__(self, name, options = None, format = None, width = None, height = None, to = None, _from = None, dest_folder = None, password = None, storage = None, folder = None, fonts_folder = None):
        self.name = name
        self.options = options
        self.format = format
        self.width = width
        self.height = height
        self.to = to
        self._from = _from
        self.dest_folder = dest_folder
        self.password = password
        self.storage = storage
        self.folder = folder
        self.fonts_folder = fonts_folder

class PutLayoutSlideRequest(object):

    def __init__(self, name, slide_index, slide_dto = None, password = None, folder = None, storage = None):
        self.name = name
        self.slide_index = slide_index
        self.slide_dto = slide_dto
        self.password = password
        self.folder = folder
        self.storage = storage

class PutNotesSlideShapeSaveAsRequest(object):

    def __init__(self, name, slide_index, shape_index, format, out_path, path = None, options = None, password = None, folder = None, storage = None, scale_x = None, scale_y = None, bounds = None, fonts_folder = None):
        self.name = name
        self.slide_index = slide_index
        self.shape_index = shape_index
        self.format = format
        self.out_path = out_path
        self.path = path
        self.options = options
        self.password = password
        self.folder = folder
        self.storage = storage
        self.scale_x = scale_x
        self.scale_y = scale_y
        self.bounds = bounds
        self.fonts_folder = fonts_folder

class PutPresentationMergeRequest(object):

    def __init__(self, name, request = None, password = None, storage = None, folder = None):
        self.name = name
        self.request = request
        self.password = password
        self.storage = storage
        self.folder = folder

class PutSetParagraphPortionPropertiesRequest(object):

    def __init__(self, name, slide_index, shape_index, paragraph_index, portion_index, path = None, dto = None, password = None, folder = None, storage = None):
        self.name = name
        self.slide_index = slide_index
        self.shape_index = shape_index
        self.paragraph_index = paragraph_index
        self.portion_index = portion_index
        self.path = path
        self.dto = dto
        self.password = password
        self.folder = folder
        self.storage = storage

class PutSetParagraphPropertiesRequest(object):

    def __init__(self, name, slide_index, shape_index, paragraph_index, path = None, dto = None, password = None, folder = None, storage = None):
        self.name = name
        self.slide_index = slide_index
        self.shape_index = shape_index
        self.paragraph_index = paragraph_index
        self.path = path
        self.dto = dto
        self.password = password
        self.folder = folder
        self.storage = storage

class PutShapeSaveAsRequest(object):

    def __init__(self, name, slide_index, shape_index, format, out_path, path = None, options = None, password = None, folder = None, storage = None, scale_x = None, scale_y = None, bounds = None, fonts_folder = None):
        self.name = name
        self.slide_index = slide_index
        self.shape_index = shape_index
        self.format = format
        self.out_path = out_path
        self.path = path
        self.options = options
        self.password = password
        self.folder = folder
        self.storage = storage
        self.scale_x = scale_x
        self.scale_y = scale_y
        self.bounds = bounds
        self.fonts_folder = fonts_folder

class PutSlideAnimationRequest(object):

    def __init__(self, name, slide_index, animation = None, password = None, folder = None, storage = None):
        self.name = name
        self.slide_index = slide_index
        self.animation = animation
        self.password = password
        self.folder = folder
        self.storage = storage

class PutSlideAnimationEffectRequest(object):

    def __init__(self, name, slide_index, effect_index, effect = None, password = None, folder = None, storage = None):
        self.name = name
        self.slide_index = slide_index
        self.effect_index = effect_index
        self.effect = effect
        self.password = password
        self.folder = folder
        self.storage = storage

class PutSlideAnimationInteractiveSequenceEffectRequest(object):

    def __init__(self, name, slide_index, sequence_index, effect_index, effect = None, password = None, folder = None, storage = None):
        self.name = name
        self.slide_index = slide_index
        self.sequence_index = sequence_index
        self.effect_index = effect_index
        self.effect = effect
        self.password = password
        self.folder = folder
        self.storage = storage

class PutSlideSaveAsRequest(object):

    def __init__(self, name, slide_index, format, out_path, options = None, width = None, height = None, password = None, folder = None, storage = None, fonts_folder = None):
        self.name = name
        self.slide_index = slide_index
        self.format = format
        self.out_path = out_path
        self.options = options
        self.width = width
        self.height = height
        self.password = password
        self.folder = folder
        self.storage = storage
        self.fonts_folder = fonts_folder

class PutSlideShapeInfoRequest(object):

    def __init__(self, name, slide_index, shape_index, path = None, dto = None, password = None, folder = None, storage = None):
        self.name = name
        self.slide_index = slide_index
        self.shape_index = shape_index
        self.path = path
        self.dto = dto
        self.password = password
        self.folder = folder
        self.storage = storage

class PutSlidesConvertRequest(object):

    def __init__(self, format, out_path, document = None, password = None, fonts_folder = None):
        self.format = format
        self.out_path = out_path
        self.document = document
        self.password = password
        self.fonts_folder = fonts_folder

class PutSlidesDocumentFromHtmlRequest(object):

    def __init__(self, name, html = None, password = None, storage = None, folder = None):
        self.name = name
        self.html = html
        self.password = password
        self.storage = storage
        self.folder = folder

class PutSlidesSaveAsRequest(object):

    def __init__(self, name, out_path, format, options = None, password = None, storage = None, folder = None, fonts_folder = None):
        self.name = name
        self.out_path = out_path
        self.format = format
        self.options = options
        self.password = password
        self.storage = storage
        self.folder = folder
        self.fonts_folder = fonts_folder

class PutSlidesSetDocumentPropertyRequest(object):

    def __init__(self, name, property_name, _property = None, password = None, folder = None, storage = None):
        self.name = name
        self.property_name = property_name
        self._property = _property
        self.password = password
        self.folder = folder
        self.storage = storage

class PutSlidesSlideRequest(object):

    def __init__(self, name, slide_index, slide_dto = None, password = None, folder = None, storage = None):
        self.name = name
        self.slide_index = slide_index
        self.slide_dto = slide_dto
        self.password = password
        self.folder = folder
        self.storage = storage

class PutSlidesSlideBackgroundRequest(object):

    def __init__(self, name, slide_index, background = None, folder = None, password = None, storage = None):
        self.name = name
        self.slide_index = slide_index
        self.background = background
        self.folder = folder
        self.password = password
        self.storage = storage

class PutSlidesSlideBackgroundColorRequest(object):

    def __init__(self, name, slide_index, color, folder = None, password = None, storage = None):
        self.name = name
        self.slide_index = slide_index
        self.color = color
        self.folder = folder
        self.password = password
        self.storage = storage

class PutSlidesSlideSizeRequest(object):

    def __init__(self, name, password = None, storage = None, folder = None, width = None, height = None, size_type = None, scale_type = None):
        self.name = name
        self.password = password
        self.storage = storage
        self.folder = folder
        self.width = width
        self.height = height
        self.size_type = size_type
        self.scale_type = scale_type

class PutUpdateNotesSlideRequest(object):

    def __init__(self, name, slide_index, dto = None, password = None, folder = None, storage = None):
        self.name = name
        self.slide_index = slide_index
        self.dto = dto
        self.password = password
        self.folder = folder
        self.storage = storage

class PutUpdateNotesSlideShapeRequest(object):

    def __init__(self, name, slide_index, shape_index, path = None, dto = None, password = None, folder = None, storage = None):
        self.name = name
        self.slide_index = slide_index
        self.shape_index = shape_index
        self.path = path
        self.dto = dto
        self.password = password
        self.folder = folder
        self.storage = storage

class PutUpdateNotesSlideShapeParagraphRequest(object):

    def __init__(self, name, slide_index, shape_index, paragraph_index, path = None, dto = None, password = None, folder = None, storage = None):
        self.name = name
        self.slide_index = slide_index
        self.shape_index = shape_index
        self.paragraph_index = paragraph_index
        self.path = path
        self.dto = dto
        self.password = password
        self.folder = folder
        self.storage = storage

class PutUpdateNotesSlideShapePortionRequest(object):

    def __init__(self, name, slide_index, shape_index, paragraph_index, portion_index, path = None, dto = None, password = None, folder = None, storage = None):
        self.name = name
        self.slide_index = slide_index
        self.shape_index = shape_index
        self.paragraph_index = paragraph_index
        self.portion_index = portion_index
        self.path = path
        self.dto = dto
        self.password = password
        self.folder = folder
        self.storage = storage

class StorageExistsRequest(object):

    def __init__(self, storage_name):
        self.storage_name = storage_name

class UploadFileRequest(object):

    def __init__(self, file, path = None, storage_name = None):
        self.file = file
        self.path = path
        self.storage_name = storage_name

