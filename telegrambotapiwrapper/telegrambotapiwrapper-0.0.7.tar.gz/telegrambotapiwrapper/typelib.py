# -*- coding: utf-8 -*-
# Copyright (c) 2019 Dzmitry Maliuzhenets; MIT License
"""The module contains data types Telegram Bot Api."""

from __future__ import annotations

from dataclasses import dataclass
from pprint import pprint
from typing import Optional, List, Union

from telegrambotapiwrapper.base import Base


@dataclass
class LoginUrl(Base):
    """This object represents a parameter of the inline keyboard button used to
    automatically authorize a user. Serves as a great replacement for the
    Telegram Login Widget when the user is coming from Telegram. All the user
    needs to do is tap/click a button and confirm that they want to log in."""

    url: str
    forward_text: Optional[str] = None
    bot_username: Optional[str] = None
    request_write_access: Optional[bool] = None


@dataclass
class User(Base):
    """This object represents a Telegram user or bot."""

    id: int
    is_bot: bool
    first_name: str
    last_name: Optional[str] = None
    username: Optional[str] = None
    language_code: Optional[str] = None


@dataclass
class Chat(Base):
    """This object represents a chat."""

    id: int
    type: str
    title: Optional[str] = None
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    all_members_are_administrators: Optional[bool] = None
    photo: Optional[ChatPhoto] = None
    description: Optional[str] = None
    invite_link: Optional[str] = None
    pinned_message: Optional[Message] = None
    sticker_set_name: Optional[str] = None
    can_set_sticker_set: Optional[bool] = None


@dataclass
class Message(Base):
    """This object represents a message."""

    message_id: int
    date: int
    chat: Chat
    from_: Optional[User] = None
    forward_from: Optional[User] = None
    forward_from_chat: Optional[Chat] = None
    forward_from_message_id: Optional[int] = None
    forward_signature: Optional[str] = None
    forward_sender_name: Optional[str] = None
    forward_date: Optional[int] = None
    reply_to_message: Optional[Message] = None
    edit_date: Optional[int] = None
    media_group_id: Optional[str] = None
    author_signature: Optional[str] = None
    text: Optional[str] = None
    entities: Optional[List[MessageEntity]] = None
    caption_entities: Optional[List[MessageEntity]] = None
    audio: Optional[Audio] = None
    document: Optional[Document] = None
    animation: Optional[Animation] = None
    game: Optional[Game] = None
    photo: Optional[List[PhotoSize]] = None
    sticker: Optional[Sticker] = None
    video: Optional[Video] = None
    voice: Optional[Voice] = None
    video_note: Optional[VideoNote] = None
    caption: Optional[str] = None
    contact: Optional[Contact] = None
    location: Optional[Location] = None
    venue: Optional[Venue] = None
    poll: Optional[Poll] = None
    new_chat_members: Optional[List[User]] = None
    left_chat_member: Optional[User] = None
    new_chat_title: Optional[str] = None
    new_chat_photo: Optional[List[PhotoSize]] = None
    delete_chat_photo: Optional[bool] = None
    group_chat_created: Optional[bool] = None
    supergroup_chat_created: Optional[bool] = None
    channel_chat_created: Optional[bool] = None
    migrate_to_chat_id: Optional[int] = None
    migrate_from_chat_id: Optional[int] = None
    pinned_message: Optional[Message] = None
    invoice: Optional[Invoice] = None
    successful_payment: Optional[SuccessfulPayment] = None
    connected_website: Optional[str] = None
    passport_data: Optional[PassportData] = None
    reply_markup: Optional[InlineKeyboardMarkup] = None


@dataclass
class MessageEntity(Base):
    """This object represents one special entity in a text message. For
       example, hashtags, usernames, URLs, etc."""

    type: str
    offset: int
    length: int
    url: Optional[str] = None
    user: Optional[User] = None


@dataclass
class PhotoSize(Base):
    """This object represents one size of a photo or a file / sticker
       thumbnail."""

    file_id: str
    width: int
    height: int
    file_size: Optional[int] = None


