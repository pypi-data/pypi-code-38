# -*- coding: utf-8 -*-
import unittest
from .. import presentation_line as presentation
import sys
sys.path.append("../")


class TestPurchaseSalesPresentationLine(unittest.TestCase):

    def _create_cabecera_line_test(self):
        
        self.cabecera_line.cuit = 30709653543
        self.cabecera_line.periodo = 201611
        self.cabecera_line.secuencia = 00
        self.cabecera_line.sinMovimiento = 'S'
        self.cabecera_line.prorratearCFC = 'N'
        self.cabecera_line.cFCGlobal = 'S'
        self.cabecera_line.importeCFCG = 100000001251200
        self.cabecera_line.importeCFCAD = 100000001251200
        self.cabecera_line.importeCFCP = 100000001251200
        self.cabecera_line.importeCFnCG = 100000001251200
        self.cabecera_line.cFCSSyOC = 100000001251200
        self.cabecera_line.cFCCSSyOC = 100000001251200

    def _create_ventas_cbte_line_test(self):
        
        self.ventas_cbte_line.fecha = 20151030
        self.ventas_cbte_line.tipo = '091'
        self.ventas_cbte_line.puntoDeVenta = 0o0001
        self.ventas_cbte_line.numeroComprobante = 4590
        self.ventas_cbte_line.numeroHasta = 4600
        self.ventas_cbte_line.codigoDocumento = 20
        self.ventas_cbte_line.numeroComprador = 51231
        self.ventas_cbte_line.denominacionComprador = 'Test Test'
        self.ventas_cbte_line.importeTotal = 5800
        self.ventas_cbte_line.importeTotalNG = 5000
        self.ventas_cbte_line.percepcionNC = 300
        self.ventas_cbte_line.importeExentos = 123   
        self.ventas_cbte_line.importePercepciones = 5123
        self.ventas_cbte_line.importePerIIBB = 3331
        self.ventas_cbte_line.importePerIM = 4234
        self.ventas_cbte_line.importeImpInt = '12312'
        self.ventas_cbte_line.codigoMoneda = '321'
        self.ventas_cbte_line.tipoCambio = '4444000000'
        self.ventas_cbte_line.cantidadAlicIva = 1
        self.ventas_cbte_line.codigoOperacion = 1
        self.ventas_cbte_line.otrosTributos = 0
        self.ventas_cbte_line.fechaVtoPago = 20151130
    
    def _create_ventas_alicuotas_line_test(self):
        
        self.ventas_alicuotas_line.tipoComprobante = 91
        self.ventas_alicuotas_line.puntoDeVenta = 0o0001
        self.ventas_alicuotas_line.numeroComprobante = 9898989898
        self.ventas_alicuotas_line.importeNetoGravado = 10000
        self.ventas_alicuotas_line.alicuotaIva = 21
        self.ventas_alicuotas_line.impuestoLiquidado = 2100
 
    def _create_compras_cbte_line_test(self):
        
        self.compras_cbte_line.fecha = 20161212
        self.compras_cbte_line.tipo = 98
        self.compras_cbte_line.puntoDeVenta = 0o001
        self.compras_cbte_line.numeroComprobante = '12345678'
        self.compras_cbte_line.despachoImportacion = 'despaimportacion'
        self.compras_cbte_line.codigoDocumento = 'CD'
        self.compras_cbte_line.numeroVendedor = '30709653543'
        self.compras_cbte_line.denominacionVendedor = 'Test test'
        self.compras_cbte_line.importeTotal = 100000
        self.compras_cbte_line.importeTotalNG = 0
        self.compras_cbte_line.importeOpExentas = 0
        self.compras_cbte_line.importePerOIva = 0
        self.compras_cbte_line.importePerOtrosImp = 0
        self.compras_cbte_line.importePerIIBB = 0
        self.compras_cbte_line.importePerIM = 0
        self.compras_cbte_line.importeImpInt = 1000
        self.compras_cbte_line.codigoMoneda = 'ARS'
        self.compras_cbte_line.tipoCambio = '1'
        self.compras_cbte_line.cantidadAlicIva = '5'
        self.compras_cbte_line.codigoOperacion = 'A'
        self.compras_cbte_line.credFiscComp = '0'
        self.compras_cbte_line.otrosTrib = '0'
        self.compras_cbte_line.cuitEmisor = '11022598'
        self.compras_cbte_line.denominacionEmisor = 'Responsable Inscripto'
        self.compras_cbte_line.ivaComision = '100' 
    
    def _create_compras_alicuotas_line_test(self):
        
        self.compras_alicuotas_line.tipoComprobante = '093'
        self.compras_alicuotas_line.puntoDeVenta = '00005'
        self.compras_alicuotas_line.numeroComprobante = 123516129872
        self.compras_alicuotas_line.codigoDocVend = 13
        self.compras_alicuotas_line.numeroIdVend = 26288940
        self.compras_alicuotas_line.importeNetoGravado = 50000
        self.compras_alicuotas_line.alicuotaIva = 3
        self.compras_alicuotas_line.impuestoLiquidado = 10000
     
    def _create_compras_importaciones_line_test(self):
        
        self.compras_importaciones_line.despachoImportacion = '18273918273JKL'
        self.compras_importaciones_line.importeNetoGravado = '100000'
        self.compras_importaciones_line.alicuotaIva = '912'
        self.compras_importaciones_line.impuestoLiquidado = '1000'
        
    def _create_credito_fiscal_importacion_serv_line_test(self):
        
        self.credito_fiscal_importacion_serv_line.tipoComprobante = '3'
        self.credito_fiscal_importacion_serv_line.descripcion = 'Descripcion'
        self.credito_fiscal_importacion_serv_line.identificacionComprobante = '981273918CCLL'
        self.credito_fiscal_importacion_serv_line.fechaOperacion = '20161212'
        self.credito_fiscal_importacion_serv_line.montoMonedaOriginal = '10000'
        self.credito_fiscal_importacion_serv_line.codigoMoneda = 'USD'
        self.credito_fiscal_importacion_serv_line.tipoCambio = '15'
        self.credito_fiscal_importacion_serv_line.cuitPrestador = '262841231'
        self.credito_fiscal_importacion_serv_line.nifPrestador = '123123123245927'
        self.credito_fiscal_importacion_serv_line.nombrePrestador = 'Nombre Apellido Prestador'
        self.credito_fiscal_importacion_serv_line.alicuotaAplicable = '2100'
        self.credito_fiscal_importacion_serv_line.fechaIngresoImpuesto = '20141213'
        self.credito_fiscal_importacion_serv_line.montoImpuesto = '1300'
        self.credito_fiscal_importacion_serv_line.impuestoComputable = '1000'
        self.credito_fiscal_importacion_serv_line.idPago = '0001-8192839192'
        self.credito_fiscal_importacion_serv_line.cuitEntidadPago = '30709612352'

    def _get_lines(self):
        
        lines = [self.cabecera_line, self.ventas_cbte_line, self.ventas_alicuotas_line,
                 self.compras_cbte_line, self.compras_alicuotas_line,
                 self.compras_importaciones_line, self.credito_fiscal_importacion_serv_line]
        
        return lines
    
    cabecera_line = presentation.PresentationLine.factory("ventasCompras", "cabecera")
    ventas_cbte_line = presentation.PresentationLine.factory("ventasCompras", "ventasCbte")
    ventas_alicuotas_line = presentation.PresentationLine.factory("ventasCompras", "ventasAlicuotas")
    compras_cbte_line = presentation.PresentationLine.factory("ventasCompras", "comprasCbte")
    compras_alicuotas_line = presentation.PresentationLine.factory("ventasCompras", "comprasAlicuotas")
    compras_importaciones_line = presentation.PresentationLine.factory("ventasCompras", "comprasImportaciones")
    credito_fiscal_importacion_serv_line = presentation.PresentationLine.factory("ventasCompras", "creditoFiscalImportacionServ")
        
    def test_create_presentation_lines(self):
        self._create_cabecera_line_test()
        self._create_ventas_cbte_line_test()
        self._create_ventas_alicuotas_line_test()
        self._create_compras_cbte_line_test()
        self._create_compras_alicuotas_line_test()
        self._create_compras_importaciones_line_test()
        self._create_credito_fiscal_importacion_serv_line_test()
                
    def test_invalid_attribute(self):
        with self.assertRaises(AttributeError):
            self.cabecera_line.otherValue = 'other value'
    
    def test_more_digits(self):
        with self.assertRaises(ValueError):
            self.credito_fiscal_importacion_serv_line.cuitEntidadPago = '307096123522'
    
    def test_caracteres_especiales(self):          
        self.credito_fiscal_importacion_serv_line.codigoMoneda = 'AÑ|'

    def test_generate_line_string(self):
        for line in self._get_lines():
            line.get_line_string()

    def test_check_lines_len(self):

        self._create_cabecera_line_test()        
        self.assertEqual(len(self.cabecera_line.get_line_string()), 112)
        self._create_ventas_cbte_line_test()
        self.assertEqual(len(self.ventas_cbte_line.get_line_string()), 266)
        self._create_ventas_alicuotas_line_test()
        self.assertEqual(len(self.ventas_alicuotas_line.get_line_string()), 62)
        self._create_compras_cbte_line_test()
        self.assertEqual(len(self.compras_cbte_line.get_line_string()), 325)
        self._create_compras_alicuotas_line_test()
        self.assertEqual(len(self.compras_alicuotas_line.get_line_string()), 84)
        self._create_compras_importaciones_line_test()
        self.assertEqual(len(self.compras_importaciones_line.get_line_string()), 50)
        self._create_credito_fiscal_importacion_serv_line_test()
        self.assertEqual(len(self.credito_fiscal_importacion_serv_line.get_line_string()), 211)


if __name__ == '__main__':
    unittest.main()
