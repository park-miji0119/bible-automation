"""Claude 프롬프트 템플릿."""

SYSTEM_PROMPT = """당신은 10분 분량 성경 1인칭 나레이션 영상을 위한 시나리오 작가입니다.
영화 대본 수준의 연출 지시(장면·카메라·인물·배경·전환) 5요소를 각 섹션마다 반드시
포함시켜 작성합니다. 줄거리 요약, 3인칭 해설, 설명조 서술은 실패한 결과물입니다.
오직 화자가 **지금 그 자리에서** 말하는 1인칭 구어체 나레이션만 허용됩니다.

대사는 극적으로 절제합니다. 직접 대사(큰따옴표로 묶은 말)는 한 편에 최대 2~3회,
진짜 결정적인 순간에만 짧고 강렬한 한 문장으로 쓰며, 나머지는 전부 1인칭 나레이션
으로 녹여냅니다. 대화가 자주 튀어나오는 각본은 실패한 결과물입니다."""


def build_prompt(topic: str, narrator: str, reference: str) -> str:
    """시나리오 생성용 유저 프롬프트."""
    return f"""다음 성경 이야기를 **10분 분량 1인칭 나레이션 시나리오**로 작성해주세요.

- 주제: {topic}
- 화자(1인칭): {narrator}
- 성경 본문: {reference}

## 반드시 지켜야 할 형식

1. **한국어 시나리오를 먼저 전부 작성**하고, 그 아래에 **영어 나레이션**을 이어서 작성합니다. 둘 다 반드시 포함.
2. 두 버전 모두 아래 5개 섹션으로 나누고, 섹션 제목 옆에 **타임코드**를 표기합니다.
   - 인트로 (0:00-0:45) / Intro (0:00-0:45)
   - 발단 (0:45-2:30) / Rising Action (0:45-2:30)
   - 전개 (2:30-5:30) / Development (2:30-5:30)
   - 클라이맥스 (5:30-8:30) / Climax (5:30-8:30)
   - 마무리 (8:30-10:00) / Conclusion (8:30-10:00)

3. **각 섹션마다 반드시 포함할 5가지 연출 요소** — 이것이 없으면 실패한 결과물입니다.
   섹션 타이틀 바로 아래에 아래 5줄을 **정확히 이 순서와 라벨**로 먼저 배치한 뒤, 빈 줄 한 줄 띄우고 1인칭 나레이션 본문을 이어씁니다. 한국어·영어 시나리오 모두 동일한 영문 라벨(SCENE / CAMERA / CHARACTER / BACKGROUND / TRANSITION) 사용.

   **① SCENE (장면 지시)**
   - 장소명 + 실내/실외(INT./EXT.) + 시간대(낮/밤/새벽/황혼) 명시
   - 예: `SCENE: EXT. 모리아 산 정상 — 새벽`

   **② CAMERA (카메라 지시)**
   - 샷 종류 명시: WIDE SHOT / CLOSE UP / MEDIUM SHOT / EXTREME CLOSE UP / PAN / TILT / ZOOM IN / ZOOM OUT / OVER THE SHOULDER / TRACKING SHOT / LOW ANGLE / HIGH ANGLE 중 하나 이상
   - 예: `CAMERA: WIDE SHOT — 산 정상을 향해 걸어오는 아브라함과 이삭의 뒷모습`

   **③ CHARACTER (인물 묘사)**
   - 인물의 표정, 행동, 움직임, 몸짓을 **구체적**으로
   - 예: `CHARACTER: 아브라함은 무거운 발걸음으로 걷는다. 눈가에 눈물이 맺혀있지만 입술은 굳게 다물고 있다.`

   **④ BACKGROUND (배경 묘사)**
   - 시대적 배경, 공간 분위기, 소품, 조명, 색감
   - 예: `BACKGROUND: 거친 돌산. 새벽빛이 지평선을 붉게 물들인다. 나무 한 그루 없는 황량한 정상.`

   **⑤ TRANSITION (전환 지시)**
   - 장면 전환 방식 명시: FADE IN / FADE OUT / CUT TO / DISSOLVE TO / SMASH CUT / MATCH CUT / JUMP CUT 중 하나
   - 첫 섹션(인트로)은 보통 FADE IN, 마지막(마무리)은 보통 FADE OUT.
   - 예: `TRANSITION: FADE IN`

4. 5가지 연출 블록 다음에 **1인칭 나레이션 본문**이 이어집니다. 반드시 "{narrator}"가 직접 말하는 방식 — "나는…", "내 눈앞에…", "심장이 뛰었다" 같은 현재·과거 회상 시점.

5. **대사 처리 원칙** — 반드시 지킬 것. 한국어·영어 시나리오 모두 동일 적용.
   - 인물의 직접 대사는 **아주 중요하고 극적인 순간에만** 사용.
   - 전체 시나리오에서 직접 대사는 **최대 2~3회**까지만 허용 (한국어·영어 각각).
   - 나머지는 모두 **1인칭 나레이션**으로 처리. 대화체로 풀어쓰지 말고 화자의 시선과 내면으로 흡수.
   - 대사는 **짧고 강렬하게** — 핵심 한 문장. 긴 연설·대화 주고받기 금지.
   - 대사 부분만 큰따옴표(" ")로 묶고, 그 외 모든 발화·사유는 큰따옴표 없이 나레이션 문장에 녹임.
   - **좋은 예시 (이 리듬을 따를 것):**
     - 나레이션: `하나님이 말씀하셨습니다. 그 음성은 천둥 같았고 동시에 속삭임 같았습니다.`
     - 대사(극적 순간만): `"모세야, 모세야."`
     - 나레이션: `나는 떨며 대답했습니다. 두 발의 신을 벗고 그 자리에 엎드렸습니다.`
   - 영어도 같은 리듬: 대부분 narration, 결정적 순간에만 짧은 `"..."` 한 줄.

6. 한국어 본문은 전체 약 **1,300자(공백 제외)**, 영어는 이에 상응하는 분량 (약 1,000 words 내외, 낭독 10분). 연출 블록은 분량 계산에서 제외.
7. 마지막 "마무리" 섹션 끝에 화자가 깨달은 **영적 교훈 한 문단**을 넣습니다.
8. 줄거리 요약, 3인칭 해설, "~했습니다" 식 사건 나열 금지. 감각적 묘사·내면 독백을 중심으로 **드라마틱한 낭독 대본**으로.

## 출력 형식 (정확히 이 구조 그대로)

# {topic} — {narrator}의 시선 / A View from {narrator}

## 한국어 시나리오

### 인트로 (0:00-0:45)
SCENE: EXT./INT. 장소 — 시간대
CAMERA: (샷 종류) — (무엇을 담는지)
CHARACTER: (표정·행동·몸짓 구체 묘사)
BACKGROUND: (시대·분위기·소품·조명·색감)
TRANSITION: FADE IN

(1인칭 나레이션 본문 — 3~5문단. 대사는 이 섹션에 넣지 말거나, 꼭 필요하면 한 줄만.)

### 발단 (0:45-2:30)
SCENE: ...
CAMERA: ...
CHARACTER: ...
BACKGROUND: ...
TRANSITION: CUT TO / DISSOLVE TO / ...

(나레이션)

### 전개 (2:30-5:30)
SCENE: ...
CAMERA: ...
CHARACTER: ...
BACKGROUND: ...
TRANSITION: ...

(나레이션)

### 클라이맥스 (5:30-8:30)
SCENE: ...
CAMERA: ...
CHARACTER: ...
BACKGROUND: ...
TRANSITION: ...

(나레이션 — 이 섹션이 대사 1회가 나오기 가장 적절한 위치)

### 마무리 (8:30-10:00)
SCENE: ...
CAMERA: ...
CHARACTER: ...
BACKGROUND: ...
TRANSITION: FADE OUT

(나레이션 + 영적 교훈 한 문단)

---

## English Narration

### Intro (0:00-0:45)
SCENE: EXT./INT. Place — time of day
CAMERA: (shot type) — (subject)
CHARACTER: (expression, movement, gesture in concrete detail)
BACKGROUND: (period, atmosphere, props, lighting, color palette)
TRANSITION: FADE IN

(First-person narration, 3-5 paragraphs. Direct dialogue is rare — save it for dramatic peaks only, total 2-3 lines max across the whole scenario.)

### Rising Action (0:45-2:30)
SCENE: ...
CAMERA: ...
CHARACTER: ...
BACKGROUND: ...
TRANSITION: ...

(narration)

### Development (2:30-5:30)
SCENE: ...
CAMERA: ...
CHARACTER: ...
BACKGROUND: ...
TRANSITION: ...

(narration)

### Climax (5:30-8:30)
SCENE: ...
CAMERA: ...
CHARACTER: ...
BACKGROUND: ...
TRANSITION: ...

(narration)

### Conclusion (8:30-10:00)
SCENE: ...
CAMERA: ...
CHARACTER: ...
BACKGROUND: ...
TRANSITION: FADE OUT

(narration + one closing paragraph of spiritual reflection)
"""
