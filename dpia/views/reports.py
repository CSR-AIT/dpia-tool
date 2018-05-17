#!/usr/bin/env python
# coding: utf8

from dpia.modules import *
from io import BytesIO
from django.http import HttpResponse
from django.template.loader import get_template
from django.http import HttpResponse
from django.views.generic import View


### REPORTLAB
## PDF Pagination
class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        canvas.Canvas.__init__(self, *args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        """add page info to each page (page x of y)"""
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_number(num_pages)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)

    def draw_page_number(self, page_count):
        self.setFont("Helvetica", 8)
        self.drawRightString(197*mm, 5*mm,
            "Page %d of %d" % (self._pageNumber, page_count))


def create_table_style(table_name):
    return table_name.setStyle(TableStyle([
                                    ('FONT', (0, 0), (-1, 0), 'Helvetica-Bold'),
                                    ('BACKGROUND', (0, 0), (-1, 0), colors.whitesmoke),
                                    ('FONTSIZE', (0, 0), (-1, -1), 8),
                                    ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),
                                    ('BOX', (0, 0), (-1, -1), 0.25, colors.black),
                                    # ('BOX', (0, 0), (-1, 0), 0.25, colors.black),
                                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                                    ('VALIGN',(0, 0),(-1,-1),'TOP'),
                                ]))


def check_risk_level(impact, max_likelihood):
    level = ''
    if max_likelihood <= "5" and impact <= "5" and impact > "0":
        level = "Negligible... may be taken, especially since the treatment of other risks could also lead to its treatment."
    elif max_likelihood >= "6" and impact <= "5":
        level = "Limited... must be reduced by implementing security measures that reduce its likelihood. Emphasis must be placed on recovery measures."
    elif max_likelihood <= "5" and impact >= "6":
        level = "Significant... must be avoided or reduced by implementing security measures that reduce either its severity or its likelihood. Emphasis must be placed on preventive measures."
    elif max_likelihood >= "6" and impact >= "6":
        level = "Maximum... must absolutely be avoided or reduced by implementing security measures that reduce both its severity and its likelihood. Ideally, care should even be taken to ensure that this risk is treated by independent measures of prevention (actions taken prior to a damaging event), protection (actions taken during a damaging event) and recovery (actions taken after a damaging event)."
    else:
        level = "Not calculated"
    return level

def check_likelihood(likelihood):
    level = ''
    if likelihood < "5" and likelihood > "0":
        level = 'Negligible'
    elif likelihood == "5":
        level = 'Limited'
    elif likelihood == "6":
        level = 'Significant'
    elif likelihood > "6":
        level = 'Maximum'
    else:
        level = 'Not calculated'
    return level

def check_impact(impact):
    level = ''
    if impact < "5" and impact > "0":
        level = 'Negligible'
    elif impact == "5":
        level = 'Limited'
    elif impact == "6":
        level = 'Significant'
    elif impact > "6":
        level = 'Maximum'
    else:
        level = 'Not calculated'
    return level

