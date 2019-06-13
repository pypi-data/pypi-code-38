from bson import ObjectId
from coolsignup.conf import conf
from coolsignup.emails import mailer
from coolsignup.new_password_validator import NewPasswordValidator, PASSWORD_MAX_LENGTH
from coolsignup.signing import (
    create_signed_document, DecodeSignedDocument, DecodeSignedString,
    create_signed_string, decode_signed_string
)
from naval import (
    ValidationError, Schema, Email, Type, Length,
    Save, SaveAs, Do, Assert, Optional, Each, Regex
)
from passlib.hash import bcrypt
from postpone import LazyString as _, evalr
from pymongo.errors import DuplicateKeyError
import time
import uuid

class Response(object):
    def __init__(self, dct, status = 200):
        self.dct = dct
        self.status = status

    def translate(self, lang):
        if 'error' in self.dct:
            self.dct['error'] = evalr(self.dct['error'], conf.translation_func(lang))

class Sch(Schema):

    def __init__(self, *args, success_key = "success", **kwargs):
        super(Sch, self).__init__(*args, **kwargs)
        self.success_key = success_key

    def __call__(self, func):
        async def new_func(clear_document, *args, **kwargs):
            try:
                validated_document = self.run(clear_document)
            except ValidationError as exc:
                if clear_document.get('authToken') and 'authToken' in exc.error_details:
                    error_status = 403
                else:
                    error_status = 400
                return Response(
                    {self.success_key: False, "error": exc.error_details},
                    status = error_status
                )
            else:
                return await func(validated_document, *args, **kwargs)
        return new_func

email_used_result = {
    "success": False, "error": _("This email address already belongs to a registered account.")
}

async def email_exists(email, case_sensitive):
    if case_sensitive:
        filter = {"email": email}
    else:
        filter = {"emailLower": email.lower()}
    result = await conf.mongo_accounts.find_one(filter)
    return bool(result)

@Sch(['email', Email])
async def send_registration_code(document, lang):
    email = document['email']
    if await email_exists(email, case_sensitive = False):
        return Response(email_used_result)
    else:
        code = create_signed_document({
            'action': 'firstRegistration',
            'email': email
        })
        mailer.send_registration_code(
            code,
            email,
            lang = lang
        )
        return Response({"success": True})

DecodeEmailCode = DecodeSignedDocument(
    max_age_days = conf.get('codeDurationSeconds') / 86400.0
)

RegistrationCode = Do(
    Type(str),
    Length(min = 1, max = 2000),
    DecodeEmailCode,
    Schema(
        ['email', Email],
        ['action', ('firstRegistration',)]
    )
)

@Sch(['code', RegistrationCode, SaveAs('decoded')])
async def check_registration_code(document):
    if await email_exists(document['decoded']['email'], case_sensitive = False):
        return Response(email_used_result)
    else:
        return Response({"success": True})

@Sch(
    ['registrationCode', RegistrationCode, SaveAs('decoded')],
    ['password',
        NewPasswordValidator,
        bcrypt.hash,
        Save
    ]
)
async def register(document):
    email = document['decoded']['email']
    email_lower = email.lower()
    password = document['password']
    try:
        insert_one_result = await conf.mongo_accounts.insert_one({
            'emailLower': email_lower,
            'email': email,
            'password': password,
            'active': False
        })
    except DuplicateKeyError:
        return Response(email_used_result)
    else:
        return Response({
            "success": True,
            "_id": str(insert_one_result.inserted_id)
        })

UserIdValidator = Do(Type(str), Length(1, 200), Assert(str.isalnum))

@Sch(["_id", UserIdValidator, ObjectId, Save])
async def activate_user(document):
    return await _set_active(document['_id'], True)

@Sch(["_id", UserIdValidator, ObjectId, Save])
async def deactivate_user(document):
    return await _set_active(document['_id'], False)

async def _set_active(user_id, value):
    update = {'$set': {'active': value}}
    if not value:
        update['$unset'] = {'authTokens': ''}
    update_result = await conf.mongo_accounts.update_one(
        filter = {'_id': user_id},
        update = update
    )
    if update_result.matched_count == 1:
        return Response({"success": True})
    else:
        return Response({"success": False, "error": _("No such user.")})

