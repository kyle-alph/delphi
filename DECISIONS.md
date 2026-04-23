# Delphi — Decision Log

Decisions made during planning. Transfer these to your repo's DECISIONS.md and continue adding as you build.

---

## Architecture: ReAct Loop with Native Tool Use

**Decision:** ReAct loop using Anthropic's native tool-use API.

**Alternatives:** Prompt chaining (hardcoded pipeline), prompt-engineered ReAct (parse free-text actions), multi-agent systems (CrewAI/AutoGen), plan-then-execute.

**Why:** Prompt chaining is too rigid for variable query types — "What's the setup for TSLA?" might need 3 or 5 tools depending on whether earnings are coming up. Prompt-engineered ReAct is fragile text parsing. Multi-agent adds unnecessary complexity and 3x token cost for a single-domain research copilot. Plan-then-execute is less adaptive to unexpected intermediate results (e.g., discovering earnings were last week, not next week). Native tool use gives structured I/O, reliable tool selection, and easy traceability.

**Trade-offs:** Less flexible than fully autonomous agents — tool set is bounded and predefined. But that's a feature for production systems, not a limitation.

**At scale:** Same pattern holds. Would add tool-call routing metrics to identify which tools are selected most/least and optimize descriptions accordingly.

---

## Database: PostgreSQL + pgvector

**Decision:** PostgreSQL with pgvector extension for both relational data and vector search.

**Alternatives:** DynamoDB (familiar from Amazon), MongoDB + Atlas Vector Search, Pinecone/Weaviate/Chroma (purpose-built vector DBs), SQLite + vector extension.

**Why:** Data is inherently relational (users → watchlists → tickers → transcripts → alerts). Need flexible querying as the project evolves — can't predict all access patterns upfront. pgvector eliminates need for a separate vector DB. SQL hybrid queries combine semantic search with metadata filtering in one statement (SELECT content FROM chunks WHERE ticker = ? ORDER BY embedding <=> ? LIMIT ?). Relational DB experience is expected outside Amazon.

**Trade-offs:** DynamoDB would scale better at millions of users. Purpose-built vector DBs (Pinecone) would outperform pgvector past ~1M vectors on search latency.

**At scale:** Add IVFFlat or HNSW index on vector column for approximate nearest neighbor search. Could migrate hot read paths to DynamoDB or add a dedicated vector DB if query volume demands it. At our scale (tens of users, thousands of rows) Postgres handles it trivially.

---

## LLM Model: Claude Sonnet

**Decision:** Claude Sonnet 4.6 as primary model for all agent interactions.

**Alternatives:** Claude Opus 4.6 (more capable, higher cost), Claude Haiku (cheaper, less capable).

**Why:** Tool orchestration and synthesis are Sonnet's strengths. At $3/$15 per million tokens (input/output), 40% cheaper than Opus with no quality gap for tool selection, multi-step chaining, and structured output tasks.

**Trade-offs:** Opus would give noticeably better output for heavy reasoning tasks like analyzing complex multi-page filings. For "decide which tools to call and synthesize results" — 90% of Delphi's workload — Sonnet is the sweet spot.

**At scale:** Would consider Haiku for simple single-tool queries (routing layer that classifies query complexity), Sonnet for multi-tool synthesis, Opus for deep analysis mode. Track quality metrics per model to validate routing doesn't degrade output.

---

## Build Approach: Hybrid (Build Core + Vibe Code Commodity)

**Decision:** Build agent loop, RAG pipeline, eval harness, and failure handling by hand. Vibe code API wrappers, tools, frontend, infrastructure.

**Alternatives:** Build everything by hand (3 weeks), vibe code everything (3-5 days).

**Why:** Core architecture (agent loop, RAG, eval) carries 80% of interview question weight — must own every line. API wrappers (Polygon.io, Finnhub, SEC EDGAR) are commodity HTTP clients with no architectural decisions to defend. Mirrors how senior engineers actually work: own the architecture, delegate the boilerplate.

**Trade-offs:** Vibe-coded components still need review — must be able to explain any tool's implementation if asked. Risk of not understanding edge cases in generated code.

**At scale:** Same principle applies in production engineering. Senior engineers design systems and review code, they don't hand-write every HTTP client.

---

## Dashboard: Live-on-Load (P0)

**Decision:** P0 dashboard fetches data live when user opens the app. No background scheduler.

**Alternatives:** Pre-computed batch job at 5:30 AM (instant load), hybrid (pre-compute slow data, live-fetch fast data).

**Why:** Simpler architecture for 2-3 users. No scheduler needed. Only burns API calls when actually used.

**Trade-offs:** User waits 30-60 seconds on load. If Polygon.io or Finnhub is slow, the whole routine is delayed.

**Two-way door to hybrid:** Tool response DTOs are designed to be serializable to PostgreSQL. Migration to hybrid = add a @Scheduled job that calls existing tool endpoints and writes to a dashboard_cache table. Frontend reads from cache instead of calling backend live. Tools don't change at all. One-day migration.

**At scale:** Would move to hybrid when load time exceeds ~10 seconds or user count grows. Pre-compute slow data (news aggregation, earnings analysis, sympathy plays) overnight, live-fetch fast data (current price, IV rank — single API calls, <500ms).

---

## Voice: Deepgram for STT (P0)

**Decision:** Deepgram (nova-2 model) for speech-to-text in v1.

**Alternatives:** OpenAI Whisper API (higher accuracy, batch-oriented).

**Why:** Latency: Deepgram returns transcripts in ~300ms vs Whisper's 1-2 seconds. For a trading copilot where speed matters, lower latency is the right default.

**Trade-offs:** Whisper has higher accuracy, especially on domain-specific financial terminology. Would use Whisper for batch/accuracy-critical workflows (e.g., transcribing an entire earnings call).

**At scale:** Would implement WebSocket streaming for real-time partial transcription (lower perceived latency — user sees words appear as they speak). Batch STT (Whisper) for background transcript ingestion. Adaptive codec selection: Opus for low bandwidth, PCM for quality. Server-side VAD for barge-in/interruption handling.

---

## Sympathy Plays: P1

**Decision:** Defer sympathy play identification to post-launch iteration.

**Alternatives:** Include in P0.

**Why:** Requires sector relationship mapping, earnings segment parsing, and cross-company exposure analysis — significant scope. Core value proposition (watchlist news + earnings summaries + chat) delivers without it.

**Trade-offs:** Missing the "killer feature" that would make the product most differentiated. But shipping a solid P0 and iterating is better than delaying launch for a complex feature.

**At scale:** Would build a sector/industry graph (GICS classification), parse earnings for segment-level revenue, and map segment exposure across companies. Could use Claude to identify sympathy relationships dynamically.
