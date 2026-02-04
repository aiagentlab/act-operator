# Act Operator 8주 완성 커리큘럼

이 커리큘럼은 uv 패키지 매니저와 AI 코딩 도구(Claude Code 등)를 활용하여, 설계부터 배포 준비까지 체계적으로 학습하는 것을 목표로 합니다.

**1~4주차**: 핵심 개념 및 기술 학습  
**5~8주차**: 실전 프로젝트 구축

---

## Part 1: 핵심 학습 (1~4주차)

### 1주차: 환경 구축 및 아키텍처 설계 (Setup & Architecting)

**목표**: Act Operator의 프로젝트 구조(Act vs Cast)를 이해하고, AI와 협업하여 첫 번째 그래프 아키텍처를 설계합니다.

**핵심 학습 내용**:
- **Act Operator 설치**: `uvx --from act-operator act new` 명령어로 프로젝트 생성 및 `uv sync`를 통한 의존성 관리
- **Act vs Cast 개념**: 'Act'는 전체 프로젝트(모노레포), 'Cast'는 개별 워크플로우(패키지)라는 구조적 차이 이해
- **AI 설계 협업**: `architecting-act` 스킬을 사용하여 "스무고개" 방식으로 요구사항을 정의하고, AI가 생성한 CLAUDE.md 명세서 검토

**실습 과제**: "주간 업무 보고서 작성기"와 같은 간단한 Cast를 생성하고, AI에게 아키텍처 다이어그램을 그리게 한 뒤 폴더 구조(modules/state.py 등)가 어떻게 생성되는지 확인하기

---

### 2주차: 핵심 로직 구현과 v1 패턴 적용 (Implementation & LangChain v1)

**목표**: LangChain v1의 새로운 패턴인 create_agent를 활용하여 비즈니스 로직을 구현합니다.

**핵심 학습 내용**:
- **Developing Skill 활용**: `developing-cast` 스킬을 호출하여 CLAUDE.md에 정의된 명세를 실제 코드로 변환 (nodes.py, tools.py 구현)
- **LangChain v1 마이그레이션**: 기존 create_react_agent 대신 `create_agent`를 사용하여 에이전트 루프를 구축하고, 도구(Tools)를 연동하는 법 학습
- **상태 관리 (State Management)**: state.py에 TypedDict를 사용하여 그래프의 상태 스키마를 정의하고 데이터 흐름 제어

**실습 과제**: 검색 도구(Tavily 등)를 tools.py에 구현하고, 이를 호출하여 답변을 생성하는 노드를 nodes.py에 작성하기

---

### 3주차: 미들웨어와 제어 흐름 (Middleware & Control Flow)

**목표**: Act Operator의 강점인 미들웨어 시스템을 적용하여 에이전트의 안정성과 제어권을 확보합니다.

**핵심 학습 내용**:
- **미들웨어(Middleware) 적용**: Human-in-the-loop(승인 절차), Summarization(대화 요약), PII(개인정보 보호) 기능을 middlewares.py에 구현
- **LangGraph 제어 흐름**: conditions.py를 활용한 조건부 분기(Conditional Edge) 및 체크포인터(Checkpointer)를 통한 상태 저장(Persistence) 구현
- **복합 패턴**: AI에게 `developing-cast` 스킬을 통해 특정 도구 실행 전 "사용자 승인"을 받도록 로직 수정 요청

**실습 과제**: 이메일 전송 전 사용자 승인을 요청하는 HumanInTheLoopMiddleware를 적용하고, 대화가 길어질 경우 자동으로 요약하는 로직 추가하기

---

### 4주차: 엔지니어링 및 운영 최적화 (Engineering & Operations)

**목표**: 다중 Cast 관리, 테스트 코드 작성, 그리고 LangSmith를 통한 관측 가능성을 확보합니다.

**핵심 학습 내용**:
- **의존성 관리**: `engineering-act` 스킬을 사용하여 모노레포 내의 여러 Cast 간 의존성(pyproject.toml)을 관리하고 새로운 Cast(`uv run act cast`) 추가
- **테스트 자동화**: `testing-cast` 스킬을 활용하여 pytest 기반의 유닛 테스트와 Mocking 코드를 자동으로 생성 및 실행
- **관측 가능성(Observability)**: `LANGSMITH_TRACING=true` 설정을 통해 에이전트의 실행 과정을 추적하고 디버깅

**실습 과제**: 메인 챗봇 Cast 외에 별도의 '데이터 전처리 Cast'를 추가하여 서브 그래프로 연결하고, 전체 파이프라인에 대한 테스트 코드 작성하기

---

## Part 2: 실전 프로젝트 (5~8주차)

### 5주차: 지능형 웹 리서치 에이전트 (The Intelligent Researcher)

**학습 목표**: Act Operator의 기본 구조(State, Nodes, Tools)와 SummarizationMiddleware 활용법 습득

**프로젝트 개요**: 사용자의 질문에 대해 웹을 검색(Tavily 등)하고, 내용을 요약하여 보고서 형태로 답변하는 에이전트입니다. 대화가 길어질 경우 자동으로 문맥을 요약하여 토큰을 절약합니다.

