"""
Generación de los archivos de los reportes: PDF (reportlab) y Excel (openpyxl).
Ambos llevan encabezado institucional, filtros aplicados, tabla con colores
del aplicativo, totales y pie de página con fecha de generación.
"""
from datetime import datetime
from io import BytesIO

from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from app.core.config import Config

AZUL = "3659D9"
AZUL_CLARO = "EEF2FF"
GRIS = "5F6B7E"
COLORES_ESTADO = {"presente": "198754", "ausente": "DC3545", "tarde": "FD7E14", "excusado": "0DCAF0"}


def _texto(valor) -> str:
    if valor is None:
        return ""
    if isinstance(valor, float):
        return f"{valor:.1f}".replace(".", ",")
    texto = str(valor)
    return texto.capitalize() if texto in COLORES_ESTADO else texto


# ----------------------------------------------------------------------------- PDF
def generar_pdf(titulo: str, columnas: list[dict], filas: list[dict], filtros: list[tuple[str, str]],
                resumen: list[tuple[str, str]], generado_por: str) -> bytes:
    buffer = BytesIO()
    fecha = datetime.now().strftime("%d/%m/%Y %H:%M")
    estilos = getSampleStyleSheet()
    normal = ParagraphStyle("normal", parent=estilos["Normal"], fontName="Helvetica", fontSize=8, leading=10)
    celda_titulo = ParagraphStyle("ct", parent=normal, fontName="Helvetica-Bold", textColor=colors.white)
    h1 = ParagraphStyle("h1", parent=estilos["Title"], fontName="Helvetica-Bold", fontSize=16,
                        textColor=colors.HexColor(f"#{AZUL}"), alignment=TA_LEFT, spaceAfter=2)
    sub = ParagraphStyle("sub", parent=normal, fontSize=9, textColor=colors.HexColor(f"#{GRIS}"))

    def pie(canvas, doc):
        canvas.saveState()
        ancho, alto = landscape(A4)
        canvas.setFillColor(colors.HexColor(f"#{AZUL}"))
        canvas.rect(0, alto - 0.6 * cm, ancho, 0.6 * cm, stroke=0, fill=1)
        canvas.setFillColor(colors.HexColor(f"#{GRIS}"))
        canvas.setFont("Helvetica", 7.5)
        canvas.line(1.5 * cm, 1.3 * cm, ancho - 1.5 * cm, 1.3 * cm)
        canvas.drawString(1.5 * cm, 0.9 * cm,
                          f"{Config.NOMBRE_INSTITUCION} · Gestor de asistencia estudiantil · Generado el {fecha} por {generado_por}")
        canvas.drawRightString(ancho - 1.5 * cm, 0.9 * cm, f"Página {doc.page}")
        canvas.restoreState()

    doc = SimpleDocTemplate(buffer, pagesize=landscape(A4), leftMargin=1.5 * cm, rightMargin=1.5 * cm,
                            topMargin=1.4 * cm, bottomMargin=1.8 * cm, title=titulo,
                            author=Config.NOMBRE_INSTITUCION)
    contenido = [
        Paragraph(Config.NOMBRE_INSTITUCION.upper(), sub),
        Paragraph(titulo, h1),
        Paragraph(" · ".join(f"<b>{e}:</b> {v}" for e, v in filtros), sub),
        Spacer(1, 0.3 * cm),
    ]
    if resumen:
        datos_resumen = [[Paragraph(f"<b>{v}</b><br/>{e}", normal) for e, v in resumen]]
        t = Table(datos_resumen, colWidths=[(landscape(A4)[0] - 3 * cm) / len(resumen)] * len(resumen))
        t.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor(f"#{AZUL_CLARO}")),
            ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#C9D3F7")),
            ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.white),
            ("TOPPADDING", (0, 0), (-1, -1), 6), ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ]))
        contenido += [t, Spacer(1, 0.4 * cm)]

    encabezado = [Paragraph(c["titulo"], celda_titulo) for c in columnas]
    def celda(fila, campo):
        texto = _texto(fila.get(campo))
        color = COLORES_ESTADO.get(str(fila.get(campo))) if campo == "estado" else None
        return Paragraph(f'<font color="#{color}"><b>{texto}</b></font>' if color else texto, normal)

    cuerpo = [[celda(f, c["campo"]) for c in columnas] for f in filas]
    if not cuerpo:
        cuerpo = [[Paragraph("No hay registros con los filtros seleccionados.", normal)] + [""] * (len(columnas) - 1)]
    pesos = [c.get("ancho", 1) for c in columnas]
    disponible = landscape(A4)[0] - 3 * cm
    tabla = Table([encabezado] + cuerpo, repeatRows=1,
                  colWidths=[disponible * p / sum(pesos) for p in pesos])
    estilo = [
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor(f"#{AZUL}")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F5F7FB")]),
        ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#E9EDF3")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 4), ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]
    if not filas:
        estilo.append(("SPAN", (0, 1), (-1, 1)))
    tabla.setStyle(TableStyle(estilo))
    contenido.append(tabla)
    doc.build(contenido, onFirstPage=pie, onLaterPages=pie)
    return buffer.getvalue()


# ----------------------------------------------------------------------------- Excel
def generar_excel(titulo: str, columnas: list[dict], filas: list[dict], filtros: list[tuple[str, str]],
                  resumen: list[tuple[str, str]], generado_por: str) -> bytes:
    libro = Workbook()
    hoja = libro.active
    hoja.title = "Reporte"
    n = len(columnas)
    ultima = get_column_letter(n)
    borde = Border(*(Side(style="thin", color="E9EDF3"),) * 4)

    hoja.merge_cells(f"A1:{ultima}1")
    hoja["A1"] = Config.NOMBRE_INSTITUCION.upper()
    hoja["A1"].font = Font(name="Calibri", size=10, bold=True, color=GRIS)
    hoja.merge_cells(f"A2:{ultima}2")
    hoja["A2"] = titulo
    hoja["A2"].font = Font(name="Calibri", size=16, bold=True, color=AZUL)
    hoja.merge_cells(f"A3:{ultima}3")
    hoja["A3"] = " · ".join(f"{e}: {v}" for e, v in filtros)
    hoja["A3"].font = Font(name="Calibri", size=10, color=GRIS)
    fila_actual = 4
    if resumen:
        hoja.merge_cells(f"A4:{ultima}4")
        hoja["A4"] = "   |   ".join(f"{e}: {v}" for e, v in resumen)
        hoja["A4"].font = Font(name="Calibri", size=10, bold=True, color=AZUL)
        hoja["A4"].fill = PatternFill("solid", fgColor=AZUL_CLARO)
        fila_actual = 5
    fila_actual += 1

    inicio_tabla = fila_actual
    for i, c in enumerate(columnas, start=1):
        celda = hoja.cell(row=fila_actual, column=i, value=c["titulo"])
        celda.font = Font(name="Calibri", bold=True, color="FFFFFF")
        celda.fill = PatternFill("solid", fgColor=AZUL)
        celda.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        celda.border = borde
    for j, f in enumerate(filas, start=1):
        for i, c in enumerate(columnas, start=1):
            valor = f.get(c["campo"])
            if isinstance(valor, str) and valor in COLORES_ESTADO:
                valor = valor.capitalize()
            celda = hoja.cell(row=fila_actual + j, column=i, value=valor)
            celda.border = borde
            celda.font = Font(name="Calibri", size=10)
            if j % 2 == 0:
                celda.fill = PatternFill("solid", fgColor="F5F7FB")
            if c["campo"] == "estado":
                color = COLORES_ESTADO.get(str(f.get("estado")))
                if color:
                    celda.font = Font(name="Calibri", size=10, bold=True, color=color)
    fin_tabla = fila_actual + max(len(filas), 1)
    if not filas:
        hoja.cell(row=fila_actual + 1, column=1, value="No hay registros con los filtros seleccionados.")
    hoja.auto_filter.ref = f"A{inicio_tabla}:{ultima}{fin_tabla}"
    hoja.freeze_panes = f"A{inicio_tabla + 1}"

    for i, c in enumerate(columnas, start=1):
        largo = max([len(str(c["titulo"]))] + [len(str(f.get(c["campo"]) or "")) for f in filas[:500]])
        hoja.column_dimensions[get_column_letter(i)].width = min(max(largo + 3, 10), 45)

    pie = fin_tabla + 2
    hoja.merge_cells(f"A{pie}:{ultima}{pie}")
    hoja[f"A{pie}"] = (f"{Config.NOMBRE_INSTITUCION} · Generado el {datetime.now():%d/%m/%Y %H:%M} "
                       f"por {generado_por} · {len(filas)} registros")
    hoja[f"A{pie}"].font = Font(name="Calibri", size=9, italic=True, color=GRIS)
    hoja.oddFooter.center.text = "Página &P de &N"
    hoja.page_setup.orientation = "landscape"
    hoja.sheet_properties.pageSetUpPr.fitToPage = True
    hoja.page_setup.fitToWidth = 1
    hoja.page_setup.fitToHeight = 0

    buffer = BytesIO()
    libro.save(buffer)
    return buffer.getvalue()