async def _generate_auth_token(user):
    now = int(time.time())
    token_duration_seconds = conf.get('tokenDurationSeconds')
    timestamp_cutoff = now - token_duration_seconds
    current_auth_tokens = user.get('authTokens', [])
    new_tokens = [
        dct
        for dct in current_auth_tokens
        if dct['timestamp'] > timestamp_cutoff
    ]
    max_tokens_per_user =  conf.get('maxTokensPerUser')
    assert max_tokens_per_user >= 1
    if len(new_tokens) >= max_tokens_per_user:
        new_tokens = new_tokens[1:]
    new_unsigned_token = str(uuid.uuid4())
    new_tokens.append({'authToken': new_unsigned_token, 'timestamp': now})
    await conf.mongo_accounts.update_one(
        filter = {'_id': user['_id']},
        update = {'$set': {'authTokens': new_tokens}}
    )
    return create_signed_string(new_unsigned_token)

def _rec_objectids_to_str(obj):
    if isinstance(obj, ObjectId):
        return str(obj)
    if isinstance(obj, list):
        return [_rec_objectids_to_str(x) for x in obj]
    if isinstance(obj, dict):
        return {key: _rec_objectids_to_str(val) for (key,val) in obj.items()}
    return obj

ReadableField = Do(Type(str),Regex('[^$.]+'))

WritableField = Do(
    Type(str),
    Regex('[^$.]+'),
    Assert(
        lambda s: s not in ('_id', 'email', 'emailLower'),
        error_message = _("_id, email and emailLower are read only.")
    )
)

ReadableFields = Do(
    Type(list),
    Each(ReadableField)
)

def _actual_fields_names(fields):
    return [
        name
        if name in ('_id', 'email', 'emailLower')
        else ('fields.' + name)
        for name in fields
    ]

def _fields_document(user, fields):
    user_data = {}
    for field in fields:
        if field in ('_id', 'email', 'emailLower'):
            if field in user:
                user_data[field] = user[field]
        else:
            if 'fields' in user and field in user['fields']:
                user_data[field] = user['fields'][field]
    return user_data

@Sch(
    ['email', Email],
    ['password', Type(str), Length(1, PASSWORD_MAX_LENGTH)],
    ['fields', Optional, ReadableFields]
)
async def login(document):
    user = await conf.mongo_accounts.find_one(
        {'email': document['email']},
        projection = (
            _actual_fields_names(document.get('fields', []))
            +
            ['authTokens', 'password', 'active']
        )
    )
    if user:
        if 'password' not in user:
            return Response({"success": False, "error": _("Password is not set for this user.")}, 403)
        if 'active' not in user or user['active'] is not True:
            return Response({"success": False, "error": _("This user isn't active.")}, 403)
        try:
            password_matches = bcrypt.verify(document['password'], user['password'])
        except ValueError: # this should not happen if the hash has been correctly computed
            return Response(
                {
                    "success": False,
                    "error": _("The password verification failed because of a server side issue.")
                },
                status = 500
            )
        else:
            if password_matches:
                dct = {
                    "success": True
                }
                fields = document.get('fields')
                if fields:
                    dct['user'] = _rec_objectids_to_str(_fields_document(user, fields))
                dct['authToken'] = await _generate_auth_token(user)
                return Response(dct)
            else:
                return Response(
                    {
                        "success": False,
                        "error": _("Incorrect password.")
                    },
                    403
                )
    else:
        return Response(
            {
                "success": False,
                "error": _("No such user.")
            },
            403
        )

@Sch(['authToken', Type(str), Length(min=1, max=2000)])
async def logout(document):
    decoded_token = decode_signed_string(
        document['authToken'],
        max_age_days = conf.get('tokenDurationSeconds') / 86400.0
    )
    if decoded_token is None:
        return Response({"success": True})
    await conf.mongo_accounts.update_one(
        {'authTokens': {'$elemMatch': {'authToken': decoded_token}}},
        {'$pull': {'authTokens': {'authToken': decoded_token}}}
    )
    return Response({"success": True})

DecodeAuthToken = DecodeSignedString(
    conf.get('tokenDurationSeconds') / 86400.0
)

