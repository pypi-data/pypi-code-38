# Tele ver 0.0.26
import json
import logging
import requests
from threading import Thread
from time import sleep
import re


def get_me():
    return _call_api('getMe')


def get_updates(offset=None, limit=None,
                allowed_updates=None, timeout=10):
    params = {
        'offset': offset,
        'limit': limit,
        'timeout': timeout
    }
    if allowed_updates:
        params['allowed_updates'] = json.dumps(allowed_updates)

    return _call_api('getUpdates', params=_remove_none(params))


def send_message(chat_id, text, parse_mode='Markdown',
                 disable_web_page_preview=None, disable_notification=None,
                 reply_to_message_id=None, reply_markup=None):
    params = {
        'chat_id': chat_id,
        'text': text,
        'parse_mode': parse_mode,
        'disable_web_page_preview': disable_web_page_preview,
        'disable_notification': disable_notification,
        'reply_to_message_id': reply_to_message_id,
        'reply_markup': reply_markup,
    }
    if type(chat_id) in (list, tuple):
        return _chat_ids(send_message, **params)
    return _call_api('sendMessage', params=_remove_none(params))


def forward_message(chat_id=None, from_chat_id=None, message_id=None,
                    disable_notification=None, update=None):
    params = {
        'chat_id': chat_id,
        'from_chat_id': from_chat_id,
        'message_id': message_id,
        'disable_notification': disable_notification,
        'update': update,
    }
    if type(chat_id) in (list, tuple):
        return _chat_ids(forward_message, **params)
    if update:
        params['from_chat_id'], params['message_id'] = _replay(update)
    return _call_api('forwardMessage', params=_remove_none(params))


def send_photo(chat_id=None, file=None, caption=None,
               reply_to_message_id=None, parse_mode='Markdown',
               disable_web_page_preview=None, disable_notification=None,
               reply_markup=None):
    params = {
        'chat_id': chat_id,
        'file': file,
        'caption': caption,
        'reply_to_message_id': reply_to_message_id,
        'parse_mode': parse_mode,
        'disable_web_page_preview': disable_web_page_preview,
        'disable_notification': disable_notification,
        'reply_markup': reply_markup,
    }
    if type(chat_id) in (list, tuple):
        return _chat_ids(send_photo, **params)
    params, files = _file('photo', params)
    return _call_api('sendPhoto', params=params, files=files)


def send_audio(chat_id=None, file=None, caption=None, parse_mode=None,
               duration=None, performer=None, title=None, thumb=None):
    params = {
        'chat_id': chat_id,
        'file': file,
        'caption': caption,
        'parse_mode': parse_mode,
        'duration': duration,
        'performer': performer,
        'title': title,
        'thumb': thumb,
    }
    if type(chat_id) in (list, tuple):
        return _chat_ids(send_audio, **params)
    params, files = _file('audio', params)
    return _call_api('sendAudio', params=params, files=files)


def send_document(chat_id, file, caption=None, thumb=None,
                  reply_to_message_id=None, parse_mode='Markdown',
                  disable_web_page_preview=None, disable_notification=None,
                  reply_markup=None):
    params = {
        'chat_id': chat_id,
        'file': file,
        'caption': caption,
        'thumb': thumb,
        'reply_to_message_id': reply_to_message_id,
        'parse_mode': parse_mode,
        'disable_web_page_preview': disable_web_page_preview,
        'disable_notification': disable_notification,
        'reply_markup': reply_markup,
    }
    if type(chat_id) in (list, tuple):
        return _chat_ids(send_document, **params)
    params, files = _file('document', params)
    return _call_api('sendDocument', params=params, files=files)


def send_video(chat_id, file, duration=None, width=None, height=None,
               thumb=None, caption=None, parse_mode=None,
               supports_streaming=None, disable_notification=None,
               reply_to_message_id=None, reply_markup=None):
    params = {
        'chat_id': chat_id,
        'file': file,
        'duration': duration,
        'width': width,
        'height': height,
        'thumb': thumb,
        'caption': caption,
        'parse_mode': parse_mode,
        'supports_streaming': supports_streaming,
        'disable_notification': disable_notification,
        'reply_to_message_id': reply_to_message_id,
        'reply_markup': reply_markup,
    }
    if type(chat_id) in (list, tuple):
        return _chat_ids(send_video, **params)
    params, files = _file('video', params)
    return _call_api('sendVideo', params=params, files=files)


def send_animation(chat_id, file, duration=None, width=None, height=None,
                   thumb=None, caption=None, parse_mode=None,
                   disable_notification=None, reply_to_message_id=None,
                   reply_markup=None):
    params = {
        'chat_id': chat_id,
        'file': file,
        'duration': duration,
        'width': width,
        'height': height,
        'thumb': thumb,
        'caption': caption,
        'parse_mode': parse_mode,
        'disable_notification': disable_notification,
        'reply_to_message_id': reply_to_message_id,
        'reply_markup': reply_markup,
    }
    if type(chat_id) in (list, tuple):
        return _chat_ids(sendAnimation, **params)
    params, files = _file('animation', params)
    return _call_api('sendAnimation', params=params, files=files)


def send_voice(chat_id, file, caption=None, parse_mode=None, duration=None,
               disable_notification=None, reply_to_message_id=None,
               reply_markup=None):
    params = {
        'chat_id': chat_id,
        'file': file,
        'caption': caption,
        'parse_mode': parse_mode,
        'duration': duration,
        'disable_notification': disable_notification,
        'reply_to_message_id': reply_to_message_id,
        'reply_markup': reply_markup,
    }
    if type(chat_id) in (list, tuple):
        return _chat_ids(send_voice, **params)
    params, files = _file('voice', params)
    return _call_api('sendVoice', params=params, files=files)


def send_video_note(chat_id, file, duration=None, length=None, thumb=None,
                    disable_notification=None, reply_to_message_id=None,
                    reply_markup=None):
    params = {
        'chat_id': chat_id,
        'file': file,
        'duration': duration,
        'length': length,
        'thumb': thumb,
        'disable_notification': disable_notification,
        'reply_to_message_id': reply_to_message_id,
        'reply_markup': reply_markup,
    }
    if type(chat_id) in (list, tuple):
        return _chat_ids(send_video_note, **params)
    params, files = _file('video_note', params)
    return _call_api('sendVideoNote', params=params, files=files)


def send_media_group(chat_id, media, disable_notification=None,
                     reply_to_message_id=None):
    files = {}
    for m in media:
        try:
            files[m['media']] = open(m['media'], 'rb')
            m['media'] = 'attach://' + m['media']
        except FileNotFoundError:
            pass
    params = {
        'chat_id': chat_id,
        'media': json.dumps(media),
        'disable_notification': disable_notification,
        'reply_to_message_id': reply_to_message_id,
    }
    return _call_api('sendMediaGroup', params=_remove_none(params), files=files)


def send_location(chat_id, latitude, longitude, live_period=None,
                  disable_notification=None, reply_to_message_id=None,
                  reply_markup=None):
    params = {
        'chat_id': chat_id,
        'latitude': latitude,
        'longitude': longitude,
        'live_period': live_period,
        'disable_notification': disable_notification,
        'reply_to_message_id': reply_to_message_id,
        'reply_markup': reply_markup,
    }
    if type(chat_id) in (list, tuple):
        return _chat_ids(send_location, **params)
    return _call_api('sendLocation', params=_remove_none(params))


def edit_message_live_location(chat_id=None, message_id=None,
                               inline_message_id=None, latitude=None,
                               longitude=None, reply_markup=None, update=None):
    params = {
        'chat_id': chat_id,
        'message_id': message_id,
        'inline_message_id': inline_message_id,
        'latitude': latitude,
        'longitude': longitude,
        'reply_markup': reply_markup,
        'update': update,
    }
    if update:
        params['chat_id'], params['message_id'] = _replay(update)
    return _call_api('editMessageLiveLocation', params=_remove_none(params))


def stop_message_live_location(chat_id=None, message_id=None,
                               inline_message_id=None, reply_markup=None,
                               update=None):
    params = {
        'chat_id': chat_id,
        'message_id': message_id,
        'inline_message_id': inline_message_id,
        'reply_markup': reply_markup,
        'update': update,
    }
    if update:
        params['chat_id'], params['message_id'] = _replay(update)
    return _call_api('stopMessageLiveLocation', params=_remove_none(params))


def send_venue(chat_id, latitude, longitude, title, address,
               foursquare_id=None, foursquare_type=None,
               disable_notification=None, reply_to_message_id=None,
               reply_markup=None):
    params = {
        'chat_id': chat_id,
        'latitude': latitude,
        'longitude': longitude,
        'title': title,
        'address': address,
        'foursquare_id': foursquare_id,
        'foursquare_type': foursquare_type,
        'disable_notification': disable_notification,
        'reply_to_message_id': reply_to_message_id,
        'reply_markup': reply_markup,
    }
    if type(chat_id) in (list, tuple):
        return _chat_ids(send_venue, **params)
    return _call_api('sendVenue', params=_remove_none(params))


def send_contact(chat_id, phone_number, first_name, last_name=None,
                 vcard=None, disable_notification=None,
                 reply_to_message_id=None, reply_markup=None):
    params = {
        'chat_id': chat_id,
        'phone_number': phone_number,
        'first_name': first_name,
        'last_name': last_name,
        'vcard': vcard,
        'disable_notification': disable_notification,
        'reply_to_message_id': reply_to_message_id,
        'reply_markup': reply_markup,
    }

    if type(chat_id) in (list, tuple):
        return _chat_ids(send_contact, **params)
    return _call_api('sendContact', params=_remove_none(params))


def send_poll(chat_id, question, options,
              disable_notification=None, reply_to_message_id=None,
              reply_markup=None):
    params = {'chat_id': chat_id,
              'question': question,
              'disable_notification': disable_notification,
              'reply_to_message_id': reply_to_message_id,
              'reply_markup': reply_markup,
              'options': json.dumps(options, ensure_ascii=False)
              }
    if type(chat_id) in (list, tuple):
        return _chat_ids(send_poll, **params)
    return _call_api('sendPoll', params=_remove_none(params))


def send_chat_action(chat_id, action):
    params = {
        'chat_id': chat_id,
        'action': action,
    }
    if type(chat_id) in (list, tuple):
        return _chat_ids(send_chat_action, **params)
    return _call_api('sendChatAction', params=_remove_none(params))


def get_user_profile_photos(user_id, offset=None, limit=None):
    params = {
        'user_id': user_id,
        'offset': offset,
        'limit': limit,
    }
    return _call_api('getUserProfilePhotos', params=_remove_none(params))


def get_file(file_id):
    return _call_api('getFile?file_id=' + file_id)


def kick_chat_member(chat_id, user_id, until_date=None):
    params = {
        'chat_id': chat_id,
        'user_id': user_id,
        'until_date': until_date,
    }
    return _call_api('kickChatMember', params=_remove_none(params))


def unban_chat_member(chat_id, user_id):
    params = {
        'chat_id': chat_id,
        'user_id': user_id,
    }
    return _call_api('unbanChatMember', params=_remove_none(params))


def restrict_chat_member(chat_id, user_id, until_date=None,
                         can_send_messages=None, can_send_media_messages=None,
                         can_send_other_messages=None,
                         can_add_web_page_previews=None):
    params = {
        'chat_id': chat_id,
        'user_id': user_id,
        'until_date': until_date,
        'can_send_messages': can_send_messages,
        'can_send_media_messages': can_send_media_messages,
        'can_send_other_messages': can_send_other_messages,
        'can_add_web_page_previews': can_add_web_page_previews,
    }

    return _call_api('restrictChatMember', params=_remove_none(params))


def promote_chat_member(chat_id, user_id, can_change_info=None,
                        can_post_messages=None, can_edit_messages=None,
                        can_delete_messages=None, can_invite_users=None,
                        can_restrict_members=None, can_pin_messages=None,
                        can_promote_members=None):
    params = {
        'chat_id': chat_id,
        'user_id': user_id,
        'can_change_info': can_change_info,
        'can_post_messages': can_post_messages,
        'can_edit_messages': can_edit_messages,
        'can_delete_messages': can_delete_messages,
        'can_invite_users': can_invite_users,
        'can_restrict_members': can_restrict_members,
        'can_pin_messages': can_pin_messages,
        'can_promote_members': can_promote_members,
    }
    return _call_api('promoteChatMember', params=_remove_none(params))


def export_chat_invite_link(chat_id):
    params = {
        'chat_id': chat_id,
    }
    return _call_api('exportChatInviteLink', params=params)


def set_chat_photo(chat_id, photo):
    params = {
        'chat_id': chat_id,
        'photo': photo,
    }

    params, files = _file('photo', params)
    return _call_api('sendVideoNote', params=params, files=files)


def delete_chat_photo(chat_id):
    params = {
        'chat_id': chat_id,
    }
    return _call_api('deleteChatPhoto', params=params)


def set_chat_title(chat_id, title):
    params = {
        'chat_id': chat_id,
        'title': title,
    }
    return _call_api('setChatTitle', params=params)


def set_chat_description(chat_id, description):
    params = {
        'chat_id': chat_id,
        'description': description,
    }

    return _call_api('setChatDescription', params=params)


def pin_chat_message(chat_id, message_id, disable_notification=None):
    params = {
        'chat_id': chat_id,
        'message_id': message_id,
        'disable_notification': disable_notification,
    }
    return _call_api('pinChatMessage', params=_remove_none(params))


def unpin_chat_message(chat_id):
    params = {
        'chat_id': chat_id,
    }
    return _call_api('unpinChatMessage', params=params)


def leave_chat(chat_id):
    params = {
        'chat_id': chat_id,
    }
    return _call_api('leaveChat', params=params)


def get_chat(chat_id):
    params = {
        'chat_id': chat_id,
    }
    return _call_api('getChat', params=params)


def get_chat_administrators(chat_id):
    params = {
        'chat_id': chat_id,
    }
    return _call_api('getChatAdministrators', params=params)


def get_chat_members_count(chat_id):
    params = {
        'chat_id': chat_id,
    }
    return _call_api('ChatMembersCount', params=params)


def get_chat_member(chat_id, user_id):
    params = {
        'chat_id': chat_id,
        'user_id': user_id,
    }
    return _call_api('getChatMember', params=params)


def set_chat_sticker_set(chat_id, sticker_set_name):
    params = {
        'chat_id': chat_id,
        'sticker_set_name': sticker_set_name,
    }
    return _call_api('setChatStickerSet', params=params)


def delete_chat_sticker_set(chat_id):
    params = {
        'chat_id': chat_id,
    }
    return _call_api('deleteChatStickerSet', params=params)


