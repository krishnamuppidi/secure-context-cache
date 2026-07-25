#!/usr/bin/env python3
"""Build static discoverability pages and machine-readable website assets."""

from __future__ import annotations

import hashlib
import html
import json
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from xml.sax.saxutils import escape

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site"
BASE_URL = "https://krishnamuppidi.github.io/secure-context-cache/"
REPOSITORY = "https://github.com/krishnamuppidi/secure-context-cache"
SECURE_REVIEW_AGENT = "https://github.com/krishnamuppidi/secreviewagent-ai"
TODAY = date(2026, 7, 25)
INDEXNOW_KEY = hashlib.sha256(BASE_URL.encode()).hexdigest()[:32]


@dataclass(frozen=True)
class Section:
    title: str
    paragraphs: tuple[str, ...]
    bullets: tuple[str, ...] = ()
    code: str = ""
    table: tuple[tuple[str, ...], ...] = ()
    citations: tuple[tuple[str, str], ...] = ()


@dataclass(frozen=True)
class Page:
    slug: str
    title: str
    kicker: str
    description: str
    keywords: tuple[str, ...]
    summary: str
    intent: str
    sections: tuple[Section, ...]
    related: tuple[str, ...]
    schema_type: str = "TechArticle"


PAGES = (
    Page(
        slug="ai-token-optimization-framework",
        title="Open-Source AI Token Optimization Framework",
        kicker="Complete optimization pipeline",
        description="Open-source AI token optimization with measurement, secure context selection, reuse, prompt caching, optional compression, routing adapters, and quality gates.",
        keywords=(
            "AI token optimization framework",
            "best LLM token optimization framework",
            "open source token optimization",
            "LLM cost optimization framework",
        ),
        summary="Use one measurable pipeline to reduce unnecessary LLM tokens while preserving task quality, provider portability, provenance, and least-privilege context controls.",
        intent="Choose and deploy a token optimization framework",
        sections=(
            Section(
                "Token optimization is a pipeline, not one trick",
                (
                    "Prompt compression, semantic caching, provider prefix caching, smaller-model routing, and inference KV caching solve different parts of the cost problem. Secure Context Cache combines the useful boundaries without pretending that one algorithm works for every prompt, provider, or workload.",
                    "The framework measures the baseline, selects the smallest authorized context, reuses compiled slices and stable prefixes, compresses only long authorized capsules, integrates with downstream routers, and verifies quality before counting savings.",
                ),
                (
                    "Measure with model tokenizers and provider-reported usage.",
                    "Select source-backed facts by task, identity, sensitivity, and freshness.",
                    "Reuse compiled context and native provider prompt caches.",
                    "Compress and route only behind explicit workload quality gates.",
                ),
                "acg optimize --repo examples/sample_repo \\\n  --task-type iac_security \\\n  --path terraform/prod/payments/lambda.tf \\\n  --prompt \"Review security risk\" \\\n  --provider openai --token-budget 800",
            ),
            Section(
                "Bring the best techniques together safely",
                (
                    "SCC supports optional LLMLingua-2 compression after authorization, native cache boundaries for OpenAI, Anthropic, and Amazon Bedrock, provider-usage normalization, and clean downstream integration with LiteLLM, Portkey, RouteLLM, vLLM, or internal gateways.",
                    "Security is the add-on generic optimizers usually lack. A cache namespace binds authorization scope and source state; denied data never enters the model or compressor; stable context retains citations; and every release has policy, provenance, expiry, and audit evidence.",
                ),
                (
                    "No heavyweight compressor in the default runtime or Lambda package.",
                    "No semantic response caching across untrusted tenants or system policies.",
                    "No savings claim without accepted-result and prohibited-release evidence.",
                    "No provider lock-in: the capsule and optimization plan are model neutral.",
                ),
            ),
            Section(
                "What to compare in a real evaluation",
                (
                    "The best framework is the one that lowers cost per accepted result on your task set. Compare full approved context, retrieval-only context, provider caching, compression, routing, and SCC policy-scoped capsules with the same models and quality rubric.",
                    "Report input, cached-input, cache-write, and output tokens; latency; pricing date; recall; reviewer acceptance; stale-context use; and prohibited-context release. Publish failures as well as averages.",
                ),
                (
                    "Start with one repeated, read-only workload.",
                    "Define must-find facts and an authorization threshold before tuning.",
                    "Use provider usage as authoritative and estimates as planning data.",
                    "Expand only after both quality and isolation thresholds pass.",
                ),
            ),
        ),
        related=("llm-token-optimization", "reduce-llm-token-cost", "prompt-caching-vs-context-caching"),
    ),
    Page(
        slug="docs",
        title="Secure Context Cache Documentation",
        kicker="Documentation hub",
        description="Documentation for Secure Context Cache: architecture, APIs, policy, deployment, integrations, benchmarks, security, and production-readiness guidance.",
        keywords=("Secure Context Cache docs", "AI context gateway API", "LLM context documentation"),
        summary="Start with the architecture, run the local demo, integrate an agent, and evaluate secure token optimization with explicit quality and authorization gates.",
        intent="Learn, integrate, and evaluate",
        sections=(
            Section(
                "Choose the shortest path to a working capsule",
                (
                    "Secure Context Cache compiles approved repository, policy, runbook, and service facts into reusable slices. Agent Context Gateway authenticates a workload, applies task and sensitivity policy, and returns a short-lived capsule containing only the facts allowed for that request.",
                    "New evaluators should run the deterministic local fixture before deploying infrastructure. The fixture makes the release and denial boundary visible without requiring a cloud account or model-provider credential.",
                ),
                (
                    "Run the local quick start and inspect the capsule, audit record, and metrics JSON.",
                    "Read the architecture and policy guides before uploading organization-owned material.",
                    "Use one client example to place the capsule before the model invocation.",
                    "Compare the optimized path with a generous approved baseline using the same tasks and quality rubric.",
                ),
                "python -m venv .venv\n. .venv/bin/activate\npip install -e \".[dev]\"\nacg demo --repo examples/sample_repo --out build/demo\npytest -q",
            ),
            Section(
                "Documentation map",
                (
                    "The repository remains the source of truth for exact commands, APIs, environment variables, and security limitations. This website provides crawlable explanations and routes agents and engineers to the canonical files.",
                    "Production adoption requires organization-specific source governance, identity, policy review, monitoring, retention, adversarial testing, and an acceptance threshold for answer quality.",
                ),
                (
                    "Getting Started, API Reference, Architecture, and Agent Integration",
                    "Policy Guide, Context Sources, Security, and Production Readiness",
                    "AWS, Kubernetes, operations, troubleshooting, and deployer IAM",
                    "Benchmark method, comparisons, provider integration patterns, and SecureReviewAgent case study",
                ),
            ),
        ),
        related=("secure-context-cache-benchmark", "ai-context-engineering", "securereviewagent-case-study"),
    ),
    Page(
        slug="reduce-llm-token-cost",
        title="How to Reduce LLM Token Cost Without Losing Answer Quality",
        kicker="Token economics",
        description="A practical method to reduce LLM input-token cost while preserving required facts, answer quality, provenance, and least-privilege controls.",
        keywords=("reduce LLM token cost", "AI token cost optimization", "lower LLM API cost"),
        summary="Optimize repeated context before model invocation, then count savings only when the result still passes a defined quality threshold.",
        intent="Reduce cost per accepted result",
        sections=(
            Section(
                "Find the repeated input before changing the model",
                (
                    "Enterprise AI cost often grows because the same repository summaries, policies, service maps, and runbooks are attached to every request. Model routing and smaller models can help, but they do not remove duplicated context or reduce the exposure created by oversized prompts.",
                    "Measure the current path first. Record provider-reported input, cached-input, and output tokens; latency; price assumptions; and whether the result was accepted. Group input by source so the team can see which material repeats and which facts actually influence the task.",
                ),
                (
                    "Separate stable enterprise context from the task-specific diff or question.",
                    "Precompute source-backed facts that can be reused safely.",
                    "Select facts by identity, task, path, environment, sensitivity, and freshness.",
                    "Retain a generous approved baseline for quality comparison.",
                ),
            ),
            Section(
                "Use quality-gated savings, not token reduction alone",
                (
                    "A cheaper answer that misses a required IAM dependency or operational constraint is not an optimization. Define must-find cases and reviewer acceptance before measuring savings. Replay the same tasks through the baseline and capsule paths with the same model settings.",
                    "The repository fixture reports a deterministic 32-to-16 word-count proxy. It demonstrates the measurement flow, not a production cost guarantee. Provider invoices and production quality evidence are required for production claims.",
                ),
                (
                    "Track recall, precision, reviewer agreement, and overrides.",
                    "Track prohibited-context release and stale-context use.",
                    "Report cost per accepted, correct, policy-compliant result.",
                    "Expand the capsule when savings reduce quality below the agreed floor.",
                ),
            ),
        ),
        related=("llm-token-optimization", "secure-context-cache-benchmark", "prompt-caching-vs-context-caching"),
    ),
    Page(
        slug="prompt-caching-vs-context-caching",
        title="Prompt Caching vs. Context Caching for AI Agents",
        kicker="Architecture comparison",
        description="Compare provider prompt caching with governed context caching, including cost, freshness, authorization, provenance, and quality tradeoffs.",
        keywords=("prompt caching vs context caching", "LLM prompt cache", "AI context cache"),
        summary="Prompt caching discounts repeated provider input; context caching decides which enterprise facts should be assembled and authorized before that input is sent.",
        intent="Choose the correct cache boundary",
        sections=(
            Section(
                "The two caches solve different problems",
                (
                    "Provider prompt caching can reduce the price or processing overhead of repeated input prefixes. It is valuable when a stable prompt segment is sent repeatedly to the same provider under compatible cache rules.",
                    "Secure context caching operates earlier. It ingests approved sources, normalizes facts, tracks versions and sensitivity, and assembles a task-scoped capsule. It can reduce the input that reaches any model while preserving the reason each fact was released.",
                ),
                (
                    "Prompt caching optimizes repeated provider input.",
                    "Context caching optimizes enterprise knowledge preparation and selection.",
                    "Prompt caching does not by itself authorize sensitive context.",
                    "Context caching does not replace provider cache accounting.",
                ),
            ),
            Section(
                "Use both when the workload supports both",
                (
                    "A strong design can build a small policy-approved capsule, place stable instructions and schemas in a provider-cacheable prefix, and keep volatile task facts outside that prefix. Each context release still needs a current authorization decision even when the underlying slice was previously cached.",
                    "Measure provider cache reads and writes separately from capsule reduction. Also record freshness, source hashes, policy version, quality, and denied context so a lower bill cannot hide a broader exposure or stale answer.",
                ),
                (
                    "Invalidate or version source-backed slices when approved sources change.",
                    "Reevaluate authorization for every task and identity.",
                    "Keep credentials and action authority outside both caches.",
                    "Fail closed when no approved context is available.",
                ),
            ),
        ),
        related=("secure-context-caching", "openai-token-optimization", "aws-bedrock-token-optimization"),
    ),
    Page(
        slug="rag-vs-secure-context-cache",
        title="Secure RAG Architecture: Authorization vs. Retrieval",
        kicker="Secure RAG architecture",
        description="Build secure RAG with identity, task, path, sensitivity, freshness, and policy authorization before retrieved content reaches an AI model.",
        keywords=(
            "secure RAG architecture",
            "RAG authorization",
            "RAG access control",
            "enterprise RAG security",
            "least privilege RAG",
        ),
        summary="Secure RAG treats retrieved chunks as candidates, then applies deterministic authorization before any candidate content crosses the model boundary.",
        intent="Authorize retrieval before model access",
        sections=(
            Section(
                "What is secure RAG?",
                (
                    "Secure RAG is a retrieval-augmented generation architecture in which retrieved content is only a candidate set. A deterministic authorization layer evaluates the requesting identity, task, resource path, environment, sensitivity, freshness, source approval, and policy before releasing content to the model.",
                    "Semantic similarity answers whether a chunk may be relevant. It does not prove that an agent may see a document, tenant, incident, production environment, or secret-adjacent runbook. Secure Context Cache adds that missing release decision while retaining provenance and token measurements.",
                ),
                (
                    "Retrieval supplies candidates; it does not grant access.",
                    "Authorization runs outside the model and before prompt construction.",
                    "Denied content stays out of model-visible context and response payloads.",
                    "Fail-closed behavior prevents unrestricted fallback from an empty authorized result.",
                ),
            ),
            Section(
                "Traditional RAG, secure RAG, and SCC",
                (
                    "Secure RAG strengthens retrieval with an authorization layer. Secure Context Cache implements that boundary and also provides token measurement, compiled-context reuse, provider-cacheable prefixes, optional compression, routing adapters, expiring capsules, and audit evidence.",
                ),
                table=(
                    ("Capability", "Traditional RAG", "Secure RAG", "Secure Context Cache"),
                    ("Semantic retrieval", "Yes", "Yes", "Optional input stage"),
                    ("User or agent identity", "Sometimes", "Required", "Required"),
                    ("Task authorization", "Rare", "Yes", "Built in"),
                    ("Path and environment policy", "Rare", "Possible", "Built in"),
                    ("Sensitivity enforcement", "Metadata dependent", "Required", "Policy evaluated"),
                    ("Denied-item audit", "Rare", "Recommended", "Built in"),
                    ("Expiring model context", "Rare", "Possible", "Capsule TTL"),
                    ("Token optimization", "Incidental", "Possible", "Primary measurement"),
                    ("Provenance and hashes", "Varies", "Recommended", "Preserved"),
                ),
            ),
            Section(
                "Authorize candidates with one API call",
                (
                    "The application performs retrieval, then sends candidate content and security metadata to `/v1/authorize-retrieval`. The response returns an approved capsule plus candidate IDs and reasons for denials. Denied content is never echoed.",
                    "If no candidate passes, `fail_closed` is true, the stable context is empty, and unrestricted fallback is explicitly prohibited. The caller must stop or use a separately authorized recovery path.",
                ),
                code='''POST /v1/authorize-retrieval
{
  "task_type": "iac_security",
  "path": "terraform/prod/payments/lambda.tf",
  "environment": "prod",
  "candidates": [
    {"candidate_id": "rag-1", "content": "KMS control...", "refs": ["terraform/prod/payments/lambda.tf"], "sensitivity": "high"},
    {"candidate_id": "rag-2", "content": "Incident detail...", "refs": ["incidents/restricted.md"], "sensitivity": "restricted"}
  ]
}

retrieval.authorized_candidate_ids = ["rag-1"]
retrieval.denied_candidates = [{"candidate_id": "rag-2", "sensitivity": "restricted", "reason": "..."}]
retrieval.unrestricted_fallback_allowed = false''',
            ),
            Section(
                "When to use each architecture",
                (
                    "Use traditional RAG for public or uniformly authorized corpora where relevance is the main risk. Add secure RAG when users, agents, tenants, tasks, paths, or environments have different access boundaries. Use Secure Context Cache when the workload also needs measurable token optimization, reusable compiled context, provenance, expiry, and release audits.",
                    "Keep action authorization separate from context authorization. Even an authorized fact does not grant permission to execute a tool, modify infrastructure, or access another system.",
                ),
                (
                    "Public knowledge base: relevance-first RAG may be enough.",
                    "Enterprise multi-tenant assistant: secure RAG is the minimum boundary.",
                    "Repeated governed agent workflow: SCC adds reusable token optimization.",
                    "High-risk actions: require a separate action-policy decision.",
                ),
            ),
            Section(
                "Independent security guidance",
                (
                    "The design aligns with independent guidance that treats authorization, tenant isolation, prompt injection, and agent identity as separate controls. These sources support the architecture; they do not endorse Secure Context Cache.",
                ),
                citations=(
                    (
                        "AWS Security: authorization mechanisms for data used in generative AI",
                        "https://aws.amazon.com/blogs/security/implement-effective-data-authorization-mechanisms-to-secure-your-data-used-in-generative-ai-applications/",
                    ),
                    (
                        "AWS Architecture: secure multi-tenant RAG with Verified Permissions",
                        "https://aws.amazon.com/blogs/architecture/secure-multi-tenant-rag-with-amazon-bedrock-and-verified-permissions/",
                    ),
                    (
                        "OWASP GenAI: prompt injection risk",
                        "https://genai.owasp.org/llmrisk/llm01-prompt-injection/",
                    ),
                    (
                        "NIST NCCoE: software and AI agent identity and authorization concept paper",
                        "https://www.nccoe.nist.gov/sites/default/files/2026-02/accelerating-the-adoption-of-software-and-ai-agent-identity-and-authorization-concept-paper.pdf",
                    ),
                ),
            ),
        ),
        related=(
            "secure-rag-architecture-checklist",
            "least-privilege-ai-context",
            "enterprise-ai-agent-memory-security",
        ),
    ),
    Page(
        slug="secure-rag-architecture-checklist",
        title="Secure RAG Architecture Review Checklist",
        kicker="Practical review artifact",
        description="Review secure RAG identity, tenant isolation, retrieval authorization, prompt injection, fail-closed behavior, provenance, audit, and token quality.",
        keywords=(
            "secure RAG checklist",
            "RAG security review",
            "RAG authorization checklist",
            "enterprise AI security checklist",
        ),
        summary="Use this implementation-neutral checklist to review whether a RAG system enforces authorization before model access and measures security with answer quality.",
        intent="Review a secure RAG design",
        sections=(
            Section(
                "Identity and isolation",
                (
                    "Record the actor that initiated the task and the workload identity that calls retrieval and authorization services. Preserve the mapping in audit records without exposing bearer tokens or credentials to the model.",
                ),
                (
                    "Propagate verified end-user and workload identities.",
                    "Enforce tenant boundaries in storage, retrieval, and authorization.",
                    "Bind cache namespaces to identity, tenant, policy, and source state.",
                    "Test cross-user, cross-agent, and cross-tenant access attempts.",
                ),
            ),
            Section(
                "Authorization before prompt construction",
                (
                    "Treat every retrieved chunk as a candidate. Evaluate identity, task, path, environment, sensitivity, freshness, approval state, and source governance before serializing any candidate into a model message.",
                ),
                (
                    "Run deterministic policy outside the model.",
                    "Return denied IDs and reasons without returning denied content.",
                    "Fail closed when the authorized candidate set is empty.",
                    "Never let model output or prompt text override a deny decision.",
                ),
            ),
            Section(
                "Injection, provenance, and freshness",
                (
                    "Retrieved text is untrusted data even when the source is approved. Separate instructions from data, retain source references and hashes, and expire or invalidate context when policy or source state changes.",
                ),
                (
                    "Test direct and indirect prompt injection in retrieved content.",
                    "Preserve source references, versions, hashes, and parser versions.",
                    "Set capsule TTLs and explicit freshness thresholds.",
                    "Keep source and index credentials outside model-visible context.",
                ),
            ),
            Section(
                "Measure accepted results",
                (
                    "A secure system can still be unusable, and a token-efficient system can still be insecure. Compare against the same approved baseline and count savings only when the result meets the agreed task-quality threshold.",
                ),
                (
                    "Capture provider-reported input, cached-input, and output usage.",
                    "Measure must-find recall, reviewer acceptance, and false positives.",
                    "Set a zero-tolerance threshold for prohibited-context release.",
                    "Retain task, policy, source, model, and evaluator versions.",
                ),
                citations=(
                    (
                        "Download the one-page Secure RAG review checklist (PDF)",
                        f"{BASE_URL}assets/secure-rag-architecture-review-checklist.pdf",
                    ),
                    ("Open the secure RAG architecture guide", f"{BASE_URL}rag-vs-secure-context-cache/"),
                ),
            ),
        ),
        related=("rag-vs-secure-context-cache", "secure-context-cache-benchmark", "docs"),
    ),
    Page(
        slug="ai-context-engineering",
        title="AI Context Engineering for Reliable Enterprise Agents",
        kicker="Context engineering",
        description="Design reliable AI-agent context with source governance, task-scoped assembly, token budgets, quality gates, provenance, and least privilege.",
        keywords=("AI context engineering", "LLM context engineering", "agent context management"),
        summary="Context engineering is the repeatable system that decides what an agent should know for one task, why it may know it, and how the result will be evaluated.",
        intent="Build an auditable context system",
        sections=(
            Section(
                "Treat context as a compiled product",
                (
                    "A prompt is only the final serialization. The durable system begins with approved sources, parsers, metadata, reusable facts, policy, task contracts, and evaluation. This makes context reproducible across models and prevents every agent team from rebuilding enterprise memory independently.",
                    "Define context types such as repository path, dependency, service ownership, environment, policy, incident, and runbook. Attach source version, freshness, sensitivity, and allowed task types. A task contract states the facts that must be found and the facts that must never be released.",
                ),
                (
                    "Compile stable knowledge once and version the output.",
                    "Keep volatile task input separate from reusable facts.",
                    "Use explicit context budgets and deny-by-default policy.",
                    "Record selection, denial, redaction, expiry, and source lineage.",
                ),
            ),
            Section(
                "Optimize around accepted results",
                (
                    "Context quality is evaluated at the task boundary. For code review, measure required issue recall and false positives. For incident assistance, measure diagnostic completeness and unsafe actions. For architecture Q&A, measure citation support and stale facts.",
                    "Token count is one dimension. A production scorecard also needs cost, latency, acceptance, sensitivity exposure, policy violations, and audit replay. Model choice can change while the context contract remains stable.",
                ),
                (
                    "Create a labeled task set before changing context selection.",
                    "Run paired baselines with the same model and settings.",
                    "Review failures to expand or correct the graph and policy.",
                    "Promote only after quality and authorization thresholds pass.",
                ),
            ),
        ),
        related=("docs", "secure-context-caching", "secure-context-cache-benchmark"),
    ),
    Page(
        slug="enterprise-ai-agent-memory-security",
        title="Enterprise AI Agent Memory Security",
        kicker="Agent security",
        description="Secure enterprise AI-agent memory with scoped sources, sensitivity labels, expiring capsules, provenance, denials, and separate action authorization.",
        keywords=("AI agent memory security", "secure agent memory", "LLM memory access control"),
        summary="Shared memory becomes an attack-path oracle when every agent can query the full enterprise map. Release task-scoped views instead.",
        intent="Prevent overbroad agent memory",
        sections=(
            Section(
                "The memory layer is part of the trust boundary",
                (
                    "Persistent agent memory may contain service topology, privileged paths, owners, incident procedures, data stores, and policy exceptions. Compromise of one agent or one retrieval credential can turn that memory into a broad map of the enterprise.",
                    "Secure Context Cache separates canonical storage from task-scoped release. Slices carry sensitivity and scope; an authenticated workload requests a defined task; policy releases derived facts or citations; and the capsule expires. The model never receives source-store credentials.",
                ),
                (
                    "Authenticate each workload rather than trusting a self-asserted agent name.",
                    "Bind context to task, path, environment, sensitivity, and approval.",
                    "Redact secrets and prefer derived facts over raw source.",
                    "Log denials and approval-required items without exposing their contents.",
                ),
            ),
            Section(
                "Keep knowledge separate from authority",
                (
                    "Knowing that a production role exists does not grant permission to assume it. Cloud credentials, deployment tokens, and write authority belong in a separate action-control path with their own identity, policy, and approvals.",
                    "Red-team the context layer for prompt injection in source documents, stale evidence replay, cross-tenant retrieval, path traversal, approval spoofing, and empty-capsule fallback. Fail closed when context cannot be authorized.",
                ),
                (
                    "Rotate workload credentials and isolate audit storage.",
                    "Verify source hashes and freshness before release.",
                    "Test negative cases alongside successful tasks.",
                    "Do not treat an audit record as proof that a model conclusion is correct.",
                ),
            ),
        ),
        related=("least-privilege-ai-context", "rag-vs-secure-context-cache", "securereviewagent-case-study"),
    ),
    Page(
        slug="mcp-context-optimization",
        title="MCP Context Optimization with Policy-Scoped Capsules",
        kicker="Model Context Protocol",
        description="Use MCP with Secure Context Cache to expose a narrow context tool instead of giving agents unrestricted repository or enterprise-memory access.",
        keywords=("MCP context optimization", "Model Context Protocol security", "MCP token optimization"),
        summary="Expose one authenticated capsule tool through MCP so the host can request approved facts without receiving broad source credentials.",
        intent="Build a safer MCP context tool",
        sections=(
            Section(
                "Put policy behind the MCP tool",
                (
                    "MCP makes tools and resources available to AI hosts, but tool availability is not the same as authorization to every enterprise fact. A broad repository resource can still create excessive token use and cross-context exposure.",
                    "A Secure Context Cache MCP server accepts a task type, path, environment, and prompt; authenticates to Agent Context Gateway outside the model; and returns only the capsule facts, references, expiry, and audit ID. Secrets remain in the server process or host credential store.",
                ),
                (
                    "Expose a narrow request_capsule tool instead of a raw source browser.",
                    "Validate task and path inputs before calling the gateway.",
                    "Return denials as metadata without revealing denied content.",
                    "Do not expose bearer tokens, API keys, or cloud credentials in tool results.",
                ),
                "result = request_capsule(\n    task_type=\"iac_security\",\n    path=\"terraform/prod/payments/lambda.tf\",\n    environment=\"prod\",\n)\nreturn {\"facts\": result[\"facts\"], \"audit_id\": result[\"audit_id\"]}",
            ),
            Section(
                "Evaluate MCP context as a security boundary",
                (
                    "Measure tokens and quality with and without the capsule tool, but also test unauthorized paths, malformed arguments, prompt injection, stale sources, and repeated calls. The MCP host should not convert a denied capsule into a broader fallback.",
                    "Use one workload identity per host or agent in production, short token lifetimes, rate limits, and audit correlation between the MCP invocation and the gateway decision.",
                ),
            ),
        ),
        related=("docs", "enterprise-ai-agent-memory-security", "ai-agent-context-gateway"),
    ),
    Page(
        slug="openai-token-optimization",
        title="OpenAI Token Optimization with Secure Context Capsules",
        kicker="OpenAI integration",
        description="Reduce repeated OpenAI input tokens by requesting a policy-scoped Secure Context Cache capsule before the model call and measuring accepted-result quality.",
        keywords=("OpenAI token optimization", "reduce OpenAI API tokens", "OpenAI context caching"),
        summary="Build and authorize the enterprise context before the OpenAI call, then combine capsule reduction with provider prompt caching where appropriate.",
        intent="Integrate a governed context boundary",
        sections=(
            Section(
                "Fetch the capsule before calling the model",
                (
                    "The application—not the model—authenticates to Agent Context Gateway. It requests context for a defined task and receives facts, references, denials, source hashes, expiry, policy version, and an audit ID. Only released facts are serialized into the OpenAI request.",
                    "Stable system instructions and schemas may be eligible for provider prompt caching, while volatile task input and the approved capsule remain task-specific. Record provider-reported usage rather than estimating production savings from words or characters.",
                ),
                (
                    "Keep the gateway credential outside model-visible messages.",
                    "Use a structured context block with source references and expiry.",
                    "Reject empty capsules instead of attaching the full repository.",
                    "Store the audit ID beside the model request and reviewer outcome.",
                ),
            ),
            Section(
                "Measure the OpenAI path with a paired benchmark",
                (
                    "Replay the same labeled tasks through full approved context and Secure Context Cache. Hold model, temperature, tools, and acceptance rubric constant. Compare input tokens, cached input where reported, output tokens, latency, cost, recall, precision, and reviewer acceptance.",
                    "The repository includes an integration example that demonstrates the boundary without embedding credentials. Production teams should add retries, rate limits, redaction review, model-output validation, and organization-specific data controls.",
                ),
            ),
        ),
        related=("reduce-llm-token-cost", "prompt-caching-vs-context-caching", "secure-context-cache-benchmark"),
    ),
    Page(
        slug="aws-bedrock-token-optimization",
        title="Amazon Bedrock Token Optimization with Secure Context Cache",
        kicker="Amazon Bedrock integration",
        description="Use Secure Context Cache before Amazon Bedrock Converse calls to reduce repeated input context while preserving policy, provenance, and quality evidence.",
        keywords=("Amazon Bedrock token optimization", "Bedrock prompt caching", "AWS AI cost optimization"),
        summary="Request an approved capsule before Bedrock Converse, keep AWS credentials outside prompts, and evaluate provider usage with the same quality gate.",
        intent="Optimize governed Bedrock workloads",
        sections=(
            Section(
                "Separate AWS authority from model context",
                (
                    "A Bedrock client can obtain an Agent Context Gateway capsule using its workload identity, then pass the released facts to the selected model. The model does not receive AWS credentials, Cognito secrets, gateway bearer tokens, or direct S3 access.",
                    "Secure Context Cache reduces and governs enterprise context. Bedrock model selection, inference profiles, provider caching features, quotas, and pricing remain separate controls. The repository's Converse example demonstrates the intended boundary.",
                ),
                (
                    "Use IAM roles or short-lived workload credentials.",
                    "Store approved source material in a separately governed location.",
                    "Attach audit IDs and source references to review records.",
                    "Use CloudWatch and provider usage fields for production measurement.",
                ),
            ),
            Section(
                "Benchmark cost and quality together",
                (
                    "Compare a full approved baseline with the capsule path across the same tasks and model configuration. Record input and output usage, latency, price assumptions, required-fact recall, false positives, and unauthorized release.",
                    "If a capsule saves tokens but misses a dependency or control, expand the graph or selection policy. Do not weaken the acceptance threshold to preserve a savings percentage.",
                ),
                (
                    "Version model identifiers, policy, source hashes, and task sets.",
                    "Separate on-demand, cached, and provisioned cost assumptions.",
                    "Retain raw provider usage for reproducibility.",
                    "Label prototype, pilot, and production evidence accurately.",
                ),
            ),
        ),
        related=("docs", "prompt-caching-vs-context-caching", "secure-context-cache-benchmark"),
    ),
    Page(
        slug="secure-context-cache-benchmark",
        title="Secure Context Cache Benchmark and Evaluation Method",
        kicker="Reproducible evidence",
        description="Reproduce the Secure Context Cache fixture and design a provider-measured benchmark for tokens, cost, quality, latency, exposure, and policy compliance.",
        keywords=("Secure Context Cache benchmark", "LLM token benchmark", "AI context evaluation"),
        summary="The public fixture proves the release and measurement path. It does not prove universal production savings; a production pilot must join provider usage with accepted-result quality.",
        intent="Reproduce claims and limits",
        sections=(
            Section(
                "What the public fixture demonstrates",
                (
                    "The local sample repository produces two file-level context slices. For an Infrastructure-as-Code security task, one slice is released and one unrelated slice is denied. Derived facts across both slices total a deterministic estimate of 32 whitespace-separated words; the capsule contains 16, producing a displayed 50% reduction.",
                    "The field names use tokens, but the fixture estimator is a word-count proxy. It is not a provider tokenizer, invoice measurement, or production-quality benchmark. Its purpose is to make the selection, denial, capsule, audit, and metrics artifacts reproducible.",
                ),
                (
                    "One released slice and one denied slice.",
                    "Source hash, freshness, policy version, expiry, and audit ID.",
                    "Deterministic 32-to-16 estimate for the included fixture.",
                    "No claim of 50% production cost or quality-equivalent savings.",
                ),
                "acg demo --repo examples/sample_repo --out build/demo\npython -m json.tool build/demo/context-capsule.json\npython -m json.tool build/demo/audit-record.json\npython -m json.tool build/demo/metrics.json",
            ),
            Section(
                "Design the production benchmark",
                (
                    "Use a labeled task set and compare changed-files-only, full approved context, relevance-only retrieval, and policy-scoped capsules. Hold model and settings constant. Capture raw provider usage, pricing timestamp, latency, must-find recall, false positives, reviewer agreement, overrides, stale-context rate, and prohibited-context release.",
                    "The separate 24-task deterministic research prototype reported a 75.3% average context-size reduction, 95.8% task success, and 98.6% required-fact coverage. These are prototype measurements, not independent field evidence. Production claims should be based on provider and reviewer records from an organization-controlled pilot.",
                ),
                (
                    "Publish task and dataset versions or a privacy-preserving manifest.",
                    "Store raw JSON/CSV results and the exact evaluation commit.",
                    "Predefine acceptance and zero-unauthorized-release thresholds.",
                    "Report failures and confidence intervals, not only averages.",
                ),
            ),
        ),
        related=("reduce-llm-token-cost", "securereviewagent-case-study", "docs"),
    ),
    Page(
        slug="securereviewagent-case-study",
        title="SecureReviewAgent: A Governed IaC AI Security Case Study",
        kicker="Flagship application",
        description="See how SecureReviewAgent uses task-scoped Secure Context Cache capsules to review Terraform and Kubernetes changes with measurable quality and exposure.",
        keywords=("AI IaC security review", "SecureReviewAgent", "Terraform AI security"),
        summary="Infrastructure review is a useful first benchmark because required facts, prohibited context, findings, and reviewer acceptance can be labeled.",
        intent="Apply the framework to IaC review",
        sections=(
            Section(
                "Why IaC review needs more than a diff",
                (
                    "A Terraform change may depend on IAM relationships, network boundaries, environment, ownership, data classification, deployment controls, and prior exceptions. Sending the entire enterprise map is expensive and creates unnecessary exposure; sending only the changed file can miss required dependencies.",
                    "SecureReviewAgent requests a capsule for the changed path and task. Agent Context Gateway authenticates the workload, selects approved facts, denies unrelated slices, and returns provenance and an audit ID. The model reviews the change using that capsule.",
                ),
                (
                    "Changed resources and local dependencies.",
                    "Relevant IAM, network, policy, ownership, and environment facts.",
                    "Denied unrelated topology and secret-adjacent material.",
                    "Review findings tied to sources and a capsule audit record.",
                ),
            ),
            Section(
                "Make the review measurable",
                (
                    "Create pull requests with labeled must-find issues and benign controls. Compare changed-files-only, full approved context, retrieval-only, and policy-scoped capsule paths. Record provider usage, security issue recall, false positives, reviewer acceptance, and prohibited-context release.",
                    "The current public fixture validates the boundary and artifacts but does not establish a production savings percentage or equal review quality. The next evidence milestone is a provider-measured, human-reviewed replay set.",
                ),
                (
                    "Fail closed when no context is approved.",
                    "Keep deployment authority outside the review model.",
                    "Require human approval for high-risk actions.",
                    "Use the case study to improve policy and context coverage.",
                ),
            ),
        ),
        related=("iac-ai-security-review", "secure-context-cache-benchmark", "enterprise-ai-agent-memory-security"),
    ),
    Page(
        slug="about",
        title="About Secure Context Cache and Its Author",
        kicker="Project identity",
        description="About Secure Context Cache, Agent Context Gateway, SecureReviewAgent, and independent researcher Naga Krishna Reddy Muppidi.",
        keywords=("Secure Context Cache author", "Naga Krishna Reddy Muppidi", "Agent Context Gateway"),
        summary="Secure Context Cache is an independent open-source project for secure token optimization and least-privilege context release across enterprise AI agents.",
        intent="Verify project identity and scope",
        sections=(
            Section(
                "One framework, one runtime, one measurable application",
                (
                    "Secure Context Cache is the research-backed framework and public product. Agent Context Gateway is the deployable API and AWS control plane that authenticates workloads, applies policy, assembles capsules, and records evidence. SecureReviewAgent is the flagship Infrastructure-as-Code security workflow.",
                    "The project is authored and maintained by Naga Krishna Reddy Muppidi, an independent researcher and senior platform engineering practitioner focused on cloud platforms, DevSecOps, FinOps, and governed enterprise AI.",
                ),
                (
                    "Open-source under the MIT License.",
                    "Public source, reproducible fixture, and documented limitations.",
                    "Accepted Secure Context Cache research paper with publication/indexing status kept separate.",
                    "Independent project; not an AWS, OpenAI, Anthropic, or Google service.",
                ),
            ),
            Section(
                "How to evaluate the project",
                (
                    "Start with the source repository and local demo. Review the architecture, security model, policy guide, benchmark method, and production-readiness checklist. Treat prototype results as evaluation evidence rather than universal savings claims.",
                    "For pilot discussions, use one read-only workflow with a labeled task set, approved sources, provider-reported usage, human review, and explicit authorization tests.",
                ),
            ),
        ),
        related=("docs", "research/secure-context-cache-paper", "secure-context-cache-benchmark"),
        schema_type="ProfilePage",
    ),
    Page(
        slug="research/secure-context-cache-paper",
        title="Secure Context Cache Research Paper",
        kicker="Research",
        description="Research status and contribution summary for Secure Context Cache: Token-Efficient and Least-Privilege Shared Memory for Enterprise Developer Agents.",
        keywords=("Secure Context Cache paper", "token-efficient agent memory", "least-privilege AI context research"),
        summary="The paper proposes reusable protected context slices and task-scoped release as a middle ground between stateless agents and unrestricted shared enterprise memory.",
        intent="Understand the research contribution",
        sections=(
            Section(
                "Research contribution",
                (
                    "The paper is titled “Secure Context Cache: Token-Efficient and Least-Privilege Shared Memory for Enterprise Developer Agents.” It proposes precomputing reusable context from approved sources, splitting it into protected path, resource, environment, and task slices, and releasing only derived facts authorized for one task.",
                    "The design targets two connected risks: repeated enterprise context increases input-token cost, while unrestricted shared memory can expose sensitive topology and attack paths. The framework combines token reduction, sensitivity exposure, provenance, expiry, and audit evidence.",
                ),
                (
                    "Canonical source-backed context graph.",
                    "Protected reusable slices with sensitivity and scope.",
                    "Identity- and task-scoped expiring capsules.",
                    "Quality, token, exposure, and reconstructability evaluation.",
                ),
            ),
            Section(
                "Publication status and evidence boundary",
                (
                    "The paper was accepted for presentation and publication at the 2026 5th International Conference on Engineering and Research Application (ICERA). Final proceedings publication and indexing are separate post-conference evidence and are not claimed here until independently confirmed.",
                    "The deterministic research prototype covered 24 tasks and 32 reusable slices. Reported prototype results include a 75.3% average context-size reduction, 95.8% task success, 98.6% required-fact coverage, and 92.3% lower high-sensitivity slice exposure compared with full-context release. These are controlled prototype measurements, not independent production results.",
                ),
                (
                    "Use accepted-for-presentation/publication wording until proceedings evidence exists.",
                    "Do not describe the prototype as a customer deployment.",
                    "Reproduce the public implementation separately from the research benchmark.",
                    "Add a formal citation and proceedings link after publication is verified.",
                ),
            ),
        ),
        related=("about", "secure-context-cache-benchmark", "ai-context-engineering"),
        schema_type="ScholarlyArticle",
    ),
)


