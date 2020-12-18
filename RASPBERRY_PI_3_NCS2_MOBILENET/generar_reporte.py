# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------
# Nombre:       generar_reporte.py
# Autor:        Juan Carlos Romero Chalco
# Creado:       20/07/2020
# Modificado:   07/08/2020
# Copyright:    (c) 2020 by Juan Carlos Romero Chalco, 2020
# License:      GNU
# ----------------------------------------------------------------------------

__versión__ = "1.0"

# Versión Python: 3.5.2

"""
El módulo *reportePDF* permite crear un reporte PDF sencillo.
"""
from datetime import datetime

from reportlab.lib.colors import PCMYKColor
from reportlab.graphics.shapes import Drawing
from reportlab.graphics.charts.barcharts import VerticalBarChart




from sqlite3 import connect

from arrow import utcnow, get
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, mm
from reportlab.lib.pagesizes import letter
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
from reportlab.lib.colors import black, purple, white
from reportlab.pdfgen import canvas


# ======================= CLASE reportePDF =========================

class reportePDF(object):
    """Exportar una lista de diccionarios a una tabla en un
       archivo PDF."""
    
    def __init__(self, titulo, cabecera, datos, nombrePDF):
        super(reportePDF, self).__init__()

        self.titulo = titulo
        self.cabecera = cabecera
        self.datos = datos
        self.nombrePDF = nombrePDF

        self.estilos = getSampleStyleSheet()

    @staticmethod
    def _encabezadoPiePagina(canvas, archivoPDF):
        """Guarde el estado de nuestro lienzo para que podamos aprovecharlo"""
        
        canvas.saveState()
        estilos = getSampleStyleSheet()

        alineacion = ParagraphStyle(name="alineacion", alignment=TA_RIGHT,
                                    parent=estilos["Normal"])
 
        # Encabezado
        encabezadoNombre = Paragraph("Sistema de Conteo y Clasificacion", estilos["Normal"])
        anchura, altura = encabezadoNombre.wrap(archivoPDF.width, archivoPDF.topMargin)
        encabezadoNombre.drawOn(canvas, archivoPDF.leftMargin, 736)

        fecha = utcnow().to("local").format("dddd, DD - MMMM - YYYY", locale="es")
        fechaReporte = fecha.replace("-", "de")

        encabezadoFecha = Paragraph(fechaReporte, alineacion)
        anchura, altura = encabezadoFecha.wrap(archivoPDF.width, archivoPDF.topMargin)
        encabezadoFecha.drawOn(canvas, archivoPDF.leftMargin, 736)
 
        # Pie de página
        piePagina = Paragraph("Reporte generado Sistema de Conteo y Casificacion.", estilos["Normal"])
        anchura, altura = piePagina.wrap(archivoPDF.width, archivoPDF.bottomMargin)
        piePagina.drawOn(canvas, archivoPDF.leftMargin, 15 * mm + (0.2 * inch))
 
        # Suelta el lienzo
        canvas.restoreState()

    def convertirDatos(self):
        """Convertir la lista de diccionarios a una lista de listas para crear
           la tabla PDF."""

        estiloEncabezado = ParagraphStyle(name="estiloEncabezado", alignment=TA_LEFT,
                                          fontSize=10, textColor=white,
                                          fontName="Helvetica-Bold",
                                          parent=self.estilos["Normal"])

        estiloNormal = self.estilos["Normal"]
        estiloNormal.alignment = TA_LEFT

        claves, nombres = zip(*[[k, n] for k, n in self.cabecera])

        encabezado = [Paragraph(nombre, estiloEncabezado) for nombre in nombres]
        nuevosDatos = [tuple(encabezado)]

        for dato in self.datos:
            nuevosDatos.append([Paragraph(str(dato[clave]), estiloNormal) for clave in claves])
            
        return nuevosDatos
        
    def Exportar(self):
        """Exportar los datos a un archivo PDF."""

        alineacionTitulo = ParagraphStyle(name="centrar", alignment=TA_CENTER, fontSize=13,
                                          leading=10, textColor=purple,
                                          parent=self.estilos["Heading1"])
        
        self.ancho, self.alto = letter

        convertirDatos = self.convertirDatos()
    
        tabla = Table(convertirDatos, colWidths=(self.ancho-100)/len(self.cabecera), hAlign="CENTER")
        tabla.setStyle(TableStyle([
            ("BACKGROUND", (0, 0),(-1, 0), purple),
            ("ALIGN", (0, 0),(0, -1), "LEFT"),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"), # Texto centrado y alineado a la izquierda
            ("INNERGRID", (0, 0), (-1, -1), 0.50, black), # Lineas internas
            ("BOX", (0, 0), (-1, -1), 0.25, black), # Linea (Marco) externa
            ]))

        historia = []
        historia.append(Paragraph(self.titulo, alineacionTitulo))
        historia.append(Spacer(1, 0.16 * inch))
        historia.append(tabla)

        archivoPDF = SimpleDocTemplate(self.nombrePDF, leftMargin=50, rightMargin=50, pagesize=letter,
                                       title="Reporte PDF", author="Juan Carlos Romero")
        
        try:
            archivoPDF.build(historia, onFirstPage=self._encabezadoPiePagina,
                             onLaterPages=self._encabezadoPiePagina,
                             canvasmaker=numeracionPaginas)
            
         # +------------------------------------+
            return "Reporte generado con éxito."
         # +------------------------------------+
        except PermissionError:
         # +--------------------------------------------+  
            return "Error inesperado: Permiso denegado."
         # +--------------------------------------------+


