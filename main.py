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
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email import encoders
from pathlib import Path

from anthropic import Anthropic
from docx import Document
from docx.shared import Pt

from prompt_template import SYSTEM_PROMPT, build_prompt
from topics import get_topic_for_week

MODEL = "claude-opus-4-5"
KST = timezone(timedelta(hours=9))


def current_week_index() -> int:
    """KST 기준 ISO 주차 + 연도로 오프셋을 섞어 반환."""
    now = datetime.now(KST)
    iso_year, iso_week, _ = now.isocalendar()
    base = iso_year * 53 + iso_week
    offset = int(os.environ.get("WEEK_OFFSET", "0"))
    return base + offset


def generate_scenario(topic: str, narrator: str, reference: str) -> str:
    client = Anthropic()
    message = client.messages.create(
        model=MODEL,
        max_tokens=8000,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": build_prompt(topic, narrator, reference)}],
    )
    return "".join(block.text for block in message.content if block.type == "text")


def safe_filename(value: str) -> str:
    return re.sub(r"[^\w\-._ ]", "_", value).strip()[:60] or "scenario"


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
        else:
            doc.add_paragraph(line)

    out_dir.mkdir(parents=True, exist_ok=True)
    filename = f"{today_kst}_{safe_filename(topic)}.docx"
    path = out_dir / filename
    doc.save(path)
    return path


def send_email(docx_path: Path, topic: str, narrator: str, scenario: str) -> None:
    sender = os.environ["NAVER_EMAIL"]
    password = os.environ["NAVER_APP_PASSWORD"]
    recipient = os.environ.get("MAIL_RECIPIENT", sender)

    msg = MIMEMultipart()
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
    msg.attach(MIMEText(body, "plain", "utf-8"))

    with docx_path.open("rb") as f:
        part = MIMEBase("application", "vnd.openxmlformats-officedocument.wordprocessingml.document")
        part.set_payload(f.read())
    encoders.encode_base64(part)
    part.add_header("Content-Disposition", f'attachment; filename="{docx_path.name}"')
    msg.attach(part)

    with smtplib.SMTP_SSL("smtp.naver.com", 465, timeout=30) as smtp:
        smtp.login(sender, password)
        smtp.sendmail(sender, [recipient], msg.as_string())


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
