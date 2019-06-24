from gql import gql


class Accounts:
    def __init__(self, transport):
        self._transport = transport

    def getAccountByUSN(self, usn):
        request = """
                query {
                     account(usn:"{usn}") {
                           branding
                           discount
                           accountCostCentre
                           reference
                           usn
                           taxable
                           accountType
                           accountUuid
                           taxSchedule
                           accountTerms
                           alternateAccountNumber
                           paymentPolicy
                           creationTime
                           timezone
                           description
                           chargeCycle
                           creationTime_iso
                           currency
                           delegateAccountUuid
                           uoobject
                           custom
                           issueCycle
                     }
                }
                """
        result = self._transport.client.execute(gql(request.replace("{usn}", usn)))
        return result.get("account")