@Sch(
    ['authToken', DecodeAuthToken, Save],
    ['fields', ReadableFields]
)
async def get_user_fields(document):
    decoded_token = document['authToken']
    user_document = await conf.mongo_accounts.find_one(
        {'authTokens': {'$elemMatch': {'authToken': decoded_token}}},
        projection = _actual_fields_names(document['fields'])
    )
    if user_document is None:
        return Response(
            {"success": False, "error": _("Unrecognized authToken.")},
            403
        )
    return Response({
        "success": True,
        "user": _rec_objectids_to_str(_fields_document(user_document, document['fields']))
    })


def _valid_field_value(val):
    if val is None or isinstance(val, (str, int, float, bool)):
        return True
    if isinstance(val, list):
        return all(_valid_field_value(x) for x in val)
    if isinstance(val, dict):
        for key in val:
            if '$' in val or '.' in val or not val.strip():
                return False
        return all(_valid_field_value(v) for v in val.values())

@Sch(
    ['authToken', DecodeAuthToken, Save],
    ['set', Type(dict), Each(WritableField), Assert(_valid_field_value)]
)
async def set_user_fields(document):
    if document['set']:
        decoded_token = document['authToken']
        update_result = await conf.mongo_accounts.update_one(
            filter = {'authTokens': {'$elemMatch': {'authToken': decoded_token}}},
            update = {'$set': {('fields.' + k): v for k,v in document['set'].items()}}
        )
        if update_result.matched_count == 0:
            return Response(
                {"success": False, "error": _("Unrecognized authToken.")},
                403
            )
    return Response({"success": True})

@Sch(
    ['authToken', DecodeAuthToken, Save],
    ['del', Type(list), Each(WritableField)]
)
async def del_user_fields(document):
    if document['del']:
        decoded_token = document['authToken']
        update_result = await conf.mongo_accounts.update_one(
            filter = {'authTokens': {'$elemMatch': {'authToken': decoded_token}}},
            update = {'$unset': {('fields.' + k): '' for k in document['del']}}
        )
        if update_result.matched_count == 0:
            return Response(
                {"success": False, "error": _("Unrecognized authToken.")},
                403
            )
    return Response({"success": True})

@Sch(['authToken', DecodeAuthToken, Save])
async def get_user_id(document):
    # TODO document in the readthedoc
    decoded_token = document['authToken']
    user_document = await conf.mongo_accounts.find_one(
        {'authTokens': {'$elemMatch': {'authToken': decoded_token}}},
        projection = ['_id']
    )
    if user_document is None:
        return Response(
            {"success": False, "error": _("Unrecognized authToken.")},
            403
        )
    else:
        return Response(
            {"success": True, "_id": str(user_document['_id'])}
        )

@Sch(['email', Email])
async def send_reset_password_code(document, lang):
    email = document['email']
    if await email_exists(email, case_sensitive = True):
        reset_password_code = create_signed_document({
            'email': email,
            'action': 'resetPassword'
        })
        mailer.send_reset_password_code(
            reset_password_code,
            to = email,
            lang = lang
        )
        return Response({"success": True})
    else:
        return Response({"success": False, "error": _("No such email in the database.")})

ResetPasswordCode = Do(
    Type(str),
    Length(min = 1, max = 2000),
    DecodeEmailCode,
    Schema(
        ['email', Email],
        ['action', ('resetPassword',)]
    )
)

@Sch(['code', ResetPasswordCode, SaveAs('decoded')])
async def check_reset_password_code(document):
    if await email_exists(document['decoded']['email'], case_sensitive = True):
        return Response({"success": True})
    else:
        # The user could have changed their email address in the meantime.
        # That would be strange but not impossible.
        return Response({
            "success": False,
            "error": _("No such email in the database.")
        })

@Sch(
    ['resetPasswordCode', ResetPasswordCode, SaveAs('decoded')],
    ['newPassword', NewPasswordValidator, bcrypt.hash, Save]
)
async def reset_password(document):
    email = document['decoded']['email']
    new_password = document['newPassword']
    update_result = await conf.mongo_accounts.update_one(
        filter = {'email': email},
        update = {'$set': {'password': new_password}}
    )
    if update_result.matched_count:
        return Response({"success": True})
    else:
        return Response({
            "success": False,
            "error": _("No such email in the database.")
        })