@dataclass
class Audio(Base):
    """This object represents an audio file to be treated as music by the
       Telegram clients."""

    file_id: str
    duration: int
    performer: Optional[str] = None
    title: Optional[str] = None
    mime_type: Optional[str] = None
    file_size: Optional[int] = None
    thumb: Optional[PhotoSize] = None


@dataclass
class Document(Base):
    """This object represents a general file (as opposed to photos, voice
       messages and audio files)."""

    file_id: str
    thumb: Optional[PhotoSize] = None
    file_name: Optional[str] = None
    mime_type: Optional[str] = None
    file_size: Optional[int] = None


@dataclass
class Video(Base):
    """This object represents a video file."""

    file_id: str
    width: int
    height: int
    duration: int
    thumb: Optional[PhotoSize] = None
    mime_type: Optional[str] = None
    file_size: Optional[int] = None


@dataclass
class Animation(Base):
    """This object represents an animation file (GIF or H.264/MPEG-4 AVC
       video without sound)."""

    file_id: str
    width: int
    height: int
    duration: int
    thumb: Optional[PhotoSize] = None
    file_name: Optional[str] = None
    mime_type: Optional[str] = None
    file_size: Optional[int] = None


@dataclass
class Voice(Base):
    """This object represents a voice note."""

    file_id: str
    duration: int
    mime_type: Optional[str] = None
    file_size: Optional[int] = None


@dataclass
class VideoNote(Base):
    """This object represents a video message     (available in Telegram
       This object represents a video message     (available in Telegram apps
       as of v.4.0)."""

    file_id: str
    length: int
    duration: int
    thumb: Optional[PhotoSize] = None
    file_size: Optional[int] = None


@dataclass
class Contact(Base):
    """This object represents a phone contact."""

    phone_number: str
    first_name: str
    last_name: Optional[str] = None
    user_id: Optional[int] = None
    vcard: Optional[str] = None


@dataclass
class Location(Base):
    """This object represents a point on the map."""

    longitude: float
    latitude: float


@dataclass
class Venue(Base):
    """This object represents a venue."""

    location: Location
    title: str
    address: str
    foursquare_id: Optional[str] = None
    foursquare_type: Optional[str] = None


@dataclass
class PollOption(Base):
    """This object contains information about one answer option in a poll."""

    text: str
    voter_count: int


@dataclass
class Poll(Base):
    """This object contains information about a poll."""

    id: str
    question: str
    options: List[PollOption]
    is_closed: bool


@dataclass
class UserProfilePhotos(Base):
    """This object represent a user's profile pictures."""

    total_count: int
    photos: List[List[PhotoSize]]


@dataclass
class File(Base):
    """This object represents a file ready to be downloaded. The file can be
       downloaded via the link
       https://api.telegram.org/file/bot<token>/<file_path>.     It is
       guaranteed that the link will be valid for at least 1 hour. When the
       link expires, a new one can be requested     by calling getFile."""

    file_id: str
    file_size: Optional[int] = None
    file_path: Optional[str] = None


@dataclass
class ReplyKeyboardMarkup(Base):
    """This object represents a custom keyboard with reply options     (see
       This object represents a custom keyboard with reply options     (see
       Introduction to bots for details and examples)."""

    keyboard: List[List[KeyboardButton]]
    resize_keyboard: Optional[bool] = None
    one_time_keyboard: Optional[bool] = None
    selective: Optional[bool] = None


@dataclass
class KeyboardButton(Base):
    """This object represents one button of the reply keyboard. For simple
       text buttons String can be used instead     of this object to specify
       text of the button. Optional fields are mutually exclusive."""

    text: str
    request_contact: Optional[bool] = None
    request_location: Optional[bool] = None


@dataclass
class ReplyKeyboardRemove(Base):
    """Upon receiving a message with this object, Telegram clients will
       remove the current custom keyboard and display the     default letter-
       keyboard. By default, custom keyboards are displayed until a new
       keyboard is sent by a bot. An     exception is made for one-time
       keyboards that are hidden immediately after the user presses a button
       (see ReplyKeyboardMarkup)."""

    remove_keyboard: bool = True
    selective: Optional[bool] = None


