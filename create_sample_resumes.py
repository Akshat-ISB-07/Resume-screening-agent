#!/usr/bin/env python3
"""Generate 3 sample Senior PM resumes that land in different evaluation buckets."""
import os
from fpdf import FPDF

os.makedirs("sample_resumes", exist_ok=True)


class PDF(FPDF):
    def header(self): pass
    def footer(self): pass


def resume(path, name, title, contact, summary, experience, education, skills):
    pdf = PDF(format="Letter")
    pdf.set_margins(22, 22, 22)
    pdf.add_page()

    # Name
    pdf.set_font("Helvetica", "B", 17)
    pdf.set_text_color(15, 23, 42)
    pdf.cell(0, 9, name, new_x="LMARGIN", new_y="NEXT")

    # Title & contact
    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(71, 85, 105)
    pdf.cell(0, 5, title, new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 8)
    pdf.set_text_color(100, 116, 139)
    pdf.cell(0, 5, contact, new_x="LMARGIN", new_y="NEXT")
    pdf.ln(3)

    def section(heading):
        pdf.set_font("Helvetica", "B", 8)
        pdf.set_text_color(99, 102, 241)
        pdf.cell(0, 5, heading.upper(), new_x="LMARGIN", new_y="NEXT")
        pdf.set_draw_color(99, 102, 241)
        pdf.set_line_width(0.3)
        pdf.line(pdf.get_x(), pdf.get_y(), pdf.get_x() + 166, pdf.get_y())
        pdf.ln(1)

    W = 166  # content width (Letter 215.9mm - 2*22mm margins, rounded down)

    def body(text, size=8.5):
        pdf.set_font("Helvetica", "", size)
        pdf.set_text_color(51, 65, 85)
        pdf.set_x(22)
        pdf.multi_cell(W, 4.5, text)

    def bullet(text):
        pdf.set_font("Helvetica", "", 8.5)
        pdf.set_text_color(51, 65, 85)
        pdf.set_x(22)
        pdf.multi_cell(W, 4.5, "- " + text)

    # Summary
    section("Summary")
    body(summary)
    pdf.ln(3)

    # Experience
    section("Experience")
    for exp in experience:
        pdf.set_font("Helvetica", "B", 9)
        pdf.set_text_color(15, 23, 42)
        pdf.cell(0, 5, exp["role"] + "  |  " + exp["company"], new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("Helvetica", "I", 8)
        pdf.set_text_color(100, 116, 139)
        pdf.cell(0, 4, exp["period"], new_x="LMARGIN", new_y="NEXT")
        for b in exp["bullets"]:
            bullet(b)
        pdf.ln(2)

    # Education
    section("Education")
    for ed in education:
        pdf.set_font("Helvetica", "B", 9)
        pdf.set_text_color(15, 23, 42)
        pdf.cell(0, 5, ed["degree"], new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("Helvetica", "", 8.5)
        pdf.set_text_color(71, 85, 105)
        pdf.cell(0, 4, ed["school"] + "  " + ed["year"], new_x="LMARGIN", new_y="NEXT")
        pdf.ln(1)

    # Skills
    section("Skills")
    body(" | ".join(skills))

    pdf.output(path)
    print(f"Created {path}")


# ── Resume 1: Sarah Chen — Strong Hire (~88) ─────────────────────────────
resume(
    "sample_resumes/sarah_chen.pdf",
    name="Sarah Chen",
    title="Senior Product Manager",
    contact="sarah.chen@email.com  |  linkedin.com/in/sarahchen  |  (415) 555-0192",
    summary=(
        "Strategic product leader with 8+ years driving 0-to-1 products and scaling platforms "
        "at top-tier tech companies. MBA from Stanford. Proven track record leading cross-functional "
        "teams of 15+ to ship high-impact products with measurable business outcomes. "
        "Deep expertise in data-driven decision-making, pricing strategy, and executive stakeholder alignment."
    ),
    experience=[
        {
            "role": "Senior Product Manager",
            "company": "Stripe",
            "period": "2021 - Present",
            "bullets": [
                "Owned end-to-end roadmap for Stripe Invoicing, driving 40% YoY revenue growth to $200M ARR.",
                "Led 18 engineers and 4 designers through 3 major product launches with zero slip in OKRs.",
                "Built company-wide A/B testing framework across 6 product lines, cutting experiment cycle time 35%.",
                "Partnered with CFO to define 3-year product strategy aligned with $1B expansion goal.",
                "Championed ML-based fraud detection feature that reduced chargebacks by 28%.",
            ],
        },
        {
            "role": "Product Manager",
            "company": "Airbnb",
            "period": "2018 - 2021",
            "bullets": [
                "Led Host Payments product; increased payout speed 60%, improving host NPS by 22 points.",
                "Launched dynamic pricing tool adopted by 1.2M hosts within 6 months of GA.",
                "Partnered with data science to build demand-forecasting models, improving supply utilization 18%.",
                "Managed $5M product budget and prioritised backlog across 3 scrum teams.",
            ],
        },
        {
            "role": "Associate Product Manager",
            "company": "Google",
            "period": "2016 - 2018",
            "bullets": [
                "APM rotation across Search and Maps; shipped 4 features to 500M+ daily active users.",
                "Defined OKRs for Maps local discovery, contributing to 12% engagement lift.",
            ],
        },
    ],
    education=[
        {"degree": "MBA, Product & Strategy", "school": "Stanford Graduate School of Business", "year": "2016"},
        {"degree": "BS, Computer Science",    "school": "UC Berkeley",                          "year": "2014"},
    ],
    skills=[
        "Product Strategy", "Roadmap Planning", "OKRs / KPIs", "A/B Testing",
        "SQL", "Python (analytics)", "Figma", "Amplitude", "Looker",
        "Cross-functional Leadership", "Stakeholder Management", "Go-to-Market",
        "Agile / Scrum", "Pricing Strategy", "ML (conceptual)",
    ],
)

# ── Resume 2: Marcus Johnson — Promising (~65) ────────────────────────────
resume(
    "sample_resumes/marcus_johnson.pdf",
    name="Marcus Johnson",
    title="Product Manager",
    contact="marcus.j@email.com  |  linkedin.com/in/marcusjohnson  |  (312) 555-0847",
    summary=(
        "Product Manager with 4 years of experience building B2B SaaS products in fintech. "
        "Comfortable leading small agile teams and translating business requirements into clear user stories. "
        "Strong communicator with solid understanding of engineering constraints. "
        "Looking to grow into a senior role with broader strategic ownership and larger-scale impact."
    ),
    experience=[
        {
            "role": "Product Manager",
            "company": "Brex",
            "period": "2022 - Present",
            "bullets": [
                "Managed expense reporting module; shipped 8 features increasing DAU 15%.",
                "Collaborated with 5 engineers and 1 designer on quarterly planning and sprint cycles.",
                "Ran customer discovery with 30+ enterprise clients to inform roadmap priorities.",
                "Introduced user story mapping to the team, reducing rework by 20%.",
            ],
        },
        {
            "role": "Associate Product Manager",
            "company": "Toast",
            "period": "2020 - 2022",
            "bullets": [
                "Supported PM for payments feature; wrote specs and managed backlog for a 3-engineer team.",
                "Coordinated QA cycles and authored release notes for 6 quarterly releases.",
                "Conducted usability tests with restaurant operators to validate UI changes.",
            ],
        },
    ],
    education=[
        {"degree": "BS, Computer Science", "school": "University of Illinois Urbana-Champaign", "year": "2020"},
    ],
    skills=[
        "Product Management", "User Story Mapping", "Agile / Scrum", "JIRA",
        "Figma", "Mixpanel", "SQL (basic)", "Customer Discovery", "B2B SaaS",
        "Roadmap Planning", "Stakeholder Communication",
    ],
)

# ── Resume 3: Priya Patel — Needs Review (~42) ───────────────────────────
resume(
    "sample_resumes/priya_patel.pdf",
    name="Priya Patel",
    title="Associate Product Manager",
    contact="priya.patel@email.com  |  linkedin.com/in/priyapatel  |  (646) 555-0321",
    summary=(
        "Motivated Associate Product Manager with 2 years in e-commerce product. "
        "Focused on execution and shipping features on schedule. "
        "Eager to take on more strategic ownership and grow as a product leader. "
        "Background in business administration; building data analytics skills."
    ),
    experience=[
        {
            "role": "Associate Product Manager",
            "company": "Shopify (contract via agency)",
            "period": "2023 - Present",
            "bullets": [
                "Supported senior PM in managing the product backlog for the checkout flow.",
                "Wrote user stories and acceptance criteria for 12 minor features.",
                "Coordinated with QA team to track bug resolution across 2 sprint cycles.",
                "Assisted in preparing monthly stakeholder update decks.",
            ],
        },
        {
            "role": "Business Analyst Intern",
            "company": "Target Corporation",
            "period": "2022 (6 months)",
            "bullets": [
                "Analysed weekly sales data to produce inventory reports for merchandising.",
                "Shadowed senior PMs during product reviews and sprint demos.",
            ],
        },
    ],
    education=[
        {"degree": "BS, Business Administration", "school": "Fordham University", "year": "2022"},
    ],
    skills=[
        "Backlog Management", "User Stories", "JIRA", "Confluence",
        "Google Analytics (basic)", "Microsoft Excel",
        "Stakeholder Communication", "E-commerce", "Agile (learning)",
    ],
)

print("\nAll sample resumes created in sample_resumes/")
