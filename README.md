# 🔍 Gemini 위조 문서 판별 시스템 (AI Forgery Document Review System)

> **Automated Multimodal Forensic Document Examination & Fraud Prevention with Gemini 3.5 & 3.1**
>
> **Gemini 3.5 Flash 및 3.1 Pro 모델을 활용한 상거래 위조 서류 탐지 및 자동 검증 가이드**

<div align="left">
  <a href="https://colab.research.google.com/github/cjk0604/AI-forgery/blob/main/hands_on/forgery_detection_hands_on.ipynb">
    <img src="https://colab.research.google.com/assets/colab-badge.svg" alt="Open In Colab">
  </a>
  <a href="https://console.cloud.google.com/vertex-ai/colab/import/https:%2F%2Fraw.githubusercontent.com%2Fcjk0604%2FAI-forgery%2Fmain%2Fhands_on%2Fforgery_detection_hands_on.ipynb">
    <img src="https://img.shields.io/badge/Colab_Enterprise-Open-blue?logo=google-cloud" alt="Open In Colab Enterprise">
  </a>
  <a href="https://github.com/cjk0604/AI-forgery/blob/main/hands_on/forgery_detection_hands_on.ipynb">
    <img src="https://img.shields.io/badge/GitHub-View_Source-black?logo=github" alt="View on GitHub">
  </a>
</div>

---