async def _can_change_email(user, new_email):
    if 'emailLower' not in user:
        return False, _("This user didn't register via email.")
    if user['emailLower'] == new_email.lower():
        return False, _("This is already the email address of this account.")
    if await email_exists(new_email, case_sensitive = False):
        return False, _("This email address already belongs to a registered account.")
    return True, None

@Sch(
    ['authToken', DecodeAuthToken, Save],
    ['email', Email]
)
async def send_change_email_code(document, lang):
    decoded_token = document['authToken']
    new_email = document['email']
    user = await conf.mongo_accounts.find_one(
        filter = {'authTokens': {'$elemMatch': {'authToken': decoded_token}}},
        projection = ['_id', 'emailLower']
    )
    if user:
        can_change, error = await _can_change_email(user, new_email)
        if can_change:
            change_email_code = create_signed_document({
                'action': 'changeEmail',
                '_id': str(user['_id']),
                'newEmail': new_email
            })
            mailer.send_change_email_code(change_email_code, new_email, lang = lang)
            return Response({"success": True})
        else:
            return Response({"success": False, "error": error})
    else:
        return Response(
            {"success": False, "error": _("Unrecognized authToken.")},
            403
        )

ChangeEmailCode = Do(
    DecodeEmailCode,
    Schema(
        ['action', ('changeEmail',)],
        ['_id', UserIdValidator, ObjectId, Save],
        ['newEmail', Email]
    )
)

@Sch(['code', ChangeEmailCode, SaveAs('decoded')])
async def check_change_email_code(document):
    user = await conf.mongo_accounts.find_one(
        filter = {'_id': document['decoded']['_id']},
        projection = ['_id', 'emailLower']
    )
    if user:
        can_change, error = await _can_change_email(user, document['decoded']['newEmail'])
        if can_change:
            return Response({"success": True})
        else:
            return Response({"success": False, "error": error})
    else:
            return Response({"success": False, "error": _("No such user.")})

@Sch(
    ['authToken', DecodeAuthToken, Save],
    ['changeEmailCode', ChangeEmailCode, SaveAs('decoded')]
)
async def change_email(document):
    decoded_token = document['authToken']
    user_id = document['decoded']['_id']
    new_email = document['decoded']['newEmail']
    new_email_lower = new_email.lower()

    try:
        update_result = await conf.mongo_accounts.update_one(
            filter = {
                '_id': user_id,
                'authTokens': {
                    '$elemMatch': {'authToken': decoded_token}
                }
            },
            update = {'$set': {
                'emailLower': new_email_lower,
                'email': new_email
            }}
        )
    except DuplicateKeyError:
        return Response(email_used_result)
    else:
        if update_result.matched_count == 1:
            return Response({"success": True})
        else:
            return Response(
                {
                    "success": False,
                    "error": _("No user account matches this user id and this authToken.")
                },
                403
            )

@Sch(
    ['authToken', DecodeAuthToken, Save],
    ['currentPassword', Type(str), Length(min=1, max=PASSWORD_MAX_LENGTH)],
    ['newPassword', NewPasswordValidator]
)
async def change_password(document):
    decoded_token = document['authToken']
    current_password = document['currentPassword']
    new_password = document['newPassword']
    user = await conf.mongo_accounts.find_one(
        filter = {'authTokens': {'$elemMatch': {'authToken': decoded_token}}},
        projection = ['_id', 'password']
    )
    if not bcrypt.verify(current_password, user['password']):
        return Response(
            {
                "success": False,
                "error": _("Incorrect password.")
            },
            403
        )
    if bcrypt.verify(new_password, user['password']):
        return Response({
            "success": False,
            "error": _("This is the same password as the current one.")
        })
    hashed_new_password = bcrypt.hash(new_password)
    await conf.mongo_accounts.update_one(
        filter = {'_id': user['_id']},
        update = {'$set': {'password': hashed_new_password}}
    )
    return Response({"success": True})

@Sch(["_id", UserIdValidator, ObjectId, Save])
async def delete_user(document):
    delete_result = await conf.mongo_accounts.delete_one(
        {'_id': document['_id']},
    )
    if delete_result.deleted_count == 1:
        return Response({"success": True})
    else:
        return Response({"success": False, "error": _("No such user.")})