@dataclass
class InlineKeyboardMarkup(Base):
    """This object represents an inline     keyboard that appears right next
       This object represents an inline     keyboard that appears right next to
       the message it belongs to."""

    inline_keyboard: List[List[InlineKeyboardButton]]


@dataclass
class InlineKeyboardButton(Base):
    """This object represents one button of an inline keyboard. You must use
       exactly one of the optional     fields."""

    text: str
    url: Optional[str] = None
    callback_data: Optional[str] = None
    switch_inline_query: Optional[str] = None
    switch_inline_query_current_chat: Optional[str] = None
    callback_game: Optional[CallbackGame] = None
    pay: Optional[bool] = None
    login_url: Optional[LoginUrl] = None


@dataclass
class CallbackQuery(Base):
    """This object represents an incoming callback query from a callback
       button in an inline keyboard. If the button that originated the
       query was attached to a message sent by the bot, the field message will
       be present. If the button was     attached to a message sent via the bot
       (in inline mode), the field     inline_message_id will be present.
       Exactly one of the fields data or game_short_name will     be present."""

    id: str
    from_: User
    chat_instance: str
    message: Optional[Message] = None
    inline_message_id: Optional[str] = None
    data: Optional[str] = None
    game_short_name: Optional[str] = None


@dataclass
class ForceReply(Base):
    """Upon receiving a message with this object, Telegram clients will
       display a reply interface to the user (act as if the     user has
       selected the bot‘s message and tapped ’Reply'). This can be extremely
       useful if you want to create     user-friendly step-by-step interfaces
       without having to sacrifice privacy mode."""

    force_reply: bool = True
    selective: Optional[bool] = None


@dataclass
class ChatPhoto(Base):
    """This object represents a chat photo."""

    small_file_id: str
    big_file_id: str


@dataclass
class ChatMember(Base):
    """This object contains information about one member of a chat."""

    user: User
    status: str
    until_date: Optional[int] = None
    can_be_edited: Optional[bool] = None
    can_change_info: Optional[bool] = None
    can_post_messages: Optional[bool] = None
    can_edit_messages: Optional[bool] = None
    can_delete_messages: Optional[bool] = None
    can_invite_users: Optional[bool] = None
    can_restrict_members: Optional[bool] = None
    can_pin_messages: Optional[bool] = None
    can_promote_members: Optional[bool] = None
    is_member: Optional[bool] = None
    can_send_messages: Optional[bool] = None
    can_send_media_messages: Optional[bool] = None
    can_send_other_messages: Optional[bool] = None
    can_add_web_page_previews: Optional[bool] = None


@dataclass
class ResponseParameters(Base):
    """Contains information about why a request was unsuccessful."""

    migrate_to_chat_id: Optional[int] = None
    retry_after: Optional[int] = None


@dataclass
class InputMediaPhoto(Base):
    """Represents a photo to be sent."""

    type: str
    media: str
    caption: Optional[str] = None
    parse_mode: Optional[str] = None


@dataclass
class InputMediaVideo(Base):
    """Represents a video to be sent."""

    type: str
    media: str
    thumb: Optional[Union[InputFile, str]] = None
    caption: Optional[str] = None
    parse_mode: Optional[str] = None
    width: Optional[int] = None
    height: Optional[int] = None
    duration: Optional[int] = None
    supports_streaming: Optional[bool] = None


@dataclass
class InputMediaAnimation(Base):
    """Represents an animation file (GIF or H.264/MPEG-4 AVC video without
       sound) to be sent."""

    type: str
    media: str
    thumb: Optional[Union[InputFile, str]] = None
    caption: Optional[str] = None
    parse_mode: Optional[str] = None
    width: Optional[int] = None
    height: Optional[int] = None
    duration: Optional[int] = None


@dataclass
class InputMediaAudio(Base):
    """Represents an audio file to be treated as music to be sent."""

    type: str
    media: str
    thumb: Optional[Union[InputFile, str]] = None
    caption: Optional[str] = None
    parse_mode: Optional[str] = None
    duration: Optional[int] = None
    performer: Optional[str] = None
    title: Optional[str] = None


