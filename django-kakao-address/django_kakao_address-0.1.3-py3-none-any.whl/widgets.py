from django import forms


class KakaoAddressWidget(forms.MultiWidget):
    template_name = 'kakao_address/'