EXISTING_PAGES = {
    "": (
        "Secure Context Cache",
        "Open-source AI token optimization framework with secure context controls.",
    ),
    "llm-token-optimization": (
        "LLM Token Optimization for Enterprise AI Agents",
        "Reduce recurring input-token cost while preserving accepted-result quality.",
    ),
    "secure-context-caching": (
        "Secure Context Caching for Enterprise AI Agents",
        "Compile approved knowledge into reusable, governed context slices.",
    ),
    "least-privilege-ai-context": (
        "Least-Privilege Context for AI Agents",
        "Authorize model context by identity, task, path, sensitivity, and freshness.",
    ),
    "ai-agent-context-gateway": (
        "AI Agent Context Gateway",
        "Authenticate workloads, enforce context policy, assemble capsules, and preserve audit evidence.",
    ),
    "iac-ai-security-review": (
        "AI-Assisted Infrastructure-as-Code Security Review",
        "Measure tokens and review quality with SecureReviewAgent as the flagship workflow.",
    ),
}

PAGE_BY_SLUG = {page.slug: page for page in PAGES}


def prefix_for(slug: str) -> str:
    return "../" * len(slug.split("/"))


def canonical(slug: str) -> str:
    return f"{BASE_URL}{slug}/" if slug else BASE_URL


