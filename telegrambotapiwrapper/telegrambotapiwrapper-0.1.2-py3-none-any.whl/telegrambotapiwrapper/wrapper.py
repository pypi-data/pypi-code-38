# -*- coding: utf-8 -*-
# Copyright (c) 2019 Dzmitry Maliuzhenets; MIT License
"""Module containing wrapper around Telegram Bot Api methods."""
import inspect
import io
from typing import BinaryIO

import requests

import telegrambotapiwrapper.frames as frames
from telegrambotapiwrapper.annotation import AnnotationWrapper
from telegrambotapiwrapper.typelib import *
from telegrambotapiwrapper.typelib import (
    PassportElementErrorDataField, PassportElementErrorFrontSide,
    PassportElementErrorReverseSide, PassportElementErrorSelfie,
    PassportElementErrorFile, PassportElementErrorFiles,
    PassportElementErrorTranslationFile, PassportElementErrorUnspecified,
    PassportElementErrorTranslationFiles, InputMediaAnimation,
    InputMediaDocument, InputMediaAudio, InputMediaPhoto, InputMediaVideo,
    InlineQueryResultCachedAudio, InlineQueryResultCachedDocument,
    InlineQueryResultCachedGif, InlineQueryResultCachedMpeg4Gif,
    InlineQueryResultCachedPhoto, InlineQueryResultCachedSticker,
    InlineQueryResultCachedVideo, InlineQueryResultCachedVoice,
    InlineQueryResultArticle, InlineQueryResultAudio, InlineQueryResultContact,
    InlineQueryResultGame, InlineQueryResultDocument, InlineQueryResultGif,
    InlineQueryResultMpeg4Gif, InlineQueryResultPhoto, InlineQueryResultVenue,
    InlineQueryResultVideo, InlineQueryResultVoice, InlineKeyboardMarkup,
    ReplyKeyboardMarkup, ReplyKeyboardRemove, ForceReply,
    InlineQueryResultLocation, MaskPosition, LabeledPrice)
from telegrambotapiwrapper.request import json_payload
from telegrambotapiwrapper.response import handle_response

PassportElementError = Union[
    PassportElementErrorDataField, PassportElementErrorFrontSide,
    PassportElementErrorReverseSide, PassportElementErrorSelfie,
    PassportElementErrorFile, PassportElementErrorFiles,
    PassportElementErrorTranslationFile, PassportElementErrorTranslationFiles,
    PassportElementErrorUnspecified]
InputMedia = Union[InputMediaAnimation, InputMediaDocument, InputMediaAudio,
                   InputMediaPhoto, InputMediaVideo]

InlineQueryResult = Union[
    InlineQueryResultCachedAudio, InlineQueryResultCachedDocument,
    InlineQueryResultCachedGif, InlineQueryResultCachedMpeg4Gif,
    InlineQueryResultCachedPhoto, InlineQueryResultCachedSticker,
    InlineQueryResultCachedVideo, InlineQueryResultCachedVoice,
    InlineQueryResultArticle, InlineQueryResultAudio, InlineQueryResultContact,
    InlineQueryResultGame, InlineQueryResultDocument, InlineQueryResultGif,
    InlineQueryResultLocation, InlineQueryResultMpeg4Gif,
    InlineQueryResultPhoto, InlineQueryResultVenue, InlineQueryResultVideo,
    InlineQueryResultVoice, ]


class ApiBase: # pylint: disable=too-few-public-methods
    """This class contains methods that are not methods Telegram Bot Api."""

    def __init__(self, token: str):
        self.token = token

    @staticmethod
    def _get_tg_api_method_name(py_style_method_name):
        """Get Telegram API method name from python method name."""
        res = py_style_method_name.replace("_", " ").title().replace(" ", "")
        res = res[0].lower() + res[1:]
        return res

    def _get_tg_api_method_url(self, api_method_name: str):
        """Get method url."""
        return "https://api.telegram.org/bot{}/{}".format(
            self.token, api_method_name)

    @classmethod
    def _get_caller_method_return_type(cls) -> AnnotationWrapper:
        """Get caller return value annotation.

        Get the annotation of the return value of the method within which this
        method is called.

        Notes:
            The result contains only the name of the type without the path to
            it.
        """
        caller_method_name = inspect.stack()[1][3]
        res = inspect.signature(getattr(cls,
                                         caller_method_name)).return_annotation
        return AnnotationWrapper(res).sanitized

    def _get_caller2_return_type(self) -> AnnotationWrapper:
        """Get caller caller return value annotation.

        Notes:
            The result contains only the name of the type without the path to
            it.
        """
        caller2_name = (inspect.stack()[2][3])
        signature = inspect.signature(getattr(self, caller2_name))
        annotation = signature.return_annotation
        anno_wrapper = AnnotationWrapper(annotation)
        return anno_wrapper.sanitized

    def _make_request(self):
        """Make a request to Telegram Bot Api."""
        args = frames.outer2_args()

        result_type = self._get_caller2_return_type()
        caller2_name = frames.outer2_name()
        tg_method_name = self._get_tg_api_method_name(caller2_name)

        payload = json_payload(args)

        url = self._get_tg_api_method_url(tg_method_name)

        r = requests.post(
            url, data=payload, headers={'Content-Type': 'application/json'})
        return handle_response(r.content.decode('utf-8'), result_type)


