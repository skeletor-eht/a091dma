#!/usr/bin/env python3
"""
Generate demo PDF documents for testing the PDF upload functionality.
"""

from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.enums import TA_JUSTIFY, TA_LEFT, TA_CENTER

def create_billing_guidelines_pdf():
    """Create a sample billing guidelines PDF for Acme Manufacturing."""

    doc = SimpleDocTemplate(
        "demo_billing_guidelines.pdf",
        pagesize=letter,
        rightMargin=72,
        leftMargin=72,
        topMargin=72,
        bottomMargin=18,
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        textColor='#0f2c4d',
        spaceAfter=30,
        alignment=TA_CENTER,
    )

    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        textColor='#0f2c4d',
        spaceAfter=12,
    )

    body_style = ParagraphStyle(
        'CustomBody',
        parent=styles['BodyText'],
        fontSize=11,
        alignment=TA_JUSTIFY,
        spaceAfter=12,
    )

    story = []

    # Title
    story.append(Paragraph("ACME MANUFACTURING CORPORATION", title_style))
    story.append(Paragraph("Legal Billing Guidelines", heading_style))
    story.append(Spacer(1, 0.2*inch))

    # Introduction
    intro = """
    These guidelines establish the standards and expectations for legal billing submitted to
    Acme Manufacturing Corporation. All outside counsel must comply with these requirements
    to ensure accurate and timely payment of invoices.
    """
    story.append(Paragraph(intro, body_style))
    story.append(Spacer(1, 0.3*inch))

    # Section 1
    story.append(Paragraph("1. NARRATIVE REQUIREMENTS", heading_style))

    req1 = """
    <b>Detail and Specificity:</b> All time entries must clearly describe the work performed
    with sufficient detail to allow assessment of the necessity and value of the services.
    Vague descriptions such as "emails," "telephone calls," or "review of documents" are
    insufficient and will be rejected.
    """
    story.append(Paragraph(req1, body_style))

    req2 = """
    <b>Subject Matter:</b> Each entry must identify the specific subject matter addressed.
    For example, instead of "reviewed correspondence," the entry should state "reviewed and
    analyzed correspondence from opposing counsel regarding discovery dispute over production
    of financial records."
    """
    story.append(Paragraph(req2, body_style))

    req3 = """
    <b>Action and Outcome:</b> Describe not only what was reviewed or discussed, but also
    the action taken or the outcome. For example: "Drafted response to opposing counsel's
    motion to compel with supporting case law analysis."
    """
    story.append(Paragraph(req3, body_style))

    story.append(Spacer(1, 0.3*inch))

    # Section 2
    story.append(Paragraph("2. PROHIBITED TERMS AND PRACTICES", heading_style))

    prohib1 = """
    The following terms and phrases are considered insufficiently descriptive and must NOT
    be used in billing narratives:
    """
    story.append(Paragraph(prohib1, body_style))

    prohibited_list = """
    • "General review"<br/>
    • "Email review" or "reviewed emails" (without specifying subject and action)<br/>
    • "Miscellaneous tasks"<br/>
    • "Administrative work"<br/>
    • "Case review" (without specifying what was reviewed and why)<br/>
    • "Conference with client" (without describing the subject matter)<br/>
    • "Legal research" (without identifying the issue researched)
    """
    story.append(Paragraph(prohibited_list, body_style))

    story.append(Spacer(1, 0.3*inch))

    # Section 3
    story.append(Paragraph("3. REQUIRED ELEMENTS", heading_style))

    required = """
    Every billing entry must include the following elements:
    """
    story.append(Paragraph(required, body_style))

    required_list = """
    1. <b>Subject:</b> Clear identification of the matter or issue addressed<br/>
    2. <b>Action:</b> Specific description of the work performed<br/>
    3. <b>Purpose:</b> Explanation of why the work was necessary<br/>
    4. <b>Outcome:</b> Result of the work (when applicable)
    """
    story.append(Paragraph(required_list, body_style))

    story.append(Spacer(1, 0.3*inch))

    # Section 4
    story.append(Paragraph("4. PREFERRED LANGUAGE AND TONE", heading_style))

    tone = """
    Billing narratives should be professional and formal. Use complete sentences where
    possible. Avoid abbreviations unless they are standard legal terms. Use past tense
    to describe completed work (e.g., "drafted," "reviewed and analyzed," "prepared").
    """
    story.append(Paragraph(tone, body_style))

    story.append(Spacer(1, 0.3*inch))

    # Section 5
    story.append(Paragraph("5. COMPLIANCE AND ENFORCEMENT", heading_style))

    compliance = """
    Invoices containing entries that do not comply with these guidelines will be returned
    for revision. Repeated non-compliance may result in termination of the engagement or
    adjustment of fees. All counsel are expected to familiarize themselves with these
    guidelines and train their billing staff accordingly.
    """
    story.append(Paragraph(compliance, body_style))

    doc.build(story)
    print("✓ Created: demo_billing_guidelines.pdf")


