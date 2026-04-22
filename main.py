"""매주 성경 시나리오를 생성하고 네이버 메일로 발송합니다.

환경변수:
    ANTHROPIC_API_KEY  - Claude API 키
    NAVER_EMAIL        - 발송/수신 네이버 계정 (예: xxx@naver.com)
    NAVER_APP_PASSWORD - 네이버 메일 SMTP 앱 비밀번호
    MAIL_RECIPIENT     - 수신자 (미지정 시 NAVER_EMAIL 로 발송)
    WEEK_OFFSET        - (선택) 주제 순환 오프셋 정수
"""

from __future__ import annotations

import os
import re
import smtplib
import sys
from datetime import datetime, timezone, timedelta
from email.message import EmailMessage
from pathlib import Path

from anthropic import Anthropic
from docx import Document
from docx.shared import Pt, RGBColor

from prompt_template import SYSTEM_PROMPT, build_prompt
from topics import get_topic_for_week

MODEL = "claude-opus-4-5"
KST = timezone(timedelta(hours=9))

for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except AttributeError:
        pass


def sanitize_text(text: str) -> str:
    return (
        text.replace(" ", "\n")
            .replace(" ", "\n\n")
            .replace("﻿", "")
    )


def current_week_index() -> int:
    now = datetime.now(KST)
    iso_year, iso_week, _ = now.isocalendar()
    base = iso_year * 53 + iso_week
    offset = int(os.environ.get("WEEK_OFFSET", "0"))
    return base + offset


def generate_scenario(topic: str, narrator: str, reference: str) -> str:
    client = Anthropic()
    message = client.messages.create(
        model=MODEL,
        max_tokens=12000,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": build_prompt(topic, narrator, reference)}],
    )
    raw = "".join(block.text for block in message.content if block.type == "text")
    return sanitize_text(raw)


def safe_filename(value: str) -> str:
    return re.sub(r"[^\w\-._ ]", "_", value).strip()[:60] or "scenario"


_SCENE_PATTERN = re.compile(r"^\[(?:장면|Scene)\s*:", re.IGNORECASE)
_DIALOG_PATTERN = re.compile(r'^["“].+["”]\s*$')


def _render_paragraph(doc: Document, line: str) -> None:
    stripped = line.strip()
    if not stripped:
        doc.add_paragraph()
        return

    if _SCENE_PATTERN.match(stripped):
        p = doc.add_paragraph()
        run = p.add_run(stripped)
        run.italic = True
        run.font.color.rgb = RGBColor(0x55, 0x6B, 0x8D)
        return

    if _DIALOG_PATTERN.match(stripped):
        p = doc.add_paragraph()
        run = p.add_run(stripped)
        run.bold = True
        return

    doc.add_paragraph(line)


def save_docx(scenario: str, topic: str, narrator: str, reference: str, out_dir: Path) -> Path:
    doc = Document()

    style = doc.styles["Normal"]
    style.font.name = "Malgun Gothic"
    style.font.size = Pt(11)

    heading = doc.add_heading(topic, level=0)
    heading.alignment = 1

    meta = doc.add_paragraph()
    meta.add_run(f"화자: {narrator}    본문: {reference}").italic = True
    today_kst = datetime.now(KST).strftime("%Y-%m-%d")
    doc.add_paragraph(f"생성일: {today_kst} (KST)")
    doc.add_paragraph()

    for line in scenario.split("\n"):
        stripped = line.strip()
        if stripped.startswith("# "):
            doc.add_heading(stripped[2:], level=1)
        elif stripped.startswith("## "):
            doc.add_heading(stripped[3:], level=2)
        elif stripped.startswith("### "):
            doc.add_heading(stripped[4:], level=3)
        elif stripped == "---":
            doc.add_paragraph().add_run("─" * 40)
        else:
            _render_paragraph(doc, line)

    out_dir.mkdir(parents=True, exist_ok=True)
    filename = f"{today_kst}_{safe_filename(topic)}.docx"
    path = out_dir / filename
    doc.save(path)
    return path


def _attachment_name(docx_path: Path) -> str:
    today_kst = datetime.now(KST).strftime("%Y-%m-%d")
    slug = re.sub(r"[^A-Za-z0-9._-]+", "_", docx_path.stem).strip("_")
    if slug and slug != today_kst:
        base = slug
    else:
        base = f"{today_kst}_bible_scenario"
    if not base.lower().endswith(".docx"):
        base += ".docx"
    return base


def send_email(docx_path: Path, topic: str, narrator: str, scenario: str) -> None:
    sender = os.environ["NAVER_EMAIL"]
    password = os.environ["NAVER_APP_PASSWORD"]
    recipient = os.environ.get("MAIL_RECIPIENT", sender)

    msg = EmailMessage()
    msg["From"] = sender
    msg["To"] = recipient
    today_kst = datetime.now(KST).strftime("%Y-%m-%d")
    msg["Subject"] = f"[주간 성경 시나리오] {today_kst} · {topic} ({narrator})"

    preview = scenario[:600].replace("\n\n", "\n")
    body = (
        f"안녕하세요.\n\n"
        f"이번 주 성경 스토리텔링 시나리오를 전달드립니다.\n\n"
        f"• 주제: {topic}\n"
        f"• 화자: {narrator}\n\n"
        f"--- 미리보기 ---\n{preview}\n...\n\n"
        f"전체 내용은 첨부된 워드 파일을 확인해 주세요.\n"
        f"— Bible Automation"
    )
    msg.set_content(body)

    attach_name = _attachment_name(docx_path)
    msg.add_attachment(
        docx_path.read_bytes(),
        maintype="application",
        subtype="vnd.openxmlformats-officedocument.wordprocessingml.document",
        filename=attach_name,
    )

    with smtplib.SMTP_SSL("smtp.naver.com", 465, timeout=30) as smtp:
        smtp.login(sender, password)
        smtp.send_message(msg)


def main() -> int:
    week_index = current_week_index()
    topic, narrator, reference = get_topic_for_week(week_index)
    print(f"[week={week_index}] topic={topic} / narrator={narrator} / ref={reference}")

    scenario = generate_scenario(topic, narrator, reference)
    print(f"Scenario generated: {len(scenario)} chars")

    out_dir = Path(__file__).parent / "output"
    docx_path = save_docx(scenario, topic, narrator, reference, out_dir)
    print(f"Saved: {docx_path}")

    send_email(docx_path, topic, narrator, scenario)
    print("Email sent successfully.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
