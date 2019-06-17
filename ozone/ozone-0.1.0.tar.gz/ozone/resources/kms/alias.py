from troposphere.kms import (
    Alias
)

def alias_build(**kwargs):
    """
    Args:
        kwargs:
                AliasName: str() is the name of the alias
                TargetKeyId: str() of the Key Unique ID or ARN
    Returns:
        alias Alias()
    """
    alias = Alias(
        'KmsKeyAlias',
        **kwargs
    )
    return alias