def answer_callback_query(callback_query_id, text=None, show_alert=None,
                          url=None, cache_time=None):
    params = {
        'callback_query_id': callback_query_id,
        'text': text,
        'show_alert': show_alert,
        'url': url,
        'cache_time': cache_time,
    }
    return _call_api('answerCallbackQuery', params=_remove_none(params))


def edit_message_text(chat_id=None, message_id=None, inline_message_id=None,
                      text=None, parse_mode='Markdown',
                      disable_web_page_preview=None,
                      reply_markup=None, update=None):
    params = {
        'chat_id': chat_id,
        'message_id': message_id,
        'inline_message_id': inline_message_id,
        'text': text,
        'parse_mode': parse_mode,
        'disable_web_page_preview': disable_web_page_preview,
        'reply_markup': reply_markup,
        'update': update,
    }
    if update:
        params['chat_id'], params['message_id'] = _replay(update)
    return _call_api('editMessageText', params=_remove_none(params))


def edit_message_caption(chat_id=None, message_id=None, inline_message_id=None,
                         caption=None, parse_mode='Markdown', reply_markup=None,
                         update=None):
    params = {
        'chat_id': chat_id,
        'message_id': message_id,
        'inline_message_id': inline_message_id,
        'caption': caption,
        'parse_mode': parse_mode,
        'reply_markup': reply_markup,
        'update': update,
    }
    if update:
        params['chat_id'], params['message_id'] = _replay(update)
    return _call_api('editMessageCaption', params=_remove_none(params))


def edit_message_media(chat_id=None, message_id=None, inline_message_id=None,
                       media=None, reply_markup=None, update=None):
    files = {}
    try:
        files[media['media']] = open(media['media'], 'rb')
        media['media'] = 'attach://' + media['media']
    except FileNotFoundError:
        pass
    params = {
        'chat_id': chat_id,
        'message_id': message_id,
        'inline_message_id': inline_message_id,
        'media': json.dumps(media),
        'reply_markup': reply_markup,
        'update': update,
    }
    if update:
        params['chat_id'], params['message_id'] = _replay(update)
    return _call_api('editMessageMedia',
                     params=_remove_none(params), files=files)


def edit_message_reply_markup(chat_id=None, message_id=None,
                              inline_message_id=None, reply_markup=None,
                              update=None):
    params = {
        'chat_id': chat_id,
        'message_id': message_id,
        'inline_message_id': inline_message_id,
        'reply_markup': reply_markup,
    }
    if update:
        params['chat_id'], params['message_id'] = _replay(update)
    return _call_api('editMessageReplyMarkup', params=_remove_none(params))


def stop_poll(chat_id, message_id=None, reply_markup=None):
    params = {
        'chat_id': chat_id,
        'message_id': message_id,
        'reply_markup': reply_markup,
    }
    return _call_api('stopPoll', params=_remove_none(params))


def delete_message(chat_id=None, message_id=None, update=None):
    if update:
        chat_id, message_id = _replay(update)
    params = {'chat_id': chat_id, 'message_id': message_id}
    return _call_api('deleteMessage', params=params)


def send_sticker(chat_id, file, disable_notification=None,
                 reply_to_message_id=None, reply_markup=None):
    params = {
        'chat_id': chat_id,
        'file': file,
        'disable_notification': disable_notification,
        'reply_to_message_id': reply_to_message_id,
        'reply_markup': reply_markup,
    }

    params, files = _file('sticker', params)
    return _call_api('sendSticker', params=params, files=files)


def get_sticker_set(name):
    params = {
        'name': name,
    }
    return _call_api('getStickerSet', params=params)


def upload_sticker_file(user_id, file):
    params = {
        'user_id': user_id,
        'file': file,
    }
    params, files = _file('png_sticker', params)
    return _call_api('uploadStickerFile', params=params, files=files)


def create_new_sticker_set(user_id, name, title, file, emojis,
                           contains_masks=None, mask_position=None):
    params = {
        'user_id': user_id,
        'name': name,
        'title': title,
        'file': file,
        'emojis': emojis,
        'contains_masks': contains_masks,
        'mask_position': mask_position,
    }
    params, files = _file('png_sticker', params)
    return _call_api('createNewStickerSet', params=params, files=files)


def add_sticker_to_set(user_id, name, file, emojis, mask_position=None):
    params = {
        'user_id': user_id,
        'name': name,
        'file': file,
        'emojis': emojis,
        'mask_position': mask_position,
    }
    params, files = _file('png_sticker', params)
    return _call_api('addStickerToSet', params=params, files=files)


def set_sticker_position_in_set(sticker, position):
    params = {
        'sticker': sticker,
        'position': position,
    }
    return _call_api('setStickerPositionInSet', params=params)


def delete_sticker_from_set(sticker):
    params = {
        'sticker': sticker,
    }
    return _call_api('deleteStickerFromSet', params=params)


def answer_inline_query(update, results, cache_time='300', is_personal=None,
                        next_offset=None, switch_pm_text=None,
                        switch_pm_parameter=None):
    params = {
        'inline_query_id': update.id,
        'results': results,
        'cache_time': cache_time,
        'is_personal': is_personal,
        'next_offset': next_offset,
        'switch_pm_text': switch_pm_text,
        'switch_pm_parameter': switch_pm_parameter,
    }
    return _call_api('answerInlineQuery', json=_remove_none(params))


def inline_query_result_article(id, title=None, input_message_content=None,
                                reply_markup=None, url=None, hide_url=None,
                                description=None, thumb_url=None,
                                thumb_width=None, thumb_height=None):
    params = {
        'id': id,
        'title': title,
        'input_message_content': input_message_content,
        'url': url,
        'hide_url': hide_url,
        'description': description,
        'thumb_url': thumb_url,
        'thumb_width': thumb_width,
        'thumb_height': thumb_height,
    }
    if reply_markup:
        params['reply_markup'] = json.loads(reply_markup)
    params = _remove_none(params)
    params['type'] = 'article'
    return params


def inline_query_result_photo(id, photo_url=None, thumb_url=None,
                              photo_width=None, photo_height=None,
                              title=None, description=None, caption=None,
                              parse_mode='Markdown', reply_markup=None,
                              input_message_content=None):
    params = {
        'id': id,
        'photo_url': photo_url,
        'thumb_url': thumb_url,
        'photo_width': photo_width,
        'photo_height': photo_height,
        'title': title,
        'description': description,
        'caption': caption,
        'parse_mode': parse_mode,
        'input_message_content': input_message_content,
    }
    if reply_markup:
        params['reply_markup'] = json.loads(reply_markup)
    params = _remove_none(params)
    params['type'] = 'photo'
    return params


def inline_query_result_gif(id, gif_url, gif_width=None, gif_height=None,
                            gif_duration=None, thumb_url=None, title=None,
                            caption=None, parse_mode=None, reply_markup=None,
                            input_message_content=None):
    params = {
        'id': id,
        'gif_url': gif_url,
        'gif_width': gif_width,
        'gif_height': gif_height,
        'gif_duration': gif_duration,
        'thumb_url': thumb_url,
        'title': title,
        'caption': caption,
        'parse_mode': parse_mode,
        'input_message_content': input_message_content,
    }
    if reply_markup:
        params['reply_markup'] = json.loads(reply_markup)
    params = _remove_none(params)
    params['type'] = 'gif'
    return params


def inline_query_result_mpeg4_gif(id, mpeg4_url, mpeg4_width=None,
                                  mpeg4_height=None, mpeg4_duration=None,
                                  thumb_url=None, title=None, caption=None,
                                  parse_mode=None, reply_markup=None,
                                  input_message_content=None):
    params = {
        'id': id,
        'mpeg4_url': mpeg4_url,
        'mpeg4_width': mpeg4_width,
        'mpeg4_height': mpeg4_height,
        'mpeg4_duration': mpeg4_duration,
        'thumb_url': thumb_url,
        'title': title,
        'caption': caption,
        'parse_mode': parse_mode,
        'input_message_content': input_message_content,
    }
    if reply_markup:
        params['reply_markup'] = json.loads(reply_markup)
    params = _remove_none(params)
    params['type'] = 'mpeg4_gif'
    return params


def inline_query_result_video(id, video_url, mime_type, thumb_url, title,
                              caption=None, parse_mode=None, video_width=None,
                              video_height=None, video_duration=None,
                              description=None, reply_markup=None,
                              input_message_content=None):
    params = {
        'id': id,
        'video_url': video_url,
        'mime_type': mime_type,
        'thumb_url': thumb_url,
        'title': title,
        'caption': caption,
        'parse_mode': parse_mode,
        'video_width': video_width,
        'video_height': video_height,
        'video_duration': video_duration,
        'description': description,
        'input_message_content': input_message_content,
    }
    if reply_markup:
        params['reply_markup'] = json.loads(reply_markup)
    params = _remove_none(params)
    params['type'] = 'video'
    return params


def inline_query_result_audio(id, audio_url, title, caption, parse_mode=None,
                              performer=None, audio_duration=None,
                              reply_markup=None, input_message_content=None):
    params = {
        'id': id,
        'audio_url': audio_url,
        'title': title,
        'caption': caption,
        'parse_mode': parse_mode,
        'performer': performer,
        'audio_duration': audio_duration,
        'input_message_content': input_message_content,
    }
    if reply_markup:
        params['reply_markup'] = json.loads(reply_markup)
    params = _remove_none(params)
    params['type'] = 'audio'
    return params


def inline_query_result_voice(id, voice_url, title, caption=None,
                              parse_mode=None, voice_duration=None,
                              reply_markup=None, input_message_content=None):
    params = {
        'id': id,
        'voice_url': voice_url,
        'title': title,
        'caption': caption,
        'parse_mode': parse_mode,
        'voice_duration': voice_duration,
        'input_message_content': input_message_content,
    }
    if reply_markup:
        params['reply_markup'] = json.loads(reply_markup)
    params = _remove_none(params)
    params['type'] = 'voice'
    return params


def inline_query_result_document(id, title=None, caption=None, parse_mode=None,
                                 document_url=None, mime_type=None,
                                 description=None, reply_markup=None,
                                 input_message_content=None, thumb_url=None,
                                 thumb_width=None, thumb_height=None):
    params = {
        'id': id,
        'title': title,
        'caption': caption,
        'parse_mode': parse_mode,
        'document_url': document_url,
        'mime_type': mime_type,
        'description': description,
        'input_message_content': input_message_content,
        'thumb_url': thumb_url,
        'thumb_width': thumb_width,
        'thumb_height': thumb_height,
    }
    if reply_markup:
        params['reply_markup'] = json.loads(reply_markup)
    params = _remove_none(params)
    params['type'] = 'document'
    return params


def inline_query_result_location(id, latitude, longitude, title,
                                 live_period=None, reply_markup=None,
                                 input_message_content=None, thumb_url=None,
                                 thumb_width=None, thumb_height=None):
    params = {
        'id': id,
        'latitude': latitude,
        'longitude': longitude,
        'title': title,
        'live_period': live_period,
        'input_message_content': input_message_content,
        'thumb_url': thumb_url,
        'thumb_width': thumb_width,
        'thumb_height': thumb_height,
    }
    if reply_markup:
        params['reply_markup'] = json.loads(reply_markup)
    params = _remove_none(params)
    params['type'] = 'location'
    return params


def inline_query_result_venue(id, latitude, longitude, title, address,
                              foursquare_id=None, reply_markup=None,
                              input_message_content=None, thumb_url=None,
                              thumb_width=None, thumb_height=None):
    params = {
        'id': id,
        'latitude': latitude,
        'longitude': longitude,
        'title': title,
        'address': address,
        'foursquare_id': foursquare_id,
        'input_message_content': input_message_content,
        'thumb_url': thumb_url,
        'thumb_width': thumb_width,
        'thumb_height': thumb_height,
    }
    if reply_markup:
        params['reply_markup'] = json.loads(reply_markup)
    params = _remove_none(params)
    params['type'] = 'venue'
    return params


def inline_query_result_contact(id, phone_number, first_name, last_name=None,
                                vcard=None, reply_markup=None,
                                input_message_content=None, thumb_url=None,
                                thumb_width=None, thumb_height=None):
    params = {
        'id': id,
        'phone_number': phone_number,
        'first_name': first_name,
        'last_name': last_name,
        'vcard': vcard,
        'input_message_content': input_message_content,
        'thumb_url': thumb_url,
        'thumb_width': thumb_width,
        'thumb_height': thumb_height,
    }
    if reply_markup:
        params['reply_markup'] = json.loads(reply_markup)
    params = _remove_none(params)
    params['type'] = 'contact'
    return params


def inline_query_result_game(id, game_short_name, reply_markup):
    params = {
        'id': id,
        'game_short_name': game_short_name,
    }
    if reply_markup:
        params['reply_markup'] = json.loads(reply_markup)
    params = _remove_none(params)
    params['type'] = 'game'
    return params


def inline_query_result_cached_photo(id, photo_file_id, title=None,
                                     description=None, caption=None,
                                     parse_mode=None, reply_markup=None,
                                     input_message_content=None):
    params = {
        'id': id,
        'photo_file_id': photo_file_id,
        'title': title,
        'description': description,
        'caption': caption,
        'parse_mode': parse_mode,
        'input_message_content': input_message_content,
    }
    if reply_markup:
        params['reply_markup'] = json.loads(reply_markup)
    params = _remove_none(params)
    params['type'] = 'photo'
    return params


def inline_query_result_cached_gif(id, gif_file_id, title=None, caption=None,
                                   parse_mode=None, reply_markup=None,
                                   input_message_content=None):
    params = {
        'id': id,
        'gif_file_id': gif_file_id,
        'title': title,
        'caption': caption,
        'parse_mode': parse_mode,
        'input_message_content': input_message_content,
    }
    if reply_markup:
        params['reply_markup'] = json.loads(reply_markup)
    params = _remove_none(params)
    params['type'] = 'gif'
    return params


def inline_query_result_cached_mpeg4_gif(id, mpeg4_file_id, title=None,
                                         caption=None, parse_mode=None,
                                         reply_markup=None,
                                         input_message_content=None):
    params = {
        'id': id,
        'mpeg4_file_id': mpeg4_file_id,
        'title': title,
        'caption': caption,
        'parse_mode': parse_mode,
        'input_message_content': input_message_content,
    }
    if reply_markup:
        params['reply_markup'] = json.loads(reply_markup)
    params = _remove_none(params)
    params['type'] = 'mpeg4_gif'
    return params


def inline_query_result_cached_sticker(id, sticker_file_id=None,
                                       reply_markup=None,
                                       input_message_content=None):
    params = {
        'id': id,
        'sticker_file_id': sticker_file_id,
        'input_message_content': input_message_content,
    }
    if reply_markup:
        params['reply_markup'] = json.loads(reply_markup)
    params = _remove_none(params)
    params['type'] = 'sticker'
    return params