@dataclass
class InputMediaDocument(Base):
    """Represents a general file to be sent."""

    type: str
    media: str
    thumb: Optional[Union[InputFile, str]] = None
    caption: Optional[str] = None
    parse_mode: Optional[str] = None


@dataclass
class InputFile(Base):
    """This object represents the contents of a file to be uploaded. Must be
       posted using multipart/form-data in the usual     way that files are
       uploaded via the browser."""


@dataclass
class Game(Base):
    """This object represents a game. Use BotFather to create and edit
       games, their short names will act as unique     identifiers."""

    title: str
    description: str
    photo: List[PhotoSize]
    text: Optional[str] = None
    text_entities: Optional[List[MessageEntity]] = None
    animation: Optional[Animation] = None


@dataclass
class CallbackGame(Base):
    """A placeholder, currently holds no information. Use BotFather to set
       up your game."""


@dataclass
class GameHighScore(Base):
    """This object represents one row of the high scores table for a game."""

    position: int
    user: User
    score: int


@dataclass
class Update(Base):
    """This object represents an incoming update.At most one of the optional
       parameters can be present in any given update."""

    update_id: int
    message: Optional[Message] = None
    edited_message: Optional[Message] = None
    channel_post: Optional[Message] = None
    edited_channel_post: Optional[Message] = None
    inline_query: Optional[InlineQuery] = None
    chosen_inline_result: Optional[ChosenInlineResult] = None
    callback_query: Optional[CallbackQuery] = None
    shipping_query: Optional[ShippingQuery] = None
    pre_checkout_query: Optional[PreCheckoutQuery] = None
    poll: Optional[Poll] = None


@dataclass
class WebhookInfo(Base):
    """Contains information about the current status of a webhook."""

    url: str
    has_custom_certificate: bool
    pending_update_count: int
    last_error_date: Optional[int] = None
    last_error_message: Optional[str] = None
    max_connections: Optional[int] = None
    allowed_updates: Optional[List[str]] = None


@dataclass
class InlineQuery(Base):
    """This object represents an incoming inline query. When the user sends
       an empty query, your bot could return some     default or trending
       results."""

    id: str
    from_: User
    query: str
    offset: str
    location: Optional[Location] = None


@dataclass
class InlineQueryResultArticle(Base):
    """Represents a link to an article or web page."""

    type: str
    id: str
    title: str
    input_message_content: InputMessageContent
    reply_markup: Optional[InlineKeyboardMarkup] = None
    url: Optional[str] = None
    hide_url: Optional[bool] = None
    description: Optional[str] = None
    thumb_url: Optional[str] = None
    thumb_width: Optional[int] = None
    thumb_height: Optional[int] = None


@dataclass
class InlineQueryResultPhoto(Base):
    """Represents a link to a photo. By default, this photo will be sent by
       the user with optional caption. Alternatively,     you can use
       input_message_content to send a message with the specified content
       instead of the photo."""

    type: str
    id: str
    photo_url: str
    thumb_url: str
    photo_width: Optional[int] = None
    photo_height: Optional[int] = None
    title: Optional[str] = None
    description: Optional[str] = None
    caption: Optional[str] = None
    parse_mode: Optional[str] = None
    reply_markup: Optional[InlineKeyboardMarkup] = None
    input_message_content: Optional[InputMessageContent] = None


@dataclass
class InlineQueryResultGif(Base):
    """Represents a link to an animated GIF file. By default, this animated
       GIF file will be sent by the user with optional     caption.
       Alternatively, you can use input_message_content to send a message with
       the specified content     instead of the animation."""

    type: str
    id: str
    gif_url: str
    thumb_url: str
    gif_width: Optional[int] = None
    gif_height: Optional[int] = None
    gif_duration: Optional[int] = None
    title: Optional[str] = None
    caption: Optional[str] = None
    parse_mode: Optional[str] = None
    reply_markup: Optional[InlineKeyboardMarkup] = None
    input_message_content: Optional[InputMessageContent] = None


