# Architecture & Design Note

## 1. Problem framing

The system is an evidence-backed decision engine, not a conversational chatbot. The primary reliability property is **grounding**: the policy PDF is authoritative, material findings need citations, and insufficient evidence must produce `NEEDS_REVIEW`.

## 2. State flow

```text
ClaimCase
  ↓
CaseAnalysisAgent
  ↓ structured State
PolicyEvidenceAgent
  ↓ ranked Evidence[]
CoverageExclusionAgent
  ↓ Findings[] + Limits[] + Missing[]
DecisionAgent
  ↓ DecisionStatus + payable amount
ValidationAgent
  ↓ PASS / FAIL
AnalysisResponse
```

The shared state is a typed Python dataclass. Agents communicate through structured fields instead of passing free-form prose between prompts.

## 3. Retrieval

The policy is parsed page-by-page. Chunks are split at meaningful headings and page boundaries, preserving `page`, `section` and `chunk_id`.

Nine targeted queries cover independent decision dimensions: hospital definition, general waiting period, pre-existing disease, financial limits, domiciliary treatment, day-care, pre/post hospitalization, cosmetic exclusion, and experimental treatment.

Dense retrieval and BM25 sparse retrieval each produce a candidate ranking. Reciprocal Rank Fusion removes the need to calibrate incompatible score ranges. A CrossEncoder reranks the fused candidates when the optional transformer stack is available.

This is deliberately multi-query because the assignment explicitly requires claims to be investigated across multiple dimensions.

## 4. Decision layer

The decision layer is intentionally deterministic for the supplied contract. This reduces hallucination risk for hard policy rules such as waiting periods and monetary caps. An LLM can be added later as a planner/summarizer, but it must not override the evidence contract.

Examples:

- 14 months current coverage + acute appendicitis → standard limits applied.
- 19 days after policy start with no qualifying prior coverage → initial waiting period.
- 27 months current coverage + pre-existing condition → 48-month waiting period not complete.
- 8-hour cataract surgery → allowed as specified Eye Surgery/day-care treatment.
- 30 pre-hospitalization days and 60 post-hospitalization days → inside policy windows.
- unknown Hospital registration/minimum criteria → abstain.

## 5. Validation

Validation is citation-aware. Every material finding must reference retrieved evidence. If the validation layer cannot see supporting evidence, the engine changes the final state to `NEEDS_REVIEW`.

The application exposes:
- agent name
- major action
- retrieval/result count
- validation status
- elapsed time

It does **not** expose hidden chain-of-thought.

## 6. Three failure cases and improvements

### Failure A — PUB-006
**Risk:** The claim looked like an ordinary acute inpatient claim, but the supplied evidence leaves hospital registration and medical necessity unresolved.

**Root cause:** A naive classifier would infer admissibility from diagnosis + inpatient duration.

**Improvement:** The Case Analysis Agent flags missing evidence and the Coverage & Exclusion Agent forces `NEEDS_REVIEW`.

### Failure B — PUB-009
**Risk:** A model could approve the full bill without checking ancillary expense timing.

**Root cause:** Retrieval of the main hospitalization clause alone misses the separate pre/post timing rule.

**Improvement:** Policy Evidence Agent runs a dedicated pre/post query and the decision layer checks 30/60-day fields.

### Failure C — PUB-010
**Risk:** A simplistic cataract rule would reject it because of the one-year cataract waiting period.

**Root cause:** It ignores the portability exception and the requirement to consider completed prior coverage years and claim history.

**Improvement:** The structured state includes prior insurer years, prior sum insured and database/claim-history receipt. The decision engine recognizes the qualifying one-year prior coverage.

## 7. Trade-offs

- **Deterministic rules over LLM adjudication:** less flexible but safer and reproducible for policy limits.
- **Local fallback retrieval:** increases portability at the cost of weaker semantic retrieval than a transformer model.
- **Multiple targeted retrieval queries:** more retrieval work, but better coverage of independent policy dimensions.
- **RRF:** robust when dense and sparse score distributions differ.
- **Citation validation:** may abstain on ambiguous cases; that is preferable to unsupported approval/rejection in this assignment.

## 8. Production hardening

For a production insurer environment I would add authentication, rate limiting, audit-log persistence, model/version pinning, retrieval regression tests, policy-version isolation, endorsement/schedule ingestion, observability, PII redaction, and human-in-the-loop escalation.