**Act Operator 활용 포인트**:
- **설계 (@architecting-act)**: AI에게 "웹 검색 도구를 사용하고, 대화가 길어지면 요약하는 챗봇을 설계해줘"라고 요청하여 CLAUDE.md 명세 생성
- **구현 (@developing-cast)**:
  - tools.py: 검색 도구 정의
  - middlewares.py: SummarizationMiddleware를 적용하여 토큰 제한 도달 시 대화 기록 압축
  - agents.py: LangChain v1의 `create_agent`를 사용하여 에이전트 루프 구축

---

### 6주차: 승인 기반 이메일 자동화 봇 (Human-in-the-loop Email Assistant)

**학습 목표**: 프로덕션 환경에서 필수적인 Human-in-the-loop(휴먼 인터럽트) 기능과 PII(개인정보) 보호 미들웨어 구현

**프로젝트 개요**: 사용자의 요청으로 이메일 초안을 작성하지만, 실제 전송(send_email 도구 실행) 전에는 반드시 사람의 승인을 받도록 중단(Interrupt)됩니다. 또한, 이메일 내용에 포함된 민감한 정보(전화번호 등)를 자동으로 마스킹합니다.

**Act Operator 활용 포인트**:
- **구조화 (modules/)**: 비즈니스 로직과 안전 장치를 분리
- **미들웨어 적용 (middlewares.py)**:
  - HumanInTheLoopMiddleware: send_email 도구 호출 시 실행을 일시 정지하고 사용자 승인/수정/거부 대기
  - PIIMiddleware: 이메일 본문이나 로그에 포함된 개인정보(PII)를 자동으로 감지하여 가림 처리
- **상태 저장 (graph.py)**: LangGraph의 Checkpointer(InMemorySaver 또는 PostgresSaver)를 설정하여 중단된 지점부터 실행을 재개

---

### 7주차: 지속성 메모리 기반 RAG 챗봇 (Persistent RAG Knowledge Base)

**학습 목표**: 벡터 데이터베이스(Pinecone/Weaviate) 연동과 장기 기억(Long-term Memory) 처리

**프로젝트 개요**: 회사 내부 문서나 특정 지식 베이스를 기반으로 답변하며, 사용자의 이전 대화 맥락을 끊기지 않고 기억하는 챗봇입니다. LangGraph의 지속성(Persistence) 기능을 활용해 서버가 재시작되어도 대화 흐름을 유지합니다.

**Act Operator 활용 포인트**:
- **엔지니어링 (@engineering-act)**: langchain-pinecone 또는 langchain-weaviate 패키지를 추가하고 환경 변수 설정
- **상태 정의 (state.py)**: 검색된 문서(Context)와 대화 기록(History)을 관리하는 TypedDict 스키마 정의
- **도구 구현 (tools.py)**: 벡터 DB에서 유사도 검색(Similarity Search)을 수행하는 도구 구현
- **테스트 (@testing-cast)**: 실제 벡터 DB 연결 없이 로직을 검증하기 위해 검색 도구에 대한 Mocking 테스트 코드 작성

---

### 8주차: 멀티 에이전트 개인 비서 (Supervisor Pattern Assistant)

**학습 목표**: 복잡한 작업을 여러 하위 에이전트(Sub-agents)로 분리하고 이를 조율하는 Supervisor 패턴 구현

**프로젝트 개요**: 사용자의 요청을 분석하여 '일정 관리(Calendar)'가 필요하면 일정 에이전트에게, '이메일 작성'이 필요하면 이메일 에이전트에게 작업을 위임하는 중앙 감독자(Supervisor) 에이전트를 만듭니다.

**Act Operator 활용 포인트**:
- **Cast 확장 (uv run act cast)**: 하나의 모노레포 안에 calendar_cast와 email_cast를 별도 패키지로 생성하여 모듈성을 극대화
- **설계 (@architecting-act)**: AI에게 "Supervisor 패턴을 사용하여 두 개의 하위 에이전트를 관리하는 아키텍처를 그려줘"라고 요청
- **의존성 관리 (@engineering-act)**: 각 Cast별로 필요한 라이브러리(예: Google Calendar API 등)를 pyproject.toml에서 독립적으로 관리

---

## 커리큘럼 요약표

| 주차 | 주제 | 핵심 키워드 |
|:---:|---|---|
| 1주차 | 환경 구축 및 아키텍처 설계 | Act vs Cast, architecting-act |
| 2주차 | 핵심 로직 구현과 v1 패턴 | create_agent, Tools, Nodes |
| 3주차 | 미들웨어와 제어 흐름 | Middleware, Persistence |
| 4주차 | 엔지니어링 및 운영 최적화 | 테스트 자동화, LangSmith |
| 5주차 | 프로젝트1: 웹 리서치 에이전트 | SummarizationMiddleware |
| 6주차 | 프로젝트2: 이메일 자동화 봇 | Human-in-the-loop, PII |
| 7주차 | 프로젝트3: RAG 챗봇 | 벡터 DB, Persistence |
| 8주차 | 프로젝트4: 멀티 에이전트 비서 | Supervisor 패턴, 모듈성 |

---

## 학습 팁

1~4주차에서 단일 에이전트와 미들웨어의 기본기를 마스터한 후, 5~8주차에서 실전 프로젝트를 통해 복합적인 아키텍처를 다루는 것이 가장 효율적입니다.