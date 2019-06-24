from gql import gql


class Payments:
    def __init__(self, transport):
        self._transport = transport

    def getPaymentTypeBy(self, attribute, reference):
        request = """
                query {
                  allPaymentTypes (filter:{{attribute}:"{reference}"}) {
                    objects {
                      surchargeAmount
                      surchargePercent
                      attemptLimit
                      paymentTypeCode
                      numberLabel
                      paymentType
                      paymentTypeUuid
                      name
                      retryInterval
                      currency
                      cvvLabel
                      bankLabel
                      processingMode
                      expiryDateLabel
                      nameLabel
                      minimumSurcharge
                    }
                  }
                }
                """
        result = self._transport.client.execute(
            gql(
                request.replace("{attribute}", attribute).replace(
                    "{reference}", reference
                )
            )
        )
        objects = result.get("allPaymentTypes", {}).get("objects", [])
        if objects:
            return objects[0]
        else:
            return None

    def storePaymentDetails(
        self, paymentTypeUuid, accountUuid, token, expiry_date, hint
    ):
        mutation = """
            mutation ($token: PanTokenInput!) {
                putToken(inputToken: $token) {
                    paymentMethodUuid
                    paymentMethod {
                        paymentMethod
                    }
                }
            }
        """
        request = gql(mutation)
        return self._transport.client.execute(
            request,
            variable_values={
                "token": {
                    "paymentTypeUuid": paymentTypeUuid,
                    "accountUuid": accountUuid,
                    "token": token,
                    "expiry": expiry_date,
                    "hint": hint,
                }
            },
        )