@dataclass
class InlineQueryResultMpeg4Gif(Base):
    """Represents a link to a video animation (H.264/MPEG-4 AVC video
       without sound). By default, this animated MPEG-4 file     will be sent
       by the user with optional caption. Alternatively, you can use
       input_message_content to send a     message with the specified content
       instead of the animation."""

    type: str
    id: str
    mpeg4_url: str
    thumb_url: str
    mpeg4_width: Optional[int] = None
    mpeg4_height: Optional[int] = None
    mpeg4_duration: Optional[int] = None
    title: Optional[str] = None
    caption: Optional[str] = None
    parse_mode: Optional[str] = None
    reply_markup: Optional[InlineKeyboardMarkup] = None
    input_message_content: Optional[InputMessageContent] = None


@dataclass
class InlineQueryResultVideo(Base):
    """Represents a link to a page containing an embedded video player or a
       video file. By default, this video file will be     sent by the user
       with an optional caption. Alternatively, you can use
       input_message_content to send a     message with the specified content
       instead of the video."""

    type: str
    id: str
    video_url: str
    mime_type: str
    thumb_url: str
    title: str
    caption: Optional[str] = None
    parse_mode: Optional[str] = None
    video_width: Optional[int] = None
    video_height: Optional[int] = None
    video_duration: Optional[int] = None
    description: Optional[str] = None
    reply_markup: Optional[InlineKeyboardMarkup] = None
    input_message_content: Optional[InputMessageContent] = None


@dataclass
class InlineQueryResultAudio(Base):
    """Represents a link to an mp3 audio file. By default, this audio file
       will be sent by the user. Alternatively, you can     use
       input_message_content to send a message with the specified content
       instead of the audio."""

    type: str
    id: str
    audio_url: str
    title: str
    caption: Optional[str] = None
    parse_mode: Optional[str] = None
    performer: Optional[str] = None
    audio_duration: Optional[int] = None
    reply_markup: Optional[InlineKeyboardMarkup] = None
    input_message_content: Optional[InputMessageContent] = None


@dataclass
class InlineQueryResultVoice(Base):
    """Represents a link to a voice recording in an .ogg container encoded
       with OPUS. By default, this voice recording will     be sent by the
       user. Alternatively, you can use input_message_content to send a message
       with the specified     content instead of the the voice message."""

    type: str
    id: str
    voice_url: str
    title: str
    caption: Optional[str] = None
    parse_mode: Optional[str] = None
    voice_duration: Optional[int] = None
    reply_markup: Optional[InlineKeyboardMarkup] = None
    input_message_content: Optional[InputMessageContent] = None


@dataclass
class InlineQueryResultDocument(Base):
    """Represents a link to a file. By default, this file will be sent by
       the user with an optional caption. Alternatively,     you can use
       input_message_content to send a message with the specified content
       instead of the file.     Currently, only .PDF and .ZIP files can be sent
       using this method."""

    type: str
    id: str
    title: str
    document_url: str
    mime_type: str
    caption: Optional[str] = None
    parse_mode: Optional[str] = None
    description: Optional[str] = None
    reply_markup: Optional[InlineKeyboardMarkup] = None
    input_message_content: Optional[InputMessageContent] = None
    thumb_url: Optional[str] = None
    thumb_width: Optional[int] = None
    thumb_height: Optional[int] = None


@dataclass
class InlineQueryResultLocation(Base):
    """Represents a location on a map. By default, the location will be sent
       by the user. Alternatively, you can use input_message_content     to
       send a message with the specified content instead of the location."""

    type: str
    id: str
    latitude: float
    longitude: float
    title: str
    live_period: Optional[int] = None
    reply_markup: Optional[InlineKeyboardMarkup] = None
    input_message_content: Optional[InputMessageContent] = None
    thumb_url: Optional[str] = None
    thumb_width: Optional[int] = None
    thumb_height: Optional[int] = None


@dataclass
class InlineQueryResultVenue(Base):
    """Represents a venue. By default, the venue will be sent by the user.
       Alternatively, you can use input_message_content     to send a message
       with the specified content instead of the venue."""

    type: str
    id: str
    latitude: float
    longitude: float
    title: str
    address: str
    foursquare_id: Optional[str] = None
    foursquare_type: Optional[str] = None
    reply_markup: Optional[InlineKeyboardMarkup] = None
    input_message_content: Optional[InputMessageContent] = None
    thumb_url: Optional[str] = None
    thumb_width: Optional[int] = None
    thumb_height: Optional[int] = None


