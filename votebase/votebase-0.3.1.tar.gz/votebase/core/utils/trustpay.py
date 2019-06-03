def generate_signature(key, data, toTrustPay):
#    Sign creation
    AID = str(data['AID'])
    AMT = str(data['AMT'])
    CUR = str(data['CUR'])
    REF = str(data['REF'])

    try:
        TYP = str(data['TYP'])
        RES = str(data['RES'])
        TID = str(data['TID'])
        OID = str(data['OID'])
        TSS = str(data['TSS'])
    except KeyError:
        TYP = None
        RES = None
        TID = None
        OID = None
        TSS = None

#    A message is created as concatenation of parameter values in this specified order:
    if toTrustPay:
#        Merchant redirect to TrustPay: AID, AMT, CUR, and REF
        message = AID + AMT + CUR + REF
    else:
#        TrustPay notification to Merchant: AID, TYP, AMT, CUR, REF, RES, TID, OID and TSS
        message = AID + TYP + AMT + CUR + REF + RES + TID + OID + TSS

    import hashlib
    import hmac

#    HMAC-SHA-256 code (32 bytes) is generated using a key obtained from TrustPay
    code = hmac.new(key, message, hashlib.sha256)

#    Then the code is converted to a string to be a hexadecimal representation of the code
    hex = code.hexdigest()

#    Return 64 upper chars
    return hex.upper()
