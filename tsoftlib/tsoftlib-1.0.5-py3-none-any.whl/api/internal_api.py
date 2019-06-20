import cx_Oracle


# Debug
from pprint import pprint as pp

class INTERNAL_API(object):

    def __init__(self, connString:str):
        self._dest = connString

    def _connect(self):
        connection = cx_Oracle.connect(self._dest, encoding='UTF-8')
        cursor = connection.cursor()
        return (connection, cursor)

    def customSQL(self, sqlQuery:str) -> set:
        (conn, cur) = self._connect()

        cur.execute(sqlQuery)

        fetched = []

        for row in cur:
            fetched.append(row)

        conn.close()

        return fetched

    def _formatEntries(self, entryList:list) -> list:
        f = ""
        for i, entry in enumerate(entryList):
            f += f"'{entry}'"
            if i != len(entryList) - 1:
                f+=', '
        return f

    def getProductDetails(self, products:list) -> [dict]:
        formatted = self._formatEntries(products)
        sqlQuery = f"""select
            P.PART_NO MALZEME,
            P.UNIT_MEAS BIRIM,
            P.DESCRIPTION ACIKLAMA,
            NVL(IFSAPP.FLASK_API.GET_PART_STOCK_NOW('KE', P.PART_NO, 'FABRIKA-DEPO'), 0) FABRIKASTOK,
            NVL(IFSAPP.FLASK_API.GET_PART_STOCK_NOW('KE', P.PART_NO, 'KE-MAGAZA'), 0) MAGAZASTOK,
            NVL(IFSAPP.FLASK_API.GET_PART_STOCK_NOW('KE', P.PART_NO, 'E-TICARET'), 0) ESTOK,
            NVL(IFSAPP.FLASK_API.GET_PART_LAST_PURC_DATE(P.CONTRACT, P.PART_NO, 1), TO_DATE('11.11.1111', 'dd.mm.yyyy')) LASTPURCHDATE,
            NVL(IFSAPP.FLASK_API.GET_PART_LAST_PURC_ORDER_NO(P.CONTRACT, P.PART_NO, 1), 'None') LASTPURCHORDER,
            NVL(IFSAPP.FLASK_API.GET_PART_LAST_PURC_PRICE(P.CONTRACT, P.PART_NO, 1, 1), 0) LASTPURCHPRICE,
            NVL(IFSAPP.FLASK_API.GET_PART_LAST_PURC_QTY(P.CONTRACT, P.PART_NO, 1), 0) LASTPURCHQTY,
            NVL(IFSAPP.FLASK_API.GET_PART_LAST_SALE_DATE(P.CONTRACT, P.PART_NO, 1), TO_DATE('11.11.1111', 'dd.mm.yyyy')) LASTSALEDATE,
            NVL(IFSAPP.FLASK_API.GET_PART_LAST_SALE_ORDER_NO(P.CONTRACT, P.PART_NO, 1), 'None') LASTSALEORDER,
            NVL(IFSAPP.FLASK_API.GET_PART_LAST_SALE_PRICE(P.CONTRACT, P.PART_NO, 1, 1), 0) LASTSALEPRICE,
            NVL(IFSAPP.FLASK_API.GET_PART_LAST_SALE_QTY(P.CONTRACT, P.PART_NO, 1), 0) LASTSALEQTY,
            NVL(IFSAPP.FLASK_API.SALE_FREQ_OF_PRODUCT(P.CONTRACT, P.PART_NO),0) THISYEARSALE,
            NVL(IFSAPP.FLASK_API.SALE_FREQ_OF_PRODUCT(P.CONTRACT, P.PART_NO, 24, 12),0) LASTYEARSALE
        from INVENTORY_PART P
        where P.PART_NO in ({formatted})
        AND P.CONTRACT = 'KE'
        """

        (conn, cur) = self._connect()

        cur.execute(sqlQuery)

        fetched = []

        for row in cur:
            r = {
                'partNo': row[0],
                'unitMeas': row[1],
                'description': row[2],
                'fabrikaStock': row[3],
                'magazaStock': row[4],
                'eticaretStock': row[5],
                'lastPurchDate': row[6],
                'lastPurchOrder': row[7],
                'lastPurchPrice': row[8],
                'lastPurchQty': row[9],
                'lastSaleDate': row[10],
                'lastSaleOrder': row[11],
                'lastSalePrice': row[12],
                'lastSaleQty': row[13],
                'thisYearSaleFreq': row[14],
                'lastYearSaleFreq': row[15]
            }

            fetched.append(r)

        conn.close()

        return fetched

    def getStocks(self, products:list) -> [dict]:
        formatted = self._formatEntries(products)
        sqlQuery = f"""SELECT T.PART_NO, NVL(IFSAPP.FLASK_API.GET_PART_STOCK_NOW('KE', T.PART_NO, 'FABRIKA-DEPO'), 0) + NVL(IFSAPP.FLASK_API.GET_PART_STOCK_NOW('KE', T.PART_NO, 'KE-MAGAZA'), 0) + NVL(IFSAPP.FLASK_API.GET_PART_STOCK_NOW('KE', T.PART_NO, 'E-TICARET'), 0) STOCK, NVL(IFSAPP.FLASK_API.GET_PART_STOCK_NOW('KE', T.PART_NO, 'FABRIKA-DEPO'), 0) FABRIKA, NVL(IFSAPP.FLASK_API.GET_PART_STOCK_NOW('KE', T.PART_NO, 'KE-MAGAZA'), 0) MAGAZA, NVL(IFSAPP.FLASK_API.GET_PART_STOCK_NOW('KE', T.PART_NO, 'E-TICARET'), 0) ELEKTRIX FROM IFSAPP.INVENTORY_PART T WHERE T.contract = 'KE' AND T.PART_NO IN ({formatted})"""

        (conn, cur) = self._connect()

        cur.execute(sqlQuery)

        fetched = []

        for row in cur:
            r = {
                'partNo': row[0],
                'totalStock': row[1],
                'fabrikaStock': row[2],
                'magazaStock': row[3],
                'eticaretStock': row[4],
            }

            fetched.append(r)

        conn.close()

        return fetched

    def getInvoices(self) -> [dict]:
        sqlQuery = """select
        s.ORDER_NO sipNo,
        CUSTOMER_ORDER_API.GET_CUSTOMER_PO_NO(s.ORDER_NO) TSoftSip,
        s.RESMI_FTU_NO FatNo,
        s.INVOICE_ID FatID,
        s.INVOICE_DATE FatTarih,
        s.IDENTITY MusteriNo,
        s.CUST_DESC Musteri,
        (select x.value from COMM_METHOD x where x.IDENTITY = s.IDENTITY and x.METHOD_ID_DB = 'E_MAIL' and x.METHOD_DEFAULT = 'TRUE') MusteriMail,
        s.SHIPMENT_ID,
        sum(FLASK_API.CALC_DISCOUNT(s.NET_DOM_AMOUNT, s.DISCOUNT)) NetTutar,
        sum(FLASK_API.CALC_DISCOUNT(s.GROSS_CURR_AMOUNT, s.DISCOUNT)) BrutTutar
        from IFSTR_KRC_REP_SALES s
        where CUSTOMER_ORDER_API.GET_SALESMAN_CODE(s.ORDER_NO) = 'ETICARET' 
            and s.CONTRACT = 'KE' 
            AND CUSTOMER_ORDER_API.GET_CUSTOMER_PO_NO(s.ORDER_NO) IS NOT NULL
        group by
        s.ORDER_NO,
        s.RESMI_FTU_NO,
        s.INVOICE_ID,
        s.INVOICE_DATE,
        s.IDENTITY,
        s.CUST_DESC,
        s.SHIPMENT_ID
        """

        (conn, cur) = self._connect()

        cur.execute(sqlQuery)

        fetched = []

        for row in cur:
            r = {
                'orderNo': row[0],
                'eCommOrderNo': row[1],
                'invoiceNo': row[2],
                'invoiceID': row[3],
                'invoiceDate': row[4],
                'customerNo': row[5],
                'customerDesc': row[6],
                'customerEmail': row[7],
                'shipmentID': row[8],
                'netPrice': row[9],
                'grossPrice': row[10],
            }

            fetched.append(r)

        conn.close()

        return fetched