def create_successful_examples_pdf():
    """Create a sample successful billing examples PDF."""

    doc = SimpleDocTemplate(
        "demo_successful_examples.pdf",
        pagesize=letter,
        rightMargin=72,
        leftMargin=72,
        topMargin=72,
        bottomMargin=18,
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        textColor='#16a34a',
        spaceAfter=30,
        alignment=TA_CENTER,
    )

    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        textColor='#16a34a',
        spaceAfter=12,
    )

    body_style = ParagraphStyle(
        'CustomBody',
        parent=styles['BodyText'],
        fontSize=11,
        spaceAfter=12,
    )

    example_style = ParagraphStyle(
        'Example',
        parent=styles['BodyText'],
        fontSize=11,
        leftIndent=20,
        rightIndent=20,
        spaceBefore=6,
        spaceAfter=12,
        backColor='#dcfce7',
    )

    story = []

    # Title
    story.append(Paragraph("APPROVED BILLING EXAMPLES", title_style))
    story.append(Paragraph("Acme Manufacturing Corporation", heading_style))
    story.append(Spacer(1, 0.2*inch))

    intro = """
    The following examples represent billing narratives that meet or exceed Acme Manufacturing's
    billing guidelines. These entries demonstrate proper detail, specificity, and professional
    language. Use these as models for your own billing submissions.
    """
    story.append(Paragraph(intro, body_style))
    story.append(Spacer(1, 0.3*inch))

    # Example 1
    story.append(Paragraph("Example 1: Discovery Correspondence", heading_style))
    example1 = """
    "Reviewed and analyzed correspondence from opposing counsel regarding discovery dispute
    over production of financial records for fiscal years 2021-2023; prepared detailed
    response outlining basis for objections to overly broad requests; conferred with client
    regarding privilege log preparation timeline."
    """
    story.append(Paragraph(example1, example_style))
    story.append(Paragraph("<i>Why this works: Specifies the subject (discovery dispute), the documents (financial records), the time period, the action taken (prepared response), and follow-up with client.</i>", body_style))
    story.append(Spacer(1, 0.2*inch))

    # Example 2
    story.append(Paragraph("Example 2: Motion Practice", heading_style))
    example2 = """
    "Drafted motion to compel production of email communications between defendant and third-party
    consultant regarding product defect; researched applicable case law on work product doctrine
    and trade secret protections; prepared supporting memorandum with citations to controlling
    circuit court decisions."
    """
    story.append(Paragraph(example2, example_style))
    story.append(Paragraph("<i>Why this works: Clear description of the motion subject, specific legal research performed, and deliverables created.</i>", body_style))
    story.append(Spacer(1, 0.2*inch))

    # Example 3
    story.append(Paragraph("Example 3: Contract Review", heading_style))
    example3 = """
    "Reviewed proposed master services agreement with Supplier XYZ focusing on limitation of
    liability provisions, indemnification clauses, and intellectual property ownership terms;
    drafted detailed redline with suggested modifications to reduce exposure; prepared summary
    memo for business team outlining key risk areas and recommended changes."
    """
    story.append(Paragraph(example3, example_style))
    story.append(Paragraph("<i>Why this works: Identifies specific contract provisions reviewed, actions taken (redline and memo), and purpose (risk reduction).</i>", body_style))
    story.append(Spacer(1, 0.2*inch))

    # Example 4
    story.append(Paragraph("Example 4: Litigation Strategy", heading_style))
    example4 = """
    "Participated in strategy conference call with client and co-counsel regarding approach to
    depositions of three key fact witnesses scheduled for next month; discussed anticipated
    testimony, potential impeachment materials, and coordination of questioning among counsel;
    prepared outline of topics to cover and documents to use in examination."
    """
    story.append(Paragraph(example4, example_style))
    story.append(Paragraph("<i>Why this works: Describes the participants, subject matter (deposition strategy), specific topics discussed, and work product created.</i>", body_style))
    story.append(Spacer(1, 0.2*inch))

    # Example 5
    story.append(Paragraph("Example 5: Regulatory Compliance", heading_style))
    example5 = """
    "Researched recent FDA guidance on medical device labeling requirements for Class II devices;
    analyzed impact of new guidelines on client's current labeling practices; prepared compliance
    memorandum with specific recommendations for label modifications to ensure regulatory compliance;
    coordinated with regulatory affairs team regarding implementation timeline."
    """
    story.append(Paragraph(example5, example_style))
    story.append(Paragraph("<i>Why this works: Identifies regulatory authority and specific guidance, describes analysis performed, deliverables created, and coordination with client team.</i>", body_style))
    story.append(Spacer(1, 0.2*inch))

    # Example 6
    story.append(Paragraph("Example 6: Client Communication", heading_style))
    example6 = """
    "Prepared comprehensive status report for client summarizing developments in patent litigation
    matter, including court's recent claim construction ruling, impact on case strategy, revised
    damages analysis, and recommended next steps for summary judgment motion practice."
    """
    story.append(Paragraph(example6, example_style))
    story.append(Paragraph("<i>Why this works: Clearly describes the communication created, its content (case developments and strategy), and forward-looking recommendations.</i>", body_style))

    doc.build(story)
    print("✓ Created: demo_successful_examples.pdf")