## 🌐 Language (언어 선택)
- [🇰🇷 한국어 설명 (#-한국어-korean)](#-한국어-korean)
- [🇺🇸 English Description (#-english)](#-english)

---

## 🇰🇷 한국어 (Korean)

### 📌 프로젝트 개요
본 프로젝트는 고객이 제출한 영수증, 구매내역서 등의 상거래 문서 이미지 내 위조, 변조, 혹은 생성형 AI 기반의 합성 흔적을 자동으로 탐지하는 **AI 위조 문서 판별 시스템**입니다. 

Google의 최신 **Gemini 3.5 Flash 및 3.1 Pro** 멀티모달 모델의 인지 분석 능력과 **수학적 합산 검증 & 사업자등록번호(BRN) 체크섬** 등의 결정적 비즈니스 규칙(Deterministic Rules)을 융합하여 오탐과 미탐을 극소화하는 포렌식 파이프라인을 구축하고 평가합니다.

### 🏗️ 아키텍처 패턴: 듀얼 티어 모델 전략 (Dual-Tiered Routing)
운영 비용과 분석 정밀도를 최적화하기 위해 다음과 같은 하이브리드 라우팅 아키텍처를 채택합니다:
- **`gemini-3.5-flash` (1차 고속 필터링):** 초고속 응답성 및 극도의 비용 효율성. 명백한 일자/금액 불일치 1차 스크리닝.
- **`gemini-3.1-pro-preview` (2차 정밀 심층 오딧):** 독보적인 인지/추론 능력. 미세한 한글/영문 오타, URL 타이포스쿼팅 도메인, 정교한 합성 레이아웃 정밀 검증.

---

### 📊 포렌식 판별 결과 대시보드 (V2 Prompt 기준)

실제 검증셋 및 사기방지 운영팀 정답지(Ground Truth)를 기준으로 평가한 결과 대시보드입니다:

| 검증 문서 이미지 | Flash V1 | Pro V1 | Flash V2 | Pro V2 (최종) | 포렌식 적발 트리거 및 모순점 (Pro V2) |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **무신사 구매내역서 (아디다스)** | `FORGED` | `FORGED` | `FORGED` | `FORGED` (1.00) ✅ | **Inspect Element 조작:** URL 파라미터 내 날짜 메타데이터(`20251228`)와 페이지 내 주문 표기 일자(`25.12.08`) 불일치 |
| **무신사 구매내역서 (내셔널지오그래픽)** | `FORGED` | `FORGED` | **`GENUINE` ❌** | `FORGED` (1.00) ✅ | **타이포스쿼팅 도메인 & 수학적 모순:** 팝업 URL 내 도메인 오타 주소(`muslnsa.com` / 소문자 'L') 및 품목 금액 합산 수학적 불일치 (`208,700` vs `267,000`) |
| **무신사 구매내역서 (아디다스 2)** | `FORGED` | `FORGED` | `FORGED` | `FORGED` (1.00) ✅ | **Inspect Element 조작:** URL 경로의 주문번호(`202512282202550002`)와 실제 페이지 상의 주문번호(`202512081527490001`) 불일치 |
| **아디다스 매장 영수증** | `FORGED` | `FORGED` | `FORGED` | `FORGED` (1.00) ✅ | **미래 일자 & 주소 불일치:** 영수증 인쇄 일자가 미래 시점(`2026/01/24`)이며, 지점명(**\"인산점\"**)과 표기된 실제 주소(**\"경기 하남시\"**)의 모순 |
| **현대백화점 영수증** | `FORGED` | `FORGED` | **`GENUINE` ❌** | `FORGED` (1.00) ✅ | **브랜드 철자 오타 & 합성 템플릿:** 미래 일자 표기 및 명품 브랜드명 오타 (**\"롱삼\"** ➡️ **\"롱샴\"** / Longchamp), 영수증 한가운데 인위적인 수직선 그어짐 흔적 |

---

### 💡 주요 분석 인사이트
1. **정밀 태스크에서의 인지 능력 편차:** 고도화된 System Prompt V2 환경에서도 **`gemini-3.5-flash` 모델은 2개의 정교한 위조본을 적발하지 못하고 `GENUINE`(정상)으로 판별하는 오류**를 범했습니다. 특히 \"롱삼\" 철자 오타나 `muslnsa.com`과 같은 1글자 도메인 차이점을 포착하지 못했습니다.
2. **Pro의 완벽한 검출 성능:** 반면 **`gemini-3.1-pro-preview` 모델은 5개 위조 서류에 대해 단 한 건의 오탐도 없이 100% 완벽하게 시각적/텍스트적 위조 징후를 탐지(신뢰도 1.00)**해 냈습니다.
3. **운영 권장 구조:** 리스크 및 금액이 높은 거래 건이나 Flash의 판별 신뢰도가 낮은 의심 거래 건은 **반드시 `gemini-3.1-pro-preview` 모델을 통한 심층 오딧(Deep Audit)** 단계를 거치도록 파이프라인 라우팅을 적용해야 합니다.

---

### 🚀 시작하기 & 실행 방법
1. 위의 **"Open in Colab"** 또는 **"Open in Colab Enterprise"** 배지를 클릭하여 실습 가이드 노트를 실행합니다.
2. **Setup & 환경 설정:** 안내에 따라 필요한 Google GenAI SDK 패키지를 원클릭 설치합니다.
3. **대화형 파일 업로드:** **Section 4**를 실행하면 업로드 브라우저 팝업창이 나타납니다. 준비하신 테스트용 위조 의심 문서 이미지 파일들을 드래그 앤 드롭으로 손쉽게 업로드합니다.
4. **인증 및 클라이언트:** 본인의 Vertex AI API Key, AI Studio API Key, 혹은 active GCP credential 환경에 맞추어 클라이언트를 자동 빌드해 주는 통합 초기화 셀을 활용해 안전하게 인증을 완료하고 테스트를 실행합니다.

---

## 🇺🇸 English

### 📌 Project Overview
This repository features an **AI Forgery Document Review System** designed to automatically detect visual tampering, inspect-element HTML modifications, and synthetic layout anomalies in user-submitted documents (receipts, statements, invoices).

By combining **multimodal forensic reasoning** using Google's latest **Gemini 3.5 Flash & 3.1 Pro** models with **deterministic business verification rules** (such as mathematical subtotal verification and Luhn-like checksums), this framework establishes a production-grade forensic pipeline maximizing recall and precision.

### 🏗️ Architectural Pattern: Dual-Tiered Routing
We implement a hybrid routing architecture to balance operations SLA, cost, and absolute precision:
- **`gemini-3.5-flash` (Tier 1 Screening):** Blazing-fast response, ultra-low cost. Ideal for quick screener checks on obvious discrepancies.
- **`gemini-3.1-pro-preview` (Tier 2 Deep Audit):** Premium cognitive auditing. Crucial for detecting subtle spelling typos, domain typosquatting, and pixel-perfect overlay manipulations.

---

### 📊 Forensic Evaluation Capability Dashboard (Prompt V2)

Our live audited evaluation dashboard compared against operations-validated ground truth:

| Document Name | Flash V1 | Pro V1 | Flash V2 | Pro V2 (Final) | Core Forgery Triggers Detected (Pro V2) |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Musinsa Adidas Screenshot** | `FORGED` | `FORGED` | `FORGED` | `FORGED` (1.00) ✅ | **Inspect Element Manipulation:** Discrepancy between URL date parameter (`20251228` / Dec 28) and visible page order date (`25.12.08` / Dec 8). |
| **Musinsa National Geographic** | `FORGED` | `FORGED` | **`GENUINE` ❌** | `FORGED` (1.00) ✅ | **Typosquatting & Arithmetic Mismatch:** Domain typosquatting (`muslnsa.com` with 'L') in browser statement URL. Product line sums do not add up to subtotal (`208,700` vs `267,000`). |
| **Musinsa Adidas Screenshot 2** | `FORGED` | `FORGED` | `FORGED` | `FORGED` (1.00) ✅ | **Inspect Element Manipulation:** Discrepancy between URL order ID parameter (`202512282202550002`) and visible order number (`202512081527490001`). |
| **Adidas Receipt** | `FORGED` | `FORGED` | `FORGED` | `FORGED` (1.00) ✅ | **Future Date & Location Conflict:** Receipt dated in the future (`2026/01/24`). Branch named **\"인산점\"** (typo for Ansan) but address lists **\"경기 하남시\"** (Hanam City). |
| **Hyundai Department Store** | `FORGED` | `FORGED` | **`GENUINE` ❌** | `FORGED` (1.00) ✅ | **Luxury Brand Spelling & Synthesized Grid:** Dated in the future. Brand printed as **\"롱삼\"** (typo for **\"롱샴\"** / Longchamp). Perfectly centered vertical crease indicates digital generation. |

---

### 💡 Key Forensic Insights
1. **The High-Precision Cognitive Gap:** Even under our strict forensic V2 prompt, **`gemini-3.5-flash` failed to flag two highly sophisticated receipts**, incorrectly evaluating them as **`GENUINE`**. Flash missed the brand spelling typo (\"롱삼\" for Longchamp) and the domain typosquatting (`muslnsa.com`), struggling with small semantic tokens in dense contexts.
2. **Pro's Superiority:** **`gemini-3.1-pro-preview` executed flawlessly, scoring 100% recall and precision (1.00 confidence score)** across all target items, identifying all spelling, address, date, and visual manipulations.
3. **Production Routing Strategy:** suspicious, high-value, or low-confidence screening outcomes should **always route to `gemini-3.1-pro-preview`** using System Prompt V2 for forensic-level auditing.

---

### 🚀 Quick Start & Run Guide
1. Click the **"Open in Colab"** or **"Open in Colab Enterprise"** badges above to launch the guide in your browser.
2. **Setup & Dependencies:** Run Section 1 to install the `google-genai` SDK and processing packages.
3. **Interactive File Upload:** Run **Section 4** to reveal the drag-and-drop file upload widget. Simply upload your own target images.
4. **Universal Authentication:** Configure your preferred authentication model (Vertex AI API Key, AI Studio API Key, environment variables, or active cloud credentials) in the flexible initial cell and start analyzing!