def inline_query_result_cached_document(id, title, document_file_id,
                                        description=None, caption=None,
                                        parse_mode=None, reply_markup=None,
                                        input_message_content=None):
    params = {
        'id': id,
        'title': title,
        'document_file_id': document_file_id,
        'description': description,
        'caption': caption,
        'parse_mode': parse_mode,
        'input_message_content': input_message_content,
    }
    if reply_markup:
        params['reply_markup'] = json.loads(reply_markup)
    params = _remove_none(params)
    params['type'] = 'document'
    return params


def inline_query_result_cached_video(id, video_file_id, title,
                                     description=None, caption=None,
                                     parse_mode=None, reply_markup=None,
                                     input_message_content=None):
    params = {
        'id': id,
        'video_file_id': video_file_id,
        'title': title,
        'description': description,
        'caption': caption,
        'parse_mode': parse_mode,
        'input_message_content': input_message_content,
    }
    if reply_markup:
        params['reply_markup'] = json.loads(reply_markup)
    params = _remove_none(params)
    params['type'] = 'video'
    return params


def inline_query_result_cached_voice(id, voice_file_id, title, caption=None,
                                     parse_mode=None, reply_markup=None,
                                     input_message_content=None):
    params = {
        'id': id,
        'voice_file_id': voice_file_id,
        'title': title,
        'caption': caption,
        'parse_mode': parse_mode,
        'input_message_content': input_message_content,
    }
    if reply_markup:
        params['reply_markup'] = json.loads(reply_markup)
    params = _remove_none(params)
    params['type'] = 'voice'
    return params


def inline_query_result_cached_audio(id, audio_file_id,
                                     caption, parse_mode=None,
                                     reply_markup=None,
                                     input_message_content=None):
    params = {
        'id': id,
        'audio_file_id': audio_file_id,
        'caption': caption,
        'parse_mode': parse_mode,
        'input_message_content': input_message_content,
    }
    if reply_markup:
        params['reply_markup'] = json.loads(reply_markup)
    params = _remove_none(params)
    params['type'] = 'audio'
    return params


def input_text_message_content(message_text=None, parse_mode=None,
                               disable_web_page_preview=None):
    params = {
        'message_text': message_text,
        'parse_mode': parse_mode,
        'disable_web_page_preview': disable_web_page_preview,
    }
    return _remove_none(params)


def input_location_message_content(latitude, longitude, live_period=None):
    params = {
        'latitude': latitude,
        'longitude': longitude,
        'live_period': live_period,
    }
    return _remove_none(params)


def input_venue_message_content(latitude, longitude, title, address,
                                foursquare_id=None, foursquare_type=None):
    params = {
        'latitude': latitude,
        'longitude': longitude,
        'title': title,
        'address': address,
        'foursquare_id': foursquare_id,
        'foursquare_type': foursquare_type,
    }
    return _remove_none(params)


def input_contact_message_content(phone_number, first_name, last_name=None,
                                  vcard=None):
    params = {
        'phone_number': phone_number,
        'first_name': first_name,
        'last_name': last_name,
        'vcard': vcard,
    }
    return _remove_none(params)


def chosen_inline_result(result_id, from_user, location=None,
                         inline_message_id=None, query=None):
    params = {
        'result_id': result_id,
        'from_user': from_user,
        'location': location,
        'inline_message_id': inline_message_id,
        'query': query,
    }
    return _remove_none(params)


def input_media_photo(media, caption=None, parse_mode=None):
    params = {
        'type': 'photo',
        'media': media,
        'caption': caption,
        'parse_mode': parse_mode,
    }
    return _remove_none(params)


def input_media_video(media, thumb=None, caption=None, parse_mode=None,
                      width=None, height=None, duration=None,
                      supports_streaming=None):
    params = {
        'type': 'video',
        'media': media,
        'thumb': thumb,
        'caption': caption,
        'parse_mode': parse_mode,
        'width': width,
        'height': height,
        'duration': duration,
        'supports_streaming': supports_streaming,
    }
    return _remove_none(params)


def input_media_animation(media, thumb=None, caption=None, parse_mode=None,
                          width=None, height=None, duration=None):
    params = {
        'media': media,
        'thumb': thumb,
        'caption': caption,
        'parse_mode': parse_mode,
        'width': width,
        'height': height,
        'duration': duration,
    }
    params = _remove_none(params)
    params['type'] = 'animation'
    return params


def input_media_audio(media, thumb=None, caption=None, parse_mode=None,
                      duration=None, performer=None, title=None):
    params = {
        'media': media,
        'thumb': thumb,
        'caption': caption,
        'parse_mode': parse_mode,
        'duration': duration,
        'performer': performer,
        'title': title,
    }
    params = _remove_none(params)
    params['type'] = 'audio'
    return params


def input_media_document(media, thumb=None, caption=None, parse_mode=None):
    params = {
        'type': 'document',
        'media': media,
        'thumb': thumb,
        'caption': caption,
        'parse_mode': parse_mode,
    }
    return _remove_none(params)


def reply_keyboard_markup(k=None, resize_keyboard=True,
                          one_time_keyboard=None, num_line=None,
                          remove=False):
    if remove:
        return '{"remove_keyboard": true}'
    if num_line:
        k = _num_ln(k, num_line)
    key = []
    for line in k:
        key.append([{'text': button} for button in line])
    key = {'keyboard': key, 'resize_keyboard': resize_keyboard}
    if one_time_keyboard:
        key['one_time_keyboard'] = one_time_keyboard

    return json.dumps(key, ensure_ascii=False)


def reply_keyboard_remove():
    return reply_keyboard_markup(remove=True)


def inline_keyboard(k=None, num_line=None, obj='callback_data'):
    if num_line:
        k = _num_ln(k, num_line)
    key = []
    for line in k:
        for b in line:
            if len(b) < 2:
                b['type'] = obj
        key.append(
            [{'text': tuple(b.keys())[0],
              tuple(b.values())[1]: tuple(b.values())[0]} for b in line]
        )
    return json.dumps({'inline_keyboard': key}, ensure_ascii=False)


def force_reply(selective=None):
    params = {'force_reply': True}
    if selective:
        params['selective'] = selective
    return json.dumps(params, ensure_ascii=False)


"""
The following functions do not exist in the methods or object of Telegram api.
These functions are optimized for use
"""


def _num_ln(keys, num):
    """Arranging buttons"""
    if type(keys[0]) is list:
        keys = keys[0]

    len_k = len(keys)
    num_of_lines = len_k // num

    lst, curr = [], 0
    for d in range(num_of_lines):
        temp_lst = []
        for e in range(curr, (num + curr)):
            temp_lst.append(keys[e])

        lst.append(temp_lst)
        curr += num

    lst.append(keys[len_k - (len_k % num):])
    return lst


def message_reply(update, text=None, file=None, photo=None,
                  parse_mode='Markdown', disable_web_page_preview=None,
                  reply_markup=None):
    """
    :param update: (:obj:`update`) getUpdates results.
    :param text: (:obj:`str`) text, to use sendMessage method or as caption.
    :param file: (:obj:`str`) path file or url to use sendDocument method
    :param photo: (:obj:`str`) path file or url to use sendDocument method
    :param parse_mode: (:obj:`str`, optional)  Send Markdown or HTML,
     if you want Telegram apps to show bold, italic, fixed-width text
      or inline URLs in your bot's message.
    :param disable_web_page_preview: (:obj:`bool`, optional)  Disables
     link previews for links in this message
    :param reply_markup: (:obj:`InlineKeyboardMarkup`,
     :obj:`ReplyKeyboardMarkup`, :obj:`ReplyKeyboardRemove`,
     :obj:`ForceReply`, optional)  Additional interface options.
     A JSON-serialized object for an inline keyboard,
     custom reply keyboard, instructions
     to remove reply keyboard or to force a reply from the user.
    """
    chat_id, reply_to_message_id = _replay(update)

    params = {
        'chat_id': chat_id,
        'reply_to_message_id': reply_to_message_id,
        'parse_mode': parse_mode,
        'disable_web_page_preview': disable_web_page_preview,
        'reply_markup': reply_markup
    }

    if file:
        params['file'], params['caption'] = file, text
        return sendDocument(**params)
    elif photo:
        params['file'], params['caption'] = file, text
        return sendPhoto(**params)

    params['text'] = text
    return sendMessage(**_remove_none(params))


def download_file(file_id, name, destination=''):
    """
    :param file_id: (:obj: `str`) file_id
    :param name: (:obj: 'str') name for the new file
    :param destination: (:obj: 'str', optional) path to save the new file.
    :return: True or Exception
    """
    try:
        file_path = getFile(file_id)['file_path']
        file = requests.get('{}file/{}/{}'.format(
            _API[:25], _API[25:], file_path))
        if destination and not destination.endswith('/'):
            destination += '/'
        with open(destination + name, 'wb') as new_file:
            new_file.write(file.content)
        return True
    except Exception as ex:
        return _error(ex)


def _chat_ids(func, **params):
    _response = []
    for chat_id in params['chat_id']:
        params['chat_id'] = chat_id
        _response += func(**params)
    return _response


def _file(func, params):
    params[func] = params.pop('file')
    params = _remove_none(params)
    try:
        files = {func: open(params[func], 'rb')}
        del params[func]
    except FileNotFoundError:
        files = None
    if 'thumb' in params:
        if params['thumb']:
            try:
                tmb = open(params['thumb'], 'rb')
                files['thumb'] = tmb
            except FileNotFoundError:
                pass
            return params, files
    return params, files


def _replay(update):
    if 'message' in update:
        return update.message.chat.id, update.message.message_id
    elif 'chat' in update:
        return update.chat.id, update.message_id

    return update['from'].id, update.message.message_id


def _remove_none(params):
    return dict(filter(lambda item: item[1] is not None, params.items()))


class _Dict(dict):
    """convert the json to dict and object.
    so:
        update['document']['file_id']
        update.document.file_id
    should work properly.."""

    def __init__(self, dict_):
        super(_Dict, self).__init__(dict_)
        for key in self:
            item = self[key]
            if isinstance(item, list):
                for idx, it in enumerate(item):
                    if isinstance(it, dict):
                        item[idx] = _Dict(it)
            elif isinstance(item, dict):
                self[key] = _Dict(item)

    def __getattr__(self, key):
        return self[key]


def _call_api(method, **kwargs):
    """Make api call"""
    try:
        response = requests.post(_API + method, **kwargs).json()
        if not response['ok']:
            _error(response)
        return _Dict(response)['result']

    except KeyError:
        raise Exception('error: Unauthorized token'
                        '\nOr, terminated by other getUpdates request; '
                        'make sure that only one bot instance is running')

    except requests.exceptions.ConnectionError as ex:
        sleep(2)
        return _error(ex)

    except requests.exceptions.RequestException as ex:
        sleep(2)
        return _error(ex)

    except Exception as ex:
        return _error(ex)


_funcs_list = {}
_error_func_list = []


def _error(update):
    logging.warning('error %s' % update)
    if _error_func_list:
        for func in _error_func_list:
            func(update)


def bot(filters=None, not_on=None, command=None,
        chat_id=None, chat_type=None, from_id=None,
        regex=None, callback_query=None, inline_query=None,
        on_error=None):
    """
    :param filters: (:obj:`str`, :obj:`tuple`, :obj:`list` optional)
     objects from https://core.telegram.org/bots/api#update, and
     and entity type https://core.telegram.org/bots/api#messageentity
     see here: https://gitlab.com/2411eliko/tele/blob/master/Examples/filters.md
    :param not_on: (:obj:`str`, :obj:`tuple`, :obj:`list` optional)
     negative objects from https://core.telegram.org/bots/api#update, and
     and entity type https://core.telegram.org/bots/api#messageentity
     see here: https://gitlab.com/2411eliko/tele/blob/master/Examples/filters.md
    :param command: (:obj:`str`, :obj:`tuple`, :obj:`list` optional) command(s)
     for example, 'start' to command '/start'. list or tuple:
     ('help', 'info'), to respond od '/help' or '/info'.
    :param chat_id: (:obj:`int`, optional) chat id
    :param chat_type: (:obj:`str`, optional) Type of chat, can be either
     “private”, “group”, “supergroup” or “channel”
    :param from_id: (:obj:`int`, optional) user id
    :param regex: (:obj:`regex-pattern`, optional) respond on
     text or caption messages contain regex pattern match
    :param callback_query: (:obj:`regex-pattern`, optional) respond on
     callback_query contain regex pattern match
    :param inline_query:  (:obj:`regex-pattern`, optional) respond on
     inline_query contain regex pattern match
    :param on_error: (:obj:`bool`, optional) pass True to receive
     any errors for logging etc...
    """

    def decorator(func):
        if on_error:
            _error_func_list.append(func)
        else:
            _funcs_list[func] = dict(
                filters=filters, not_on=not_on,
                command=command, chat_id=chat_id,
                chat_type=chat_type, from_id=from_id,
                regex=regex,
                callback_query=callback_query,
                inline_query=inline_query,
                on_error=on_error
            )

    return decorator


def _filter_key(fil, keys):
    if type(fil) in (list, tuple):
        for f in fil:
            if f in keys:
                return True
    else:
        if fil in keys:
            return True


def _filter_command(command, text):
    if type(command) in (list, tuple):
        for cmd in command:
            if text.startswith('/%s' % cmd):
                return True

    elif text.startswith('/%s' % command):
        return True


def _filter_equal(fil, from_id):
    if type(fil) in (list, tuple):
        for f in fil:
            if f == from_id:
                return True
    elif fil == from_id:
        return True


def _filtering(up):
    key1 = tuple(up.keys())[1]
    up = up[key1]
    filter_keys = list(up.keys()) + [key1]
    if 'entities' in up:
        for ent in up['entities']:
            filter_keys.append(ent['type'])

    for func in _funcs_list:
        f = _funcs_list[func]
        if 'from' in up:
            if f['from_id'] and not _filter_equal(f['from_id'],
                                                  up['from']['id']):
                continue
            if 'chat' in up:
                if f['chat_id'] and not _filter_equal(f['chat_id'],
                                                      up['chat']['id']):
                    continue
                if f['chat_type'] and not _filter_equal(
                        f['chat_type'],
                        up['chat']['type']):
                    continue

        if f['not_on'] and _filter_key(f['not_on'], filter_keys):
            continue

        if f['filters'] and not _filter_key(f['filters'], filter_keys):
            continue

        if f['command']:
            if 'text' in up:
                if not _filter_command(f['command'], up['text']):
                    continue
            else:
                continue

        if f['regex']:
            pattern = re.compile(f['regex'])
            if 'text' in up:
                if not pattern.search(up['text']):
                    continue
            elif 'caption' in up:
                if not pattern.search(up['caption']):
                    continue
            else:
                continue

        if f['callback_query']:
            if 'callback_query' in filter_keys:
                pattern = re.compile(f['callback_query'])
                if not pattern.search(up['data']):
                    continue
            else:
                continue

        if f['inline_query']:
            if 'inline_query' in filter_keys:
                pattern = re.compile(f['inline_query'])
                if not pattern.search(up['query']):
                    continue
            else:
                continue
        try:
            func(up)
        except TypeError as ex:
            _error(ex)