@dataclass
class InlineQueryResultContact(Base):
    """Represents a contact with a phone number. By default, this contact
       will be sent by the user. Alternatively, you can     use
       input_message_content to send a message with the specified content
       instead of the contact."""

    type: str
    id: str
    phone_number: str
    first_name: str
    last_name: Optional[str] = None
    vcard: Optional[str] = None
    reply_markup: Optional[InlineKeyboardMarkup] = None
    input_message_content: Optional[InputMessageContent] = None
    thumb_url: Optional[str] = None
    thumb_width: Optional[int] = None
    thumb_height: Optional[int] = None


@dataclass
class InlineQueryResultGame(Base):
    """Represents a Game."""

    type: str
    id: str
    game_short_name: str
    reply_markup: Optional[InlineKeyboardMarkup] = None


@dataclass
class InlineQueryResultCachedPhoto(Base):
    """Represents a link to a photo stored on the Telegram servers. By
       default, this photo will be sent by the user with an     optional
       caption. Alternatively, you can use input_message_content to send a
       message with the specified     content instead of the photo."""

    type: str
    id: str
    photo_file_id: str
    title: Optional[str] = None
    description: Optional[str] = None
    caption: Optional[str] = None
    parse_mode: Optional[str] = None
    reply_markup: Optional[InlineKeyboardMarkup] = None
    input_message_content: Optional[InputMessageContent] = None


@dataclass
class InlineQueryResultCachedGif(Base):
    """Represents a link to an animated GIF file stored on the Telegram
       servers. By default, this animated GIF file will be     sent by the user
       with an optional caption. Alternatively, you can use
       input_message_content to send a     message with specified content
       instead of the animation."""

    type: str
    id: str
    gif_file_id: str
    title: Optional[str] = None
    caption: Optional[str] = None
    parse_mode: Optional[str] = None
    reply_markup: Optional[InlineKeyboardMarkup] = None
    input_message_content: Optional[InputMessageContent] = None


@dataclass
class InlineQueryResultCachedMpeg4Gif(Base):
    """Represents a link to a video animation (H.264/MPEG-4 AVC video
       without sound) stored on the Telegram servers. By     default, this
       animated MPEG-4 file will be sent by the user with an optional caption.
       Alternatively, you can use     input_message_content to send a message
       with the specified content instead of the animation."""

    type: str
    id: str
    mpeg4_file_id: str
    title: Optional[str] = None
    caption: Optional[str] = None
    parse_mode: Optional[str] = None
    reply_markup: Optional[InlineKeyboardMarkup] = None
    input_message_content: Optional[InputMessageContent] = None


@dataclass
class InlineQueryResultCachedSticker(Base):
    """Represents a link to a sticker stored on the Telegram servers. By
       default, this sticker will be sent by the user.     Alternatively, you
       can use input_message_content to send a message with the specified
       content instead of     the sticker."""

    type: str
    id: str
    sticker_file_id: str
    reply_markup: Optional[InlineKeyboardMarkup] = None
    input_message_content: Optional[InputMessageContent] = None


@dataclass
class InlineQueryResultCachedDocument(Base):
    """Represents a link to a file stored on the Telegram servers. By
       default, this file will be sent by the user with an     optional
       caption. Alternatively, you can use input_message_content to send a
       message with the specified     content instead of the file."""

    type: str
    id: str
    title: str
    document_file_id: str
    description: Optional[str] = None
    caption: Optional[str] = None
    parse_mode: Optional[str] = None
    reply_markup: Optional[InlineKeyboardMarkup] = None
    input_message_content: Optional[InputMessageContent] = None


@dataclass
class InlineQueryResultCachedVideo(Base):
    """Represents a link to a video file stored on the Telegram servers. By
       default, this video file will be sent by the     user with an optional
       caption. Alternatively, you can use input_message_content to send a
       message with the     specified content instead of the video."""

    type: str
    id: str
    video_file_id: str
    title: str
    description: Optional[str] = None
    caption: Optional[str] = None
    parse_mode: Optional[str] = None
    reply_markup: Optional[InlineKeyboardMarkup] = None
    input_message_content: Optional[InputMessageContent] = None