def render_markdown(page: Page) -> str:
    lines = [
        f"# {page.title}",
        "",
        f"> {page.summary}",
        "",
        f"Canonical URL: {canonical(page.slug)}",
        f"Source code: {REPOSITORY}",
        "",
    ]
    for section in page.sections:
        lines.extend((f"## {section.title}", ""))
        for paragraph in section.paragraphs:
            lines.extend((paragraph, ""))
        for bullet in section.bullets:
            lines.append(f"- {bullet}")
        if section.bullets:
            lines.append("")
        if section.code:
            lines.extend(("```text", section.code, "```", ""))
        if section.table:
            header, *rows = section.table
            lines.append("| " + " | ".join(header) + " |")
            lines.append("| " + " | ".join("---" for _ in header) + " |")
            lines.extend("| " + " | ".join(row) + " |" for row in rows)
            lines.append("")
        if section.citations:
            lines.extend(f"- [{label}]({url})" for label, url in section.citations)
            lines.append("")
    lines.extend(("## Related resources", ""))
    for slug in page.related:
        related = PAGE_BY_SLUG.get(slug)
        label = related.title if related else EXISTING_PAGES.get(slug, (slug, ""))[0]
        lines.append(f"- [{label}]({canonical(slug)})")
    lines.extend(
        (
            "",
            "## Evidence boundary",
            "",
            "Prototype and fixture results are not universal production claims. A production pilot must use provider-reported usage, a labeled task set, and an agreed quality threshold.",
            "",
        )
    )
    return "\n".join(lines)