class Api(ApiBase): # pylint: disable=too-many-public-methods
    """Class containing methods Telegram Bot Api.

    Args:
        token (str): token

    Attributes:
        token (str): token
    """

    def __init__(self, token: str):
        super().__init__(token=token)

    def set_chat_photo(
            self,
            chat_id: Union[int, str],
            photo: BinaryIO,
    ) -> bool:
        """Use this method to set a new profile photo for the chat. Photos can't
           be changed for private chats. The bot must be an administrator in
           the chat for this to work and must have the appropriate admin rights.
           Returns True on success."""

        url = self._get_tg_api_method_url('setChatPhoto')
        values = frames.outer_args()

        del values['photo']
        files = {'photo': photo}

        r = requests.post(url, files=files, data=values)
        return handle_response(
            r.content.decode('utf-8'), AnnotationWrapper('bool'))

    def send_sticker(
            self,
            chat_id: Union[int, str],
            sticker: Union[BinaryIO, str],
            disable_notification: Optional[bool] = None,
            reply_to_message_id: Optional[int] = None,
            reply_markup: Optional[
                Union[InlineKeyboardMarkup, ReplyKeyboardMarkup,
                      ReplyKeyboardRemove, ForceReply]] = None,
    ) -> Message:
        """Use this method to send .webp stickers. On success, the sent Message
           is returned."""

        url = self._get_tg_api_method_url('sendSticker')
        values = frames.outer_args()
        del values['sticker']

        if isinstance(sticker, str):
            return self._make_request()
        else:
            # assert isinstance(png_sticker, io.BytesIO):
            files = {'sticker': sticker}

            r = requests.post(url, files=files, data=values)
            return handle_response(
                r.content.decode('utf-8'), AnnotationWrapper('Message'))

    def add_sticker_to_set(
            self,
            user_id: int,
            name: str,
            png_sticker: Union[BinaryIO, str],
            emojis: str,
            mask_position: Optional[MaskPosition] = None,
    ) -> bool:
        """Use this method to add a new sticker to a set created by the bot.
           Returns True on success."""

        url = self._get_tg_api_method_url('addStickerToSet')
        values = frames.outer_args()
        del values['png_sticker']

        if isinstance(png_sticker, str):
            return self._make_request()
        else:
            # assert isinstance(png_sticker, io.BytesIO):
            files = {'png_sticker': png_sticker}

            r = requests.post(url, files=files, data=values)
            return handle_response(
                r.content.decode('utf-8'), AnnotationWrapper('bool'))

    def create_new_sticker_set(
            self,
            user_id: int,
            name: str,
            title: str,
            png_sticker: Union[BinaryIO, str],
            emojis: str,
            contains_masks: Optional[bool] = None,
            mask_position: Optional[MaskPosition] = None,
    ) -> bool:
        """Use this method to create new sticker set owned by a user. The bot
           will be able to edit the created sticker set. Returns True on
           success."""

        url = self._get_tg_api_method_url('createNewStickerSet')
        values = frames.outer_args()
        del values['png_sticker']

        if isinstance(png_sticker, str):
            return self._make_request()
        else:
            # assert isinstance(png_sticker, io.BytesIO):
            files = {'png_sticker': png_sticker}

            r = requests.post(url, files=files, data=values)
            return handle_response(
                r.content.decode('utf-8'), AnnotationWrapper('bool'))

    def upload_sticker_file(
            self,
            user_id: int,
            png_sticker: BinaryIO,
    ) -> File:
        """Use this method to upload a .png file with a sticker for later use in
           createNewStickerSet and addStickerToSet methods (can be used
           multiple times). Returns the uploaded File on success."""

        url = self._get_tg_api_method_url('uploadStickerFile')
        values = frames.outer_args()

        del values['png_sticker']
        files = {'png_sticker': png_sticker}

        r = requests.post(url, files=files, data=values)
        return handle_response(
            r.content.decode('utf-8'), AnnotationWrapper('File'))

    def set_webhook(
            self,
            url: str,
            certificate: Optional[BinaryIO] = None,
            max_connections: Optional[int] = None,
            allowed_updates: Optional[List[str]] = None,
    ) -> bool:
        """Use this method to specify a url and receive incoming updates via an
           outgoing webhook. Whenever there is an update for the bot, we will
           send an HTTPS POST request to the specified url, containing a JSON-
           serialized Update. In case of an unsuccessful request, we will give up
           after a reasonable amount of attempts. Returns True on success."""
        if certificate is not None:
            url = self._get_tg_api_method_url('setWebhook')
            values = frames.outer_args()

            del values['certificate']
            files = {'certificate': certificate}

            r = requests.post(url, files=files, data=values)
            return handle_response(
                r.content.decode('utf-8'), AnnotationWrapper('bool'))
        else:
            return self._make_request()

    def send_audio(
            self,
            chat_id: Union[int, str],
            audio: Union[BinaryIO, str],
            caption: Optional[str] = None,
            parse_mode: Optional[str] = None,
            duration: Optional[int] = None,
            performer: Optional[str] = None,
            title: Optional[str] = None,
            thumb: Optional[Union[BinaryIO, str]] = None,
            disable_notification: Optional[bool] = None,
            reply_to_message_id: Optional[int] = None,
            reply_markup: Optional[
                Union[InlineKeyboardMarkup, ReplyKeyboardMarkup,
                      ReplyKeyboardRemove, ForceReply]] = None,
    ) -> Message:
        """Use this method to send audio files, if you want Telegram clients to
           display them in the music player. Your audio must be in the .mp3
           format. On success, the sent Message is returned. Bots can currently
           send audio files of up to 50 MB in size, this limit may be changed
           in the future."""

        url = self._get_tg_api_method_url('sendAudio')
        values = frames.outer_args()

        if thumb is not None:
            if isinstance(audio, str) and isinstance(thumb, str):
                return self._make_request()

            elif isinstance(audio, io.BytesIO) and isinstance(thumb, str):
                del values['audio']
                files = {'audio': audio}

                r = requests.post(url, files=files, data=values)
                return handle_response(
                    r.content.decode('utf-8'), AnnotationWrapper('Message'))

            elif isinstance(audio, str) and isinstance(thumb, io.BytesIO):
                del values['thumb']
                files = {'thumb': thumb}

                r = requests.post(url, files=files, data=values)
                return handle_response(
                    r.content.decode('utf-8'), AnnotationWrapper('Message'))

            else:
                # assert isinstance(audio, io.BytesIO) and isinstance(thumb, io.BytesIO)
                del values['audio']
                del values['thumb']
                files = {'audio': audio, 'thumb': thumb}
                r = requests.post(url, files=files, data=values)
                return handle_response(
                    r.content.decode('utf-8'), AnnotationWrapper('Message'))
        else:

            if isinstance(audio, str):
                return self._make_request()

            else:
                # assert isinstance(audio, io.BytesIO)
                del values['audio']
                files = {'audio': audio}

                r = requests.post(url, files=files, data=values)
                return handle_response(
                    r.content.decode('utf-8'), AnnotationWrapper('Message'))

    def send_photo(
            self,
            chat_id: Union[int, str],
            photo: Union[BinaryIO, str],
            caption: Optional[str] = None,
            parse_mode: Optional[str] = None,
            disable_notification: Optional[bool] = None,
            reply_to_message_id: Optional[int] = None,
            reply_markup: Optional[
                Union[InlineKeyboardMarkup, ReplyKeyboardMarkup,
                      ReplyKeyboardRemove, ForceReply]] = None,
    ) -> Message:
        """Use this method to send photos. On success, the sent Message is
           returned."""

        url = self._get_tg_api_method_url('sendPhoto')
        values = frames.outer_args()
        del values['photo']

        if isinstance(photo, str):
            return self._make_request()
        else:
            # assert isinstance(photo, io.BytesIO):
            files = {'photo': photo}

            r = requests.post(url, files=files, data=values)
            return handle_response(
                r.content.decode('utf-8'), AnnotationWrapper('Message'))

    def answer_callback_query(
            self,
            callback_query_id: str,
            text: Optional[str] = None,
            show_alert: Optional[bool] = None,
            url: Optional[str] = None,
            cache_time: Optional[int] = None,
    ) -> bool:
        """Use this method to send answers to callback queries sent from inline
           keyboards. The answer will be displayed to the user as a
           notification at the top of the chat screen or as an alert. On success,
           True is returned."""

        return self._make_request()

    def answer_inline_query(
            self,
            inline_query_id: str,
            results: List[InlineQueryResult],
            cache_time: Optional[int] = None,
            is_personal: Optional[bool] = None,
            next_offset: Optional[str] = None,
            switch_pm_text: Optional[str] = None,
            switch_pm_parameter: Optional[str] = None,
    ) -> bool:
        """Use this method to send answers to an inline query. On success, True
           is returned.No more than 50 results per query are allowed."""

        return self._make_request()

    def answer_pre_checkout_query(
            self,
            pre_checkout_query_id: str,
            ok: bool,
            error_message: Optional[str] = None,
    ) -> bool:
        """Once the user has confirmed their payment and shipping details, the
           Bot API sends the final confirmation in the form     of an Update with
           the field pre_checkout_query. Use this method to respond to such
           pre-checkout queries. On success, True is returned. Note: The Bot API
           must receive an answer within 10 seconds after the pre-checkout
           query was sent."""

        return self._make_request()

    def answer_shipping_query(
            self,
            shipping_query_id: str,
            ok: bool,
            shipping_options: Optional[List[LabeledPrice]] = None,
            error_message: Optional[str] = None,
    ) -> bool:
        """If you sent an invoice requesting a shipping address and the
           parameter is_flexible was specified, the Bot API will send an Update
           with a shipping_query field to the bot. Use this method to reply to
           shipping queries. On success, True is returned."""

        return self._make_request()

    def delete_chat_photo(
            self,
            chat_id: Union[int, str],
    ) -> bool:
        """Use this method to delete a chat photo. Photos can't be changed for
           private chats. The bot must be an administrator in the chat for this
           to work and must have the appropriate admin rights. Returns True on
           success."""

        return self._make_request()

    def delete_chat_sticker_set(
            self,
            chat_id: Union[int, str],
    ) -> bool:
        """Use this method to delete a group sticker set from a supergroup. The
           bot must be an administrator in the chat for this to work and must
           have the appropriate admin rights. Use the field can_set_sticker_set
           optionally returned in getChat requests to check if the bot can use
           this method. Returns True on success."""

        return self._make_request()

    def delete_message(
            self,
            chat_id: Union[int, str],
            message_id: int,
    ) -> bool:
        """Use this method to delete a message, including service messages, with
           the following limitations:- A message can only be deleted if it was
           sent less than 48 hours ago.- Bots can delete outgoing messages in
           private chats, groups, and supergroups.- Bots granted
           can_post_messages permissions can delete outgoing messages in
           channels.- If the bot is an administrator of a group, it can delete any
           message there.- If the bot has can_delete_messages permission in a
           supergroup or a channel, it can delete any message there.Returns True on
           success."""

        return self._make_request()

    def delete_sticker_from_set(
            self,
            sticker: str,
    ) -> bool:
        """Use this method to delete a sticker from a set created by the bot.
           Returns True on success."""

        return self._make_request()

    def delete_webhook(self, ) -> bool:
        """Use this method to remove webhook integration if you decide to switch
           back to getUpdates. Returns True on success."""

        return self._make_request()

    def edit_message_caption(
            self,
            chat_id: Optional[Union[int, str]] = None,
            message_id: Optional[int] = None,
            inline_message_id: Optional[str] = None,
            caption: Optional[str] = None,
            parse_mode: Optional[str] = None,
            reply_markup: Optional[InlineKeyboardMarkup] = None,
    ) -> Union[Message, bool]:
        """Use this method to edit captions of messages sent by the bot or via
           the bot (for inline bots). On success, if edited message is sent by
           the bot, the edited Message is returned, otherwise True is returned."""

        return self._make_request()

    def edit_message_live_location(
            self,
            latitude: float,
            longitude: float,
            chat_id: Optional[Union[int, str]] = None,
            message_id: Optional[int] = None,
            inline_message_id: Optional[str] = None,
            reply_markup: Optional[InlineKeyboardMarkup] = None,
    ) -> Union[Message, bool]:
        """Use this method to edit live location messages sent by the bot or via
           the bot (for inline bots). A location can be edited until its
           live_period expires or editing is explicitly disabled by a call to
           stopMessageLiveLocation. On success, if the edited message was sent
           by the bot, the edited Message is returned, otherwise True is returned."""

        return self._make_request()

    def edit_message_media(
            self,
            media: InputMedia,
            chat_id: Optional[Union[int, str]] = None,
            message_id: Optional[int] = None,
            inline_message_id: Optional[str] = None,
            reply_markup: Optional[InlineKeyboardMarkup] = None,
    ) -> Union[Message, bool]:
        """Use this method to edit animation, audio, document, photo, or video
           messages. If a message is a part of a message album, then it can be
           edited only to a photo or a video. Otherwise, message type can be
           changed arbitrarily. When inline message is edited, new file can't
           be uploaded. Use previously uploaded file via its file_id or specify a
           URL. On success, if the edited message was sent by the bot, the edited
           Message is returned, otherwise True is returned."""

        return self._make_request()

    def edit_message_reply_markup(
            self,
            chat_id: Optional[Union[int, str]] = None,
            message_id: Optional[int] = None,
            inline_message_id: Optional[str] = None,
            reply_markup: Optional[InlineKeyboardMarkup] = None,
    ) -> Union[Message, bool]:
        """Use this method to edit only the reply markup of messages sent by the
           bot or via the bot (for inline bots). On success, if edited message
           is sent by the bot, the edited Message is returned, otherwise True
           is returned."""

        return self._make_request()

    def edit_message_text(
            self,
            text: str,
            chat_id: Optional[Union[int, str]] = None,
            message_id: Optional[int] = None,
            inline_message_id: Optional[str] = None,
            parse_mode: Optional[str] = None,
            disable_web_page_preview: Optional[bool] = None,
            reply_markup: Optional[InlineKeyboardMarkup] = None,
    ) -> Union[Message, bool]:
        """Use this method to edit text and game messages sent by the bot or via
           the bot (for inline bots). On success, if edited message is sent by the
           bot, the edited Message is returned, otherwise True is returned."""

        return self._make_request()

    def export_chat_invite_link(
            self,
            chat_id: Union[int, str],
    ) -> str:
        """Use this method to generate a new invite link for a chat; any
           previously generated link is revoked. The bot must be     an
           administrator in the chat for this to work and must have the appropriate
           admin rights. Returns the new invite link as String on success."""

        return self._make_request()

    def forward_message(
            self,
            chat_id: Union[int, str],
            from_chat_id: Union[int, str],
            message_id: int,
            disable_notification: Optional[bool] = None,
    ) -> Message:
        """Use this method to forward messages of any kind. On success, the sent
           Message is returned."""

        return self._make_request()

    def get_chat(
            self,
            chat_id: Union[int, str],
    ) -> Chat:
        """Use this method to get up to date information about the chat (current
           name of the user for one-on-one conversations, current username of a
           user, group or channel, etc.). Returns a Chat object on success."""

        return self._make_request()

    def get_chat_administrators(
            self,
            chat_id: Union[int, str],
    ) -> List[ChatMember]:
        """Use this method to get a list of administrators in a chat. On
           success, returns an Array of ChatMember objects that contains
           information about all chat administrators except other bots. If the chat
           is a group or a supergroup and no administrators were appointed,
           only the creator will be returned."""

        return self._make_request()

    def get_chat_member(
            self,
            chat_id: Union[int, str],
            user_id: int,
    ) -> ChatMember:
        """Use this method to get information about a member of a chat. Returns
           a ChatMember object on success."""

        return self._make_request()

    def get_chat_members_count(
            self,
            chat_id: Union[int, str],
    ) -> int:
        """Use this method to get the number of members in a chat. Returns Int
           on success."""

        return self._make_request()

    def get_file(
            self,
            file_id: str,
    ) -> File:
        """Use this method to get basic info about a file and prepare it for
           downloading. For the moment, bots can download files of up to 20MB
           in size. On success, a File object is returned. The file can then be
           downloaded via the link
           https://api.telegram.org/file/bot<token>/<file_path>, where <file_path>
           is taken from the response. It is guaranteed that the link will be valid
           for at least 1 hour. When the link expires, a new one can be
           requested by calling getFile again."""

        return self._make_request()

    def get_game_high_scores(
            self,
            user_id: int,
            chat_id: Optional[int] = None,
            message_id: Optional[int] = None,
            inline_message_id: Optional[str] = None,
    ) -> List[GameHighScore]:
        """Use this method to get data for high score tables. Will return the
           score of the specified user and several of his neighbors in a game.
           On success, returns an Array of GameHighScore objects."""

        return self._make_request()

    def get_me(self, ) -> User:
        """A simple method for testing your bot's auth token. Requires no
           parameters. Returns basic information about the bot in form of a
           User object."""

        return self._make_request()

    def get_sticker_set(
            self,
            name: str,
    ) -> StickerSet:
        """Use this method to get a sticker set. On success, a StickerSet object
           is returned."""

        return self._make_request()

    def get_updates(
            self,
            offset: Optional[int] = None,
            limit: Optional[int] = None,
            timeout: Optional[int] = None,
            allowed_updates: Optional[List[str]] = None,
    ) -> List[Update]:
        """Use this method to receive incoming updates using long polling.
           An Array of Update objects is returned."""

        return self._make_request()

    def get_user_profile_photos(
            self,
            user_id: int,
            offset: Optional[int] = None,
            limit: Optional[int] = None,
    ) -> UserProfilePhotos:
        """Use this method to get a list of profile pictures for a user. Returns
           a UserProfilePhotos object."""

        return self._make_request()

    def get_webhook_info(self, ) -> WebhookInfo:
        """Use this method to get current webhook status. Requires no
           parameters. On success, returns a WebhookInfo object. If the bot is
           using getUpdates, will return an object with the url field empty."""

        return self._make_request()

    def kick_chat_member(
            self,
            chat_id: Union[int, str],
            user_id: int,
            until_date: Optional[int] = None,
    ) -> bool:
        """Use this method to kick a user from a group, a supergroup or a
           channel. In the case of supergroups and channels, the user will not
           be able to return to the group on their own using invite links, etc.,
           unless unbanned first. The bot must be an administrator in the chat for
           this to work and must have the appropriate admin rights. Returns
           True on success."""

        return self._make_request()

    def leave_chat(
            self,
            chat_id: Union[int, str],
    ) -> bool:
        """Use this method for your bot to leave a group, supergroup or channel.
           Returns True on success."""

        return self._make_request()

    def pin_chat_message(
            self,
            chat_id: Union[int, str],
            message_id: int,
            disable_notification: Optional[bool] = None,
    ) -> bool:
        """Use this method to pin a message in a group, a supergroup, or a
           channel. The bot must be an administrator in the chat for this to work
           and must have the ‘can_pin_messages’ admin right in the supergroup or
           ‘can_edit_messages’ admin right in the channel. Returns True on success."""

        return self._make_request()

    def promote_chat_member(
            self,
            chat_id: Union[int, str],
            user_id: int,
            can_change_info: Optional[bool] = None,
            can_post_messages: Optional[bool] = None,
            can_edit_messages: Optional[bool] = None,
            can_delete_messages: Optional[bool] = None,
            can_invite_users: Optional[bool] = None,
            can_restrict_members: Optional[bool] = None,
            can_pin_messages: Optional[bool] = None,
            can_promote_members: Optional[bool] = None,
    ) -> bool:
        """Use this method to promote or demote a user in a supergroup or a
           channel. The bot must be an administrator in the chat for this to
           work and must have the appropriate admin rights. Pass False for all
           boolean parameters to demote a user. Returns True on success."""

        return self._make_request()

    def restrict_chat_member(
            self,
            chat_id: Union[int, str],
            user_id: int,
            until_date: Optional[int] = None,
            can_send_messages: Optional[bool] = None,
            can_send_media_messages: Optional[bool] = None,
            can_send_other_messages: Optional[bool] = None,
            can_add_web_page_previews: Optional[bool] = None,
    ) -> bool:
        """Use this method to restrict a user in a supergroup. The bot must be
           an administrator in the supergroup for this to work and must have
           the appropriate admin rights. Pass True for all boolean parameters to
           lift restrictions from a user. Returns True on success."""

        return self._make_request()

    def send_animation(
            self,
            chat_id: Union[int, str],
            animation: Union[BinaryIO, str],
            duration: Optional[int] = None,
            width: Optional[int] = None,
            height: Optional[int] = None,
            thumb: Optional[Union[BinaryIO, str]] = None,
            caption: Optional[str] = None,
            parse_mode: Optional[str] = None,
            disable_notification: Optional[bool] = None,
            reply_to_message_id: Optional[int] = None,
            reply_markup: Optional[
                Union[InlineKeyboardMarkup, ReplyKeyboardMarkup,
                      ReplyKeyboardRemove, ForceReply]] = None,
    ) -> Message:
        """Use this method to send animation files (GIF or H.264/MPEG-4 AVC
           video without sound). On success, the sent Message is returned. Bots can
           currently send animation files of up to 50 MB in size, this limit
           may be changed in the future."""

        url = self._get_tg_api_method_url('sendAnimation')
        values = frames.outer_args()

        if thumb is not None:
            if isinstance(animation, str) and isinstance(thumb, str):
                return self._make_request()

            elif isinstance(animation, io.BytesIO) and isinstance(thumb, str):
                del values['animation']
                files = {'animation': animation}

                r = requests.post(url, files=files, data=values)
                return handle_response(
                    r.content.decode('utf-8'), AnnotationWrapper('Message'))

            elif isinstance(animation, str) and isinstance(thumb, io.BytesIO):
                del values['thumb']
                files = {'thumb': thumb}

                r = requests.post(url, files=files, data=values)
                return handle_response(
                    r.content.decode('utf-8'), AnnotationWrapper('Message'))

            else:
                # assert isinstance(audio, io.BytesIO) and isinstance(thumb, io.BytesIO)
                del values['animation']
                del values['thumb']
                files = {'animation': animation, 'thumb': thumb}
                r = requests.post(url, files=files, data=values)
                return handle_response(
                    r.content.decode('utf-8'), AnnotationWrapper('Message'))
        else:

            if isinstance(animation, str):
                return self._make_request()

            else:
                # assert isinstance(animation, io.BytesIO)
                del values['animation']
                files = {'animation': animation}

                r = requests.post(url, files=files, data=values)
                return handle_response(
                    r.content.decode('utf-8'), AnnotationWrapper('Message'))

    def send_chat_action(
            self,
            chat_id: Union[int, str],
            action: str,
    ) -> bool:
        """Use this method when you need to tell the user that something is
           happening on the bot's side. The status is set for 5 seconds or less
           (when a message arrives from your bot, Telegram clients clear its typing
           status). Returns True on success."""

        return self._make_request()

    def send_contact(
            self,
            chat_id: Union[int, str],
            phone_number: str,
            first_name: str,
            last_name: Optional[str] = None,
            vcard: Optional[str] = None,
            disable_notification: Optional[bool] = None,
            reply_to_message_id: Optional[int] = None,
            reply_markup: Optional[
                Union[InlineKeyboardMarkup, ReplyKeyboardMarkup,
                      ReplyKeyboardRemove, ForceReply]] = None,
    ) -> Message:
        """Use this method to send phone contacts. On success, the sent Message
           is returned."""

        return self._make_request()

    def send_document(
            self,
            chat_id: Union[int, str],
            document: Union[BinaryIO, str],
            thumb: Optional[Union[BinaryIO, str]] = None,
            caption: Optional[str] = None,
            parse_mode: Optional[str] = None,
            disable_notification: Optional[bool] = None,
            reply_to_message_id: Optional[int] = None,
            reply_markup: Optional[
                Union[InlineKeyboardMarkup, ReplyKeyboardMarkup,
                      ReplyKeyboardRemove, ForceReply]] = None,
    ) -> Message:
        """Use this method to send general files. On success, the sent Message
           is returned. Bots can currently send files of any type of up to 50
           MB in size, this limit may be changed in the future."""

        url = self._get_tg_api_method_url('sendDocument')
        values = frames.outer_args()

        if thumb is not None:
            if isinstance(document, str) and isinstance(thumb, str):
                return self._make_request()

            elif isinstance(document, io.BytesIO) and isinstance(thumb, str):
                del values['document']
                files = {'document': document}

                r = requests.post(url, files=files, data=values)
                return handle_response(
                    r.content.decode('utf-8'), AnnotationWrapper('Message'))

            elif isinstance(document, str) and isinstance(thumb, io.BytesIO):
                del values['thumb']
                files = {'thumb': thumb}

                r = requests.post(url, files=files, data=values)
                return handle_response(
                    r.content.decode('utf-8'), AnnotationWrapper('Message'))

            else:
                # assert isinstance(audio, io.BytesIO) and isinstance(thumb, io.BytesIO)
                del values['document']
                del values['thumb']
                files = {'document': document, 'thumb': thumb}
                r = requests.post(url, files=files, data=values)
                return handle_response(
                    r.content.decode('utf-8'), AnnotationWrapper('Message'))
        else:

            if isinstance(document, str):
                return self._make_request()

            else:
                # assert isinstance(document, io.BytesIO)
                del values['document']
                files = {'document': document}

                r = requests.post(url, files=files, data=values)
                return handle_response(
                    r.content.decode('utf-8'), AnnotationWrapper('Message'))

    def send_game(
            self,
            chat_id: int,
            game_short_name: str,
            disable_notification: Optional[bool] = None,
            reply_to_message_id: Optional[int] = None,
            reply_markup: Optional[InlineKeyboardMarkup] = None,
    ) -> Message:
        """Use this method to send a game. On success, the sent Message is
           returned."""

        return self._make_request()

    def send_invoice(
            self,
            chat_id: int,
            title: str,
            description: str,
            payload: str,
            provider_token: str,
            start_parameter: str,
            currency: str,
            prices: List[LabeledPrice],
            provider_data: Optional[str] = None,
            photo_url: Optional[str] = None,
            photo_size: Optional[int] = None,
            photo_width: Optional[int] = None,
            photo_height: Optional[int] = None,
            need_name: Optional[bool] = None,
            need_phone_number: Optional[bool] = None,
            need_email: Optional[bool] = None,
            need_shipping_address: Optional[bool] = None,
            send_phone_number_to_provider: Optional[bool] = None,
            send_email_to_provider: Optional[bool] = None,
            is_flexible: Optional[bool] = None,
            disable_notification: Optional[bool] = None,
            reply_to_message_id: Optional[int] = None,
            reply_markup: Optional[InlineKeyboardMarkup] = None,
    ) -> Message:
        """Use this method to send invoices. On success, the sent Message is
           returned."""

        return self._make_request()

    def send_location(
            self,
            chat_id: Union[int, str],
            latitude: float,
            longitude: float,
            live_period: Optional[int] = None,
            disable_notification: Optional[bool] = None,
            reply_to_message_id: Optional[int] = None,
            reply_markup: Optional[
                Union[InlineKeyboardMarkup, ReplyKeyboardMarkup,
                      ReplyKeyboardRemove, ForceReply]] = None,
    ) -> Message:
        """Use this method to send point on the map. On success, the sent
           Message is returned."""

        return self._make_request()

    def send_media_group(
            self,
            chat_id: Union[int, str],
            media: List[Union[InputMediaPhoto, InputMediaVideo]],
            disable_notification: Optional[bool] = None,
            reply_to_message_id: Optional[int] = None,
    ) -> Message:
        """Use this method to send a group of photos or videos as an album. On
           success, an array of the sent Messages is returned."""

        return self._make_request()

    def send_message(
            self,
            chat_id: Union[int, str],
            text: str,
            parse_mode: Optional[str] = None,
            disable_web_page_preview: Optional[bool] = None,
            disable_notification: Optional[bool] = None,
            reply_to_message_id: Optional[int] = None,
            reply_markup: Optional[
                Union[InlineKeyboardMarkup, ReplyKeyboardMarkup,
                      ReplyKeyboardRemove, ForceReply]] = None,
    ) -> Message:
        """Use this method to send text messages. On success, the sent Message
           is returned."""

        return self._make_request()

    def send_poll(
            self,
            chat_id: Union[int, str],
            question: str,
            options: List[str],
            disable_notification: Optional[bool] = None,
            reply_to_message_id: Optional[int] = None,
            reply_markup: Optional[
                Union[InlineKeyboardMarkup, ReplyKeyboardMarkup,
                      ReplyKeyboardRemove, ForceReply]] = None,
    ) -> Message:
        """Use this method to send a native poll. A native poll can't be sent to
           a private chat. On success, the sent Message is returned."""

        return self._make_request()

    def send_venue(
            self,
            chat_id: Union[int, str],
            latitude: float,
            longitude: float,
            title: str,
            address: str,
            foursquare_id: Optional[str] = None,
            foursquare_type: Optional[str] = None,
            disable_notification: Optional[bool] = None,
            reply_to_message_id: Optional[int] = None,
            reply_markup: Optional[
                Union[InlineKeyboardMarkup, ReplyKeyboardMarkup,
                      ReplyKeyboardRemove, ForceReply]] = None,
    ) -> Message:
        """Use this method to send information about a venue. On success, the
           sent Message is returned."""

        return self._make_request()

    def send_video(
            self,
            chat_id: Union[int, str],
            video: Union[BinaryIO, str],
            duration: Optional[int] = None,
            width: Optional[int] = None,
            height: Optional[int] = None,
            thumb: Optional[Union[BinaryIO, str]] = None,
            caption: Optional[str] = None,
            parse_mode: Optional[str] = None,
            supports_streaming: Optional[bool] = None,
            disable_notification: Optional[bool] = None,
            reply_to_message_id: Optional[int] = None,
            reply_markup: Optional[
                Union[InlineKeyboardMarkup, ReplyKeyboardMarkup,
                      ReplyKeyboardRemove, ForceReply]] = None,
    ) -> Message:
        """Use this method to send video files, Telegram clients support mp4
           videos (other formats may be sent as Document). On success, the sent
           Message is returned. Bots can currently send video files of up to 50
           MB in size, this limit may be changed in the future."""

        url = self._get_tg_api_method_url('sendVideo')
        values = frames.outer_args()

        if thumb is not None:
            if isinstance(video, str) and isinstance(thumb, str):
                return self._make_request()

            elif isinstance(video, io.BytesIO) and isinstance(thumb, str):
                del values['video']
                files = {'video': video}

                r = requests.post(url, files=files, data=values)
                return handle_response(
                    r.content.decode('utf-8'), AnnotationWrapper('Message'))

            elif isinstance(video, str) and isinstance(thumb, io.BytesIO):
                del values['thumb']
                files = {'thumb': thumb}

                r = requests.post(url, files=files, data=values)
                return handle_response(
                    r.content.decode('utf-8'), AnnotationWrapper('Message'))

            else:
                # assert isinstance(audio, io.BytesIO) and isinstance(thumb, io.BytesIO)
                del values['video']
                del values['thumb']
                files = {'video': video, 'thumb': thumb}
                r = requests.post(url, files=files, data=values)
                return handle_response(
                    r.content.decode('utf-8'), AnnotationWrapper('Message'))
        else:

            if isinstance(video, str):
                return self._make_request()

            else:
                # assert isinstance(document, io.BytesIO)
                del values['video']
                files = {'video': video}

                r = requests.post(url, files=files, data=values)
                return handle_response(
                    r.content.decode('utf-8'), AnnotationWrapper('Message'))

    def send_video_note(
            self,
            chat_id: Union[int, str],
            video_note: Union[BinaryIO, str],
            duration: Optional[int] = None,
            length: Optional[int] = None,
            thumb: Optional[Union[BinaryIO, str]] = None,
            disable_notification: Optional[bool] = None,
            reply_to_message_id: Optional[int] = None,
            reply_markup: Optional[
                Union[InlineKeyboardMarkup, ReplyKeyboardMarkup,
                      ReplyKeyboardRemove, ForceReply]] = None,
    ) -> Message:
        """As of v.4.0, Telegram clients support rounded square mp4 videos
           of up to 1 minute long. Use this method to send video messages.
           On success, the sent Message is returned."""

        url = self._get_tg_api_method_url('sendVideoNote')
        values = frames.outer_args()

        if thumb is not None:
            if isinstance(video_note, str) and isinstance(thumb, str):
                return self._make_request()

            elif isinstance(video_note, io.BytesIO) and isinstance(thumb, str):
                del values['video_note']
                files = {'video_note': video_note}

                r = requests.post(url, files=files, data=values)
                return handle_response(
                    r.content.decode('utf-8'), AnnotationWrapper('Message'))

            elif isinstance(video_note, str) and isinstance(thumb, io.BytesIO):
                del values['thumb']
                files = {'thumb': thumb}

                r = requests.post(url, files=files, data=values)
                return handle_response(
                    r.content.decode('utf-8'), AnnotationWrapper('Message'))

            else:
                # assert isinstance(audio, io.BytesIO) and isinstance(thumb, io.BytesIO)
                del values['video_note']
                del values['thumb']
                files = {'video_note': video_note, 'thumb': thumb}
                r = requests.post(url, files=files, data=values)
                return handle_response(
                    r.content.decode('utf-8'), AnnotationWrapper('Message'))
        else:

            if isinstance(video_note, str):
                return self._make_request()

            else:
                # assert isinstance(document, io.BytesIO)
                del values['video_note']
                files = {'video_note': video_note}

                r = requests.post(url, files=files, data=values)
                return handle_response(
                    r.content.decode('utf-8'), AnnotationWrapper('Message'))

    def send_voice(
            self,
            chat_id: Union[int, str],
            voice: Union[BinaryIO, str],
            caption: Optional[str] = None,
            parse_mode: Optional[str] = None,
            duration: Optional[int] = None,
            disable_notification: Optional[bool] = None,
            reply_to_message_id: Optional[int] = None,
            reply_markup: Optional[
                Union[InlineKeyboardMarkup, ReplyKeyboardMarkup,
                      ReplyKeyboardRemove, ForceReply]] = None,
    ) -> Message:
        """Use this method to send audio files, if you want Telegram clients to
           display the file as a playable voice message. For this to work, your
           audio must be in an .ogg file encoded with OPUS (other formats may be
           sent as Audio or Document). On success, the sent Message is
           returned. Bots can currently send voice messages of up to 50 MB in size,
           this limit may be changed in the future."""

        url = self._get_tg_api_method_url('sendVoice')
        values = frames.outer_args()
        del values['voice']

        if isinstance(voice, str):
            return self._make_request()
        else:
            # assert isinstance(photo, io.BytesIO):
            files = {'voice': voice}

            r = requests.post(url, files=files, data=values)
            return handle_response(
                r.content.decode('utf-8'), AnnotationWrapper('Message'))

    def set_chat_description(
            self,
            chat_id: Union[int, str],
            description: Optional[str] = None,
    ) -> bool:
        """Use this method to change the description of a supergroup or a
           channel. The bot must be an administrator in the chat for this to
           work and must have the appropriate admin rights. Returns True on
           success."""

        return self._make_request()

    def set_chat_sticker_set(
            self,
            chat_id: Union[int, str],
            sticker_set_name: str,
    ) -> bool:
        """Use this method to set a new group sticker set for a supergroup. The
           bot must be an administrator in the chat for this to work and must
           have the appropriate admin rights. Use the field can_set_sticker_set
           optionally returned in getChat requests to check if the bot can use
           this method. Returns True on success."""

        return self._make_request()

    def set_chat_title(
            self,
            chat_id: Union[int, str],
            title: str,
    ) -> bool:
        """Use this method to change the title of a chat. Titles can't be
           changed for private chats. The bot must be an administrator in the
           chat for this to work and must have the appropriate admin rights.
           Returns True on success."""

        return self._make_request()

    def set_game_score(
            self,
            user_id: int,
            score: int,
            force: Optional[bool] = None,
            disable_edit_message: Optional[bool] = None,
            chat_id: Optional[int] = None,
            message_id: Optional[int] = None,
            inline_message_id: Optional[str] = None,
    ) -> Union[Message, bool]:
        """Use this method to set the score of the specified user in a game. On
           success, if the message was sent by the bot, returns the edited
           Message, otherwise returns True. Returns an error, if the new score
           is not greater than the user's current score in the chat and force is
           False."""

        return self._make_request()

    def set_passport_data_errors(
            self,
            user_id: int,
            errors: List[PassportElementError],
    ) -> bool:
        """Informs a user that some of the Telegram Passport elements they
           provided contains errors. The user will not be able to re-submit
           their Passport to you until the errors are fixed (the contents of the
           field for which you returned the error must change). Returns True on
           success."""

        return self._make_request()

    def set_sticker_position_in_set(
            self,
            sticker: str,
            position: int,
    ) -> bool:
        """Use this method to move a sticker in a set created by the bot to a
           specific position . Returns True on success."""

        return self._make_request()

    def stop_message_live_location(
            self,
            chat_id: Optional[Union[int, str]] = None,
            message_id: Optional[int] = None,
            inline_message_id: Optional[str] = None,
            reply_markup: Optional[InlineKeyboardMarkup] = None,
    ) -> Union[Message, bool]:
        """Use this method to stop updating a live location message sent by the
           bot or via the bot (for inline bots) before live_period expires. On
           success, if the message was sent by the bot, the sent Message is
           returned, otherwise True is returned."""

        return self._make_request()

    def stop_poll(
            self,
            chat_id: Union[int, str],
            message_id: int,
            reply_markup: Optional[InlineKeyboardMarkup] = None,
    ) -> Poll:
        """Use this method to stop a poll which was sent by the bot. On success,
           the stopped Poll with the final results is returned."""

        return self._make_request()

    def unban_chat_member(
            self,
            chat_id: Union[int, str],
            user_id: int,
    ) -> bool:
        """Use this method to unban a previously kicked user in a supergroup or
           channel. The user will not return to the group or channel
           automatically, but will be able to join via link, etc. The bot must be
           an administrator for this to work. Returns True on success."""

        return self._make_request()

    def unpin_chat_message(
            self,
            chat_id: Union[int, str],
    ) -> bool:
        """Use this method to unpin a message in a group, a supergroup, or a
           channel. The bot must be an administrator in the chat for this to work
           and must have the ‘can_pin_messages’ admin right in the supergroup or
           ‘can_edit_messages’ admin right in the channel. Returns True on success."""

        return self._make_request()