def bot_run(offset_=None, multi=None, limit=None,
            timeout=10, allowed_updates=None
            ):
    """
    :param offset_: (:obj:`bool`, optional) True to handle only new updates
    :param multi: (:obj:`bool`, optional) True to run in Threading mode
    :param limit: (:obj:`int`, optional) Limits the number of updates
     to be retrieved. Values between 1—100 are accepted. Defaults to 100.
    :param timeout: (:obj:`int`, optional) timeout for the getUpdates
    10 seconds by default
    :param allowed_updates: (:obj:`list`, optional) List the types of
     updates you want your bot to receive. For example, specify [“message”,
     “edited_channel_post”, “callback_query”] to only receive updates of
     these types. See Update for a complete list of available update types.
     Specify an empty list to receive all updates regardless of type
     (default). If not specified, the previous setting will be used.
    """
    if not _API:
        raise Exception('You need to insert token to "account" function')

    if offset_:
        try:
            # Delete all previous updates
            get_updates(offset=get_updates(offset=-1,
                                           timeout=0)[-1]['update_id'] + 1)
        except IndexError:
            pass

    offset = None

    if multi:
        while True:
            updates = getUpdates(offset=offset, limit=limit, timeout=timeout,
                                 allowed_updates=allowed_updates)
            if updates:
                for up in updates:
                    Thread(target=_filtering, args=(up,)).start()
                offset = updates[-1]['update_id'] + 1

    while True:
        updates = getUpdates(offset=offset, limit=limit, timeout=timeout,
                             allowed_updates=allowed_updates)
        if updates:
            for up in updates:
                _filtering(up)
            offset = updates[-1]['update_id'] + 1


_API = None


def account(token=None):
    if not token:
        raise Exception('no token')
    global _API
    _API = 'https://api.telegram.org/bot%s/' % token
    return _API


# camelCase aliases and docstring

getMe = get_me
"""
    information
    :return  Returns basic information about the bot in form of a User object:
"""
getUpdates = get_updates
"""
    :param offset: (:obj:`int`, optional) Identifier of the first
     update to be returned. Must be greater by one than the
     highest among the identifiers of previously received
     updates. By default, updates starting with the earliest
     unconfirmed update are returned. An update is considered
     confirmed as soon as getUpdates is called with an offset
     higher than its update_id. The negative offset can be
     specified to retrieve updates starting from -offset
     update from the end of the updates queue.
     All previous updates will forgotten.
    :param limit: (:obj:`int`, optional) Limits the number of
     updates to be retrieved. Values between 1—100 are
     accepted. Defaults to 100.
    :param allowed_updates: (:obj:`Array of String`, optional) List
     the types of updates you want your bot to
     receive. For example,  specify [“message”, “edited_channel_post”,
     “callback_query”] to only receive updates of these types. See
     Update for a complete list of available update types. Specify
     an empty list to receive all updates regardless of type (default).
     If not specified, the previous setting will be used. Please
     note that this parameter doesn't affect updates created before
     the call to the getUpdates, so unwanted updates may be
     received for a short period of time.
    :param timeout: (:obj:`int`, optional) Timeout in seconds for
     long polling. Defaults to 0, i.e. usual short polling. Should
     be positive, short polling should be used for testing purposes

"""

sendMessage = send_message
"""
    :param chat_id: (:obj:`int`)
     Unique identifier for the target chat or
     username of the target channel (in the format @channelusername)
    :param text: (:obj:`str`) Text of the message to be sent
    :param parse_mode: (:obj:`str`, optional)  Send Markdown or HTML,
     if you want Telegram apps to show bold, italic, fixed-width text
      or inline URLs in your bot's message.
    :param disable_web_page_preview: (:obj:`bool`, optional)  Disables link
     previews for links in this message
    :param disable_notification: (:obj:`bool`, optional)  Sends the message
     silently. Users will receive a notification with no sound.
    :param reply_to_message_id: (:obj:`int`, optional)  If the message is a
     reply, ID of the original message
    :param reply_markup: (:obj:`InlineKeyboardMarkup`,
     :obj:`ReplyKeyboardMarkup`, :obj:`ReplyKeyboardRemove`, :obj:`ForceReply`,
     optional)  Additional interface options. A JSON-serialized object for an
     inline keyboard, custom reply keyboard, instructions to remove reply
     keyboard or to force a reply from the user.
"""
forwardMessage = forward_message
"""
    :param chat_id: (:obj:`int`)
     Unique identifier for the target chat or
     username of the target channel (in the format @channelusername)
    :param from_chat_id: (:obj:`int`) Unique identifier for the chat where the
     original message was sent (or channel username in the format
     @channelusername)
    :param message_id: (:obj:`int`) Message identifier in the chat specified in
     from_chat_id

    :param disable_notification: (:obj:`bool`, optional)  Sends the message
     silently. Users will receive a notification with no sound.
    :param update: (:obj:`update`, optional) getUpdates results. instead of
     entering from_chat_id and message_id
"""
sendPhoto = send_photo
"""

    :param chat_id: (:obj:`int`)
     Unique identifier for the target chat or
     username of the target channel (in the format @channelusername)
    :param file: (:obj:`str`) Photo to send. Pass a file_id as String to send a
     photo that exists on the Telegram servers (recommended), pass an HTTP URL
     as a String for Telegram to get a photo from the Internet, or upload a new
     photo using multipart/form-data.

    :param caption: (:obj:`str`, optional)  Photo caption (may also be used
     when resending photos by file_id), 0-1024 characters
    :param reply_to_message_id: (:obj:`int`, optional)  If the message is a
     reply, ID of the original message
    :param parse_mode: (:obj:`str`, optional)  Send Markdown or HTML, if you
     want Telegram apps to show bold, italic, fixed-width text or inline URLs
     in your bot's message.
    :param disable_web_page_preview: (:obj:`bool`, optional)  Disables link
     previews for links in this message
    :param disable_notification: (:obj:`bool`, optional)  Sends the message
     silently. Users will receive a notification with no sound.
    :param reply_markup: (:obj:`InlineKeyboardMarkup`,
     :obj:`ReplyKeyboardMarkup`, :obj:`ReplyKeyboardRemove`, :obj:`ForceReply`,
     optional)  Additional interface options. A JSON-serialized object for an
     inline keyboard, custom reply keyboard, instructions to remove reply
     keyboard or to force a reply from the user.
"""
sendAudio = send_audio
"""

    :param chat_id: (:obj:`int`)
     Unique identifier for the target chat or
     username of the target channel (in the format @channelusername)
    :param file: (:obj:`str`) Audio file to send. Pass a file_id as String to
     send an audio file that exists on the Telegram servers (recommended), pass
     an HTTP URL as a String for Telegram to get an audio file from the
     Internet, or upload a new one using multipart/form-data.
    :param caption: (:obj:`str`, optional) Audio caption, 0-1024 characters
    :param parse_mode: (:obj:`str`, optional)  Send Markdown or HTML, if you
     want Telegram apps to show bold, italic, fixed-width text or inline URLs
     in your bot's message.
    :param duration: (:obj:`int`, optional)  Duration of the audio in seconds
    :param performer: (:obj:`str`, optional)  Performer
    :param title: (:obj:`str`, optional) Track name
    :param thumb: (:obj:`str`, optional) Thumbnail of the file sent. path file
     | file_id | url
"""
sendDocument = send_document
"""

    :param chat_id: (:obj:`int`)
     Unique identifier for the target chat or
     username of the target channel (in the format @channelusername)
    :param file: (:obj:`str`) path file | file_id | url
    :param caption: (:obj:`str`, optional) Document caption (may also be used
     when resending documents by file_id), 0-1024 characters
    :param thumb: (:obj:`str`, optional) Thumbnail of the file sent. path file
     | file_id | url
    :param reply_to_message_id: (:obj:`int`, optional)  If the message is a
     reply, ID of the original message
    :param parse_mode: (:obj:`str`, optional)  Send Markdown or HTML, if you
     want Telegram apps to show bold, italic, fixed-width text or inline URLs
     in your bot's message.
    :param disable_web_page_preview: (:obj:`bool`, optional)  Disables link
     previews for links in this message
    :param disable_notification: (:obj:`bool`, optional)  Sends the message
     silently. Users will receive a notification with no sound.
    :param reply_markup: (:obj:`InlineKeyboardMarkup`,
     :obj:`ReplyKeyboardMarkup`, :obj:`ReplyKeyboardRemove`, :obj:`ForceReply`,
     optional)  Additional interface options. A JSON-serialized object for an
     inline keyboard, custom reply keyboard, instructions to remove reply
     keyboard or to force a reply from the user.
"""
sendVideo = send_video
"""

    :param chat_id: (:obj:`int`)
     Unique identifier for the target chat or
     username of the target channel (in the format @channelusername)
    :param file: (:obj:`str`) path file | file_id | url. Video to send.Pass a
     file_id as String to send a video that exists on the Telegram servers
     (recommended), pass an HTTP URL as a String for Telegram to get a video
     from the Internet, or upload a new video using multipart/form-data
    :param duration: (:obj:`int`, optional) Duration of the video in seconds
    :param width: (:obj:`int`, optional) Video width
    :param height: (:obj:`int`, optional) Video height
    :param thumb: (:obj:`str`, optional) Thumbnail of the file sent. path file
     | file_id | url
    :param caption: (:obj:`str`, optional) Video caption (may also be used when
     resending videos by file_id), 0-1024 characters
    :param parse_mode: (:obj:`str`, optional)  Send Markdown or HTML, if you
     want Telegram apps to show bold, italic, fixed-width text or inline URLs
     in your bot's message.
    :param supports_streaming: (:obj:`bool`, optional) Pass True, if the
     uploaded video is suitable for streaming
    :param disable_notification: (:obj:`bool`, optional)  Sends the message
     silently. Users will receive a notification with no sound.
    :param reply_to_message_id: (:obj:`int`, optional)  If the message is a
     reply, ID of the original message
    :param reply_markup: (:obj:`InlineKeyboardMarkup`,
     :obj:`ReplyKeyboardMarkup`, :obj:`ReplyKeyboardRemove`, :obj:`ForceReply`,
     optional)  Additional interface options. A JSON-serialized object for an
     inline keyboard, custom reply keyboard, instructions to remove reply
     keyboard or to force a reply from the user.
"""
sendAnimation = send_animation
"""

    :param chat_id: (:obj:`int`)
     Unique identifier for the target chat or
     username of the target channel (in the format @channelusername)
    :param file: (:obj:`str`) Animation to send. Pass a file_id as String to
     send an animation that exists on the Telegram servers (recommended), pass
     an HTTP URL as a String for Telegram to get an animation from the
     Internet, or upload a new animation using multipart/form-data
    :param duration: (:obj:`int`, optional)  Duration of sent animation in
     seconds
    :param width: (:obj:`int`, optional) Animation width
    :param height: (:obj:`int`, optional) Animation height
    :param thumb: (:obj:`str`, optional) Thumbnail of the file sent. path file
     | file_id | url
    :param caption: (:obj:`str`, optional) Animation caption (may also be used
     when resending animation by file_id), 0-1024 characters
    :param parse_mode: (:obj:`str`, optional)  Send Markdown or HTML, if you
     want Telegram apps to show bold, italic, fixed-width text or inline URLs
     in your bot's message.
    :param disable_notification: (:obj:`bool`, optional)  Sends the message
     silently. Users will receive a notification with no sound.
    :param reply_to_message_id: (:obj:`int`, optional)  If the message is a
     reply, ID of the original message
    :param reply_markup: (:obj:`InlineKeyboardMarkup`,
     :obj:`ReplyKeyboardMarkup`, :obj:`ReplyKeyboardRemove`, :obj:`ForceReply`,
     optional)  Additional interface options. A JSON-serialized object for an
     inline keyboard, custom reply keyboard, instructions to remove reply
     keyboard or to force a reply from the user.
"""
sendVoice = send_voice
"""

    :param chat_id: (:obj:`int`)
     Unique identifier for the target chat or
     username of the target channel (in the format @channelusername)
    :param file: (:obj:`str`) Audio file to send. Pass a file_id as String to
     send a file that exists on the Telegram servers (recommended), pass an
     HTTP URL as a String for Telegram to get a file from the Internet, or
     upload a new one using multipart/form-data.
    :param caption: (:obj:`str`, optional) Voice message caption, 0-1024
     characters
    :param parse_mode: (:obj:`str`, optional)  Send Markdown or HTML, if you
     want Telegram apps to show bold, italic, fixed-width text or inline URLs
     in your bot's message.
    :param duration: (:obj:`int`, optional) Duration of the voice message in
     seconds
    :param disable_notification: (:obj:`bool`, optional)  Sends the message
     silently. Users will receive a notification with no sound.
    :param reply_to_message_id: (:obj:`int`, optional)  If the message is a
     reply, ID of the original message
    :param reply_markup: (:obj:`InlineKeyboardMarkup`,
     :obj:`ReplyKeyboardMarkup`, :obj:`ReplyKeyboardRemove`, :obj:`ForceReply`,
     optional)  Additional interface options. A JSON-serialized object for an
     inline keyboard, custom reply keyboard, instructions to remove reply
     keyboard or to force a reply from the user.
"""
sendVideoNote = send_video_note
"""

    :param chat_id: (:obj:`int`)
     Unique identifier for the target chat or
     username of the target channel (in the format @channelusername)
    :param file: (:obj:`str`) Video note to send. Pass a file_id as String to
     send a video note that exists on the Telegram servers (recommended) or
     upload a new video using multipart/form-data
    :param duration: (:obj:`str`, optional) Duration of sent video in seconds
    :param length: (:obj:`int`, optional) Video width and height, i.e. diameter
     of the video message
    :param thumb: (:obj:`str`, optional) Thumbnail of the file sent. path file
     | file_id | url
    :param disable_notification: (:obj:`bool`, optional)  Sends the message
     silently. Users will receive a notification with no sound.
    :param reply_to_message_id: (:obj:`int`, optional)  If the message is a
     reply, ID of the original message
    :param reply_markup: (:obj:`InlineKeyboardMarkup`,
     :obj:`ReplyKeyboardMarkup`, :obj:`ReplyKeyboardRemove`, :obj:`ForceReply`,
     optional)  Additional interface options. A JSON-serialized object for an
     inline keyboard, custom reply keyboard, instructions to remove reply
     keyboard or to force a reply from the user.
"""
sendMediaGroup = send_media_group
"""

    :param chat_id: (:obj:`int`)
     Unique identifier for the target chat or
     username of the target channel (in the format @channelusername)
    :param media: (:obj:`Array of InputMediaPhoto` :obj:`InputMediaVideo`) A
     JSON-serialized array describing photos and videos to be sent, must
     include 2–10 items
    :param disable_notification: (:obj:`bool`, optional)  Sends the message
     silently. Users will receive a notification with no sound.
    :param reply_to_message_id: (:obj:`int`, optional)  If the message is a
     reply, ID of the original message
"""
sendLocation = send_location
"""

    :param chat_id: (:obj:`int`)
     Unique identifier for the target chat or
     username of the target channel (in the format @channelusername)
    :param latitude: (:obj:`float`) Latitude of the location
    :param longitude: (:obj:`float`) longitude of the location
    :param live_period: (:obj:`int`, optional) Period in seconds for which
     the location will be updated (see Live Locations, should be between 60 and
     86400.
    :param disable_notification: (:obj:`bool`, optional)  Sends the message
     silently. Users will receive a notification with no sound.
    :param reply_to_message_id: (:obj:`int`, optional)  If the message is a
     reply, ID of the original message
    :param reply_markup: (:obj:`InlineKeyboardMarkup`,
     :obj:`ReplyKeyboardMarkup`, :obj:`ReplyKeyboardRemove`, :obj:`ForceReply`,
     optional)  Additional interface options. A JSON-serialized object for an
     inline keyboard, custom reply keyboard, instructions to remove reply
     keyboard or to force a reply from the user.
"""
editMessageLiveLocation = edit_message_live_location
"""

    :param chat_id: (:obj:`int`)
     Unique identifier for the target chat or
     username of the target channel (in the format @channelusername)
    :param message_id: (:obj:`int`) Message identifier in the chat specified in
     from_chat_id
    :param inline_message_id: (:obj:`str`, optional) Required if chat_id and
     message_id are not specified. Identifier of the inline message
    :param latitude: (:obj:`float`) Latitude of new location
    :param longitude: (:obj:`float`) longitude of new location
    :param reply_markup: (:obj:`InlineKeyboardMarkup`,
     :obj:`ReplyKeyboardMarkup`, :obj:`ReplyKeyboardRemove`, :obj:`ForceReply`,
     optional)  Additional interface options. A JSON-serialized object for an
     inline keyboard, custom reply keyboard, instructions to remove reply
     keyboard or to force a reply from the user.
    :param update: (:obj:`update`, optional) getUpdates results. instead of
     entering from_chat_id and message_id
"""
stopMessageLiveLocation = stop_message_live_location
"""

    :param chat_id: (:obj:`int`)
     Unique identifier for the target chat or
     username of the target channel (in the format @channelusername)
    :param message_id: (:obj:`int`) Required if inline_message_id is not
     specified. Identifier of the sent message
    :param inline_message_id: (:obj:`str`, optional) Required if chat_id
     and message_id are not specified. Identifier of the inline message
    :param reply_markup: (:obj:`InlineKeyboardMarkup`,
     :obj:`ReplyKeyboardMarkup`, :obj:`ReplyKeyboardRemove`, :obj:`ForceReply`,
     optional)  Additional interface options. A JSON-serialized object for an
     inline keyboard, custom reply keyboard, instructions to remove reply
     keyboard or to force a reply from the user.
    :param update: (:obj:`update`, optional) getUpdates results. instead of
     entering from_chat_id and message_id
"""
sendVenue = send_venue
"""

    :param chat_id: (:obj:`int`)
     Unique identifier for the target chat or
     username of the target channel (in the format @channelusername)
    :param latitude: (:obj:`float`) Latitude of the venue
    :param longitude: (:obj:`float`) Longitude of the venue
    :param title: (:obj:`str`) Name of the venue
    :param address: (:obj:`str`, optional) Address of the venue
    :param foursquare_id: (:obj:`str`, optional) Foursquare identifier of the
     venue
    :param foursquare_type: (:obj:`str`, optional) Foursquare type of the
     venue, if known. (For example, “arts_entertainment/default”,
     “arts_entertainment/aquarium” or “food/icecream”.)
    :param disable_notification: (:obj:`bool`, optional)  Sends the message
     silently.
    :param reply_to_message_id: (:obj:`int`, optional)  If the message is a
     reply, ID of the original message
    :param reply_markup: (:obj:`InlineKeyboardMarkup`,
     :obj:`ReplyKeyboardMarkup`, :obj:`ReplyKeyboardRemove`, :obj:`ForceReply`,
     optional)  Additional interface options. A JSON-serialized object for an
     inline keyboard, custom reply keyboard, instructions to remove reply
     keyboard or to force a reply from the user.
"""
sendContact = send_contact
"""

    :param chat_id: (:obj:`int`)
     Unique identifier for the target chat or
     username of the target channel (in the format @channelusername)
    :param phone_number: (:obj:`str`) Contact's phone number
    :param first_name: (:obj:`str`) Contact's first name
    :param last_name: (:obj:`str`, optional) Contact's last name
    :param vcard: (:obj:`str`, optional) Additional data about the contact in
     the form of a vCard, 0-2048 bytes
    :param disable_notification: (:obj:`bool`, optional)  Sends the message
     silently. Users will receive a notification with no sound.
    :param reply_to_message_id: (:obj:`int`, optional)  If the message is a
     reply, ID of the original message
    :param reply_markup: (:obj:`InlineKeyboardMarkup`,
     :obj:`ReplyKeyboardMarkup`, :obj:`ReplyKeyboardRemove`, :obj:`ForceReply`,
     optional)  Additional interface options. A JSON-serialized object for an
     inline keyboard, custom reply keyboard, instructions to remove reply
     keyboard or to force a reply from the user.
"""
sendChatAction = send_chat_action
"""

    :param chat_id: (:obj:`int`)
     Unique identifier for the target chat or
     username of the target channel (in the format @channelusername)
    :param action: (:obj:`str`) Type of action to broadcast. Choose one,
     depending on what the user is about to receive: typing for text messages,
     upload_photo for photos, record_video or upload_video for videos,
     record_audio or upload_audio for audio files, upload_document for general
     files, find_location for location data, record_video_note or
     upload_video_note for video notes.
"""