def render_existing_markdown(slug: str, title: str, description: str) -> str:
    focus = {
        "": (
            "Secure Context Cache combines token measurement, task-aware selection, compiled "
            "context reuse, provider prompt caching, optional compression, routing adapters, and "
            "quality gates. Its secure context layer authenticates each workload and releases "
            "only source-backed facts allowed for the task."
        ),
        "llm-token-optimization": (
            "Token optimization starts with repeated input, not with a cheaper model alone. "
            "Separate stable approved context from task-specific input, measure provider-reported "
            "usage, and count a saving only when the result passes the same quality threshold as "
            "the approved baseline."
        ),
        "secure-context-caching": (
            "Secure context caching prepares reusable facts before model invocation while "
            "preserving provenance, sensitivity, freshness, and policy metadata. Every request "
            "still receives a current authorization decision; a cached slice is never an "
            "authorization grant."
        ),
        "least-privilege-ai-context": (
            "Least-privilege context limits what an AI workload can know for one task. Identity, "
            "task type, repository path, environment, sensitivity, source approval, and freshness "
            "determine which facts cross the model boundary."
        ),
        "ai-agent-context-gateway": (
            "Agent Context Gateway is the stable runtime and API boundary. It authenticates "
            "workloads, applies deterministic context policy, assembles expiring capsules, and "
            "records release and denial evidence without giving the model direct source access."
        ),
        "iac-ai-security-review": (
            "SecureReviewAgent is the flagship Infrastructure-as-Code workflow. It demonstrates "
            "how an agent can combine changed files with policy-approved architecture and "
            "ownership facts while measuring both token use and review quality."
        ),
    }[slug]
    canonical_url = canonical(slug)
    return "\n".join(
        (
            f"# {title}",
            "",
            f"> {description}",
            "",
            f"Canonical URL: {canonical_url}",
            f"Source code: {REPOSITORY}",
            "",
            "## Overview",
            "",
            focus,
            "",
            (
                "The public deterministic fixture reports a 32-to-16 word-count proxy. It shows "
                "the measurement path; it is not provider-billed production savings. Production "
                "evaluation requires provider usage data, labeled tasks, authorization tests, "
                "and an agreed acceptance threshold."
            ),
            "",
            "## Continue",
            "",
            f"- [Documentation]({BASE_URL}docs/index.md)",
            f"- [Token optimization framework]({BASE_URL}ai-token-optimization-framework/index.md)",
            f"- [Benchmark method]({BASE_URL}secure-context-cache-benchmark/index.md)",
            f"- [Prompt caching vs. context caching]({BASE_URL}prompt-caching-vs-context-caching/index.md)",
            f"- [RAG vs. Secure Context Cache]({BASE_URL}rag-vs-secure-context-cache/index.md)",
            f"- [SecureReviewAgent case study]({BASE_URL}securereviewagent-case-study/index.md)",
            f"- [GitHub repository]({REPOSITORY})",
            "",
        )
    )