# ================== CLASE numeracionPaginas =======================

class numeracionPaginas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        canvas.Canvas.__init__(self, *args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        """Agregar información de la página a cada página (página x de y)"""
        numeroPaginas = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_number(numeroPaginas)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)
 
    def draw_page_number(self, conteoPaginas):
        self.drawRightString(204 * mm, 15 * mm + (0.2 * inch),
                             "Página {} de {}".format(self._pageNumber, conteoPaginas))        


# ===================== FUNCIÓN generarReporte =====================

def generarReporte():
    """Ejecutar consulta a la base de datos (bd_conteo_clasificacion.db) y llamar la función Exportar, la
       cuál esta en la clase reportePDF, a esta clase le pasamos el título de la tabla, la
       cabecera y los datos que llevará."""
    
    def dict_factory(cursor, row):
        d = {}
        for idx, col in enumerate(cursor.description):
            d[col[0]] = row[idx]
        return d

    conexionDB = connect("bd/bd_conteo_clasificacion.db")
    conexionDB.row_factory = dict_factory # Forma avanzada de obtener resultados
    cursor = conexionDB.cursor()

    cursor.execute("SELECT Id, tipos, porcentajes, hora, fecha FROM tclasificacion")
    datos = cursor.fetchall()
    
    conexionDB.close()

    titulo = "ESTUDIO DE CONTEO Y CLASIFACION VEHICULAR"

    cabecera = (
        ("Id","Id"),  
        ("tipos","Tipos"),
        ("porcentajes","Estimacion%"),
        ("hora","Hora"),
        ("fecha","Fecha"),  
        )
    
     
    now = datetime.now()
    nombrePDF = "Reporte"+str(now)+".pdf"

    reporte = reportePDF(titulo, cabecera, datos, nombrePDF).Exportar()
    print(reporte)

def create_bar_graph():
    """
    Creates a bar graph in a PDF
    """
    d = Drawing(280, 250)
    bar = VerticalBarChart()
    bar.x = 50
    bar.y = 85
    data = [[1,2,3,None,None,None,5],
            [10,5,2,6,8,3,5],
            [5,7,2,8,8,2,5],
            [2,10,2,1,8,9,5],
            ]
    bar.data = data
    bar.categoryAxis.categoryNames = ['Year1', 'Year2', 'Year3',
                                      'Year4', 'Year5', 'Year6',
                                      'Year7']
    bar.bars[0].fillColor   = PCMYKColor(0,100,100,40,alpha=85)
    bar.bars[1].fillColor   = PCMYKColor(23,51,0,4,alpha=85)
    bar.bars.fillColor       = PCMYKColor(100,0,90,50,alpha=85)
    d.add(bar, '')
    d.save(formats=['pdf'], outDir='.', fnRoot='test')

# ======================== LLAMAR FUNCIÓN ==========================

generarReporte()
create_bar_graph()
