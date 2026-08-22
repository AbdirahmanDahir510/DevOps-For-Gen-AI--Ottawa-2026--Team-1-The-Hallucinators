"""
Generates docs/sample-security-policy.pdf
Run from the repo root:
    python docs/generate_sample_pdf.py
"""

from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
)
import os

OUTPUT = os.path.join(os.path.dirname(__file__), "sample-security-policy.pdf")


def build():
    doc = SimpleDocTemplate(
        OUTPUT,
        pagesize=letter,
        rightMargin=inch,
        leftMargin=inch,
        topMargin=inch,
        bottomMargin=inch,
    )

    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(
        "CustomTitle",
        parent=styles["Title"],
        fontSize=22,
        spaceAfter=6,
        textColor=colors.HexColor("#111827"),
    )
    h1 = ParagraphStyle(
        "H1",
        parent=styles["Heading1"],
        fontSize=14,
        spaceBefore=18,
        spaceAfter=6,
        textColor=colors.HexColor("#1d4ed8"),
    )
    h2 = ParagraphStyle(
        "H2",
        parent=styles["Heading2"],
        fontSize=12,
        spaceBefore=12,
        spaceAfter=4,
        textColor=colors.HexColor("#374151"),
    )
    body = ParagraphStyle(
        "Body",
        parent=styles["Normal"],
        fontSize=10,
        leading=16,
        spaceAfter=8,
        textColor=colors.HexColor("#1f2937"),
    )
    meta = ParagraphStyle(
        "Meta",
        parent=styles["Normal"],
        fontSize=9,
        textColor=colors.HexColor("#6b7280"),
        spaceAfter=4,
    )

    story = []

    # ── Cover ──────────────────────────────────────────────────────────────
    story.append(Spacer(1, 0.3 * inch))
    story.append(Paragraph("Acme Corp Information Security Policy", title_style))
    story.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor("#1d4ed8")))
    story.append(Spacer(1, 0.1 * inch))
    story.append(Paragraph("Version 2.4  |  Effective: January 1, 2026  |  Classification: Internal", meta))
    story.append(Paragraph("Owner: Information Security Team  |  Review Cycle: Annual", meta))
    story.append(Spacer(1, 0.2 * inch))
    story.append(Paragraph(
        "This document defines the information security policies and standards for all employees, "
        "contractors, and third parties who access Acme Corp systems or data. Compliance with this "
        "policy is mandatory. Violations may result in disciplinary action up to and including termination.",
        body,
    ))

    # ── Section 1 ──────────────────────────────────────────────────────────
    story.append(Paragraph("1. Password Policy", h1))
    story.append(Paragraph("1.1 Password Requirements", h2))
    story.append(Paragraph(
        "All user account passwords must meet the following minimum requirements:", body))

    pw_data = [
        ["Requirement", "Standard"],
        ["Minimum length", "14 characters"],
        ["Character classes required", "Uppercase, lowercase, digit, and symbol"],
        ["Maximum age", "90 days"],
        ["Minimum age", "1 day (prevents immediate reuse)"],
        ["History", "Last 12 passwords cannot be reused"],
        ["Lockout threshold", "5 failed attempts"],
        ["Lockout duration", "30 minutes or until administrator reset"],
    ]
    pw_table = Table(pw_data, colWidths=[3 * inch, 3.5 * inch])
    pw_table.setStyle(TableStyle([
        ("BACKGROUND",  (0, 0), (-1, 0),  colors.HexColor("#1d4ed8")),
        ("TEXTCOLOR",   (0, 0), (-1, 0),  colors.white),
        ("FONTNAME",    (0, 0), (-1, 0),  "Helvetica-Bold"),
        ("FONTSIZE",    (0, 0), (-1, -1), 9),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.HexColor("#f9fafb"), colors.white]),
        ("GRID",        (0, 0), (-1, -1), 0.5, colors.HexColor("#e5e7eb")),
        ("PADDING",     (0, 0), (-1, -1), 6),
    ]))
    story.append(pw_table)
    story.append(Spacer(1, 0.1 * inch))

    story.append(Paragraph("1.2 Multi-Factor Authentication (MFA)", h2))
    story.append(Paragraph(
        "MFA is mandatory for all accounts with access to: production systems, administrative "
        "consoles, cloud infrastructure, VPN, and any system storing or processing Personally "
        "Identifiable Information (PII) or payment card data. "
        "Acceptable MFA methods are: hardware security keys (FIDO2/WebAuthn), "
        "authenticator apps (TOTP), and SMS as a last resort. "
        "SMS-based MFA is deprecated and will be removed by Q3 2026.",
        body,
    ))

    story.append(Paragraph("1.3 Service Account Credentials", h2))
    story.append(Paragraph(
        "Service account passwords must be at least 32 characters in length, randomly generated, "
        "and stored exclusively in the approved secrets manager (HashiCorp Vault). "
        "Service accounts must not be used for interactive logins. "
        "All service account credentials must be rotated every 180 days.",
        body,
    ))

    # ── Section 2 ──────────────────────────────────────────────────────────
    story.append(Paragraph("2. Data Classification", h1))
    story.append(Paragraph(
        "Acme Corp classifies all data into four tiers. Each tier carries specific handling, "
        "storage, and transmission requirements.",
        body,
    ))

    cls_data = [
        ["Tier",         "Label",        "Examples",                          "Encryption Required"],
        ["1 (Highest)",  "Restricted",   "PII, payment data, health records", "At rest and in transit"],
        ["2",            "Confidential", "Business plans, source code",       "At rest and in transit"],
        ["3",            "Internal",     "Policies, org charts",              "In transit"],
        ["4 (Lowest)",   "Public",       "Marketing material",                "Optional"],
    ]
    cls_table = Table(cls_data, colWidths=[1.0*inch, 1.2*inch, 2.5*inch, 1.8*inch])
    cls_table.setStyle(TableStyle([
        ("BACKGROUND",  (0, 0), (-1, 0),  colors.HexColor("#374151")),
        ("TEXTCOLOR",   (0, 0), (-1, 0),  colors.white),
        ("FONTNAME",    (0, 0), (-1, 0),  "Helvetica-Bold"),
        ("FONTSIZE",    (0, 0), (-1, -1), 9),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.HexColor("#f9fafb"), colors.white]),
        ("GRID",        (0, 0), (-1, -1), 0.5, colors.HexColor("#e5e7eb")),
        ("PADDING",     (0, 0), (-1, -1), 6),
        ("VALIGN",      (0, 0), (-1, -1), "TOP"),
    ]))
    story.append(cls_table)

    # ── Section 3 ──────────────────────────────────────────────────────────
    story.append(Paragraph("3. Acceptable Use Policy", h1))
    story.append(Paragraph("3.1 Permitted Activities", h2))
    story.append(Paragraph(
        "Company systems and networks may be used for: conducting Acme Corp business, "
        "approved software development and testing, accessing training and professional development "
        "resources, and incidental personal use that does not interfere with business operations.",
        body,
    ))
    story.append(Paragraph("3.2 Prohibited Activities", h2))
    story.append(Paragraph(
        "The following activities are strictly prohibited on Acme Corp systems: "
        "accessing, storing, or distributing illegal content; "
        "installing unauthorised software or circumventing security controls; "
        "sharing credentials or granting unauthorised access to others; "
        "using company resources for personal financial gain or outside business activities; "
        "connecting unapproved personal devices to internal network segments; "
        "attempting to access systems or data beyond the scope of your role.",
        body,
    ))

    # ── Section 4 ──────────────────────────────────────────────────────────
    story.append(Paragraph("4. Incident Response", h1))
    story.append(Paragraph(
        "All suspected security incidents must be reported to security@acmecorp.example within one hour "
        "of discovery. An incident is defined as any event that threatens the confidentiality, "
        "integrity, or availability of Acme Corp systems or data.",
        body,
    ))

    ir_data = [
        ["Phase",       "Owner",               "SLA"],
        ["Detection",   "Any employee",        "Report within 1 hour"],
        ["Triage",      "Security team",       "Acknowledge within 2 hours"],
        ["Containment", "Security + IT Ops",   "Within 4 hours of triage"],
        ["Eradication", "Security team",       "Within 24 hours"],
        ["Recovery",    "IT Ops",              "Within 48 hours"],
        ["Post-mortem", "Security + affected teams", "Within 5 business days"],
    ]
    ir_table = Table(ir_data, colWidths=[1.5*inch, 2.3*inch, 2.7*inch])
    ir_table.setStyle(TableStyle([
        ("BACKGROUND",  (0, 0), (-1, 0),  colors.HexColor("#1d4ed8")),
        ("TEXTCOLOR",   (0, 0), (-1, 0),  colors.white),
        ("FONTNAME",    (0, 0), (-1, 0),  "Helvetica-Bold"),
        ("FONTSIZE",    (0, 0), (-1, -1), 9),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.HexColor("#f9fafb"), colors.white]),
        ("GRID",        (0, 0), (-1, -1), 0.5, colors.HexColor("#e5e7eb")),
        ("PADDING",     (0, 0), (-1, -1), 6),
    ]))
    story.append(ir_table)

    # ── Section 5 ──────────────────────────────────────────────────────────
    story.append(Paragraph("5. Remote Work and VPN", h1))
    story.append(Paragraph(
        "All remote access to internal Acme Corp systems must be made through the company-approved "
        "VPN (Tailscale). Split-tunnel VPN is not permitted for Restricted or Confidential data. "
        "Employees must not use public Wi-Fi networks without VPN active. "
        "Home routers must use WPA3 encryption where supported, or WPA2 as a minimum.",
        body,
    ))

    story.append(Paragraph("5.1 Approved Devices", h2))
    story.append(Paragraph(
        "Only Acme Corp-managed devices with current endpoint protection software and full-disk "
        "encryption enabled may connect to internal systems. "
        "Personal device access is limited to email and calendar via the approved web portal only.",
        body,
    ))

    # ── Section 6 ──────────────────────────────────────────────────────────
    story.append(Paragraph("6. AI and Machine Learning Tools", h1))
    story.append(Paragraph(
        "Employees may use approved AI coding assistants and productivity tools listed in the "
        "approved software catalogue. "
        "Inputting Restricted or Confidential data into any external AI service (including public "
        "LLM APIs) is strictly prohibited without written approval from the CISO. "
        "All AI-generated code must be reviewed by a human engineer before merging to production. "
        "Security testing of internal AI systems must follow the procedures in Annex A.",
        body,
    ))

    # ── Footer ─────────────────────────────────────────────────────────────
    story.append(Spacer(1, 0.3 * inch))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#e5e7eb")))
    story.append(Paragraph(
        "Acme Corp Information Security Policy v2.4  |  © 2026 Acme Corp  |  "
        "Questions: security@acmecorp.example",
        meta,
    ))

    doc.build(story)
    print(f"Created: {OUTPUT}")


if __name__ == "__main__":
    build()