def render_json_ld(page: Page) -> str:
    url = canonical(page.slug)
    data = {
        "@context": "https://schema.org",
        "@graph": [
            {
                "@type": page.schema_type,
                "headline": page.title,
                "name": page.title,
                "description": page.description,
                "datePublished": TODAY.isoformat(),
                "dateModified": TODAY.isoformat(),
                "mainEntityOfPage": url,
                "url": url,
                "author": {
                    "@type": "Person",
                    "name": "Naga Krishna Reddy Muppidi",
                    "url": f"{BASE_URL}about/",
                    "sameAs": [
                        "https://github.com/krishnamuppidi",
                        "https://www.linkedin.com/in/krishna-reddy-4b11ab133",
                    ],
                },
                "isPartOf": {"@type": "WebSite", "name": "Secure Context Cache", "url": BASE_URL},
                "about": list(page.keywords),
            },
            {
                "@type": "BreadcrumbList",
                "itemListElement": [
                    {
                        "@type": "ListItem",
                        "position": 1,
                        "name": "Secure Context Cache",
                        "item": BASE_URL,
                    },
                    {
                        "@type": "ListItem",
                        "position": 2,
                        "name": page.title,
                        "item": url,
                    },
                ],
            },
        ],
    }
    return json.dumps(data, indent=8, ensure_ascii=False)


