# agentic-rag

A **LangGraph agent that turns a natural-language telemetry request into a deployed gNMI subscription** on a Nokia SR Linux router. You say *"monitor the management-interface stats on my SR Linux router, dial-out gRPC to my collector at 10.0.0.5:50000, 2 s sample interval"* — the agent extracts a validated intent, resolves it to concrete YANG paths (RAG over the schema), renders a `gnmic.yaml`, and restarts the collector container so the telemetry is live.

> **Status:** early-stage research scaffold. The intent-extraction graph and the config-generation / deployment tool work end to end against a local Containerlab telemetry lab; retrieval over the YANG knowledge base and evaluation are works in progress.

## How it works

```
natural-language request
        │
        ▼
  LangGraph graph (src/graph.py)
   ├─ extract → IntentSkeleton  (Pydantic, src/schema.py — target router, collector,
   │                             telemetry goals, interfaces, sample interval, encoding…)
   ├─ retrieve → YANG paths     (RAG over the schema KB in kb/ — Qdrant / Chroma)
   └─ act → deploy_telemetry()  (src/tools.py)
                │
                ├─ resolve telemetry goals → /platform/control/cpu, /interface[name=…]/statistics, …
                ├─ render gnmic.yaml (targets + subscriptions + Prometheus output)
                └─ docker restart clab-…-gnmic   → subscription is live
```

LLM access is provider-agnostic (`src/llm.py` — OpenAI, Google Gemini, DeepSeek, or local HF models via LangChain), so you can swap the model without touching the graph.

## Layout

| Path | Contents |
|---|---|
| `src/graph.py` | The LangGraph state graph that ties extraction → retrieval → action together |
| `src/schema.py` | `IntentSkeleton` and friends — the Pydantic contract the LLM must fill |
| `src/agent.py`, `src/tools.py` | YANG-path resolution, `gnmic.yaml` generation, container reload |
| `src/llm.py`, `src/prompts.py` | Model selection and the extraction prompt |
| `src/main.py` | Minimal CLI entry point — feeds a query through the graph and prints the parsed intent |
| `kb/` | YANG / schema knowledge base used for retrieval |
| `containerlab/` | Telemetry lab topology (SR Linux + gnmic + Prometheus) the agent deploys against |
| `notebooks/` | `debug.ipynb`, `evaluate_intent_llm.ipynb` — interactive runs and intent-extraction evaluation |

## Run

```bash
uv sync                       # Python 3.13
cp .env.example .env          # add your LLM API key(s)
uv run python src/main.py     # extract intent from the example query and print it
```

To exercise the full deploy path you need the Containerlab telemetry lab from `containerlab/` running locally.

## Related

Part of a small family of network-telemetry + LLM experiments: [`telemetry-rag`](https://github.com/musel25/telemetry-rag) (RAG over telemetry docs), [`AutoNET-LLM`](https://github.com/musel25/AutoNET-LLM) (YANG catalog + RAG), [`zero-trust-agentic-network-telemetry`](https://github.com/musel25/zero-trust-agentic-network-telemetry) (proposer/executor governance for the same kind of intent).
