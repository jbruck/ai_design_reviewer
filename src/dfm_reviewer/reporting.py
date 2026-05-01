from pathlib import Path

from dfm_reviewer.models import Review

REPORT_FILENAME = "mechanical-dfm-review.md"


def render_markdown_report(review: Review) -> str:
    routes = _join_values(route.value for route in review.intake.manufacturing_routes)
    ex_concepts = _join_values(concept.value for concept in review.intake.ex_concepts)
    supporting_documents = _join_values(review.intake.supporting_documents)

    lines = [
        f"# Mechanical DFM Review: {review.part_number} Rev {review.revision}",
        "",
        "## Review Summary",
        "",
        f"- **Title:** {_value_or_default(review.title)}",
        f"- **Review ID:** `{review.review_id}`",
        f"- **Source PDF:** `{_markdown_path(review.source_pdf)}`",
        f"- **ECN:** {_value_or_default(review.intake.ecn)}",
        "",
        "## Drawing Metadata",
        "",
        f"- **Part/assembly number:** {review.part_number}",
        f"- **Revision:** {review.revision}",
        f"- **Title:** {_value_or_default(review.title)}",
        "",
        "## Intake And Context",
        "",
        f"- **Drawing purpose:** {_value_or_default(review.intake.drawing_purpose)}",
        f"- **Product/system:** {_value_or_default(review.intake.product_or_system)}",
        f"- **Supplier/process:** {_value_or_default(review.intake.supplier_or_process)}",
        f"- **Known risks:** {_value_or_default(review.intake.known_risks)}",
        f"- **Supporting documents:** {supporting_documents}",
        "",
        "## Manufacturing Route",
        "",
        f"- **Selected route(s):** {routes}",
        "",
        "## IECEx Context And Evidence Status",
        "",
        f"- **Certification status:** {review.intake.certification_status.value}",
        f"- **Ex concept(s):** {ex_concepts}",
        "- **Advisory note:** This report captures review evidence and questions; it is not a "
        "certification determination.",
        "",
        "## Stakeholder Needs",
        "",
        *_stakeholder_need_lines(review),
        "",
        "## Technical Requirements",
        "",
        *_requirement_lines(review),
        "",
        "## Design Evidence",
        "",
        *_evidence_lines(review),
        "",
        "## DFM Findings",
        "",
        *_finding_lines(review),
        "",
        "## Open Questions And Missing Information",
        "",
        *_open_question_lines(review),
        "",
        "## Suggested Inspection Or Verification Items",
        "",
        *_verification_lines(review),
        "",
        "## Appendix: Extracted Text",
        "",
        "### Extracted Title Block",
        "",
        _code_block(review.extracted_title_block_text),
        "",
        "### Extracted Drawing Notes",
        "",
        _code_block(review.extracted_notes_text),
        "",
        "### OCR Status",
        "",
        "No separate OCR pass has been run for this MVP report.",
        "",
        "### OCR Text",
        "",
        "OCR text is not captured separately in this MVP report.",
        "",
    ]

    return "\n".join(lines).rstrip() + "\n"


def write_markdown_report(review: Review, reports_dir: Path) -> Path:
    reports_dir.mkdir(parents=True, exist_ok=True)
    output_path = reports_dir / REPORT_FILENAME
    output_path.write_text(render_markdown_report(review), encoding="utf-8")
    return output_path


def _stakeholder_need_lines(review: Review) -> list[str]:
    if not review.stakeholder_needs:
        return ["No stakeholder needs have been captured yet."]
    return [
        f"- **{need.need_id}:** {need.text} "
        f"(stakeholder: {_value_or_default(need.stakeholder)})"
        for need in review.stakeholder_needs
    ]


def _requirement_lines(review: Review) -> list[str]:
    if not review.requirements:
        return ["No technical requirements have been captured yet."]
    return [
        f"- **{requirement.requirement_id}:** {requirement.text} "
        f"(source need: {_value_or_default(requirement.source_need_id)}, "
        f"status: {requirement.status})"
        for requirement in review.requirements
    ]


def _evidence_lines(review: Review) -> list[str]:
    if not review.evidence:
        return ["No evidence crops have been captured yet."]

    lines = [
        "| Evidence | Source PDF | Page | Page Image | Crop | Region | Linked Requirement | "
        "Linked Finding | Confidence | Note |",
        "| --- | --- | ---: | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for evidence in review.evidence:
        lines.append(
            "| "
            f"{_table_cell(evidence.evidence_id)} | "
            f"`{_table_cell(_markdown_path(evidence.source_pdf))}` | "
            f"{evidence.page_number} | "
            f"`{_table_cell(_markdown_path(evidence.page_image_path))}` | "
            f"`{_table_cell(_markdown_path(evidence.crop_image_path))}` | "
            f"{_table_cell(_format_region(evidence.region))} | "
            f"{_table_cell(_value_or_default(evidence.linked_requirement_id))} | "
            f"{_table_cell(_value_or_default(evidence.linked_finding_id))} | "
            f"{_table_cell(evidence.confidence.value)} | "
            f"{_table_cell(_value_or_default(evidence.reviewer_note))} |"
        )
        if evidence.extracted_text:
            lines.append(f"- **{evidence.evidence_id} extracted text:** {evidence.extracted_text}")
    return lines


def _finding_lines(review: Review) -> list[str]:
    if not review.findings:
        return ["No DFM findings have been captured yet."]

    lines: list[str] = []
    for finding in review.findings:
        evidence_ids = _join_values(finding.linked_evidence_ids)
        lines.extend(
            [
                f"### {finding.finding_id}: {finding.title}",
                "",
                f"- **Status:** {finding.status.value}",
                f"- **Confidence:** {finding.confidence.value}",
                f"- **Linked evidence:** {evidence_ids}",
                f"- **Details:** {finding.details}",
                f"- **Recommendation:** {_value_or_default(finding.recommendation)}",
                "",
            ]
        )
    return lines[:-1]


def _open_question_lines(review: Review) -> list[str]:
    if not review.open_questions:
        return ["No open questions have been captured yet."]
    return [
        f"- **{question.question_id}:** {question.text} "
        f"(context: {_value_or_default(question.context)}, resolved: {question.resolved})"
        for question in review.open_questions
    ]


def _verification_lines(review: Review) -> list[str]:
    if not review.verification_items:
        return ["No inspection or verification suggestions have been captured yet."]
    return [
        f"- **{item.verification_id}:** {item.text} "
        f"(method: {item.method}, "
        f"linked requirement: {_value_or_default(item.linked_requirement_id)})"
        for item in review.verification_items
    ]


def _join_values(values: object) -> str:
    rendered = [str(value) for value in values if str(value)]
    return ", ".join(rendered) if rendered else "not specified"


def _value_or_default(value: object) -> str:
    if value is None or value == "":
        return "not specified"
    return str(value)


def _code_block(value: str) -> str:
    text = value or "not captured"
    fence = "```"
    while fence in text:
        fence += "`"
    return f"{fence}\n{text}\n{fence}"


def _markdown_path(path: Path) -> str:
    return path.as_posix()


def _format_region(region: list[int]) -> str:
    return ", ".join(str(coordinate) for coordinate in region)


def _table_cell(value: object) -> str:
    return str(value).replace("|", "\\|").replace("\r\n", "\n").replace("\n", "<br>")
