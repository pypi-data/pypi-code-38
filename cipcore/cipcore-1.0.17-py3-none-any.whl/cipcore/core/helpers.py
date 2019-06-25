from datetime import datetime


class Helpers:

    def build_error_general_email_body(self, recipients_group, process_step, title, media_id, error, resolution=None):
        email_json = dict()
        date_today = datetime.now().strftime("%d/%m/%Y - %H:%M:%S")
        email_json['to'] = recipients_group
        email_json['subject'] = f'[Media Delivery – Hands][ERRO] Nova publicação G1 em 1 Minuto'
        if media_id:
            media_ef = f'https://ef.globoi.com/archived_medias/{media_id}/edit'
        else:
            media_ef = "O erro foi antes de processar a mídia"
        error_code = error.code if error.code else ''
        error_msg = error.message
        body = f'\nEtapa do processo: {process_step}' \
               f'\nTítulo: {title}' \
               f'\nId EF: {media_id}' \
               f'\nResolução: {resolution}' \
               f'\nHora: {date_today}' \
               f'\nMensagem: {error.friendly_message}' \
               f'\nCódigo do erro: {error_code}' \
               f'\nURL da mídia na EF: {media_ef}' \
               f'\nLog do erro: {error_msg}'

        email_json['body'] = body

        return email_json

    def build_database_connection_error_email_body(self, recipients_group, process_step, error):
        email_json = dict()
        date_today = datetime.now().strftime("%d/%m/%Y - %H:%M:%S")
        email_json['to'] = recipients_group
        email_json['subject'] = f'[Media Delivery – Hands][ERRO] Nova publicação G1 em 1 Minuto'
        error_code = error.code if error.code else ''
        error_msg = error.message
        body = f'\nEtapa do processo: {process_step}' \
            f'\nErro: Não foi possivel conectar com o banco de dados.' \
            f'\nHora: {date_today}' \
            f'\nMensagem: {error.friendly_message}' \
            f'\nCódigo do erro: {error_code}' \
            f'\nLog do erro: {error_msg}'

        email_json['body'] = body

        return email_json

    def build_success_email_body(self, recipients_group, process_step, title, media_id, resolution=None):
        email_json = dict()
        date_today = datetime.now().strftime("%d/%m/%Y - %H:%M:%S")
        email_json['to'] = recipients_group
        email_json['subject'] = f'[Media Delivery – Hands] Nova publicação G1 em 1 Minuto'
        media_ef = f'https://ef.globoi.com/archived_medias/{media_id}/edit'
        body = f'\nEtapa do processo: {process_step}' \
                f'\nTítulo: {title}' \
                f'\nId EF: {media_id}' \
                f'\nResolução: {resolution}' \
                f'\nHora: {date_today}' \
                f'\nMensagem: Uma nova publicação do G1 em 1 Minuto foi realizada com sucesso.' \
                f'\nURL da mídia na EF: {media_ef}'

        email_json['body'] = body

        return email_json