def render_page(page: Page) -> str:
    prefix = prefix_for(page.slug)
    related_cards = []
    for slug in page.related:
        related = PAGE_BY_SLUG.get(slug)
        title, description = (
            (related.title, related.summary)
            if related
            else EXISTING_PAGES.get(slug, (slug.replace("-", " ").title(), "Related guide"))
        )
        related_cards.append(
            f'<a class="related-card" href="{prefix}{slug}/"><span>Related</span>'
            f"<h3>{html.escape(title)}</h3><p>{html.escape(description)}</p></a>"
        )

    body_sections = []
    for index, section in enumerate(page.sections):
        bullets = ""
        if section.bullets:
            bullets = '<div class="article-points">' + "".join(
                f'<div class="article-point"><span>{number:02d}</span><h3>{html.escape(item.split(" ", 1)[0])}</h3>'
                f"<p>{html.escape(item)}</p></div>"
                for number, item in enumerate(section.bullets, 1)
            ) + "</div>"
        code = (
            f'<pre class="article-code"><code>{html.escape(section.code)}</code></pre>'
            if section.code
            else ""
        )
        table = ""
        if section.table:
            header, *rows = section.table
            table = (
                '<div class="article-table-wrap"><table class="article-table"><thead><tr>'
                + "".join(f"<th>{html.escape(cell)}</th>" for cell in header)
                + "</tr></thead><tbody>"
                + "".join(
                    "<tr>"
                    + "".join(f"<td>{html.escape(cell)}</td>" for cell in row)
                    + "</tr>"
                    for row in rows
                )
                + "</tbody></table></div>"
            )
        citations = ""
        if section.citations:
            citations = '<ul class="article-citations">' + "".join(
                f'<li><a href="{html.escape(url)}" target="_blank" rel="noreferrer">'
                f"{html.escape(label)} ↗</a></li>"
                for label, url in section.citations
            ) + "</ul>"
        paragraphs = "".join(f"<p>{html.escape(p)}</p>" for p in section.paragraphs)
        body_sections.append(
            f'<section class="article-section{" alt" if index % 2 else ""}"><div class="container article-layout">'
            f'<aside class="article-aside"><span class="article-label">{html.escape(page.kicker)}</span>'
            f"<h2>{html.escape(section.title)}</h2><p>{html.escape(page.intent)}</p></aside>"
            f'<article class="article-content"><h2>{html.escape(section.title)}</h2>'
            f"{paragraphs}{bullets}{code}{table}{citations}</article>"
            "</div></section>"
        )

    diagram_alt = f"Secure Context Cache flow for {page.title}"
    return f"""<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <meta name="theme-color" content="#07110f" />
    <meta name="description" content="{html.escape(page.description)}" />
    <meta name="keywords" content="{html.escape(", ".join(page.keywords))}" />
    <meta name="robots" content="index, follow, max-image-preview:large" />
    <link rel="canonical" href="{canonical(page.slug)}" />
    <link rel="alternate" type="text/markdown" href="{canonical(page.slug)}index.md" />
    <link rel="alternate" type="application/rss+xml" href="{BASE_URL}feed.xml" title="Secure Context Cache updates" />
    <meta property="og:type" content="article" />
    <meta property="og:site_name" content="Secure Context Cache" />
    <meta property="og:title" content="{html.escape(page.title)}" />
    <meta property="og:description" content="{html.escape(page.summary)}" />
    <meta property="og:url" content="{canonical(page.slug)}" />
    <meta property="og:image" content="{BASE_URL}assets/secure-context-cache-social-preview.png" />
    <meta property="og:image:alt" content="Secure Context Cache secure token optimization architecture" />
    <meta name="twitter:card" content="summary_large_image" />
    <meta name="twitter:title" content="{html.escape(page.title)}" />
    <meta name="twitter:description" content="{html.escape(page.summary)}" />
    <meta name="twitter:image" content="{BASE_URL}assets/secure-context-cache-social-preview.png" />
    <title>{html.escape(page.title)} | Secure Context Cache</title>
    <link rel="icon" href="{prefix}favicon.svg" type="image/svg+xml" />
    <link rel="stylesheet" href="{prefix}styles.css" />
    <link rel="stylesheet" href="{prefix}seo-pages.css" />
    <script type="application/ld+json">
{render_json_ld(page)}
    </script>
    <script defer src="{prefix}analytics.js"></script>
    <script defer src="{prefix}app.js"></script>
  </head>
  <body class="article-page">
    <a class="skip-link" href="#main">Skip to content</a>
    <nav class="nav article-nav scrolled" aria-label="Primary navigation">
      <div class="container nav-inner">
        <a class="brand" href="{prefix}" aria-label="Secure Context Cache home"><span class="brand-mark" aria-hidden="true"><span></span><span></span><span></span></span><span>Secure Context Cache</span></a>
        <button class="menu-button" type="button" aria-expanded="false" aria-controls="nav-links" aria-label="Open navigation"><span></span><span></span><span></span></button>
        <div class="nav-links" id="nav-links"><a href="{prefix}docs/">Docs</a><a href="{prefix}secure-context-cache-benchmark/">Benchmark</a><a href="{prefix}prompt-caching-vs-context-caching/">Compare</a><a href="{prefix}mcp-context-optimization/">MCP</a></div>
        <a class="button button-small nav-cta" href="{REPOSITORY}" target="_blank" rel="noreferrer">View GitHub →</a>
      </div>
    </nav>
    <main id="main">
      <header class="article-hero">
        <div class="container article-hero-layout">
          <div>
            <nav class="article-breadcrumb" aria-label="Breadcrumb"><a href="{prefix}">Home</a><span>/</span><span>{html.escape(page.title)}</span></nav>
            <span class="article-kicker">{html.escape(page.kicker)}</span>
            <h1>{html.escape(page.title)}</h1>
            <p class="article-summary">{html.escape(page.summary)}</p>
            <div class="article-actions"><a class="button button-primary" href="{REPOSITORY}" target="_blank" rel="noreferrer">Run the open-source demo ↗</a><a class="button button-ghost" href="{prefix}docs/">Read the docs</a></div>
          </div>
          <aside class="article-fact-card visual-card">
            <img src="{prefix}assets/context-capsule-flow.svg" width="560" height="360" alt="{html.escape(diagram_alt)}" />
            <span class="article-label">{html.escape(page.intent)}</span>
            <h2>One canonical context graph. Many policy-scoped capsules.</h2>
            <p>Optimize context before model invocation and preserve the evidence behind every release.</p>
          </aside>
        </div>
      </header>
      {"".join(body_sections)}
      <section class="related-section"><div class="container"><div class="related-head"><div><span class="article-label">Continue exploring</span><h2>Related Secure Context Cache resources</h2></div></div><div class="related-grid">{"".join(related_cards)}</div><p class="article-disclaimer">Prototype and fixture results are not universal production claims. Production evaluation requires provider-reported usage and an agreed quality threshold.</p></div></section>
    </main>
    <footer class="footer"><div class="container footer-top"><div><a class="brand" href="{prefix}"><span class="brand-mark small" aria-hidden="true"><span></span><span></span><span></span></span><span>Secure Context Cache</span></a><p>Secure token optimization. Deployable context gateway. Measurable flagship agent.</p></div><div class="footer-links"><div><b>Explore</b><a href="{prefix}docs/">Documentation</a><a href="{prefix}secure-context-cache-benchmark/">Benchmark</a><a href="{prefix}about/">About</a></div><div><b>Compare</b><a href="{prefix}prompt-caching-vs-context-caching/">Prompt vs context cache</a><a href="{prefix}rag-vs-secure-context-cache/">RAG vs SCC</a><a href="{prefix}enterprise-ai-agent-memory-security/">Agent memory security</a></div><div><b>Code</b><a href="{REPOSITORY}" target="_blank" rel="noreferrer">Secure Context Cache ↗</a><a href="{SECURE_REVIEW_AGENT}" target="_blank" rel="noreferrer">SecureReviewAgent ↗</a></div></div></div><div class="container footer-bottom"><span>© <span id="year">2026</span> Naga Krishna Reddy Muppidi. MIT License.</span><span>Independent project. <button class="privacy-link" id="analytics-preferences" type="button">Analytics preferences</button></span></div></footer>
    <aside class="analytics-consent" id="analytics-consent" role="dialog" aria-labelledby="analytics-consent-title" aria-describedby="analytics-consent-description" hidden><div><strong id="analytics-consent-title">Optional, privacy-conscious analytics</strong><p id="analytics-consent-description">Google Analytics helps measure aggregate site traffic and resource engagement. It stays off until allowed. No names, email addresses, form contents, or full link URLs are sent. See <a href="https://policies.google.com/privacy" target="_blank" rel="noreferrer">Google's privacy policy</a>.</p></div><div class="analytics-consent-actions"><button type="button" class="button button-ghost" data-analytics-choice="denied">No thanks</button><button type="button" class="button button-primary" data-analytics-choice="granted">Allow analytics</button></div></aside>
  </body>
</html>
"""