## ReportLab pdf-generator
# @primary_assets_required
# @supporting_assets_required
# @threats_required
# @threat_assessment_required
# @risk_assessment_required
# @threat_controls_required
# @privacy_targets_required
# @privacy_threats_required
# @privacy_controls_required
@login_required
def pdf_reportlab(request, q_id=None):
    q = get_object_or_404(Questionaire, q_in_membership__member=request.user, id=q_id)
    risks = q.get_risks()
    high_risks = q.get_high_risks()
    high_threats = q.get_high_threats()
    report_time = datetime.now()
    filename = q.description
    # Create the HttpResponse object with the appropriate PDF headers.
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="DPIA report_%s.pdf"' %(filename)

    doc = SimpleDocTemplate(response, pagesize=A4, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30)
    # container for the 'Flowable' objects
    elements = []
    # A large collection of style sheets pre-made for us
    styles = getSampleStyleSheet()
    styles.pagesize = A4
    title = styles['Title']
    styleN = styles['BodyText']
    styleN.alignment = TA_LEFT
    styles.add(ParagraphStyle(name='Subtitle',
                                  parent=styles['Normal'],
                                #   fontName = 'Times',
                                  fontSize=15,
                                  leading=15,
                                  spaceAfter=6,
                                  alignment=TA_CENTER
                                  ),
                   alias='subtitle')
    styles.add(ParagraphStyle(name='TableTitle',
                                    parent=styles['Normal'],
                                    # fontName = 'Times',
                                    fontSize=14,
                                    leading=15,
                                    spaceBefore=14,
                                    spaceAfter=12,
                                    alignment=TA_LEFT
                                      ),
                       alias='tabletitle')
    styles.add(ParagraphStyle(name='SubTableTitle',
                                    parent=styles['Normal'],
                                    # fontName = 'Times',
                                    fontSize=11,
                                    leading=15,
                                    spaceBefore=14,
                                    spaceAfter=7,
                                    alignment=TA_LEFT
                                      ),
                       alias='subtabletitle')
    styles.add(ParagraphStyle(name='TableText',
                                #   fontName='Times',
                                  fontSize=9,
                                  leading=12,
                                  spaceBefore=4,
                                  spaceAfter=4)
                   )
    styles.add(ParagraphStyle(name='TableRedText',
                                #   fontName='Times',
                                  fontSize=9,
                                  leading=12,
                                  backColor=colors.red,
                                  textColor=colors.white,
                                  spaceBefore=4,
                                  spaceAfter=4)
                   )
    styles.add(ParagraphStyle(name='TableOrangeText',
                                #   fontName='Times',
                                  fontSize=9,
                                  leading=12,
                                  backColor=colors.orange,
                                  textColor=colors.white,
                                  spaceBefore=4,
                                  spaceAfter=4)
                   )
    styles.add(ParagraphStyle(name='TableYellowText',
                                #   fontName='Times',
                                  fontSize=9,
                                  leading=12,
                                  backColor=colors.yellow,
                                  textColor=colors.black,
                                  spaceBefore=4,
                                  spaceAfter=4)
                   )
    styles.add(ParagraphStyle(name='TableGreenText',
                                #   fontName='Times',
                                  fontSize=9,
                                  leading=12,
                                  backColor=colors.green,
                                  textColor=colors.white,
                                  spaceBefore=4,
                                  spaceAfter=4)
                   )
    styles.add(ParagraphStyle(name='TableTextIndent',
                                #   fontName='Times',
                                  fontSize=9,
                                  leftIndent=10,
                                  leading=12,
                                  spaceBefore=4,
                                  spaceAfter=4)
                   )


    styles.add(ParagraphStyle(name='Right', alignment=TA_RIGHT), alias='right')
    styleSubtitle = styles['Subtitle']
    styleRight = styles['Right']
    styleTableTitle = styles['TableTitle']
    styleSubTableTitle = styles['SubTableTitle']
    styleTableText = styles['TableText']
    styleTableRedText = styles['TableRedText']
    styleTableOrangeText = styles['TableOrangeText']
    styleTableYellowText = styles['TableYellowText']
    styleTableGreenText = styles['TableGreenText']
    styleTableTextIndent = styles['TableTextIndent']


    elements.append(Paragraph('Data Protection Impact Assessment Report <br/>', title))
    elements.append(Paragraph(q.description, styleSubtitle))
    elements.append(Paragraph('<br/><br/>', styleN))

    ## 1. MEMBERS TABLE
    elements.append(Paragraph('1. Team Members', styleTableTitle))
    # elements.append(HRFlowable(width="100%", thickness=1, lineCap='round', color=colors.gray, spaceBefore=0, spaceAfter=1, hAlign='LEFT', vAlign='TOP', dash=None))
    members_table = [['#', 'Name', 'Expertise', 'Responsibility in DPIA'],]
    if q.q_in_membership.exists():
        for i, membership in enumerate(q.q_in_membership.all()):
            # Add rows to the table
            name = ''
            if membership.member.get_full_name():
                name = membership.member.get_full_name()
            else:
                name = membership.member.username
            members_table.append([
                                str(i+1),
                                Paragraph(name, styleTableText),
                                Paragraph(membership.member.profile.expertise, styleTableText),
                                Paragraph(membership.responsibility_in_dpia, styleTableText)
                            ])
    # Create the table
    user_table = Table(members_table, hAlign='LEFT', colWidths=[0.25*inch, None, None, None], repeatRows=True, splitByRow=1) #colWidths=[doc.width/4.0]*3,
    create_table_style(user_table)
    elements.append(user_table)
    elements.append(Paragraph('<br/><br/>', styleN))

    # ------------ #

    ## 2. SOURCES TABLE
    elements.append(Paragraph('2. Sources', styleTableTitle))
    sources_table = [['#', 'Name', 'Description', 'Type', 'Purpose'],]
    if q.q_in_source.exists():
        for i, source in enumerate(q.q_in_source.all()):
            # Add a row to the table
            sources_table.append([str(i+1),
                                    Paragraph(source.name, styleTableText),
                                    Paragraph(source.description, styleTableText),
                                    source.source_type,
                                    source.purpose])
    else:
        sources_table.append(['', Paragraph('0 sources.', styleTableYellowText)])
    source_table = Table(sources_table, hAlign='LEFT', colWidths=[0.25*inch, None, None, None, None], repeatRows=True, splitByRow=1)
    create_table_style(source_table)
    elements.append(source_table)
    # elements.append(PageBreak())
    elements.append(Paragraph('<br/><br/>', styleN))

    # ------------ #

    ## 3. USECASES TABLE
    # elements.append(Paragraph('3. Use cases', styleTableTitle))
    # for i, usecase in enumerate(q.usecase.all()):
    #     elements.append(Paragraph('3.' + str(i+1) + '. ' + usecase.name, styleSubTableTitle))
    #     elements.append(Paragraph('<strong>Description: </strong>' + usecase.description, styleTableText))
    #     elements.append(Paragraph('<strong>Domain: </strong>' + usecase.domain, styleTableText))
    #     elements.append(Paragraph('<strong>Business Goal: </strong>' + usecase.business_goal, styleTableText))
    #     elements.append(Paragraph('<br/>', styleN))
    #     # elements.append(Paragraph('<strong>Scenario: </strong>', styleTableText))
    #     # query all the processes of the usecase
    #     processes = usecase.process.all()
    #     # Processes TABLE
    #     processes_table = [['#', 'Description', 'Information Exchanged', 'Information Producer', 'Information Receiver'],]
    #
    #     for j, process in enumerate(processes):
    #         # Add processes to the table
    #         processes_table.append([str(j+1), Paragraph(process.description, styleTableText), Paragraph(process.information_exchanged.name, styleTableText), Paragraph(process.information_producer.name, styleTableText), Paragraph(process.information_receiver.name, styleTableText)])
    #
    #     # Create the table
    #     process_table = Table(processes_table, hAlign='LEFT', colWidths=[0.25*inch, 2*inch, None, None, None], repeatRows=True, splitByRow=1) #colWidths=[doc.width/5.0]*5,
    #     process_table.setStyle(TableStyle([
    #                                     ('FONT', (0, 0), (-1, 0), 'Helvetica-Bold'),
    #                                     ('BACKGROUND', (0, 0), (-1, 0), colors.whitesmoke),
    #                                     ('FONTSIZE', (0, 0), (-1, -1), 8),
    #                                     ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),
    #                                     ('BOX', (0, 0), (-1, -1), 0.25, colors.black),
    #                                     ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
    #                                     ('VALIGN',(0, 0),(-1,-1),'TOP'),
    #                                     ]))
    #
    #     elements.append(process_table)
    #     elements.append(Paragraph('<br/><br/>', styleN))
    #
    # elements.append(PageBreak())

    # ------------ #

    ## 4. PRIMARY ASSETS TABLE
    elements.append(Paragraph('3. Primary Assets and Supporting Assets', styleTableTitle))
    primaries_table = [['#', 'Name', 'Reading frequency', 'Retention Time', 'Supporting Assets'],]
    primaries = q.q_in_primary.all()
    if primaries.exists():
        for i, primary in enumerate(primaries):
            supporting_assets = [pa_sa_rel.supporting.description for pa_sa_rel in primary.primary_in_psrel.all()]
            # supporting_assets_split = [sa.split() for sa in supporting_assets]
            #
            # for sa in supporting_assets:
            #     sa_split = sa.split()
            #     text = ''.join([word for word in sa_split])
            #     print(text)
            # Add Primary Assets to the table
            primaries_table.append([
                str(i+1),
                Paragraph(primary.name, styleTableText),
                Paragraph(primary.reading_frequency, styleTableText),
                Paragraph(primary.retention_time, styleTableText),
                Paragraph('; '.join([sa for sa in supporting_assets]), styleTableText)
                ])
    else:
        primaries_table.append(['', Paragraph('0 primary assets.', styleTableYellowText)])
    # Create the table
    primary_table = Table(primaries_table, hAlign='LEFT', colWidths=[0.25*inch, 2*inch, None, None, None], repeatRows=True, splitByRow=1) #colWidths=[doc.width/5.0]*5,
    create_table_style(primary_table)
    elements.append(primary_table)
    elements.append(Paragraph('<br/><br/>', styleN))
    # elements.append(PageBreak())

    ## 5. SUMMARY OF DPIA RESULTS
    # 5.1. Risk Levels Table
    elements.append(Paragraph('4. Summary of DPIA Results', styleTableTitle))
    elements.append(Paragraph('4.1. Summary of Highest Risks', styleSubTableTitle))
    risk_levels_table = [['#', 'Type of Jeopardy', 'Risk Level'],]
    if high_risks.exists():
        for i, risk in enumerate(high_risks):
            impact = str(risk.impact)
            max_likelihood = str(risk.max_likelihood)
            risk_level = check_risk_level(impact, max_likelihood)
            pa_name = ''
            if risk.primary_asset_affected.name:
                pa_name = risk.primary_asset_affected.name
            risk_levels_table.append([
                str(i+1),
                Paragraph(str(risk.type_of_jeopardy) + ' of ' + pa_name, styleTableText),
                Paragraph(risk_level, styleTableText)
            ])
    else:
        risk_levels_table.append(['', Paragraph('0 high risks.', styleTableYellowText)])

    # Create the table
    risk_level_table = Table(risk_levels_table, hAlign='LEFT', colWidths=[0.25*inch, 2*inch, None], repeatRows=True, splitByRow=1) #colWidths=[doc.width/5.0]*5,
    create_table_style(risk_level_table)
    elements.append(risk_level_table)
    elements.append(Paragraph('<br/>', styleN))

    # 5.2. Summary of Essential Controls
    elements.append(Paragraph('4.2. Summary of Essential Controls', styleSubTableTitle))
    threat_controls_table = [['#', 'Affected Supporting Asset', 'Threat', 'Likelihood', 'Control'],]
    if high_threats.exists():
        for i, threat_sa_rel in enumerate(high_threats):
            likelihood = str(threat_sa_rel.likelihood)
            likelihood_level = check_likelihood(likelihood)
            sa_desc = ''
            threat_control = 'None'
            if threat_sa_rel.affected_supporting_asset.description:
                sa_desc = threat_sa_rel.affected_supporting_asset.description
            if threat_sa_rel.control:
                threat_control = threat_sa_rel.control
            threat_controls_table.append([
                str(i+1),
                Paragraph(sa_desc, styleTableText),
                Paragraph(threat_sa_rel.threat.name, styleTableText),
                Paragraph(likelihood_level, styleTableText),
                Paragraph(threat_control, styleTableText)
            ])
    else:
        threat_controls_table.append(['', Paragraph("0 hight threats.", styleTableYellowText)])
    # Create the table
    threat_control_table = Table(threat_controls_table, hAlign='LEFT', colWidths=[0.25*inch, None, None, 0.8*inch, None], repeatRows=True, splitByRow=1) #colWidths=[doc.width/5.0]*5,
    create_table_style(threat_control_table)
    elements.append(threat_control_table)
    elements.append(Paragraph('<br/><br/>', styleN))


    # 6. RISKS
    elements.append(Paragraph('5. Risks', styleTableTitle))
    if risks.exists():
        risk_length = risks.count()
        for i, risk in enumerate(risks):
            impact = str(risk.impact)
            max_likelihood = str(risk.max_likelihood)
            pa_name = ''
            consequences = 'None'
            risk_treatment = 'None'
            residual_risk = 'None'
            if risk.primary_asset_affected.name:
                pa_name = risk.primary_asset_affected.name
            if risk.consequences:
                consequences = risk.consequences
            if risk.risk_treatment:
                risk_treatment = risk.risk_treatment
            if risk.residual_risk:
                residual_risk = risk.residual_risk

            risk_level = check_risk_level(impact, max_likelihood)
            elements.append(Paragraph('5.' + str(i+1) + '.' + ' Risk to ' + str(risk.type_of_jeopardy) + ' of ' + pa_name, styleSubTableTitle))
            elements.append(Paragraph("<strong>Risk level: </strong>" + risk_level, styleTableText))
            elements.append(Paragraph('<strong>Consequences: </strong>' + consequences, styleTableText))
            elements.append(Paragraph('<strong>Risk owner: </strong>' + str(risk.risk_owner), styleTableText))
            impact_level = check_impact(impact)
            elements.append(Paragraph('<strong>Impact: </strong>' + impact_level, styleTableText))
            elements.append(Paragraph('<strong>Level of Identification: </strong>' + str(risk.primary_asset_affected.get_level_of_identification_display()), styleTableTextIndent))
            elements.append(Paragraph('<strong>Prejudicial Effects: </strong>' + str(risk.get_prejudicial_effects_display()), styleTableTextIndent))
            elements.append(Paragraph('<strong>Risk treatment: </strong>' + risk_treatment, styleTableText))
            elements.append(Paragraph('<strong>Residual risk: </strong>' + residual_risk, styleTableText))
            elements.append(Paragraph('Potential Threats', styleSubTableTitle))
            risks_table = [['Affected Supporting Asset', 'Threat', 'Level of vulnerability', 'Risk Source Capability', 'Likelihood',],]
            threat_sa_rels = Threat_SA_REL.objects.select_related('threat', 'affected_supporting_asset').filter(affected_supporting_asset__primary=risk.primary_asset_affected,
                    affected_supporting_asset__supporting_in_psrel__isnull=False).order_by('-likelihood').distinct()
            for j, threat_sa_rel in enumerate(threat_sa_rels):
                if str(threat_sa_rel.threat.type_of_jeopardy) == (risk.type_of_jeopardy):
                    sa_desc = ''
                    if threat_sa_rel.affected_supporting_asset.description:
                        sa_desc = threat_sa_rel.affected_supporting_asset.description
                    likelihood = str(threat_sa_rel.likelihood)
                    likelihood_level = check_likelihood(likelihood)
                    risks_table.append([
                        Paragraph(sa_desc, styleTableText),
                        Paragraph(threat_sa_rel.threat.name, styleTableText),
                        Paragraph(str(threat_sa_rel.get_level_of_vulnerability_display()), styleTableText),
                        Paragraph(str(threat_sa_rel.get_risk_source_capability_display()), styleTableText),
                        Paragraph(likelihood_level, styleTableText)
                    ])

            # Create the table
            risk_table = Table(risks_table, hAlign='LEFT', colWidths=[None, None, None, None, None], repeatRows=True, splitByRow=1) #colWidths=[doc.width/5.0]*5,
            create_table_style(risk_table)
            elements.append(risk_table)
            elements.append(Paragraph('<br/>', styleN))

            ## Risk-threat-controls
            elements.append(Paragraph('Threat Controls', styleSubTableTitle))
            risks_controls_table = [['Affected Supporting Asset', 'Threat', 'Controls',],]
            for j, threat_sa_rel in enumerate(threat_sa_rels):
                if str(threat_sa_rel.threat.type_of_jeopardy) == (risk.type_of_jeopardy):
                    sa_desc = ''
                    threat_control = 'None'
                    if threat_sa_rel.affected_supporting_asset.description:
                        sa_desc = threat_sa_rel.affected_supporting_asset.description
                    if threat_sa_rel.control:
                        threat_control = threat_sa_rel.control
                    risks_controls_table.append([
                        Paragraph(sa_desc, styleTableText),
                        Paragraph(threat_sa_rel.threat.name, styleTableText),
                        Paragraph(threat_control, styleTableText),
                    ])
            # Create the table
            risks_control_table = Table(risks_controls_table, hAlign='LEFT', colWidths=[None, None, None], repeatRows=True, splitByRow=1) #colWidths=[doc.width/5.0]*5,
            create_table_style(risks_control_table)
            elements.append(risks_control_table)
            elements.append(Paragraph('<br/><br/>', styleN))
    else:
        elements.append(Paragraph('0 risks.', styleTableYellowText))
    elements.append(Paragraph('<br/><br/>', styleN))



    ## 7. PRIVACY TARGETS and PRIVACY THREATS TABLE
    elements.append(Paragraph('6. Privacy Targets', styleTableTitle))
    if q.q_in_pqrel.exists():
        for i, p_q_rel in enumerate(q.q_in_pqrel.all()):
            elements.append(Paragraph('6.' + str(i+1) + '. ' +  str(p_q_rel.privacy_target.name), styleSubTableTitle))
            elements.append(Paragraph('<strong>Description: </strong>' + str(p_q_rel.privacy_target.description), styleTableText))
            elements.append(Paragraph('Potential Threats', styleSubTableTitle))

            pthreats_table = [['#', 'Privacy Threat', 'Affected Primary Assets', 'Privacy Controls' ],] ## TABLE
            if p_q_rel.pqrel_in_pthreatrel.exists():
                for j, p_threat_rel in enumerate(p_q_rel.pqrel_in_pthreatrel.all()):
                    affected_assets = [target_threat_rel.name for target_threat_rel in p_threat_rel.affected_primary_assets.all()]
                    privacy_controls = [str(threat_control.name) for threat_control in p_threat_rel.controls.all()]
                    pthreats_table.append([
                        str(j+1),
                        Paragraph(str(p_threat_rel.privacy_threat.name), styleTableText),
                        Paragraph('<br/>'.join([asset for asset in affected_assets]), styleTableText),
                        Paragraph('<br/>'.join([str(control) for control in privacy_controls]), styleTableText)
                        ])
            else:
                pthreats_table.append(['', Paragraph("0 privacy threats.", styleTableText)])
            # Create the table
            target_table = Table(pthreats_table, hAlign='LEFT', colWidths=[0.25*inch, 2*inch, None, None, None], repeatRows=True, splitByRow=1) #colWidths=[doc.width/5.0]*5,
            create_table_style(target_table)
            elements.append(target_table)
            elements.append(Paragraph('<br/>', styleTableText))
        elements.append(Paragraph('<br/><br/>', styleN))
    else:
        elements.append(Paragraph('0 privacy targets.', styleTableYellowText))
    elements.append(Paragraph('<br/><br/>', styleN))

    ## Appendix A: Supporting Assets Types
    elements.append(Paragraph('Appendix A: Supporting Asset Types', styleTableTitle))
    supportings_table = [['#', 'Description', 'Support Asset Type'],]
    if q.q_in_supporting.exists():
        for i, supporting in enumerate(q.q_in_supporting.all()):
            supportings_table.append([str(i+1), Paragraph(supporting.description, styleTableText), str(supporting.supporting_type)])
    else:
        supportings_table.append(["", Paragraph("0 supporting assets.", styleTableYellowText)])
    # Create the table
    supporting_table = Table(supportings_table, hAlign='LEFT', colWidths=[0.25*inch, None, None, None, None], repeatRows=True, splitByRow=1)
    create_table_style(supporting_table)
    elements.append(supporting_table)

    ## Build PDF and define numbered pages
    doc.build(elements, canvasmaker=NumberedCanvas)
    file_size = len(response.content)
    return response



