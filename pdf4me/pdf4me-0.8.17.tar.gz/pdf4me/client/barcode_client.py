from pdf4me.helper.pdf4me_exceptions import Pdf4meClientException
from pdf4me.model import ReadBarcodes
from pdf4me.helper.json_converter import JsonConverter


class BarcodeClient(object):

    def __init__(self, pdf4me_client):
        self.pdf4me_client = pdf4me_client

    def read_barcodes(self, read_barcodes):
        """The predefined read barcodes setting is carried out.

        :param read_barcodes: read barcode configuration
        :type read_barcodes: ReadBarcodes
        :return: ReadBarcodeRes, contains the barcode
        """

        # check read_barcodes validity
        self.__check_read_barcodes_object_validity(read_barcodes)

        res = self.pdf4me_client.custom_http.post_universal_object(universal_object=read_barcodes,
                                                                   controller='Barcode/ReadBarcodes')

        return res

    def read_barcodes_by_type(self, barcode_type, file):
        """Reads barcodes from the file based on the barcode type

        :param barcode_type: barcode type
        :type barcode_type: str: ( 'all','unknown','code11','code39','code93','code128','codabar','inter2of5',
                                'patchcode','ean8','upce','ean13','upca','plus2','plus5','pdf417','datamatrix','qrcode',
                                'postnet','planet','rm4scc','australiapost','intelligentmail','code39extended',
                                'microqrcode','all_2d','pharmacode','ucc128','rss14','rsslimited','rssexpanded','all_1d')
        :param file: to be read barcode form
        :type file: file handler, use the method get_file_handler from FileReader to obtain it
        :return: ReadBarcodeRes, contains the barcode
        """

        streams = [('file', file)]
        params = [('barcodeType', barcode_type)]

        res = self.pdf4me_client.custom_http.post_wrapper(octet_streams=streams, values=params,
                                                           controller='Barcode/ReadBarcodesByType')

        json_response = JsonConverter().load(res)

        return json_response

    def create_barcode_by_type(self, barcode_type, content):
        """Creates barcodes from the content based on the barcode type

        :param barcode_type: barcode type
        :type barcode_type: str: ( 'none','australianpostcustom','australianpostcustom2','australianpostcustom3',
                                'australianpostredirection','australianpostreplypaid','australianpostrouting','aztec',
                                'cepnet','codabar18','codabar2','codablockf','code11','code128','code128subseta',
                                'code128subsetb','code128subsetc','code2of5datalogic','code2of5iata','code2of5industry',
                                'code2of5interleaved','code2of5matrix','code2of5standard','code32','code39',
                                'code39extended','code93','code93extended','datamatrix','deutschepostidentcode',
                                'deutschepostleitcode','dotcode','dpd','ean13','ean13with2addon','ean13with5addon',
                                'ean14','ean8','ean8with2addon','ean8with5addon','eanucc128','fim','flattermarken',
                                'gs1_128','gs1databar','gs1databarexpanded','gs1databarexpandedstacked',
                                'gs1databarlimited','gs1databarstacked','gs1databarstackedomnidirectional',
                                'gs1databartruncated','hanxin','hibclic128','hibclic3of9','hibclicaztec',
                                'hibcliccodablock_f','hibclicdatamatrix','hibclicmpdf417','hibclicpdf417',
                                'hibclicqrcode','hibcpas128','hibcpas3of9','hibcpasaztec','hibcpascodablock_f',
                                'hibcpasdatamatrix','hibcpasmpdf417','hibcpaspdf417','hibcpasqrcode','isbn13',
                                'isbn13with5addon','ismn','issn','issnwith2addon','italianpostal2of5',
                                'italianpostal3of9','itf14','japanesepostal','kix','koreanpostalauthority','logmars',
                                'mailmark_2d','mailmark_4state','maxicode','micropdf417','microqrcode','msi','ntin',
                                'nve18','pdf417','pdf417truncated','pharmacodeonetrack','pharmacodetwotrack','planet12',
                                'planet14','plessey','plesseybidirectional','ppn','pzn7','pzn8','qrcode','qrcode2005',
                                'rm4scc','sscc18','swedishpostalshipmentid','swissqrcode','telepen','telepenalpha',
                                'ucc128','upc12','upca','upcawith2addon','upcawith5addon','upce','upcewith2addon',
                                'upcewith5addon','upus10','uspsimpackage','uspsintelligentmail','uspspostnet10',
                                'uspspostnet11','uspspostnet12','uspspostnet5','uspspostnet6','uspspostnet9','vin')
        :param content: text to be converted to barcode
        :type content: str
        :return: bytes of resulting file, can be directly written to file on disk
        """

        streams = None
        params = [('barcodType', barcode_type), ('content', content)]

        return self.pdf4me_client.custom_http.post_wrapper(octet_streams=streams, values=params,
                                                           controller='Barcode/CreateBarcodeByType')


    def __check_read_barcodes_object_validity(self, read_barcodes):
        """checks whether the read_barcodes object contains the essential information to be
        processed by the server."""

        if read_barcodes is None:
            raise Pdf4meClientException('The read_barcodes parameter cannot be None.')
        elif read_barcodes.document is None or read_barcodes.document.doc_data is None:
            raise Pdf4meClientException('The read_barcodes document cannot be None.')
        # elif read_barcodes.barcode_action is None:
        #     raise Pdf4meClientException('The read_barcodes_action cannot be None.')