def make_visual_assets() -> None:
    assets = SITE / "assets"
    assets.mkdir(parents=True, exist_ok=True)
    flow_svg = """<svg xmlns="http://www.w3.org/2000/svg" width="1120" height="720" viewBox="0 0 1120 720" role="img" aria-labelledby="title desc">
<title id="title">Secure Context Cache context capsule flow</title><desc id="desc">Approved sources become a canonical graph, protected slices, a policy-scoped capsule, and model input.</desc>
<defs><linearGradient id="bg" x1="0" x2="1"><stop stop-color="#07110f"/><stop offset="1" stop-color="#0c211b"/></linearGradient><filter id="glow"><feGaussianBlur stdDeviation="7" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter></defs>
<rect width="1120" height="720" rx="36" fill="url(#bg)"/><g fill="none" stroke="#58e6a9" stroke-width="3" opacity=".7"><path d="M235 360H330"/><path d="M535 360H630"/><path d="M835 360H925"/></g>
<g font-family="Arial, sans-serif" text-anchor="middle"><g transform="translate(35 250)"><rect width="200" height="220" rx="24" fill="#10231f" stroke="#294a40"/><text x="100" y="58" fill="#58e6a9" font-size="17">APPROVED SOURCES</text><text x="100" y="102" fill="#f4fbf8" font-size="21">Repos · IaC · Docs</text><text x="100" y="138" fill="#a9bdb6" font-size="16">Policies · Runbooks</text><text x="100" y="180" fill="#769087" font-size="14">versioned + labeled</text></g>
<g transform="translate(330 250)"><rect width="205" height="220" rx="24" fill="#10231f" stroke="#58e6a9" filter="url(#glow)"/><text x="102" y="58" fill="#58e6a9" font-size="17">CONTEXT GRAPH</text><text x="102" y="103" fill="#f4fbf8" font-size="21">Protected slices</text><text x="102" y="140" fill="#a9bdb6" font-size="16">facts + provenance</text><text x="102" y="180" fill="#769087" font-size="14">compile once</text></g>
<g transform="translate(630 250)"><rect width="205" height="220" rx="24" fill="#10231f" stroke="#67a9ff"/><text x="102" y="58" fill="#67a9ff" font-size="17">POLICY GATE</text><text x="102" y="103" fill="#f4fbf8" font-size="21">Identity + task</text><text x="102" y="140" fill="#a9bdb6" font-size="16">path · sensitivity</text><text x="102" y="180" fill="#769087" font-size="14">authorize every release</text></g>
<g transform="translate(925 250)"><rect width="160" height="220" rx="24" fill="#123327" stroke="#58e6a9"/><text x="80" y="58" fill="#58e6a9" font-size="17">CAPSULE</text><text x="80" y="103" fill="#f4fbf8" font-size="21">Minimum facts</text><text x="80" y="140" fill="#a9bdb6" font-size="16">expiry + audit</text><text x="80" y="180" fill="#769087" font-size="14">model-ready</text></g></g>
<text x="50" y="90" fill="#f4fbf8" font-family="Arial, sans-serif" font-size="42" font-weight="700">Secure token optimization before model invocation</text><text x="50" y="135" fill="#a9bdb6" font-family="Arial, sans-serif" font-size="22">One canonical context graph. Many policy-scoped agent capsules.</text></svg>"""
    (assets / "context-capsule-flow.svg").write_text(flow_svg)

    font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
    bold_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
    font_big = ImageFont.truetype(bold_path, 62)
    font_mid = ImageFont.truetype(bold_path, 26)
    font_small = ImageFont.truetype(font_path, 22)
    image = Image.new("RGB", (1200, 630), "#06100e")
    draw = ImageDraw.Draw(image)
    for x in range(0, 1200, 60):
        draw.line((x, 0, x, 630), fill="#0d211c", width=1)
    for y in range(0, 630, 60):
        draw.line((0, y, 1200, y), fill="#0d211c", width=1)
    draw.rounded_rectangle((58, 58, 1142, 572), 32, fill="#091815", outline="#1e4d3d", width=3)
    draw.text((98, 96), "SECURE CONTEXT CACHE", font=font_mid, fill="#58e6a9")
    draw.multiline_text((98, 160), "Optimize every token.\nProtect context quality.", font=font_big, fill="#f4fbf8", spacing=10)
    draw.text((100, 340), "Measure · Select · Reuse · Compress · Route · Verify", font=font_small, fill="#a9bdb6")
    labels = ("APPROVED SOURCES", "PROTECTED SLICES", "POLICY GATE", "AGENT CAPSULE")
    positions = (100, 365, 635, 900)
    for index, (label, x) in enumerate(zip(labels, positions)):
        color = "#67a9ff" if index == 2 else "#58e6a9"
        draw.rounded_rectangle((x, 430, x + 205, 510), 15, fill="#10231f", outline=color, width=2)
        draw.text((x + 14, 458), label, font=ImageFont.truetype(bold_path, 15), fill=color)
        if index < 3:
            draw.line((x + 207, 470, x + 255, 470), fill="#58e6a9", width=3)
    image.save(assets / "secure-context-cache-social-preview.png", optimize=True)

    frames = []
    steps = (
        ("1", "Ingest approved sources", "Repositories · IaC · policies · runbooks"),
        ("2", "Build protected slices", "Facts · sensitivity · provenance · freshness"),
        ("3", "Authorize the request", "Identity · task · path · environment"),
        ("4", "Release a short-lived capsule", "Minimum facts · denials · audit ID"),
        ("5", "Measure the accepted result", "Tokens · cost · quality · exposure"),
    )
    for step, title, subtitle in steps:
        frame = Image.new("RGB", (960, 540), "#06100e")
        canvas = ImageDraw.Draw(frame)
        canvas.rounded_rectangle((45, 45, 915, 495), 28, fill="#0b1916", outline="#225846", width=3)
        canvas.ellipse((82, 92, 190, 200), fill="#133c2e", outline="#58e6a9", width=4)
        canvas.text((122, 115), step, font=ImageFont.truetype(bold_path, 44), fill="#58e6a9")
        canvas.text((230, 105), title, font=ImageFont.truetype(bold_path, 36), fill="#f4fbf8")
        canvas.text((232, 162), subtitle, font=ImageFont.truetype(font_path, 20), fill="#a9bdb6")
        canvas.text((85, 275), "Secure Context Cache", font=ImageFont.truetype(bold_path, 32), fill="#58e6a9")
        canvas.text((85, 330), "one canonical context graph → many policy-scoped capsules", font=ImageFont.truetype(font_path, 22), fill="#d4e9e0")
        for completed in range(int(step)):
            left = 85 + completed * 155
            canvas.rounded_rectangle((left, 408, left + 125, 426), 9, fill="#58e6a9")
        frames.append(frame)
    frames[0].save(
        assets / "secure-context-cache-demo.gif",
        save_all=True,
        append_images=frames[1:],
        duration=1300,
        loop=0,
        optimize=True,
    )