if __name__ == '__main__':
    bot_api = Api(token="432916128:AAG-rZvzYDzZCUr2psOlBrYeJa0_is7LR9o")
    # with open("/home/dzmitry/Downloads/johnnysinsbrazzers_1.png",
    #           'rb') as photo:
    #     bot_api.send_poll(
    #         chat_id=-1001373939377,
    #         question="какие телочки больше всего тебе нравятся?",
    #         options=[
    #             "молоденькие телочки", "больше нравятся зрелые красотки",
    #             "горячие бабульки"
    #         ],
    #         disable_notification=True)

    with open('/home/dzmitry/Downloads/3.mp3', 'rb') as audio:
        with open("/home/dzmitry/Pictures/download.jpeg", 'rb') as thumb:
            result = bot_api.send_audio(
                chat_id=-1001373939377,
                audio=audio,
                caption="hello world",
                thumb=thumb,
            )
            print(result)

    # btn1 = InlineKeyboardButton(text='add', url='http://lenta.ru')
    # btn2 = InlineKeyboardButton(text='sub', url='http://topwar.ru')
    # btn3 = InlineKeyboardButton(text='mul', url='http://waralbum.ru')
    # btn4 = InlineKeyboardButton(text='div', url='http://antio.ru')
    # inline_kb = InlineKeyboardMarkup([[btn1, btn2], [btn3, btn4]])
    # res = bot_api.send_message(
    #     -1001373939377, "werfew", reply_markup=inline_kb)
    # print(res)
    # bot_api.send_message()