sendPoll = send_poll
"""
    :param chat_id: (:obj:`int`)
     Unique identifier for the target chat or
     username of the target channel (in the format @channelusername)
    :param question: (:obj:`str`) Poll question, 1-255 characters
    :param options: (:obj:`Array of String`) List of answer options, 2-10
     strings 1-100 characters each
    :param disable_notification: (:obj:`bool`, optional)  Sends the message
     silently. Users will receive a notification with no sound.
    :param reply_to_message_id: (:obj:`int`, optional)  If the message is a
     reply, ID of the original message
    :param reply_markup: (:obj:`InlineKeyboardMarkup`,
     :obj:`ReplyKeyboardMarkup`, :obj:`ReplyKeyboardRemove`, :obj:`ForceReply`,
     optional)  Additional interface options. A JSON-serialized object for an
     inline keyboard, custom reply keyboard, instructions to remove reply
     keyboard or to force a reply from the user.
"""

getUserProfilePhotos = get_user_profile_photos
"""

    :param user_id: (:obj:`int`)  Unique identifier of the target user
    :param offset: (:obj:`int`, optional) Sequential number of the first photo
     to be returned. By default, all photos are returned.
    :param limit: (:obj:`int`, optional) Limits the number of photos to be
     retrieved. Values between 1—100 are accepted. Defaults to 100.
"""
getFile = get_file
"""

    :param file_id: (:obj:`str`) File identifier to get info about
"""
kickChatMember = kick_chat_member
"""

    :param chat_id: (:obj:`int`)
     Unique identifier for the target chat or
     username of the target channel (in the format @channelusername)
    :param user_id: (:obj:`int`)  Unique identifier of the target user
    :param until_date: (:obj:`int`, optional) Date when the user will
     be unbanned, unix time. If user is banned for more than 366 days or less
     than 30 seconds from the current time they are considered to be banned
     forever
"""
unbanChatMember = unban_chat_member
"""

    :param chat_id: (:obj:`int`)
     Unique identifier for the target chat or
     username of the target channel (in the format @channelusername)
    :param user_id: (:obj:`int`)  Unique identifier of the target user
"""
restrictChatMember = restrict_chat_member
"""

    :param chat_id: (:obj:`int`)
     Unique identifier for the target chat or
     username of the target channel (in the format @channelusername)
    :param user_id: (:obj:`int`)  Unique identifier of the target user
    :param until_date: (:obj:`int`, optional) Date when restrictions will be
     lifted for the user, unix time. If user is restricted for more than 366
     days or less than 30 seconds from the current time, they are considered to
     be restricted forever
    :param can_send_messages: (:obj:`bool`, optional) Pass True, if the user
     can send text messages, contacts, locations and venues
    :param can_send_media_messages: (:obj:`bool`, optional) Pass True, if the
     user can send audios, documents, photos, videos, video notes and voice
     notes, implies can_send_messages
    :param can_send_other_messages: (:obj:`bool`, optional) Pass True, if the
     user can send animations, games, stickers and use inline bots,
     implies can_send_media_messages
    :param can_add_web_page_previews: (:obj:`bool`, optional)  Pass True, if
     the user may add web page previews to their messages, implies
     can_send_media_messages

"""
promoteChatMember = promote_chat_member
"""

    :param chat_id: (:obj:`int`)
     Unique identifier for the target chat or
     username of the target channel (in the format @channelusername)
    :param user_id: (:obj:`int`)  Unique identifier of the target user
    :param can_change_info: (:obj:`bool`, optional) Pass True, if the
     administrator can change chat title, photo and other settings
    :param can_post_messages: (:obj:`bool`, optional) Pass True, if the
     administrator can create channel posts, channels only
    :param can_edit_messages: (:obj:`bool`, optional) Pass True, if the
     administrator can edit messages of other users and can pin messages,
     channels only
    :param can_delete_messages: (:obj:`bool`, optional) Pass True, if the
     administrator
    :param can_invite_users: (:obj:`bool`, optional) Pass True, if the
     administrator can invite new users to the chat
    :param can_restrict_members: (:obj:`bool`, optional) Pass True, if the
     administrator can restrict, ban or unban chat members
    :param can_pin_messages: (:obj:`bool`, optional) Pass True, if the
     administrator can pin messages, supergroups only
    :param can_promote_members: (:obj:`bool`, optional) Pass True, if the
     administrator can add new administrators with a subset of his own
     privileges or demote administrators that he has promoted, directly or
     indirectly (promoted by administrators that were appointed by him)
"""
exportChatInviteLink = export_chat_invite_link
"""

    :param chat_id: (:obj:`int`)
     Unique identifier for the target chat or
     username of the target channel (in the format @channelusername)
"""
setChatPhoto = set_chat_photo
"""

    :param chat_id: (:obj:`int`)
     Unique identifier for the target chat or
     username of the target channel (in the format @channelusername)
    :param photo: (:obj:`str`) path file | file_id | url .New chat photo,
     uploaded using multipart/form-data
"""
deleteChatPhoto = delete_chat_photo
"""

    :param chat_id: (:obj:`int`)
     Unique identifier for the target chat or
     username of the target channel (in the format @channelusername)
"""
setChatTitle = set_chat_title
"""

    :param chat_id: (:obj:`int`)
     Unique identifier for the target chat or
     username of the target channel (in the format @channelusername)
    :param title: (:obj:`str`) New chat title, 1-255 characters
"""
setChatDescription = set_chat_description
"""

    :param chat_id: (:obj:`int`)
     Unique identifier for the target chat or
     username of the target channel (in the format @channelusername)
    :param description: (:obj:`str`, optional) New chat description, 0-255
     characters

"""
pinChatMessage = pin_chat_message
"""

    :param chat_id: (:obj:`int`)
     Unique identifier for the target chat or
     username of the target channel (in the format @channelusername)
    :param message_id: (:obj:`int`) Identifier of a message to pin
    :param disable_notification: (:obj:`bool`, optional)  Sends the message
     silently. Users will receive a notification with no sound.
"""
unpinChatMessage = unpin_chat_message
"""

    :param chat_id: (:obj:`int`)
     Unique identifier for the target chat or
     username of the target channel (in the format @channelusername)
"""
leaveChat = leave_chat
"""

    :param chat_id: (:obj:`int`)
     Unique identifier for the target chat or
     username of the target channel (in the format @channelusername)
"""
getChat = get_chat
"""

    :param chat_id: (:obj:`int`)
     Unique identifier for the target chat or
     username of the target channel (in the format @channelusername)
"""
getChatAdministrators = get_chat_administrators
"""

    :param chat_id: (:obj:`int`)
     Unique identifier for the target chat or
     username of the target channel (in the format @channelusername)
"""
getChatMembersCount = get_chat_members_count
"""

    :param chat_id: (:obj:`int`)
     Unique identifier for the target chat or
     username of the target channel (in the format @channelusername)
"""
getChatMember = get_chat_member
"""

    :param chat_id: (:obj:`int`)
     Unique identifier for the target chat or
     username of the target channel (in the format @channelusername)
    :param user_id: (:obj:`int`)  Unique identifier of the target user
"""
setChatStickerSet = set_chat_sticker_set
"""

    :param chat_id: (:obj:`int`)
     Unique identifier for the target chat or
     username of the target channel (in the format @channelusername)
    :param sticker_set_name:
"""
deleteChatStickerSet = delete_chat_sticker_set
"""

    :param chat_id: (:obj:`int`)
     Unique identifier for the target chat or
     username of the target channel (in the format @channelusername)
"""
answerCallbackQuery = answer_callback_query
"""

    :param callback_query_id:
    :param text: (:obj:`str`, optional) Text of the notification. If not
     specified, nothing will be shown to the user, 0-200 characters
    :param show_alert: (:obj:`bool`, optional) If true, an alert will be shown
     by the client instead of a notification at the top of the chat screen.
     Defaults to false.
    :param url: (:obj:`str`, optional) URL that will be opened by the user's
     client. If you have created a Game and accepted the conditions via
     @Botfather, specify the URL that opens your game – note that this will
     only work if the query comes from
     a callback_game button. Otherwise, you may use links like
     t.me/your_bot?start=XXXX that open your bot with a parameter.
    :param cache_time: (:obj:`int`, optional) The maximum amount of time in
     seconds that the result of the callback query may be cached client-side.
     Telegram apps will support caching starting in version 3.14. Defaults to 0
"""
editMessageText = edit_message_text
"""

    :param chat_id: (:obj:`int`)
     Unique identifier for the target chat or
     username of the target channel (in the format @channelusername)
    :param message_id: (:obj:`int`) Required if inline_message_id is not
     specified. Identifier of the sent message
    :param inline_message_id: (:obj:`str`, optional) Required if chat_id and
     message_id are not specified. Identifier of the inline message
    :param text: (:obj:`str`) Text of the message to be sent
    :param parse_mode: (:obj:`str`, optional)  Send Markdown or HTML, if you
     want Telegram apps to show bold, italic, fixed-width text or inline URLs
     in your bot's message.
    :param disable_web_page_preview: (:obj:`bool`, optional)  Disables link
     previews for links in this message
    :param reply_markup: (:obj:`InlineKeyboardMarkup`,
     :obj:`ReplyKeyboardMarkup`, :obj:`ReplyKeyboardRemove`, :obj:`ForceReply`,
     optional)  Additional interface options. A JSON-serialized object for an
     inline keyboard, custom reply keyboard, instructions to remove reply
     keyboard or to force a reply from the user.
    :param update: (:obj:`update`, optional) getUpdates results. instead of
     entering from_chat_id and message_id
"""
editMessageCaption = edit_message_caption
"""

    :param chat_id: (:obj:`int`)
     Unique identifier for the target chat or
     username of the target channel (in the format @channelusername)
    :param message_id: (:obj:`int`) Required if inline_message_id is not
     specified. Identifier of the sent message
    :param inline_message_id: (:obj:`str`, optional) Required if
     chat_id and message_id are not specified. Identifier of the inline message
    :param caption: (:obj:`str`, optional) New caption of the message
    :param parse_mode: (:obj:`str`, optional)  Send Markdown or HTML, if you
     want Telegram apps to show bold, italic, fixed-width text or inline URLs
     in your bot's message.
    :param reply_markup: (:obj:`InlineKeyboardMarkup`,
     :obj:`ReplyKeyboardMarkup`, :obj:`ReplyKeyboardRemove`, :obj:`ForceReply`,
     optional)  Additional interface options. A JSON-serialized object for an
     inline keyboard, custom reply keyboard, instructions to remove reply
     keyboard or to force a reply from the user.
    :param update: (:obj:`update`, optional) getUpdates results. instead of
     entering from_chat_id and message_id
"""
editMessageMedia = edit_message_media
"""

    :param chat_id: (:obj:`int`)
     Unique identifier for the target chat or
     username of the target channel (in the format @channelusername)
    :param message_id: (:obj:`int`) Required if inline_message_id is not
     specified. Identifier of the sent message
    :param inline_message_id: (:obj:`str`, optional) Required if chat_id and
     message_id are not specified. Identifier of the inline message
    :param media: (:obj:`InputMedia`) A JSON-serialized object for a new media
     content of the message
    :param reply_markup: (:obj:`InlineKeyboardMarkup`,
     :obj:`ReplyKeyboardMarkup`, :obj:`ReplyKeyboardRemove`, :obj:`ForceReply`,
     optional)  Additional interface options. A JSON-serialized object for an
     inline keyboard, custom reply keyboard, instructions to remove reply
     keyboard or to force a reply from the user.
    :param update: (:obj:`update`, optional) getUpdates results. instead of
     entering from_chat_id and message_id
"""
editMessageReplyMarkup = edit_message_reply_markup
"""

    :param chat_id: (:obj:`int`)
     Unique identifier for the target chat or
     username of the target channel (in the format @channelusername)
    :param message_id: (:obj:`int`) Required if inline_message_id is not
     specified. Required if inline_message_id is not specified. Identifier of
     the sent message
    :param inline_message_id: (:obj:`str`, optional) Required if chat_id and
     message_id are not specified. Identifier of the inline message
    :param reply_markup: (:obj:`InlineKeyboardMarkup`,
     :obj:`ReplyKeyboardMarkup`, :obj:`ReplyKeyboardRemove`, :obj:`ForceReply`,
     optional)  Additional interface options. A JSON-serialized object for an
     inline keyboard, custom reply keyboard, instructions to remove reply
     keyboard or to force a reply from the user.
    :param update: (:obj:`update`, optional) getUpdates results. instead of
     entering from_chat_id and message_id
"""
stopPoll = stop_poll
"""
    :param chat_id: (:obj:`int`)
     Unique identifier for the target chat or
     username of the target channel (in the format @channelusername)
    :param message_id: (:obj:`int`) Identifier of the original message with
     the poll
    :param reply_markup: (:obj:`InlineKeyboardMarkup`,
     :obj:`ReplyKeyboardMarkup`, :obj:`ReplyKeyboardRemove`, :obj:`ForceReply`,
     optional)  Additional interface options. A JSON-serialized object for an
     inline keyboard, custom reply keyboard, instructions to remove reply
     keyboard or to force a reply from the user.
"""
deleteMessage = delete_message
"""

    :param chat_id: (:obj:`int`)
     Unique identifier for the target chat or
     username of the target channel (in the format @channelusername)
    :param message_id: (:obj:`int`) Identifier of the message to delete
    :param update: (:obj:`update`, optional) getUpdates results. instead of
     entering from_chat_id and message_id
"""
sendSticker = send_sticker
"""

    :param chat_id: (:obj:`int`)
     Unique identifier for the target chat or
     username of the target channel (in the format @channelusername)
    :param file: (:obj:`str`) Sticker to send. Pass a file_id as String to send
     a file that exists on the Telegram servers (recommended), pass an HTTP URL
     as a String for Telegram to get a .webp file from the Internet, or upload
     a new one using multipart/form-data.
    :param disable_notification: (:obj:`bool`, optional)  Sends the message
     silently. Users will receive a notification with no sound.
    :param reply_to_message_id: (:obj:`int`, optional)  If the message is a
     reply, ID of the original message
    :param reply_markup: (:obj:`InlineKeyboardMarkup`,
     :obj:`ReplyKeyboardMarkup`, :obj:`ReplyKeyboardRemove`, :obj:`ForceReply`,
     optional)  Additional interface options. A JSON-serialized object for an
     inline keyboard, custom reply keyboard, instructions to remove reply
     keyboard or to force a reply from the user.
"""
getStickerSet = get_sticker_set
"""

    :param name: (:obj:`str`) Name of the sticker set
"""
uploadStickerFile = upload_sticker_file
"""

    :param user_id: (:obj:`int`)  Unique identifier of the target user
    :param file: (:obj:`str`) Png image with the sticker, must be up to 512
     kilobytes in size, dimensions must not exceed 512px, and either width or
     height must be exactly 512px.
"""
createNewStickerSet = create_new_sticker_set
"""

    :param user_id: (:obj:`int`)  Unique identifier of the target user
    :param name: (:obj:`str`) Short name of sticker set, to be used in
     t.me/addstickers/ URLs (e.g., animals). Can contain only english letters,
     digits and underscores. Must begin with a letter, can't contain
     consecutive underscores and must end in “_by_<bot username>”.
     <bot_username> is case insensitive. 1-64 characters.
    :param title: (:obj:`str`) Sticker set title, 1-64 characters
    :param file: (:obj:`str`) Png image with the sticker, must be up to 512
     kilobytes in size, dimensions must not exceed 512px, and either width or
     height must be exactly 512px. Pass a file_id as a String to send a file
     that already exists on the Telegram servers, pass an HTTP URL as a String
     for Telegram to get a file from the Internet, or upload a new one using
     multipart/form-data. More info on Sending Files »
    :param emojis: (:obj:`str`) One or more emoji corresponding to the sticker
    :param contains_masks: (:obj:`bool`, optional) Pass True, if a set of mask
     stickers should be created
    :param mask_position: (:obj:`MaskPosition`, optional) A JSON-serialized
     object for position where the mask should be placed on faces
"""
addStickerToSet = add_sticker_to_set
"""

    :param user_id: (:obj:`int`)  Unique identifier of the target user
    :param name: (:obj:`str`) Sticker set name
    :param file: (:obj:`str`) Png image with the sticker, must be up to 512
     kilobytes in size, dimensions must not exceed 512px, and either width or
     height must be exactly 512px. Pass a file_id as a String to send a file
     that already exists on the Telegram servers, pass an HTTP URL as a String
     for Telegram to get a file from the Internet, or upload a new one using
     multipart/form-data.
    :param emojis: (:obj:`str`) One or more emoji corresponding to the sticker
    :param mask_position: (:obj:`MaskPosition`, optional) A JSON-serialized
     object for position where the mask should be placed on faces
"""
setStickerPositionInSet = set_sticker_position_in_set
"""

    :param sticker: (:obj:`str`) File identifier of the sticker
    :param position: (:obj:`int`) New sticker position in the set, zero-based
"""
deleteStickerFromSet = delete_sticker_from_set
"""

    :param sticker: (:obj:`str`) File identifier of the sticker
"""
answerInlineQuery = answer_inline_query
"""

    :param update: (:obj:`update`, optional) getUpdates results. instead of
     entering from_chat_id and message_id
    :param results: (:obj:`InlineQueryResult`) A JSON-serialized array of
     results for the inline query
    :param cache_time: (:obj:`int`, optional) The maximum amount of time in
     seconds that the result of the inline query may be cached on the server.
     Defaults to 300.
    :param is_personal: (:obj:`bool`, optional) Pass True, if results may be
     cached on the server side only for the user that sent the query. By
     default, results may be returned to any user who sends the same query
    :param next_offset: (:obj:`str`, optional) Pass the offset that a client
     should send in the next query with the same text to receive more results.
     Pass an empty string if there are no more results or if you don‘t support
     pagination. Offset length can’t exceed 64 bytes.
    :param switch_pm_text: (:obj:`str`, optional) If passed, clients will
     display a button with specified text that switches the user to a private
     chat with the bot and sends the bot a start message with the parameter
     switch_pm_parameter
    :param switch_pm_parameter: (:obj:`str`, optional) Deep-linking parameter
     for the /start message sent to the bot when user presses the switch
     button. 1-64 characters, only A-Z, a-z, 0-9, _ and - are allowed. Example:
     An inline bot that sends YouTube videos can ask the user to connect the
     bot to their YouTube account to adapt search results accordingly. To do
     this, it displays a ‘Connect your YouTube account’ button above the
     results, or even before showing any. The user presses the button, switches
     to a private chat with the bot and, in doing so, passes a start parameter
     that instructs the bot to return an oauth link. Once done, the bot can
     offer a switch_inline button so that the user can easily return to the
     chat where they wanted to use the bot's inline capabilities.
     InlineQueryResult
"""
InlineQueryResultArticle = inline_query_result_article