### GENERATE WORD DOCX
## set column width
def set_column_width(column, width):
    for cell in column.cells:
        cell.width = width

# @primary_assets_required
# @supporting_assets_required
# @threats_required
# @threat_assessment_required
# @risk_assessment_required
# @threat_controls_required
# @privacy_targets_required
# @privacy_threats_required
# @privacy_controls_required
@login_required
def generate_docx(request, q_id=None):
    q = get_object_or_404(Questionaire, q_in_membership__member=request.user, id=q_id)
    risks = q.get_risks()
    high_risks = q.get_high_risks()
    high_threats = q.get_high_threats()
    ## Document properties
    document = Document()
    style = document.styles['Normal']
    font = style.font
    font.name = 'Calibri'
    font.size = Pt(11)
    paragraph_format = style.paragraph_format
    paragraph_format.space_after = Pt(1.3)

    ## Doc Title
    document.add_heading('DPIA report: %s' %(q.description), 0)
    ### Members
    heading_members = document.add_heading('1. Members', level=1)
    members_table = document.add_table(1, 4)
    # members_table.autofit = False  # defaults to True, so have to explicitly turn it off
    # members_table.columns[0].width = Inches(1.5)
    members_table.style = 'Light Shading Accent 1'
    set_column_width(members_table.columns[3], Cm(5))
    # populate header row
    heading_cells = members_table.rows[0].cells
    heading_cells[0].text = '#'
    heading_cells[1].text = 'Name'
    heading_cells[2].text = 'Expertise'
    heading_cells[3].text = 'Responsibility in DPIA'
    # add a data row for each item
    memberships = q.q_in_membership.all()
    if memberships:
        for i, membership in enumerate(memberships):
            name = ''
            if membership.member.get_full_name():
                name = membership.member.get_full_name()
            else:
                name = membership.member.username
            cells = members_table.add_row().cells
            cells[0].text = str(i+1)
            cells[1].text = name
            cells[2].text = membership.member.profile.expertise
            cells[3].text = membership.responsibility_in_dpia
    document.add_paragraph('') ## Empty row

    ### Sources
    heading_sources = document.add_heading('2. Sources', level=1)
    sources_table = document.add_table(1, 5)
    sources_table.style = 'Light Shading Accent 1'
    set_column_width(sources_table.columns[1], Cm(5))
    set_column_width(sources_table.columns[2], Cm(5))
    # populate header row
    heading_cells = sources_table.rows[0].cells
    heading_cells[0].text = '#'
    heading_cells[1].text = 'Name'
    heading_cells[2].text = 'Description'
    heading_cells[3].text = 'Type'
    heading_cells[4].text = 'Purpose'
    # add a data row for each item
    sources = q.q_in_source.all()
    if sources.exists():
        for i, source in enumerate(sources):
            cells = sources_table.add_row().cells
            cells[0].text = str(i+1)
            cells[1].text = source.name
            cells[2].text = source.description
            cells[3].text = source.source_type
            cells[4].text = source.purpose
    else:
        cells = sources_table.add_row().cells
        cells[0].text = "0 sources."
    # document.add_page_break() ##Page break
    document.add_paragraph('') ## Empty row

    # ### Use Cases
    # heading_usecases = document.add_heading('3. Use Cases', level=1)
    # usecases = q.usecase.all()
    # for i, usecase in enumerate(usecases):
    #     document.add_heading('3.%s. %s' %(str(i+1), usecase.name), level=2)
    #     paragraph_usecase_description = document.add_paragraph('Description: %s' %(usecase.description))
    #     paragraph_usecase_domain = document.add_paragraph('Domain: %s' %(usecase.domain))
    #     paragraph_usecase_business_goal = document.add_paragraph('Business goal: %s' %(usecase.business_goal))
    #
    #     ## Table of processes
    #     heading_scenario = document.add_heading('Scenario', level=3)
    #     processes_table = document.add_table(1, 5)
    #     processes_table.style = 'Light Shading Accent 1'
    #     set_column_width(processes_table.columns[1], Cm(5))
    #     # populate header row
    #     heading_cells = processes_table.rows[0].cells
    #     heading_cells[0].text = '#'
    #     heading_cells[1].text = 'Description'
    #     heading_cells[2].text = 'Information Exchanged'
    #     heading_cells[3].text = 'Information Producer'
    #     heading_cells[4].text = 'Information Receiver'
    #     # query processes of every usecase
    #     processes = usecase.process.all() #process.objects.select_related('usecase', 'information_producer', 'information_receiver', 'information_exchanged').filter(usecases=usecase)
    #     for i, process in enumerate(processes):
    #         cells = processes_table.add_row().cells
    #         cells[0].text = str(i+1)
    #         cells[1].text = process.description
    #         cells[2].text = process.information_exchanged.name
    #         cells[3].text = process.information_producer.name
    #         cells[4].text = process.information_receiver.name
    #
    #
    #     document.add_paragraph('') ## Empty row
    #
    # document.add_page_break() ##Page break

    ### Primary and Supporting Assets
    heading_primaries = document.add_heading('3. Primary and Supporting Assets', level=1)
    ## Table of primary and supporting assets
    primaries_table = document.add_table(1, 5)
    primaries_table.style = 'Light Shading Accent 1'
    set_column_width(primaries_table.columns[0], Cm(6))
    set_column_width(primaries_table.columns[2], Cm(4))
    # populate header
    heading_cells = primaries_table.rows[0].cells
    heading_cells[0].text = '#'
    heading_cells[1].text = 'Name'
    heading_cells[2].text = 'Reading frequency'
    heading_cells[3].text = 'Retention time'
    heading_cells[4].text = 'Supporting assets'
    #query primary assets and supporting assets of every primary asset
    primaries = q.q_in_primary.all()
    if primaries.exists():
        for i, primary in enumerate(primaries):
            # if primary.primary_in_psrel.exists():
            supporting_assets = [pa_sa_rel.supporting.description for pa_sa_rel in primary.primary_in_psrel.all()] ## query the desc of supporting asset
            cells = primaries_table.add_row().cells
            cells[0].text = str(i+1)
            cells[1].text = primary.name
            cells[2].text = primary.reading_frequency
            cells[3].text = primary.retention_time
            cells[4].text = '; '.join([sa for sa in supporting_assets]) ## new line per each supporting asset
    else:
        cells = primaries_table.add_row().cells
        cells[0].text = "0 primary assets."
    # document.add_page_break() ##Page break
    document.add_paragraph('') ## Empty row

    ### High Risks
    document.add_heading('4. Summary of DPIA Results', level=1)
    heading_high_risks = document.add_heading('4.1. Summary of high risks', level=2)
    ## table
    high_risks_table = document.add_table(1, 3)
    high_risks_table.style = 'Light Shading Accent 1'
    set_column_width(high_risks_table.columns[2], Cm(15))
    # high_risks_table.allow_autofit = True
    # populate header
    heading_cells = high_risks_table.rows[0].cells
    heading_cells[0].text = '#'
    heading_cells[1].text = 'Type of jeopardy'
    heading_cells[2].text = 'Risk level'
    # query only the high risks
    if high_risks.exists():
        for i, high_risk in enumerate(high_risks):
            pa_name = ''
            if high_risk.primary_asset_affected.name:
                pa_name = high_risk.primary_asset_affected.name
            cells = high_risks_table.add_row().cells
            cells[0].text = str(i+1)
            cells[1].text = str(high_risk.type_of_jeopardy) + ' of ' + pa_name
            impact = str(high_risk.impact)
            max_likelihood = str(high_risk.max_likelihood)
            risk_level = check_risk_level(impact, max_likelihood)
            cells[2].text = risk_level
    else:
        cells = high_risks_table.add_row().cells
        cells[0].text = "0 high risks."
    document.add_paragraph('') ## Empty row

    ### High Threats
    heading_high_threats = document.add_heading('4.2. Summary of essential controls', level=2)
    ## table
    high_threats_table = document.add_table(1, 5)
    high_threats_table.style = 'Light Shading Accent 1'
    # high_threats_table.allow_autofit = True
    set_column_width(high_threats_table.columns[4], Cm(15))
    # populate header
    heading_cells = high_threats_table.rows[0].cells
    heading_cells[0].text = '#'
    heading_cells[1].text = 'Affected supporting asset'
    heading_cells[2].text = 'Threat'
    heading_cells[3].text = 'Likelihood'
    heading_cells[4].text = 'Control'
    # query only the high threats
    if high_threats.exists():
        for i, high_threat in enumerate(high_threats):
            sa_desc = ''
            threat_control = ''
            if high_threat.affected_supporting_asset.description:
                sa_desc = high_threat.affected_supporting_asset.description
            if high_threat.control:
                threat_control = high_threat.control
            cells = high_threats_table.add_row().cells
            cells[0].text = str(i+1)
            cells[1].text = sa_desc
            cells[2].text = high_threat.threat.name
            likelihood_level = check_likelihood(str(high_threat.likelihood))
            cells[3].text = likelihood_level
            cells[4].text = threat_control
    else:
        cells = high_threats_table.add_row().cells
        cells[0].text = "0 high threats."
    # document.add_page_break() ##Page break
    document.add_paragraph('') ## Empty row


    ### All Risks
    heading_risks = document.add_heading('5. Risks', level=1)
    risk_length = risks.count()
    if risks.exists():
        for i, risk in enumerate(risks):
            pa_name = ''
            consequences = 'None'
            risk_treatment = 'None'
            residual_risk = 'None'
            if risk.primary_asset_affected.name:
                pa_name = risk.primary_asset_affected.name
            if risk.consequences:
                consequences = risk.consequences
            if risk.risk_treatment:
                risk_treatment = risk.risk_treatment
            if risk.residual_risk:
                residual_risk = risk.residual_risk
            paragraph_risk_name = document.add_heading('5.%s. Risk to %s of %s' %(str(i+1), str(risk.type_of_jeopardy), pa_name), level=2)
            impact = str(risk.impact)
            max_likelihood = str(risk.max_likelihood)
            risk_level = check_risk_level(impact, max_likelihood)
            document.add_paragraph('Risk level: ' + risk_level)
            paragraph_risk_consequences = document.add_paragraph('Consequences: %s' %(consequences))
            paragraph_risk_owner = document.add_paragraph('Risk owner: %s' %(risk.risk_owner))
            impact_level = check_impact(impact)
            document.add_paragraph('Impact: ' + impact_level)
            paragraph_loi = document.add_paragraph('Level of Identification: %s' %(str(risk.primary_asset_affected.get_level_of_identification_display())))
            paragraph_loi.style = 'List Bullet'
            paragraph_pe = document.add_paragraph('Prejudicial Effects: %s' %(str(risk.get_prejudicial_effects_display())))
            paragraph_pe.style = 'List Bullet'
            paragraph_risk_treatment = document.add_paragraph('Risk treatment: %s' %(risk_treatment))
            paragraph_residual_risk = document.add_paragraph('Residual risk: %s' %(residual_risk))

            ## Potential threats
            heading_threats = document.add_heading('Potential Threats', level=3)
            risk_threats_table = document.add_table(1, 5)
            risk_threats_table.style = 'Light Shading Accent 1'
            set_column_width(risk_threats_table.columns[0], Cm(0.5))
            # populate header row
            heading_cells = risk_threats_table.rows[0].cells
            # heading_cells[0].text = '#'
            heading_cells[0].text = 'Affected supporting asset'
            heading_cells[1].text = 'Threat'
            heading_cells[2].text = 'Level of vulnerability'
            heading_cells[3].text = 'Risk source capability'
            heading_cells[4].text = 'Likelihood'
            # query threats of every risk
            threat_sa_rels = Threat_SA_REL.objects.select_related('threat', 'affected_supporting_asset').filter(affected_supporting_asset__primary=risk.primary_asset_affected,
                                affected_supporting_asset__supporting_in_psrel__isnull=False).order_by('-likelihood').distinct()
            if threat_sa_rels:
                for i, threat_sa_rel in enumerate(threat_sa_rels):
                    if str(threat_sa_rel.threat.type_of_jeopardy) == (risk.type_of_jeopardy):
                        sa_desc = ''
                        if threat_sa_rel.affected_supporting_asset.description:
                            sa_desc = threat_sa_rel.affected_supporting_asset.description
                        cells = risk_threats_table.add_row().cells
                        # cells[0].text = str(i+1)
                        cells[0].text = sa_desc
                        cells[1].text = threat_sa_rel.threat.name
                        cells[2].text = str(threat_sa_rel.get_level_of_vulnerability_display())
                        cells[3].text =str(threat_sa_rel.get_risk_source_capability_display())
                        likelihood_level = check_likelihood(str(threat_sa_rel.likelihood))
                        cells[4].text = likelihood_level

                ## Controls of the potential threats
                heading_scenario = document.add_heading('Threat controls', level=3)
                threat_controls_table = document.add_table(1, 3)
                # threat_controls_table.allow_autofit = True
                threat_controls_table.style = 'Light Shading Accent 1'
                set_column_width(threat_controls_table.columns[2], Cm(15))
                # document.add_paragraph('') ## Empty row
                for i, threat_sa_rel in enumerate(threat_sa_rels):
                    if str(threat_sa_rel.threat.type_of_jeopardy) == (risk.type_of_jeopardy):
                        sa_desc = ''
                        threat_control = 'None'
                        if threat_sa_rel.affected_supporting_asset.description:
                            sa_desc = threat_sa_rel.affected_supporting_asset.description
                        if threat_sa_rel.control:
                            threat_control = threat_sa_rel.control
                        # populate header row
                        heading_cells = threat_controls_table.rows[0].cells
                        # heading_cells[0].text = '#'
                        heading_cells[0].text = 'Affected supporting asset'
                        heading_cells[1].text = 'Threat'
                        heading_cells[2].text = 'Controls'
                        # query threats controls of every risk
                        cells = threat_controls_table.add_row().cells
                        # cells[0].text = str(i+1)
                        cells[0].text = sa_desc
                        cells[1].text = threat_sa_rel.threat.name
                        cells[2].text = threat_control
            else:
                cells = risk_threats_table.add_row().cells
                cells[0].text = "0 potential threats."
            document.add_paragraph('') ## Empty row
    else:
        document.add_heading('0 risks.', level=2)
    # document.add_page_break() ##Page break
    document.add_paragraph('') ## Empty row


    ### Privacy targets, threats and controls
    heading_privacy = document.add_heading('6. Privacy Targets')
    if q.q_in_pqrel.exists():
        for i, p_q_rel in enumerate(q.q_in_pqrel.all()):
            privacy_paragraph = document.add_heading('6.%s. %s' %(str(i+1), str(p_q_rel.privacy_target.name)), level=2)
            privacy_description_paragraph = document.add_paragraph('Description: %s' %(str(p_q_rel.privacy_target.description)))
            ## Potential threats of privacy targets
            heading_scenario = document.add_heading('Potential Threats', level=3)
            privacy_threats_table = document.add_table(1, 4)
            privacy_threats_table.style = 'Light Shading Accent 1'
            set_column_width(privacy_threats_table.columns[1], Cm(4))
            set_column_width(privacy_threats_table.columns[3], Cm(10))
            # populate header row
            heading_cells = privacy_threats_table.rows[0].cells
            heading_cells[0].text = '#'
            heading_cells[1].text = 'Privacy Threat'
            heading_cells[2].text = 'Affected Primary Assets'
            heading_cells[3].text = 'Privacy Controls'
            # query threats and controls of the privacy targets
            if p_q_rel.pqrel_in_pthreatrel.exists():
                for i, privacy_threat_rel in enumerate(p_q_rel.pqrel_in_pthreatrel.all()):
                    cells = privacy_threats_table.add_row().cells
                    cells[0].text = str(i+1)
                    cells[1].text = str(privacy_threat_rel.privacy_threat.name)
                    affected_assets = [target_threat_rel.name for target_threat_rel in privacy_threat_rel.affected_primary_assets.all()]
                    privacy_controls = [str(threat_control.name) for threat_control in privacy_threat_rel.controls.all()]
                    cells[2].text = '\n'.join([privacy_assets for privacy_assets in affected_assets])
                    cells[3].text = '\n'.join([str(privacy_control) for privacy_control in privacy_controls])
            else:
                cells = privacy_threats_table.add_row().cells
                cells[0].text = "0 privacy threats."
            document.add_paragraph('') ## Empty row
    else:
        document.add_heading('0 privacy targets.', level=2)

    document.add_paragraph('') ## Empty row
    ## Appendix
    heading_privacy = document.add_heading('Appendix A: Supporting Asset Types')
    appendix_table = document.add_table(1, 3)
    appendix_table.style = 'Light Shading Accent 1'
    set_column_width(appendix_table.columns[0], Cm(1))
    set_column_width(appendix_table.columns[1], Cm(10))
    set_column_width(appendix_table.columns[2], Cm(10))
    # populate header row
    heading_cells = appendix_table.rows[0].cells
    heading_cells[0].text = '#'
    heading_cells[1].text = 'Description'
    heading_cells[2].text = 'Supporting Asset Type'
    if q.q_in_supporting.exists():
        for i, sa in enumerate(q.q_in_supporting.all()):
            cells = appendix_table.add_row().cells
            cells[0].text = str(i+1)
            cells[1].text = sa.description
            cells[2].text = str(sa.supporting_type)
    document.add_paragraph('') ## Empty row

    ### save the document
    f = StringIO.StringIO()
    document.save(f)
    length = f.tell()
    f.seek(0)
    response = HttpResponse(
        f.getvalue(),
        content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    )
    response['Content-Disposition'] = 'attachment; filename="DPIA report_%s.docx"' %(q.description)
    response['Content-Length'] = length
    return response
