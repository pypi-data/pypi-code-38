def get_fund_list_payload(start_date, end_date, **kwargs):
    payload_template = \
        '''<?xml version="1.0" encoding="utf-8"?>
    <message>
    <proframeHeader>
        <pfmAppName>FS-DIS2</pfmAppName>
        <pfmSvcName>DISNewEstSO</pfmSvcName>
        <pfmFnName>select</pfmFnName>
    </proframeHeader>
    <systemHeader></systemHeader>
        <DISCondFuncDTO>
        <tmpV30>{start_date}</tmpV30>
        <tmpV31>{end_date}</tmpV31>
    </DISCondFuncDTO>
    </message>
    '''
    payload = payload_template.format(
        start_date=start_date,
        end_date=end_date
    )
    return payload


def get_fund_etc_payload(fund_std_code, company_code, **kwargs):
    payload_template = \
        '''<?xml version="1.0" encoding="utf-8"?>
    <message>
    <proframeHeader>
        <pfmAppName>FS-COM</pfmAppName>
        <pfmSvcName>COMFundUnityBasInfoSO</pfmSvcName>
        <pfmFnName>fundStdcotInfoSrch</pfmFnName>
    </proframeHeader>
    <systemHeader></systemHeader>
        <COMFundUnityInfoInputDTO>
        <standardCd>{fund_std_code}</standardCd>
        <companyCd>{company_code}</companyCd>
        <standardDt></standardDt>
    </COMFundUnityInfoInputDTO>
    </message>
    '''
    payload = payload_template.format(
        fund_std_code=fund_std_code,
        company_code=company_code
    )
    return payload


def get_fund_detail_payload(fund_std_code, **kwargs):
    payload_template = \
        '''<?xml version="1.0" encoding="utf-8"?>
    <message>
    <proframeHeader>
        <pfmAppName>FS-COM</pfmAppName>
        <pfmSvcName>COMFundUnityBasInfoSO</pfmSvcName>
        <pfmFnName>fundBasInfoSrch</pfmFnName>
    </proframeHeader>
    <systemHeader></systemHeader>
        <COMFundUnityInfoInputDTO>
        <standardCd>{fund_std_code}</standardCd>
        <companyCd></companyCd>
        <standardDt></standardDt>
    </COMFundUnityInfoInputDTO>
    </message>'''

    payload = payload_template.format(fund_std_code=fund_std_code)
    return payload


def get_price_change_progress_payload(fund_std_code, company_code, start_date, end_date, daily=True, **kwargs):
    payload_template = \
        '''<?xml version="1.0" encoding="utf-8"?>
    <message>
    <proframeHeader>
        <pfmAppName>FS-COM</pfmAppName>
        <pfmSvcName>COMFundPriceModSO</pfmSvcName>
        <pfmFnName>priceModSrch</pfmFnName>
    </proframeHeader>
    <systemHeader></systemHeader>
        <COMFundUnityInfoInputDTO>
        <standardCd>{fund_std_code}</standardCd>
        <companyCd>{company_code}</companyCd>
        <vSrchTrmFrom>{start_date}</vSrchTrmFrom>
        <vSrchTrmTo>{end_date}</vSrchTrmTo>
        <vSrchStd>{daily}</vSrchStd>
    </COMFundUnityInfoInputDTO>
    </message>'''

    payload = payload_template.format(
        fund_std_code=fund_std_code,
        company_code=company_code,
        start_date=start_date,
        end_date=end_date,
        daily=1 if daily else 2
    )
    return payload


def get_fund_exso_payload(fund_std_code, company_code, **kwargs):
    payload_template = \
        '''<?xml version="1.0" encoding="utf-8"?>
    <message>
    <proframeHeader>
        <pfmAppName>FS-COM</pfmAppName>
        <pfmSvcName>COMFundSettleExSO</pfmSvcName>
        <pfmFnName>settleExSrch</pfmFnName>
    </proframeHeader>
    <systemHeader></systemHeader>
        <COMFundUnityInfoInputDTO>
        <standardCd>{fund_std_code}</standardCd>
        <companyCd>{company_code}</companyCd>
    </COMFundUnityInfoInputDTO>
    </message>'''
    payload = payload_template.format(
        fund_std_code=fund_std_code,
        company_code=company_code
    )
    return payload


def get_fund_exso_payload_by_date(start_date, end_date, **kwargs):
    payload_template = \
        '''<?xml version="1.0" encoding="utf-8"?>
    <message>
    <proframeHeader>
        <pfmAppName>FS-DIS2</pfmAppName>
        <pfmSvcName>DISFundRdmpSO</pfmSvcName>
        <pfmFnName>select</pfmFnName>
    </proframeHeader>
    <systemHeader></systemHeader>
        <DISCondFuncDTO>
        <tmpV30>{start_date}</tmpV30>
        <tmpV31>{end_date}</tmpV31>
        <tmpV12></tmpV12>
        <tmpV3></tmpV3>
        <tmpV5></tmpV5>
        <tmpV4></tmpV4>
        <tmpV7></tmpV7>
    </DISCondFuncDTO>
    </message>'''
    payload = payload_template.format(
        start_date=start_date,
        end_date=end_date
    )
    return payload