"""

    :param id: (:obj:`str`)  Unique identifier for this result, 1-64 Bytes
    :param title: (:obj:`str`) Title of the result
    :param input_message_content: (:obj:`input_message_content`)  Unique
     identifier for this result, 1-64 Bytes
    :param reply_markup: (:obj:`InlineKeyboardMarkup`,
     :obj:`ReplyKeyboardMarkup`, :obj:`ReplyKeyboardRemove`, :obj:`ForceReply`,
     optional)  Additional interface options. A JSON-serialized object for an
     inline keyboard, custom reply keyboard, instructions to remove reply
     keyboard or to force a reply from the user.
    :param url: (:obj:`str`) Optional. URL of the result
    :param hide_url: (:obj:`bool`) Optional. Pass True, if you don't want the
     URL to be shown in the message
    :param description: (:obj:`str`) Optional. Short description of the result
    :param thumb_url: (:obj:`str`) Optional. Url of the thumbnail for the
     result
    :param thumb_width: (:obj:`int`) Optional. Thumbnail width
    :param thumb_height: (:obj:`int`) Optional. Thumbnail height
"""
InlineQueryResultPhoto = inline_query_result_photo
"""

    :param id: (:obj:`str`)  Unique identifier for this result, 1-64 Bytes
    :param photo_url: (:obj:`str`) A valid URL of the photo. Photo must be in
     jpeg format. Photo size must not exceed 5MB
    :param thumb_url: (:obj:`str`)  URL of the thumbnail for the photo
    :param photo_width: (:obj:`int`) Optional. Width of the photo
    :param photo_height: (:obj:`int`) Optional. Height of the photo
    :param title:  (:obj:`str`)    Optional. Title for the result
    :param description: (:obj:`str`) Optional. Short description of the result
    :param caption: (:obj:`str`)  Optional. Caption of the photo to be sent,
     0-1024 characters
    :param parse_mode: (:obj:`str`, optional)  Send Markdown or HTML, if you
     want Telegram apps to show bold, italic, fixed-width text or inline URLs
     in your bot's message.
    :param reply_markup: (:obj:`InlineKeyboardMarkup`,
     :obj:`ReplyKeyboardMarkup`, :obj:`ReplyKeyboardRemove`, :obj:`ForceReply`,
     optional)  Additional interface options. A JSON-serialized object for an
     inline keyboard, custom reply keyboard, instructions to remove reply
     keyboard or to force a reply from the user.
    :param input_message_content: (:obj:`input_message_content`, optional)
     Unique identifier for this result, 1-64 Bytes
"""
InlineQueryResultGif = inline_query_result_gif
"""

    :param id: (:obj:`str`)  Unique identifier for this result, 1-64 Bytes
    :param gif_url: (:obj:`str`) A valid URL for the GIF file. File size must
     not exceed 1MB
    :param gif_width: (:obj:`int`)  Optional. Width of the GIF
    :param gif_height: (:obj:`int`) Optional. Height of the GIF
    :param gif_duration: (:obj:`int`) Optional. Duration of the GIF
    :param thumb_url: (:obj:`str`) URL of the static thumbnail for the result
     (jpeg or gif)
    :param title: (:obj:`str`) Optional. Title for the result
    :param caption: (:obj:`str`) Optional. Caption of the GIF file to be sent,
     0-1024 characters
    :param parse_mode: (:obj:`str`, optional)  Send Markdown or HTML, if you
     want Telegram apps to show bold, italic, fixed-width text or inline URLs
     in your bot's message.
    :param reply_markup: (:obj:`InlineKeyboardMarkup`,
     :obj:`ReplyKeyboardMarkup`, :obj:`ReplyKeyboardRemove`, :obj:`ForceReply`,
     optional)  Additional interface options. A JSON-serialized object for an
     inline keyboard, custom reply keyboard, instructions to remove reply
     keyboard or to force a reply from the user.
    :param input_message_content: (:obj:`input_message_content`, optional)
     Unique identifier for this result, 1-64 Bytes
"""
InlineQueryResultMpeg4Gif = inline_query_result_mpeg4_gif
"""

    :param id: (:obj:`str`)  Unique identifier for this result, 1-64 Bytes
    :param mpeg4_url: (:obj:`str`) A valid URL for the MP4 file. File size must
     not exceed 1MB
    :param mpeg4_width: (:obj:`int`) Optional. Video width
    :param mpeg4_height: (:obj:`int`) Optional. Video height
    :param mpeg4_duration: (:obj:`int`) Optional. Video duration
    :param thumb_url: (:obj:`str`) URL of the static thumbnail (jpeg or gif)
     for the result
    :param title: (:obj:`str`) Optional. Title for the result
    :param caption: (:obj:`str`)  Optional. Caption of the MPEG-4 file to be
     sent, 0-1024 characters
    :param parse_mode: (:obj:`str`, optional)  Send Markdown or HTML, if you
     want Telegram apps to show bold, italic, fixed-width text or inline URLs
     in your bot's message.
    :param reply_markup: (:obj:`InlineKeyboardMarkup`,
     :obj:`ReplyKeyboardMarkup`, :obj:`ReplyKeyboardRemove`, :obj:`ForceReply`,
     optional)  Additional interface options. A JSON-serialized object for an
     inline keyboard, custom reply keyboard, instructions to remove reply
     keyboard or to force a reply from the user.
    :param input_message_content: (:obj:`input_message_content`, optional)
     Unique identifier for this result, 1-64 Bytes
"""
InlineQueryResultVideo = inline_query_result_video
"""

    :param id: (:obj:`str`)  Unique identifier for this result, 1-64 Bytes
    :param video_url: (:obj:`str`)    A valid URL for the embedded video player
     or video file
    :param mime_type: (:obj:`str`) Mime type of the content of video url,
     “text/html” or “video/mp4”
    :param thumb_url: (:obj:`str`)     URL of the thumbnail (jpeg only) for the
     video
    :param title: (:obj:`str`) Title for the result
    :param caption: (:obj:`str`) Optional. Caption of the video to be sent,
     0-1024 characters
    :param parse_mode: (:obj:`str`, optional)  Send Markdown or HTML, if you
     want Telegram apps to show bold, italic, fixed-width text or inline URLs
     in your bot's message.
    :param video_width: (:obj:`int`) Optional. Video width
    :param video_height: (:obj:`int`) Optional. Video height
    :param video_duration: (:obj:`int`) Optional. Video duration in seconds
    :param description: (:obj:`str`) Optional. Short description of the result
    :param reply_markup: (:obj:`InlineKeyboardMarkup`,
     :obj:`ReplyKeyboardMarkup`, :obj:`ReplyKeyboardRemove`, :obj:`ForceReply`,
     optional)  Additional interface options. A JSON-serialized object for an
     inline keyboard, custom reply keyboard, instructions to remove reply
     keyboard or to force a reply from the user.
    :param input_message_content: (:obj:`input_message_content`, optional)
     Unique identifier for this result, 1-64 Bytes
"""
InlineQueryResultAudio = inline_query_result_audio
"""

    :param id: (:obj:`str`)  Unique identifier for this result, 1-64 Bytes
    :param audio_url: (:obj:`str`) A valid URL for the audio file
    :param title: (:obj:`str`) Title
    :param caption: (:obj:`str`) Optional. Caption, 0-1024 characters
    :param parse_mode: (:obj:`str`, optional)  Send Markdown or HTML, if you
     want Telegram apps to show bold, italic, fixed-width text or inline URLs
     in your bot's message.
    :param performer: (:obj:`str`) Optional. Performer
    :param audio_duration: (:obj:`int`) Optional. Audio duration in seconds
    :param reply_markup: (:obj:`InlineKeyboardMarkup`,
     :obj:`ReplyKeyboardMarkup`, :obj:`ReplyKeyboardRemove`, :obj:`ForceReply`,
     optional)  Additional interface options. A JSON-serialized object for an
     inline keyboard, custom reply keyboard, instructions to remove reply
     keyboard or to force a reply from the user.
    :param input_message_content: (:obj:`input_message_content`, optional)
     Unique identifier for this result, 1-64 Bytes
"""
InlineQueryResultVoice = inline_query_result_voice
"""

    :param id: (:obj:`str`)  Unique identifier for this result, 1-64 Bytes
    :param voice_url: (:obj:`str`) A valid URL for the voice recording
    :param title: (:obj:`str`) Recording title
    :param caption: (:obj:`str`) Optional. Caption, 0-1024 characters
    :param parse_mode: (:obj:`str`, optional)  Send Markdown or HTML, if you
     want Telegram apps to show bold, italic, fixed-width text or inline URLs
     in your bot's message.
    :param voice_duration: (:obj:`int`) Optional. Recording duration in seconds
    :param reply_markup: (:obj:`InlineKeyboardMarkup`,
     :obj:`ReplyKeyboardMarkup`, :obj:`ReplyKeyboardRemove`, :obj:`ForceReply`,
     optional)  Additional interface options. A JSON-serialized object for an
     inline keyboard, custom reply keyboard, instructions to remove reply
     keyboard or to force a reply from the user.
    :param input_message_content: (:obj:`input_message_content`, optional)
     Unique identifier for this result, 1-64 Bytes
"""
InlineQueryResultDocument = inline_query_result_document
"""

    :param id: (:obj:`str`)  Unique identifier for this result, 1-64 Bytes
    :param title: (:obj:`str`) Title for the result
    :param caption: (:obj:`str`) Optional. Caption of the document to be sent,
     0-1024 characters
    :param parse_mode: (:obj:`str`, optional)  Send Markdown or HTML, if you
     want Telegram apps to show bold, italic, fixed-width text or inline URLs
     in your bot's message.
    :param document_url: (:obj:`str`) A valid URL for the file
    :param mime_type: (:obj:`str`) Mime type of the content of the file, either
     “application/pdf” or “application/zip”
    :param description: (:obj:`str`) Optional. Short description of the result
    :param reply_markup: (:obj:`InlineKeyboardMarkup`,
     :obj:`ReplyKeyboardMarkup`, :obj:`ReplyKeyboardRemove`, :obj:`ForceReply`,
     optional)  Additional interface options. A JSON-serialized object for an
     inline keyboard, custom reply keyboard, instructions to remove reply
     keyboard or to force a reply from the user.
    :param input_message_content: (:obj:`input_message_content`, optional)
     Unique identifier for this result, 1-64 Bytes
    :param thumb_url: (:obj:`str`) Optional. URL of the thumbnail (jpeg only)
     for the file
    :param thumb_width: (:obj:`int`) Optional. Thumbnail width
    :param thumb_height: (:obj:`int`) Optional. Thumbnail height
"""
InlineQueryResultLocation = inline_query_result_location
"""

    :param id: (:obj:`str`)  Unique identifier for this result, 1-64 Bytes
    :param latitude: (:obj:`float`) Location latitude in degrees
    :param longitude: (:obj:`float`) Location longitude in degrees
    :param title: (:obj:`str`) Location title
    :param live_period: (:obj:`int`) Optional. Period in seconds for which the
     location can be updated, should be between 60 and 86400.
    :param reply_markup: (:obj:`InlineKeyboardMarkup`,
     :obj:`ReplyKeyboardMarkup`, :obj:`ReplyKeyboardRemove`, :obj:`ForceReply`,
     optional)  Additional interface options. A JSON-serialized object for an
     inline keyboard, custom reply keyboard, instructions to remove reply
     keyboard or to force a reply from the user.
    :param input_message_content: (:obj:`input_message_content`, optional)
     Unique identifier for this result, 1-64 Bytes
    :param thumb_url: (:obj:`str`) Optional. Url of the thumbnail for the
      result
    :param thumb_width: (:obj:`int`) Optional. Thumbnail width
    :param thumb_height: (:obj:`int`) Optional. Thumbnail height
"""
InlineQueryResultVenue = inline_query_result_venue
"""

    :param id: (:obj:`str`)  Unique identifier for this result, 1-64 Bytes
    :param latitude: (:obj:`float`) Latitude of the venue location in degrees
    :param longitude: (:obj:`float`) Longitude of the venue location in degrees
    :param title: (:obj:`str`) Title of the venue
    :param address: (:obj:`str`) Address of the venue
    :param foursquare_id: (:obj:`str`) Optional. Foursquare identifier of the
     venue if known
    :param reply_markup: (:obj:`InlineKeyboardMarkup`,
     :obj:`ReplyKeyboardMarkup`, :obj:`ReplyKeyboardRemove`, :obj:`ForceReply`,
     optional)  Additional interface options. A JSON-serialized object for an
     inline keyboard, custom reply keyboard, instructions to remove reply
     keyboard or to force a reply from the user.
    :param input_message_content: (:obj:`input_message_content`, optional)
     Unique identifier for this result, 1-64 Bytes
    :param thumb_url: (:obj:`str`) Optional. Url of the thumbnail for the
     result
    :param thumb_width: (:obj:`int`) Optional. Thumbnail width
    :param thumb_height: (:obj:`int`) Optional. Thumbnail height
"""
InlineQueryResultContact = inline_query_result_contact
"""

    :param id: (:obj:`str`)  Unique identifier for this result, 1-64 Bytes
    :param phone_number: (:obj:`str`) Contact's phone number
    :param first_name: (:obj:`str`) Contact's first name
    :param last_name: (:obj:`str`) Optional. Contact's last name
    :param vcard: (:obj:`str`) Optional. Additional data about the contact in
     the form of a vCard, 0-2048 bytes
    :param reply_markup: (:obj:`InlineKeyboardMarkup`,
     :obj:`ReplyKeyboardMarkup`, :obj:`ReplyKeyboardRemove`, :obj:`ForceReply`,
     optional)  Additional interface options. A JSON-serialized object for an
     inline keyboard, custom reply keyboard, instructions to remove reply
     keyboard or to force a reply from the user.
    :param input_message_content: (:obj:`input_message_content`, optional)
     Unique identifier for this result, 1-64 Bytes
    :param thumb_url: Optional. Url of the thumbnail for the result
    :param thumb_width: (:obj:`int`) Optional. Thumbnail width
    :param thumb_height: (:obj:`int`) Optional. Thumbnail height
"""
InlineQueryResultGame = inline_query_result_game
"""

    :param id: (:obj:`str`)  Unique identifier for this result, 1-64 Bytes
    :param game_short_name: (:obj:`str`)      Short name of the game
    :param reply_markup: (:obj:`InlineKeyboardMarkup`,
     :obj:`ReplyKeyboardMarkup`, :obj:`ReplyKeyboardRemove`, :obj:`ForceReply`,
     optional)  Additional interface options. A JSON-serialized object for an
     inline keyboard, custom reply keyboard, instructions to remove reply
     keyboard or to force a reply from the user.
"""
InlineQueryResultCachedPhoto = inline_query_result_cached_photo
"""

    :param id: (:obj:`str`)  Unique identifier for this result, 1-64 Bytes
    :param photo_file_id: (:obj:`str`)  A valid file identifier of the photo
    :param title: (:obj:`str`)  Optional. Title for the result
    :param description: (:obj:`str`)  Optional. Short description of the result
    :param caption: (:obj:`str`)  Optional. Caption of the photo to be sent,
     0-1024 characters
    :param parse_mode: (:obj:`str`, optional)  Send Markdown or HTML, if you
     want Telegram apps to show bold, italic, fixed-width text or inline URLs
     in your bot's message.
    :param reply_markup: (:obj:`InlineKeyboardMarkup`,
     :obj:`ReplyKeyboardMarkup`, :obj:`ReplyKeyboardRemove`, :obj:`ForceReply`,
     optional)  Additional interface options. A JSON-serialized object for an
     inline keyboard, custom reply keyboard, instructions to remove reply
     keyboard or to force a reply from the user.
    :param input_message_content: (:obj:`input_message_content`, optional)
     Unique identifier for this result, 1-64 Bytes
"""
InlineQueryResultCachedGif = inline_query_result_cached_gif
"""

    :param id: (:obj:`str`)  Unique identifier for this result, 1-64 Bytes
    :param gif_file_id: A valid file identifier for the GIF file
    :param title: (:obj:`str`)     Optional. Title for the result
    :param caption: (:obj:`str`) Optional. Caption of the GIF file to be sent,
     0-1024 characters
    :param parse_mode: (:obj:`str`, optional)  Send Markdown or HTML, if you
     want Telegram apps to show bold, italic, fixed-width text or inline URLs
     in your bot's message.
    :param reply_markup: (:obj:`InlineKeyboardMarkup`,
     :obj:`ReplyKeyboardMarkup`, :obj:`ReplyKeyboardRemove`, :obj:`ForceReply`,
     optional)  Additional interface options. A JSON-serialized object for an
     inline keyboard, custom reply keyboard, instructions to remove reply
     keyboard or to force a reply from the user.
    :param input_message_content: (:obj:`input_message_content`, optional)
     Unique identifier for this result, 1-64 Bytes
"""
InlineQueryResultCachedMpeg4Gif = inline_query_result_cached_mpeg4_gif
"""

    :param id: (:obj:`str`)  Unique identifier for this result, 1-64 Bytes
    :param mpeg4_file_id: (:obj:`str`) A valid file identifier for the MP4 file
    :param title: (:obj:`str`) Optional. Title for the result
    :param caption: (:obj:`str`) Optional. Caption of the MPEG-4 file to be
     sent, 0-1024 characters
    :param parse_mode: (:obj:`str`, optional)  Send Markdown or HTML, if you
     want Telegram apps to show bold, italic, fixed-width text or inline URLs
     in your bot's message.
    :param reply_markup: (:obj:`InlineKeyboardMarkup`,
     :obj:`ReplyKeyboardMarkup`, :obj:`ReplyKeyboardRemove`, :obj:`ForceReply`,
     optional)  Additional interface options. A JSON-serialized object for an
     inline keyboard, custom reply keyboard, instructions to remove reply
     keyboard or to force a reply from the user.
    :param input_message_content: (:obj:`input_message_content`, optional)
     Unique identifier for this result, 1-64 Bytes
"""
InlineQueryResultCachedSticker = inline_query_result_cached_sticker
"""

    :param id: (:obj:`str`)  Unique identifier for this result, 1-64 Bytes
    :param sticker_file_id: (:obj:`str`) A valid file identifier of the sticker
    :param reply_markup: (:obj:`InlineKeyboardMarkup`,
     :obj:`ReplyKeyboardMarkup`, :obj:`ReplyKeyboardRemove`, :obj:`ForceReply`,
     optional)  Additional interface options. A JSON-serialized object for an
     inline keyboard, custom reply keyboard, instructions to remove reply
     keyboard or to force a reply from the user.
    :param input_message_content: (:obj:`input_message_content`, optional)
     Unique identifier for this result, 1-64 Bytes
"""
InlineQueryResultCachedDocument = inline_query_result_cached_document
"""

    :param id: (:obj:`str`)  Unique identifier for this result, 1-64 Bytes
    :param title: (:obj:`str`) Title for the result
    :param document_file_id: (:obj:`str`) A valid file identifier for the file
    :param description: (:obj:`str`) Optional. Short description of the result
    :param caption: (:obj:`str`) Optional. Caption of the document to be sent,
     0-1024 characters
    :param parse_mode: (:obj:`str`, optional)  Send Markdown or HTML, if you
     want Telegram apps to show bold, italic, fixed-width text or inline URLs
     in your bot's message.
    :param reply_markup: (:obj:`InlineKeyboardMarkup`,
     :obj:`ReplyKeyboardMarkup`, :obj:`ReplyKeyboardRemove`, :obj:`ForceReply`,
     optional)  Additional interface options. A JSON-serialized object for an
     inline keyboard, custom reply keyboard, instructions to remove reply
     keyboard or to force a reply from the user.
    :param input_message_content: (:obj:`input_message_content`, optional)
     Unique identifier for this result, 1-64 Bytes
"""
InlineQueryResultCachedVideo = inline_query_result_cached_video
"""

    :param id: (:obj:`str`)  Unique identifier for this result, 1-64 Bytes
    :param video_file_id: (:obj:`str`) A valid file identifier for the video
     file
    :param title: (:obj:`str`) Title for the result
    :param description: (:obj:`str`) Optional. Short description of the result
    :param caption: (:obj:`str`) Optional. Caption of the video to be sent,
     0-1024 characters
    :param parse_mode: (:obj:`str`, optional)  Send Markdown or HTML, if you
     want Telegram apps to show bold, italic, fixed-width text or inline URLs
     in your bot's message.
    :param reply_markup: (:obj:`InlineKeyboardMarkup`,
     :obj:`ReplyKeyboardMarkup`, :obj:`ReplyKeyboardRemove`, :obj:`ForceReply`,
     optional)  Additional interface options. A JSON-serialized object for an
     inline keyboard, custom reply keyboard, instructions to remove reply
     keyboard or to force a reply from the user.
    :param input_message_content: (:obj:`input_message_content`, optional)
     Unique identifier for this result, 1-64 Bytes
"""
InlineQueryResultCachedVoice = inline_query_result_cached_voice
"""

    :param id: (:obj:`str`)  Unique identifier for this result, 1-64 Bytes
    :param voice_file_id: (:obj:`str`) A valid file identifier for the voice
     message
    :param title: (:obj:`str`) Voice message title
    :param caption: (:obj:`str`) Optional. Caption, 0-1024 characters
    :param parse_mode: (:obj:`str`, optional)  Send Markdown or HTML, if you
     want Telegram apps to show bold, italic, fixed-width text or inline URLs
     in your bot's message.
    :param reply_markup: (:obj:`InlineKeyboardMarkup`,
     :obj:`ReplyKeyboardMarkup`, :obj:`ReplyKeyboardRemove`, :obj:`ForceReply`,
     optional)  Additional interface options. A JSON-serialized object for an
     inline keyboard, custom reply keyboard, instructions to remove reply
     keyboard or to force a reply from the user.
    :param input_message_content: (:obj:`input_message_content`, optional)
     Unique identifier for this result, 1-64 Bytes
"""
InlineQueryResultCachedAudio = inline_query_result_cached_audio
"""

    :param id: (:obj:`str`)  Unique identifier for this result, 1-64 Bytes
    :param audio_file_id: (:obj:`str`) A valid file identifier for the audio
     file
    :param caption: (:obj:`str`) Optional. Caption, 0-1024 characters
    :param parse_mode: (:obj:`str`, optional)  Send Markdown or HTML, if you
     want Telegram apps to show bold, italic, fixed-width text or inline URLs
     in your bot's message.
    :param reply_markup: (:obj:`InlineKeyboardMarkup`,
     :obj:`ReplyKeyboardMarkup`, :obj:`ReplyKeyboardRemove`, :obj:`ForceReply`,
     optional)  Additional interface options. A JSON-serialized object for an
     inline keyboard, custom reply keyboard, instructions to remove reply
     keyboard or to force a reply from the user.
     :param input_message_content: (:obj:`input_message_content`, optional)
      Unique identifier for this result, 1-64 Bytes
"""
InputTextMessageContent = input_text_message_content
"""

    :param message_text: (:obj:`str`) Text of the message to be sent, 1-4096
     characters
    :param parse_mode: (:obj:`str`, optional)  Send Markdown or HTML, if you
     want Telegram apps to show bold, italic, fixed-width text or inline URLs
     in your bot's message.
    :param disable_web_page_preview : (:obj:`bool`)  Optional. Disables link
     previews for links in the sent message
"""
InputLocationMessageContent = input_location_message_content
"""

    :param latitude: (:obj:`float`) Latitude of the location in degrees
    :param longitude: (:obj:`float`) Longitude of the location in degrees
    :param live_period: (:obj:`int`) Optional. Period in seconds for which the
     location can be updated, should be between 60 and 86400.
"""
InputVenueMessageContent = input_venue_message_content
"""

    :param latitude: (:obj:`float`) Latitude of the venue in degrees
    :param longitude: (:obj:`float`) Longitude of the venue in degrees
    :param title: (:obj:`str`) Name of the venue
    :param address: (:obj:`str`) Address of the venue
    :param foursquare_id: (:obj:`str`) Optional. Foursquare identifier of the
     venue, if known
    :param foursquare_type: (:obj:`str`) Optional. Foursquare type of the
     venue, if known. (For example, “arts_entertainment/default”,
     “arts_entertainment/aquarium” or “food/icecream”.)
"""
InputContactMessageContent = input_contact_message_content
"""
    :param phone_number: (:obj:`str`) Contact's phone number
    :param first_name: (:obj:`str`) Contact's first name
    :param last_name: (:obj:`str`) Optional. Contact's last name
    :param vcard: (:obj:`str`) Optional. Additional data about the contact in
     the form of a vCard, 0-2048 bytes
"""
chosenInlineResult = chosen_inline_result
"""
    :param result_id: (:obj:`str`) The unique identifier for the result that
     was chosen
    :param from_user:  (:obj:`User`) The user that chose the result
    :param location: (:obj:`Location`) Optional. Sender location, only for bots
     that require user location
    :param inline_message_id: (:obj:`str`) Optional. Identifier of the sent
     inline message. Available only if there is an inline keyboard attached to
     the message. Will be also received in callback queries and can be used to
     edit the message.
    :param query: (:obj:`str`) The query that was used to obtain the result
"""
InputMediaPhoto = input_media_photo
"""

    :param media: (:obj:`str`) File to send. Pass a file_id to send a file that
     exists on the Telegram servers (recommended), pass an HTTP URL for
     Telegram to get a file from the Internet, or pass
     “attach://<file_attach_name>” to upload a new one using
     multipart/form-data under <file_attach_name> name.
    :param caption: (:obj:`str`) Optional. Caption of the photo to be sent,
     0-1024 characters
    :param parse_mode: (:obj:`str`, optional)  Send Markdown or HTML, if you
     want Telegram apps to show bold, italic, fixed-width text or inline URLs
     in your bot's message.
"""
InputMediaVideo = input_media_video
"""
    :param media: (:obj:`str`) File to send. Pass a file_id to send a file that
     exists on the Telegram servers (recommended), pass an HTTP URL for
     Telegram to get a file from the Internet, or pass
     “attach://<file_attach_name>” to upload a new one using
     multipart/form-data under
    :param thumb: (:obj:`str`, :obj:`InputFile`) Optional. Thumbnail of the
     file sent; can be ignored if thumbnail generation for the file is
     supported erver-side. The thumbnail should be in JPEG format and less than
     200 kB in size. A thumbnail‘s width and height should not exceed 90.
     Ignored if the file is not uploaded using multipart/form-data. Thumbnails
     can’t be reused and can be only uploaded as a new file, so you can pass
     “attach://<file_attach_name>” if the thumbnail was uploaded using
     multipart/form-data under <file_attach_name>
    :param caption: (:obj:`str`) Optional. Caption of the video to be sent,
     0-1024 characters
    :param parse_mode: (:obj:`str`, optional)  Send Markdown or HTML, if you
     want Telegram apps to show bold, italic, fixed-width text or inline URLs
     in your bot's message.
    :param width: (:obj:`int`) Optional. Video width
    :param height: (:obj:`int`)  Optional. Video height
    :param duration: (:obj:`int`)  Optional. Video duration
    :param supports_streaming: (:obj:`bool`) Optional. Pass True, if the
     uploaded video is suitable for streaming
"""
InputMediaAnimation = input_media_animation
"""

    :param media: (:obj:`str`) File to send. Pass a file_id to send a file that
     exists on the Telegram servers (recommended), pass an HTTP URL for
     Telegram to get a file from the Internet, or pass
     “attach://<file_attach_name>” to upload a new one using
      multipart/form-data under <file_attach_name> name.
    :param thumb: (:obj:`str`, :obj:`InputFile`) Optional. Thumbnail of the
     file sent; can be ignored if thumbnail generation for the file is
     supported server-side. The thumbnail should be in JPEG format and less
     than 200 kB in size. A thumbnail‘s width and height should not exceed 90.
     Ignored if the file is not uploaded using multipart/form-data. Thumbnails
     can’t be reused and can be only uploaded as a new file, so you can pass
     “attach://<file_attach_name>” if the thumbnail was uploaded using
     multipart/form-data under <file_attach_name>.
    :param caption: (:obj:`str`) Optional. Caption of the animation to be sent,
     0-1024 characters
    :param parse_mode: (:obj:`str`, optional)  Send Markdown or HTML, if you
     want Telegram apps to show bold, italic, fixed-width text or inline URLs
     in your bot's message.
    :param width: (:obj:`int`) Optional. Animation width
    :param height: (:obj:`int`) Optional. Animation height
    :param duration: (:obj:`int`) Optional. Animation duration
"""
InputMediaAudio = input_media_audio
"""

    :param media: (:obj:`str`) File to send. Pass a file_id to send a file that
     exists on the Telegram servers (recommended), pass an HTTP URL for
     Telegram to get a file from the Internet, or pass
     “attach://<file_attach_name>” to upload a new one using
     multipart/form-data under <file_attach_name> name.
    :param thumb: (:obj:`str`, :obj:`InputFile`) Optional. Thumbnail of the
     file sent; can be ignored if thumbnail generation for the file is
     supported server-side. The thumbnail should be in JPEG format and less
     than 200 kB in size. A thumbnail‘s width and height should not exceed 90.
     Ignored if the file is not uploaded using multipart/form-data. Thumbnails
     can’t be reused and can be only uploaded as a new file, so you can pass
     “attach://<file_attach_name>” if the thumbnail was uploaded
     using multipart/form-data under <file_attach_name>.
    :param caption: (:obj:`str`) Optional. Caption of the audio to be sent,
     0-1024 characters
    :param parse_mode: (:obj:`str`, optional)  Send Markdown or HTML, if you
     want Telegram apps to show bold, italic, fixed-width text or inline URLs
     in your bot's message.
    :param duration: (:obj:`int`) Optional. Duration of the audio in seconds
    :param performer: (:obj:`str`) Optional. Performer of the audio
    :param title: (:obj:`str`) Optional. Title of the audio
"""
InputMediaDocument = input_media_document
"""

    :param media: (:obj:`str`) File to send. Pass a file_id to send a file that
     exists on the Telegram servers (recommended), pass an HTTP URL for
     Telegram to get a file from the Internet, or pass
     “attach://<file_attach_name>” to upload a new one using
     multipart/form-data under <file_attach_name> name.
    :param thumb: (:obj:`str`, :obj:`InputFile`) Optional. Thumbnail of the
     file sent; can be ignored if thumbnail generation for the file is
     supported server-side. The thumbnail should be in JPEG format and less
     than 200 kB in size. A thumbnail‘s width and height should not exceed 90.
     Ignored if the file is not uploaded using multipart/form-data. Thumbnails
     can’t be reused and can be only uploaded as a new file, so you can pass
     “attach://<file_attach_name>” if the thumbnail was uploaded using
     multipart/form-data under <file_attach_name>.
    :param caption: (:obj:`str`) Optional. Caption of the document to be sent,
     0-1024 characters
    :param parse_mode: (:obj:`str`, optional)  Send Markdown or HTML, if you
     want Telegram apps to show bold, italic, fixed-width text or inline URLs
     in your bot's message.
"""