def upgrade_existing_metadata() -> None:
    for path in [SITE / "index.html", *sorted(SITE.glob("*/index.html"))]:
        text = path.read_text()
        if 'property="og:image"' not in text:
            anchor = '    <meta name="twitter:card" content="summary" />'
            replacement = (
                '    <meta property="og:image" content="https://krishnamuppidi.github.io/secure-context-cache/assets/secure-context-cache-social-preview.png" />\n'
                '    <meta property="og:image:alt" content="Secure Context Cache secure token optimization architecture" />\n'
                '    <meta name="twitter:card" content="summary_large_image" />\n'
                '    <meta name="twitter:image" content="https://krishnamuppidi.github.io/secure-context-cache/assets/secure-context-cache-social-preview.png" />'
            )
            text = text.replace(anchor, replacement)
        if 'type="application/rss+xml"' not in text:
            canonical_end = text.find("/>", text.find('rel="canonical"'))
            if canonical_end != -1:
                canonical_end += 2
                relative = path.relative_to(SITE)
                prefix = "../" * (len(relative.parts) - 1)
                text = (
                    text[:canonical_end]
                    + f'\n    <link rel="alternate" type="application/rss+xml" href="{prefix}feed.xml" title="Secure Context Cache updates" />'
                    + text[canonical_end:]
                )
        if 'type="text/markdown"' not in text:
            canonical_end = text.find("/>", text.find('rel="canonical"'))
            if canonical_end != -1:
                canonical_end += 2
                text = (
                    text[:canonical_end]
                    + '\n    <link rel="alternate" type="text/markdown" href="index.md" />'
                    + text[canonical_end:]
                )
        path.write_text(text)


def write_machine_files() -> None:
    curated = [
        "# Secure Context Cache",
        "",
        "> Secure Context Cache is an open-source AI token-optimization framework combining measurement, selection, compiled-context reuse, provider prompt caching, optional compression, routing adapters, and quality gates. Secure relevant-context release is its differentiating control layer.",
        "",
        "Canonical terminology: Secure Context Cache is the token-optimization framework and public product; secure context release is the differentiating add-on; Agent Context Gateway is the deployable API/runtime control plane; SecureReviewAgent is the flagship Infrastructure-as-Code workflow.",
        "",
        "Claim boundary: the public 32-to-16 result is a deterministic word-count fixture, not provider-billed production savings. The 75.3% research result is a controlled prototype benchmark, not independent adoption evidence.",
        "",
        "## Start here",
        "",
        f"- [Product website]({BASE_URL}): Product, architecture, economics, research, security, and deployment overview.",
        f"- [Token optimization framework]({BASE_URL}ai-token-optimization-framework/index.md): Measure, select, reuse, compress, route, and verify through one framework.",
        f"- [Documentation]({BASE_URL}docs/index.md): Machine-readable documentation hub.",
        f"- [GitHub repository]({REPOSITORY}): Canonical source, tests, deployment, and examples.",
        f"- [Benchmark method]({BASE_URL}secure-context-cache-benchmark/index.md): Reproducible fixture and production evaluation design.",
        f"- [SecureReviewAgent case study]({BASE_URL}securereviewagent-case-study/index.md): Flagship IaC review workflow.",
        "",
        "## Topic guides",
        "",
    ]
    for slug, (title, description) in EXISTING_PAGES.items():
        if not slug:
            continue
        curated.append(f"- [{title}]({canonical(slug)}): {description}")
    for page in PAGES:
        curated.append(f"- [{page.title}]({canonical(page.slug)}index.md): {page.summary}")
    curated.extend(
        (
            "",
            "## Optional",
            "",
            f"- [SecureReviewAgent source]({SECURE_REVIEW_AGENT}): Separate flagship application repository.",
            f"- [Full machine-readable site context]({BASE_URL}llms-full.txt): Consolidated documentation for retrieval and agent use.",
            f"- [RSS update feed]({BASE_URL}feed.xml): Newly published technical resources.",
            "",
        )
    )
    (SITE / "llms.txt").write_text("\n".join(curated))

    full = [
        "# Secure Context Cache — Full Machine-Readable Context",
        "",
        "This file consolidates the project's public technical explanations. Prefer the canonical URLs and repository for exact commands and current implementation behavior.",
        "",
        "## Core project facts",
        "",
        "- Product: Secure Context Cache",
        "- Runtime/API: Agent Context Gateway (`acg` CLI and `/v1/capsules` API)",
        "- Flagship application: SecureReviewAgent",
        "- License: MIT",
        f"- Repository: {REPOSITORY}",
        f"- Website: {BASE_URL}",
        "- Core thesis: one canonical context graph, many policy-scoped agent capsules.",
        "- Production claim rule: count token savings only when the optimized result passes a predefined quality and authorization threshold.",
        "",
    ]
    for page in PAGES:
        full.extend((render_markdown(page), "\n---\n"))
    (SITE / "llms-full.txt").write_text("\n".join(full))


def write_sitemaps_and_feed() -> None:
    urls = [BASE_URL]
    urls.extend(canonical(slug) for slug in EXISTING_PAGES if slug)
    urls.extend(canonical(page.slug) for page in PAGES)
    urls = list(dict.fromkeys(urls))
    xml_lines = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for url in urls:
        frequency = "weekly" if url in {BASE_URL, f"{BASE_URL}docs/", f"{BASE_URL}secure-context-cache-benchmark/"} else "monthly"
        priority = "1.0" if url == BASE_URL else ("0.9" if frequency == "weekly" else "0.8")
        xml_lines.extend(
            (
                "  <url>",
                f"    <loc>{escape(url)}</loc>",
                f"    <lastmod>{TODAY.isoformat()}</lastmod>",
                f"    <changefreq>{frequency}</changefreq>",
                f"    <priority>{priority}</priority>",
                "  </url>",
            )
        )
    xml_lines.append("</urlset>")
    (SITE / "sitemap.xml").write_text("\n".join(xml_lines) + "\n")
    (SITE / "sitemap.txt").write_text("\n".join(urls) + "\n")

    items = []
    for page in reversed(PAGES[-8:]):
        items.append(
            f"""    <item>
      <title>{escape(page.title)}</title>
      <link>{escape(canonical(page.slug))}</link>
      <guid isPermaLink="true">{escape(canonical(page.slug))}</guid>
      <pubDate>Sat, 25 Jul 2026 15:00:00 GMT</pubDate>
      <description>{escape(page.description)}</description>
    </item>"""
        )
    feed = f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
  <channel>
    <title>Secure Context Cache Updates</title>
    <link>{BASE_URL}</link>
    <description>Technical guides, benchmarks, integrations, and release notes for secure AI-agent token optimization.</description>
    <language>en-us</language>
    <lastBuildDate>Sat, 25 Jul 2026 15:00:00 GMT</lastBuildDate>
{chr(10).join(items)}
  </channel>
</rss>
"""
    (SITE / "feed.xml").write_text(feed)


def write_robots_and_indexnow() -> None:
    robots = f"""# Search and answer-engine crawlers
User-agent: Googlebot
Allow: /

User-agent: Bingbot
Allow: /

User-agent: OAI-SearchBot
Allow: /

User-agent: ChatGPT-User
Allow: /

User-agent: Claude-SearchBot
Allow: /

User-agent: Claude-User
Allow: /

User-agent: PerplexityBot
Allow: /

# Public open-source documentation may also be used by training crawlers.
User-agent: GPTBot
Allow: /

User-agent: ClaudeBot
Allow: /

User-agent: Google-Extended
Allow: /

User-agent: *
Allow: /

Sitemap: {BASE_URL}sitemap.xml
Sitemap: {BASE_URL}sitemap.txt
"""
    (SITE / "robots.txt").write_text(robots)
    (SITE / f"{INDEXNOW_KEY}.txt").write_text(f"{INDEXNOW_KEY}\n")
    (SITE / "indexnow-urls.json").write_text(
        json.dumps(
            {
                "host": "krishnamuppidi.github.io",
                "key": INDEXNOW_KEY,
                "keyLocation": f"{BASE_URL}{INDEXNOW_KEY}.txt",
                "urlList": [line for line in (SITE / "sitemap.txt").read_text().splitlines() if line],
            },
            indent=2,
        )
        + "\n"
    )


def main() -> None:
    SITE.mkdir(parents=True, exist_ok=True)
    for page in PAGES:
        directory = SITE / page.slug
        directory.mkdir(parents=True, exist_ok=True)
        (directory / "index.html").write_text(render_page(page))
        (directory / "index.md").write_text(render_markdown(page))
    for slug, (title, description) in EXISTING_PAGES.items():
        directory = SITE / slug if slug else SITE
        (directory / "index.md").write_text(
            render_existing_markdown(slug, title, description)
        )
    make_visual_assets()
    upgrade_existing_metadata()
    write_machine_files()
    write_sitemaps_and_feed()
    write_robots_and_indexnow()
    print(f"Generated {len(PAGES)} discoverability pages; IndexNow key {INDEXNOW_KEY}")


if __name__ == "__main__":
    main()
