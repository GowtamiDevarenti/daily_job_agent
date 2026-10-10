from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

def build_pdf():
    pdf_filename = "CV_Gowtami_Devarenti.pdf"
    doc = SimpleDocTemplate(
        pdf_filename,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()
    
    # Custom styles
    name_style = ParagraphStyle(
        'NameStyle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=24,
        textColor=colors.HexColor('#1E3C72'),
        alignment=0,
        spaceAfter=4
    )

    contact_style = ParagraphStyle(
        'ContactStyle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=13,
        textColor=colors.HexColor('#4A5568'),
        spaceAfter=10
    )

    heading_style = ParagraphStyle(
        'HeadingStyle',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=15,
        textColor=colors.HexColor('#1E3C72'),
        spaceBefore=10,
        spaceAfter=4
    )

    body_style = ParagraphStyle(
        'BodyStyle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=13.5,
        textColor=colors.HexColor('#2D3748'),
        spaceAfter=6
    )

    bullet_style = ParagraphStyle(
        'BulletStyle',
        parent=body_style,
        leftIndent=12,
        firstLineIndent=-8,
        spaceAfter=4
    )

    story = []

    # Name & Contact
    story.append(Paragraph("GOWTAMI DEVARENTI", name_style))
    story.append(Paragraph("Göteborg, Sweden | gowtamiamarnath@gmail.com | github.com/GowtamiDevarenti | Full Right to Work in Sweden (EU/EEA / Permanent Resident)", contact_style))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#CBD5E1'), spaceAfter=10))

    # Summary
    story.append(Paragraph("PROFESSIONAL SUMMARY", heading_style))
    story.append(Paragraph("Analytical <b>Python AI/ML Developer</b> & <b>MBA in Finance</b> graduate with proven business leadership experience managing cross-functional teams of 40. Currently undergoing intensive software engineering and machine learning training at <b>Lexicon IT-Proffs, Stockholm</b> (Sept 2026 – March 2027). Skilled in Python (intermediate), SQL database querying, Git/GitHub, Data Analytics, and Machine Learning. Seeking Junior Developer, Data Analyst, Data Engineer, or LIA Internship roles in Göteborg or Remote.", body_style))

    # Education
    story.append(Paragraph("EDUCATION & FORMAL TRAINING", heading_style))
    story.append(Paragraph("• <b>Python AI/ML Developer Program</b> | Lexicon IT-Proffs, Stockholm (Sept 2026 – March 2027)", bullet_style))
    story.append(Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;<i>Core Subjects: Advanced Python, SQL Database Design, Machine Learning Algorithms, Data Pipelines, Git/GitHub Version Control, Agile Development.</i>", bullet_style))
    story.append(Paragraph("• <b>MBA in Finance</b> | Business Administration", bullet_style))
    story.append(Paragraph("&nbsp;&nbsp;&nbsp;&nbsp;<i>Specialization: Financial Analysis, Strategic Management, Quantitative Analytics.</i>", bullet_style))

    # Skills
    story.append(Paragraph("TECHNICAL SKILLS & COMPETENCIES", heading_style))
    story.append(Paragraph("• <b>Programming Languages:</b> Python (basic-to-intermediate), SQL", bullet_style))
    story.append(Paragraph("• <b>Data Analytics & AI/ML:</b> Machine Learning Fundamentals, Data Cleaning, Data Pipelines, Pandas, NumPy", bullet_style))
    story.append(Paragraph("• <b>Tools & Version Control:</b> Git, GitHub, VS Code, REST APIs, JSON", bullet_style))
    story.append(Paragraph("• <b>Business & Leadership:</b> Team Leadership (Managed team of 40), Strategic Operations, Client Acquisition, Agile/Scrum", bullet_style))
    story.append(Paragraph("• <b>Languages:</b> English (Professional Working Proficiency), Swedish (Basic), Telugu (Native)", bullet_style))

    # Experience
    story.append(Paragraph("PROFESSIONAL EXPERIENCE & LEADERSHIP", heading_style))
    story.append(Paragraph("<b>Real-Estate Sales & Business Development Team Lead</b> (Managed Team of 40)", body_style))
    story.append(Paragraph("• Led a 40-member cross-functional sales and business development team, consistently achieving revenue targets.", bullet_style))
    story.append(Paragraph("• Implemented data-driven sales tracking workflows and optimized client acquisition pipelines.", bullet_style))
    story.append(Paragraph("• Managed stakeholder relationships, operational strategy, and team performance evaluations.", bullet_style))

    # Target Roles
    story.append(Paragraph("TARGET ROLES & AVAILABILITY", heading_style))
    story.append(Paragraph("• <b>Target Roles:</b> Junior Python Developer, AI/ML Developer, Data Analyst, Data Engineer, LIA Internships, Trainee Programs", bullet_style))
    story.append(Paragraph("• <b>Preferred Locations:</b> Göteborg, Sweden & Remote", bullet_style))
    story.append(Paragraph("• <b>Availability:</b> LIA Internships starting late 2026 / early 2027, Trainee & Junior roles.", bullet_style))

    doc.build(story)
    print("Successfully generated CV_Gowtami_Devarenti.pdf!")

if __name__ == "__main__":
    build_pdf()