ReplyKeyboardMarkup = reply_keyboard_markup
Keyboard = reply_keyboard_markup
"""

    :param k: Array of KeyboardButton see examples here:
     https://gitlab.com/2411eliko/tele/blob/master/Examples/keyboard_and_inlinekeyboard.md
    :param resize_keyboard: (:obj:`bool`) Optional. Requests clients
     to resize the keyboard vertically for optimal fit (e.g., make the
     keyboard smaller if there are just two rows of buttons). Defaults
     to false, in which case the custom keyboard is always of the same
     height as the app's standard keyboard.
    :param one_time_keyboard: (:obj:`bool`) Optional. Requests clients
     to hide the keyboard as soon as it's been used. The keyboard will
     still be available, but clients will automatically display the usual
     letter-keyboard in the chat – the user can press a
     special button in the input field to see the custom keyboard
     again. Defaults to false.
    :param num_line: ** optional ** number of buttons in each line.
    :param remove: (:obj:`bool`) optional. Requests clients to remove
     the custom keyboard (user will not be able to summon this keyboard;
     if you want to hide the keyboard from sight but keep it accessible,
     use one_time_keyboard in ReplyKeyboardMarkup)
    """

ReplyKeyboardRemove = reply_keyboard_remove

InlineKeyboardMarkup = inline_keyboard
InlineKeyboard = inline_keyboard
"""

    :param k: Array of InlineKeyboardButton see examples here:
     https://gitlab.com/2411eliko/tele/blob/master/Examples/keyboard_and_inlinekeyboard.md
    :param num_line: ** optional ** number of buttons in each line.
    :param obj: type of the button can be: "url", "callback_data",
     "switch_inline_query", "switch_inline_query_current_chat",
     "callback_game" . see here:
     https://core.telegram.org/bots/api#inlinekeyboardbutton
    """

ForceReply = force_reply
"""
    :param selective: (:obj:`bool`, optional)
"""

