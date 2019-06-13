from coolsignup.conf import conf
from naval import Type, Length, Assert, Do
from postpone import LazyString as _
from zxcvbn import zxcvbn

PASSWORD_MAX_LENGTH = 800

NewPasswordValidator = Do(
    Type(str),
    Length(conf.get('passwordMinLength'), PASSWORD_MAX_LENGTH),
    Assert(
        (
            lambda p: zxcvbn(p)['guesses_log10'] >= conf.get('passwordStrength')
        ),
        error_message = _("Password too easy to guess.")
    )
)