@dataclass
class InlineQueryResultCachedVoice(Base):
    """Represents a link to a voice message stored on the Telegram servers.
       By default, this voice message will be sent by     the user.
       Alternatively, you can use input_message_content to send a message with
       the specified content     instead of the voice message."""

    type: str
    id: str
    voice_file_id: str
    title: str
    caption: Optional[str] = None
    parse_mode: Optional[str] = None
    reply_markup: Optional[InlineKeyboardMarkup] = None
    input_message_content: Optional[InputMessageContent] = None


@dataclass
class InlineQueryResultCachedAudio(Base):
    """Represents a link to an mp3 audio file stored on the Telegram
       servers. By default, this audio file will be sent by     the user.
       Alternatively, you can use input_message_content to send a message with
       the specified content     instead of the audio."""

    type: str
    id: str
    audio_file_id: str
    caption: Optional[str] = None
    parse_mode: Optional[str] = None
    reply_markup: Optional[InlineKeyboardMarkup] = None
    input_message_content: Optional[InputMessageContent] = None


@dataclass
class InputMessageContent(Base):
    """This object represents the content of a message to be sent as a
       result of an inline query. Telegram clients currently     support the
       following 4 types:"""


@dataclass
class InputTextMessageContent(Base):
    """Represents the content of a text message to be sent as the result of
       an inline     query."""

    message_text: str
    parse_mode: Optional[str] = None
    disable_web_page_preview: Optional[bool] = None


@dataclass
class InputLocationMessageContent(Base):
    """Represents the content of a location message to be sent as the result
       of an inline     query."""

    latitude: float
    longitude: float
    live_period: Optional[int] = None


@dataclass
class InputVenueMessageContent(Base):
    """Represents the content of a venue message to be sent as the result of
       an inline     query."""

    latitude: float
    longitude: float
    title: str
    address: str
    foursquare_id: Optional[str] = None
    foursquare_type: Optional[str] = None


@dataclass
class InputContactMessageContent(Base):
    """Represents the content of a contact message to be sent as the result
       of an inline     query."""

    phone_number: str
    first_name: str
    last_name: Optional[str] = None
    vcard: Optional[str] = None


@dataclass
class ChosenInlineResult(Base):
    """Represents a result of an inline query that was chosen by the user
       and sent to their     chat partner."""

    result_id: str
    from_: User
    query: str
    location: Optional[Location] = None
    inline_message_id: Optional[str] = None


@dataclass
class PassportData(Base):
    """Contains information about Telegram Passport data shared with the bot
       by the user."""

    data: List[EncryptedPassportElement]
    credentials: EncryptedCredentials


@dataclass
class PassportFile(Base):
    """This object represents a file uploaded to Telegram Passport.
       Currently all Telegram Passport files are in JPEG format     when
       decrypted and don't exceed 10MB."""

    file_id: str
    file_size: int
    file_date: int


@dataclass
class EncryptedPassportElement(Base):
    """Contains information about documents or other Telegram Passport
       elements shared with the bot by the user."""

    type: str
    hash: str
    data: Optional[str] = None
    phone_number: Optional[str] = None
    email: Optional[str] = None
    files: Optional[List[PassportFile]] = None
    front_side: Optional[PassportFile] = None
    reverse_side: Optional[PassportFile] = None
    selfie: Optional[PassportFile] = None
    translation: Optional[List[PassportFile]] = None


@dataclass
class EncryptedCredentials(Base):
    """Contains data required for decrypting and authenticating
       EncryptedPassportElement. See the Telegram Passport Documentation for a
       complete description of the data decryption and authentication
       processes."""

    data: str
    hash: str
    secret: str


@dataclass
class PassportElementErrorDataField(Base):
    """Represents an issue in one of the data fields that was provided by
       the user. The error is considered resolved when     the field's value
       changes."""

    source: str
    type: str
    field_name: str
    data_hash: str
    message: str


