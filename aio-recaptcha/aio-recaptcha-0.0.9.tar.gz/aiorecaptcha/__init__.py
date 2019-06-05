from urllib.parse import urlencode
import aiohttp


__all__ = [
    "html",
    "js",
    "verify",
    "RecaptchaError",
    "TESTING_SITE_KEY",
    "TESTING_SECRET_KEY",
]

# ref: https://developers.google.com/recaptcha/docs/faq#id-like-to-hide-the-recaptcha-v3-badge-what-is-allowed
TESTING_SITE_KEY = "6LeIxAcTAAAAAJcZVRqyHh71UMIEGNQ_MXjiZKhI"
TESTING_SECRET_KEY = "6LeIxAcTAAAAAGG-vFI1TnRWxMZNFuojJ4WifJWe"

# Misc
CONSENT = """
This site is protected by reCAPTCHA and the Google
    <a href="https://policies.google.com/privacy">Privacy Policy</a> and
    <a href="https://policies.google.com/terms">Terms of Service</a> apply.
"""

RECAPTCHA_VERIFY_URL = "https://www.google.com/recaptcha/api/siteverify"
RECAPTCHA_ERROR_CODES = {
    "missing-input-secret": "The secret parameter is missing.",
    "invalid-input-secret": "The secret parameter is invalid or malformed.",
    "missing-input-response": "The response parameter is missing.",
    "invalid-input-response": "The response parameter is invalid or malformed.",
    "bad-request": "bad-request	The request is invalid or malformed.",
}

RECAPTCHA_SCRIPT_URL = "www.google.com/recaptcha/api.js"
BASE_JS = "<script src='//{SCRIPT_URL}'{ASYNC_DEFER}></script>"

BASE_HTML = '<div class="g-recaptcha"{}></div>'


class RecaptchaError(Exception):
    def __init__(self, msg, *args, **kwargs):
        self.msg = msg
        super().__init__(msg, *args, **kwargs)


def js(**kwargs):
    """
    Get JS script that loads the Recaptcha V2/V3 script

    Appending this script to your HTML will expose the following API:

        https://developers.google.com/recaptcha/docs/display#js_api

        **If your html div is invisible, it will expose this API:**

        https://developers.google.com/recaptcha/docs/invisible#js_api

    Arguments:

        onload (str):
            * Optional
            * The name of your callback function to be executed once all the dependencies have loaded.

        render (str):

            * Optional
            
            * Whether to render the widget explicitly. 
              
            * Defaults to onload, which will render the widget in the first g-recaptcha tag it finds.

            * Either: ``"onload"`` or explicitly specify a widget value

        language (str):

            * Optional

            * hl language code

            * Reference: https://developers.google.com/recaptcha/docs/language

        async_ (bool):

            * Optional

            * add async tag to JS script

            * Default True

        defer (bool):

            * Optional

            * Add def tag to JS Script

            * Default True
    """

    # 1. JS
    onload = {"onload": kwargs.pop("onload", None)}
    render = {"render": kwargs.pop("render", None)}
    language = {"hl": kwargs.pop("language", None)}
    async_ = kwargs.pop("async_", True)
    defer = kwargs.pop("defer", True)

    if kwargs:
        raise TypeError("Extra kwargs: " + str(kwargs))

    url = RECAPTCHA_SCRIPT_URL

    if onload or render or language:
        url += "?"
        for arg in [onload, render, language]:
            if None not in arg.values():
                url += urlencode(arg) + "&"
        url = url[:-1]  # Remove trailing and

    async_defer = ""
    if async_ is True:
        async_defer += " async"
    if defer is True:
        async_defer += " defer"

    return BASE_JS.format(SCRIPT_URL=url, ASYNC_DEFER=async_defer)


def html(**kwargs):
    """
    Get HTML <div> used by Recaptcha's JS script

    Arguments:

        site_key:

            * Required

            * Your Sitekey

        theme:

            * The color theme of the widget.

            * Optional

            * One of: (dark, light)

            * Default: light

        badge:

            * Reposition the reCAPTCHA badge. 'inline' lets you position it with CSS.

            * Optional

            * One of: ('bottomright', 'bottomleft', 'inline')

            * Default: None

        size:

            * Optional

            * The size of the widget

            * One of: ("compact", "normal", "invisible")

            * Default: normal

        type_:

            * Optional

            * One of: ('image', 'audio')

            * Default: 'image'

        tabindex (int):

            * Optional

            * The tabindex of the widget and challenge. 
            
            * If other elements in your page use tabindex, it should be set to make user navigation easier.

            * Default: 0

        callback (str):

            * Optional

            * The name of your callback function, executed when the user submits a successful response.

            * The **g-recaptcha-response** token is passed to your callback.

        expired_callback (str):

            * Opional

            * The name of your callback function, executed when the reCAPTCHA response expires and the user needs to re-verify.

        error_callback (str):

            * Optional

            * The name of your callback function, executed when reCAPTCHA encounters an error 
              (usually network connectivity) and cannot continue until connectivity is restored.

            * If you specify a function here, you are responsible for informing the user that they should retry.

    """

    site_key = {"data-sitekey": kwargs.pop("site_key", None)}
    theme = {"data-theme": kwargs.pop("theme", "light")}
    badge = {"data-badge": kwargs.pop("badge", None)}
    size = {"data-size": kwargs.pop("size", "normal")}
    type_ = {"data-type": kwargs.pop("type_", "image")}
    tabindex = {"data-tabindex": kwargs.pop("tabindex", None)}
    callback = {"data-callback": kwargs.pop("callback", None)}
    expired_callback = {"expired-callback": kwargs.pop("expired_callback", None)}
    error_callback = {"error-callback": kwargs.pop("error_callback", None)}

    if kwargs:
        raise TypeError("Extra kwargs: " + str(kwargs))

    kwargs = ""
    for kwarg in [
        site_key,
        theme,
        badge,
        size,
        type_,
        tabindex,
        callback,
        expired_callback,
        error_callback,
    ]:
        for k, v in kwarg.items():
            if v is not None:
                kwargs += " " + k + '="' + str(v) + '"'

    return BASE_HTML.format(kwargs)


async def verify(secret, response, remoteip=None):
    """
    Returns None if Recaptcha's response is valid, raises error

    Arguments:

        secret:

            * Required

            * The shared key between your site and reCAPTCHA.

        response:

            * Required

            * The user response token provided by reCAPTCHA, verifying the user on your site.

            * Should be typically found as an item named: 'g-recaptcha-response'.

        remoteip:

            * Optional

            * The user's IP address.
    """

    data = dict(secret=secret, response=response)
    if remoteip is not None:
        data["remoteip"] = remoteip
    form = urlencode(data)

    async with aiohttp.ClientSession() as sess:
        async with sess.post(
            url=RECAPTCHA_VERIFY_URL,
            data=form,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        ) as http_resp:
            json_resp = await http_resp.json()

    if json_resp.get("success") is True:
        return

    for error_code in json_resp.get("error-codes", []):
        if error_code in RECAPTCHA_ERROR_CODES:
            raise RecaptchaError(RECAPTCHA_ERROR_CODES[error_code])

    raise RecaptchaError("Unknown response type: " + str(json_resp))
