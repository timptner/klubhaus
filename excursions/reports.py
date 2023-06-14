from pathlib import Path
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfgen.canvas import Canvas
from reportlab.platypus import (
    Table, TableStyle, BaseDocTemplate, Frame, PageTemplate, NextPageTemplate, Image, FrameBreak, Paragraph, PageBreak
)
from reportlab.lib.enums import TA_CENTER

from django.conf import settings

from .models import Excursion, Participant


class ParticipantList:
    def __init__(self, excursion: Excursion):
        self.excursion = excursion

    def generate_pdf(self, file):
        title = "Teilnehmerliste"

        canvas = Canvas(file, pagesize=A4)

        width, height = A4

        doc = BaseDocTemplate(file)

        contents = []

        border = 25 * mm
        header_height = 30 * mm
        logo_width = header_height
        logo_border = 5 * mm

        logo_frame = Frame(
            x1=border,
            y1=height - border - header_height,
            width=logo_width,
            height=header_height,
        )

        header_frame = Frame(
            x1=border + logo_width,
            y1=height - border - header_height,
            width=width - 2 * border - logo_width,
            height=header_height,
        )

        body_frame = Frame(
            x1=border,
            y1=border,
            width=width - 2 * border,
            height=height - 2 * border - header_height,
        )

        page_frame = Frame(
            x1=border,
            y1=border,
            width=width - 2 * border,
            height=height - 2 * border,
        )

        first_page = PageTemplate(id='first_page', frames=[logo_frame, header_frame, body_frame])
        full_page = PageTemplate(id='full_page', frames=page_frame)

        contents.append(NextPageTemplate('first_page'))

        logo_path = Path(settings.STATIC_ROOT) / 'img' / 'logo-512.png'
        logo = Image(
            filename=logo_path,
            width=logo_width - logo_border,
            height=header_height - logo_border,
            kind='proportional',
        )
        logo.hAlign = 'CENTER'
        logo.vAlign = 'CENTER'

        contents.append(logo)
        contents.append(FrameBreak())

        style_sheet = getSampleStyleSheet()

        style_title = style_sheet['Heading1']
        style_title.fontSize = 20
        style_title.fontName = 'Helvetica-Bold'
        style_title.alignment = TA_CENTER

        style_data = style_sheet['Normal']
        style_data.fontSize = 14
        style_data.fontName = 'Helvetica'
        style_data.alignment = TA_CENTER

        canvas.setTitle(title)

        contents.append(Paragraph(title, style_title))
        contents.append(Paragraph(self.excursion.title, style_data))
        text = f"{self.excursion.location}, {self.excursion.date.strftime('%d.%m.%Y')}"
        contents.append(Paragraph(text, style_data))

        contents.append(FrameBreak())

        participants = (
            self.excursion.participant_set
            .filter(state=Participant.APPROVED)
            .order_by('user__last_name', 'user__first_name')
        )

        data = [
            ("Lfd. Nr.", "Nachname", "Vorname", "Matrikelnr.", "Unterschrift")
        ]

        for index, participant in enumerate(participants, start=1):
            row = (
                index,
                participant.user.last_name,
                participant.user.first_name,
                participant.user.student,
                None
            )
            data.append(row)

        table = Table(
            data=data,
            colWidths=[i * (width - 2 * 25 * mm) for i in [.1, .25, .25, .15, .25]],
            rowHeights=(participants.count() + 1) * [10 * mm],
            repeatRows=1
        )

        table_style = TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('GRID', (0, 0), (-1, -1), .25, colors.black),
        ])
        table.setStyle(table_style)

        contents.append(NextPageTemplate('full_page'))
        contents.append(table)

        contents.append(PageBreak())

        doc.addPageTemplates([first_page, full_page])
        doc.build(contents)
