import datetime

from .base import TelegramEndpoint


class KickChatMember(TelegramEndpoint):
    def __init__(self, chat_id, user_id):
        args = {
            'chat_id': chat_id,
            'user_id': user_id
        }
        super().__init__(args=args)

    def until_date(self, date):
        self.args['until_date'] = date
        return self

    def forever(self):
        self.args['until_date'] = (datetime.datetime.utcnow() + datetime.timedelta(days=369)).timestamp()
        return self


class UnbanChatMember(TelegramEndpoint):
    def __init__(self, chat_id, user_id):
        args = {
            'chat_id': chat_id,
            'user_id': user_id
        }
        super().__init__(args=args)


class RestrictChatMember(TelegramEndpoint):
    def __init__(self, chat_id, user_id):
        args = {
            'chat_id': chat_id,
            'user_id': user_id
        }
        super().__init__(args=args)

    def until_date(self, date):
        self.args['until_date'] = date
        return self

    def can_send_messages(self):
        self.args['can_send_messages'] = True
        return self

    def can_send_media_messages(self):
        self.args['can_send_media_messages'] = True
        return self

    def can_send_other_messages(self):
        self.args['can_send_other_messages'] = True
        return self

    def can_add_web_page_previews(self):
        self.args['can_add_web_page_previews'] = True
        return self


class PromoteChatMember(TelegramEndpoint):
    def __init__(self, chat_id, user_id):
        args = {
            'chat_id': chat_id,
            'user_id': user_id
        }
        super().__init__(args=args)

    def can_change_info(self):
        self.args['can_change_info'] = True
        return self

    def can_post_messages(self):
        self.args['can_post_messages'] = True
        return self

    def can_edit_messages(self):
        self.args['can_edit_messages'] = True
        return self

    def can_delete_messages(self):
        self.args['can_delete_messages'] = True
        return self

    def can_invite_users(self):
        self.args['can_invite_users'] = True
        return self

    def can_restrict_members(self):
        self.args['can_restrict_members'] = True
        return self

    def can_pin_messages(self):
        self.args['can_pin_messages'] = True
        return self

    def can_promote_members(self):
        self.args['can_promote_members'] = True
        return self