def create_failed_examples_pdf():
    """Create a sample failed/rejected billing examples PDF."""

    doc = SimpleDocTemplate(
        "demo_failed_examples.pdf",
        pagesize=letter,
        rightMargin=72,
        leftMargin=72,
        topMargin=72,
        bottomMargin=18,
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        textColor='#dc2626',
        spaceAfter=30,
        alignment=TA_CENTER,
    )

    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        textColor='#dc2626',
        spaceAfter=12,
    )

    body_style = ParagraphStyle(
        'CustomBody',
        parent=styles['BodyText'],
        fontSize=11,
        spaceAfter=12,
    )

    example_style = ParagraphStyle(
        'Example',
        parent=styles['BodyText'],
        fontSize=11,
        leftIndent=20,
        rightIndent=20,
        spaceBefore=6,
        spaceAfter=12,
        backColor='#fee2e2',
    )

    story = []

    # Title
    story.append(Paragraph("REJECTED BILLING EXAMPLES", title_style))
    story.append(Paragraph("Acme Manufacturing Corporation", heading_style))
    story.append(Spacer(1, 0.2*inch))

    intro = """
    The following examples represent billing narratives that were REJECTED for insufficient
    detail, vague language, or non-compliance with Acme Manufacturing's billing guidelines.
    DO NOT use these patterns in your billing submissions. Each example is followed by an
    explanation of why it was rejected.
    """
    story.append(Paragraph(intro, body_style))
    story.append(Spacer(1, 0.3*inch))

    # Example 1
    story.append(Paragraph("Rejected Example 1:", heading_style))
    example1 = '"Email review."'
    story.append(Paragraph(example1, example_style))
    story.append(Paragraph("<b>Why rejected:</b> Completely lacking in detail. Does not specify whose emails, what subject matter, what action was taken, or what was accomplished.", body_style))
    story.append(Spacer(1, 0.2*inch))

    # Example 2
    story.append(Paragraph("Rejected Example 2:", heading_style))
    example2 = '"Telephone conference with client."'
    story.append(Paragraph(example2, example_style))
    story.append(Paragraph("<b>Why rejected:</b> No description of what was discussed, what issues were addressed, or what decisions were made. Generic and uninformative.", body_style))
    story.append(Spacer(1, 0.2*inch))

    # Example 3
    story.append(Paragraph("Rejected Example 3:", heading_style))
    example3 = '"Legal research."'
    story.append(Paragraph(example3, example_style))
    story.append(Paragraph("<b>Why rejected:</b> Does not identify what legal issue was researched, what sources were consulted, or what was discovered. Too vague.", body_style))
    story.append(Spacer(1, 0.2*inch))

    # Example 4
    story.append(Paragraph("Rejected Example 4:", heading_style))
    example4 = '"Reviewed documents."'
    story.append(Paragraph(example4, example_style))
    story.append(Paragraph("<b>Why rejected:</b> Does not specify which documents, why they were reviewed, what was found, or what action was taken as a result.", body_style))
    story.append(Spacer(1, 0.2*inch))

    # Example 5
    story.append(Paragraph("Rejected Example 5:", heading_style))
    example5 = '"General case review and analysis."'
    story.append(Paragraph(example5, example_style))
    story.append(Paragraph("<b>Why rejected:</b> Uses prohibited language ('general'). Completely non-specific about what was reviewed, why, or what analysis was performed.", body_style))
    story.append(Spacer(1, 0.2*inch))

    # Example 6
    story.append(Paragraph("Rejected Example 6:", heading_style))
    example6 = '"Miscellaneous work on case."'
    story.append(Paragraph(example6, example_style))
    story.append(Paragraph("<b>Why rejected:</b> Uses prohibited term ('miscellaneous'). No description of actual work performed. Appears to be block billing or padding.", body_style))
    story.append(Spacer(1, 0.2*inch))

    # Example 7
    story.append(Paragraph("Rejected Example 7:", heading_style))
    example7 = '"Conference call."'
    story.append(Paragraph(example7, example_style))
    story.append(Paragraph("<b>Why rejected:</b> Minimal detail. Does not identify participants, topics discussed, or outcomes. Insufficient for billing purposes.", body_style))
    story.append(Spacer(1, 0.2*inch))

    # Example 8
    story.append(Paragraph("Rejected Example 8:", heading_style))
    example8 = '"Drafted correspondence."'
    story.append(Paragraph(example8, example_style))
    story.append(Paragraph("<b>Why rejected:</b> Does not specify to whom the correspondence was addressed, what subject it concerned, or what purpose it served.", body_style))
    story.append(Spacer(1, 0.2*inch))

    # Example 9
    story.append(Paragraph("Rejected Example 9:", heading_style))
    example9 = '"Review of file."'
    story.append(Paragraph(example9, example_style))
    story.append(Paragraph("<b>Why rejected:</b> Too vague. Does not explain what was reviewed in the file, why it was necessary, or what was accomplished.", body_style))
    story.append(Spacer(1, 0.2*inch))

    # Example 10
    story.append(Paragraph("Rejected Example 10:", heading_style))
    example10 = '"Administrative tasks."'
    story.append(Paragraph(example10, example_style))
    story.append(Paragraph("<b>Why rejected:</b> Uses prohibited language. Administrative tasks should generally not be billed to client unless specifically authorized.", body_style))

    doc.build(story)
    print("✓ Created: demo_failed_examples.pdf")


if __name__ == "__main__":
    print("\nGenerating demo PDF documents...")
    print("-" * 50)

    create_billing_guidelines_pdf()
    create_successful_examples_pdf()
    create_failed_examples_pdf()

    print("-" * 50)
    print("\n✅ All demo PDFs created successfully!")
    print("\nFiles created in current directory:")
    print("  1. demo_billing_guidelines.pdf")
    print("  2. demo_successful_examples.pdf")
    print("  3. demo_failed_examples.pdf")
    print("\nYou can now test the PDF upload functionality!")
    print("Upload these to a client in the admin panel.\n")