@dataclass
class PassportElementErrorFrontSide(Base):
    """Represents an issue with the front side of a document. The error is
       considered resolved when the file with the front     side of the
       document changes."""

    source: str
    type: str
    file_hash: str
    message: str


@dataclass
class PassportElementErrorReverseSide(Base):
    """Represents an issue with the reverse side of a document. The error is
       considered resolved when the file with reverse     side of the document
       changes."""

    source: str
    type: str
    file_hash: str
    message: str


@dataclass
class PassportElementErrorSelfie(Base):
    """Represents an issue with the selfie with a document. The error is
       considered resolved when the file with the selfie     changes."""

    source: str
    type: str
    file_hash: str
    message: str


@dataclass
class PassportElementErrorFile(Base):
    """Represents an issue with a document scan. The error is considered
       resolved when the file with the document scan     changes."""

    source: str
    type: str
    file_hash: str
    message: str


@dataclass
class PassportElementErrorFiles(Base):
    """Represents an issue with a list of scans. The error is considered
       resolved when the list of files containing the     scans changes."""

    source: str
    type: str
    file_hashes: List[str]
    message: str


@dataclass
class PassportElementErrorTranslationFile(Base):
    """Represents an issue with one of the files that constitute the
       translation of a document. The error is considered     resolved when the
       file changes."""

    source: str
    type: str
    file_hash: str
    message: str


@dataclass
class PassportElementErrorTranslationFiles(Base):
    """Represents an issue with the translated version of a document. The
       error is considered resolved when a file with the     document
       translation change."""

    source: str
    type: str
    file_hashes: List[str]
    message: str


@dataclass
class PassportElementErrorUnspecified(Base):
    """Represents an issue in an unspecified place. The error is considered
       resolved when new data is added."""

    source: str
    type: str
    element_hash: str
    message: str


@dataclass
class LabeledPrice(Base):
    """This object represents a portion of the price for goods or services."""

    label: str
    amount: int


@dataclass
class Invoice(Base):
    """This object contains basic information about an invoice."""

    title: str
    description: str
    start_parameter: str
    currency: str
    total_amount: int


@dataclass
class ShippingAddress(Base):
    """This object represents a shipping address."""

    country_code: str
    state: str
    city: str
    street_line1: str
    street_line2: str
    post_code: str


@dataclass
class OrderInfo(Base):
    """This object represents information about an order."""

    name: Optional[str] = None
    phone_number: Optional[str] = None
    email: Optional[str] = None
    shipping_address: Optional[ShippingAddress] = None


@dataclass
class ShippingOption(Base):
    """This object represents one shipping option."""

    id: str
    title: str
    prices: List[LabeledPrice]


@dataclass
class SuccessfulPayment(Base):
    """This object contains basic information about a successful payment."""

    currency: str
    total_amount: int
    invoice_payload: str
    telegram_payment_charge_id: str
    provider_payment_charge_id: str
    shipping_option_id: Optional[str] = None
    order_info: Optional[OrderInfo] = None


@dataclass
class ShippingQuery(Base):
    """This object contains information about an incoming shipping query."""

    id: str
    from_: User
    invoice_payload: str
    shipping_address: ShippingAddress


@dataclass
class PreCheckoutQuery(Base):
    """This object contains information about an incoming pre-checkout
       query."""

    id: str
    from_: User
    currency: str
    total_amount: int
    invoice_payload: str
    shipping_option_id: Optional[str] = None
    order_info: Optional[OrderInfo] = None


@dataclass
class Sticker(Base):
    """This object represents a sticker."""

    file_id: str
    width: int
    height: int
    thumb: Optional[PhotoSize] = None
    emoji: Optional[str] = None
    set_name: Optional[str] = None
    mask_position: Optional[MaskPosition] = None
    file_size: Optional[int] = None


@dataclass
class StickerSet(Base):
    """This object represents a sticker set."""

    name: str
    title: str
    contains_masks: bool
    stickers: List[Sticker]


@dataclass
class MaskPosition(Base):
    """This object describes the position on faces where a mask should be
       placed by default."""

    point: str
    x_shift: float
    y_shift: float
    scale: float
