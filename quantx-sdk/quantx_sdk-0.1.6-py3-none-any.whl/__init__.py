from quantx_sdk.api import API
from quantx_sdk.root import Root


def QX(
    public_key,
    secret_key,
    api_entry_point="https://api.quantx.io/public/api/v1",
    websocket_entry_point="wss://ws.quantx.io/ws/v1",
):
    """QuantX SDKの初期化

        SDKを初期化し、Rootオブジェクトを作成します。

        Parameters
        ----------
        public_key : str
            QuantX Factory で発行したPublic Key
        secret_key : str
            QuantX Factory で発行したSecret Key
        api_entry_point: str
            APIのエントリポイントを指定します。
        websocket_entry_point: str
            Websocketのエントリポイントを指定します。

        Returns
        -------
        quantx_sdk.Root

        Examples
        --------
        >>> from quantx_sdk import QX
        >>> qx = QX(publicKey, secretKey)

        """
    api = API(
        public_key,
        secret_key,
        api_entry_point=api_entry_point,
        websocket_entry_point=websocket_entry_point,
    )
    return Root(api)
