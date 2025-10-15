"""
Workflow Orchestrator — Minimal Example
---------------------------------------
A compact, production-leaning workflow skeleton that:
1) pulls data (mock),
2) summarizes key metrics,
3) builds a short action plan,
4) shares a summary email.

Each step is logged and traceable for transparency.

Replace mock_* functions with real integrations later.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Dict, List, Callable
import json
import time
import argparse
import logging
from datetime import datetime

# ---------- Logging ----------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-7s | %(message)s",
)
log = logging.getLogger("workflow-orchestrator")


# ---------- Tracing ----------
@dataclass
class Trace:
    step: str
    input: Dict[str, Any]
    output: Dict[str, Any]
    started_at: float = field(default_factory=time.time)
    finished_at: float = field(default=0.0)

    def close(self):
        self.finished_at = time.time()

    def as_dict(self) -> Dict[str, Any]:
        return {
            "step": self.step,
            "started_at": self.started_at,
            "finished_at": self.finished_at,
            "latency_ms": round((self.finished_at - self.started_at) * 1000, 2),
            "input": self.input,
            "output": self.output,
        }


# ---------- Workflow Context ----------
@dataclass
class Context:
    """Keeps shared data and step results."""
    data: Dict[str, Any] = field(default_factory=dict)
    traces: List[Trace] = field(default_factory=list)

    def add_trace(self, trace: Trace):
        self.traces.append(trace)

    def get(self, key: str, default: Any = None) -> Any:
        return self.data.get(key, default)

    def set(self, key: str, value: Any):
        self.data[key] = value


# ---------- Step Base ----------
@dataclass
class Step:
    name: str
    fn: Callable[[Context], Dict[str, Any]]

    def run(self, ctx: Context):
        trace = Trace(step=self.name, input=dict(ctx.data), output={})
        log.info(f"▶ Running step: {self.name}")
        try:
            output = self.fn(ctx) or {}
            trace.output = output
            # Merge output into context
            for k, v in output.items():
                ctx.set(k, v)
            log.info(f"✔ Completed: {self.name}")
        except Exception as e:
            log.exception(f"✖ Error in step {self.name}: {e}")
            trace.output = {"error": str(e)}
            raise
        finally:
            trace.close()
            ctx.add_trace(trace)


# ---------- Mock Integrations ----------
def mock_pull_marketing_data(ctx: Context) -> Dict[str, Any]:
    """Simulate fetching performance metrics from a data source."""
    sample = {
        "week_over_week": {"conv_rate": +0.14, "traffic": +0.07},
        "top_channels": [
            {"name": "Organic", "conv": 0.036},
            {"name": "LinkedIn", "conv": 0.028}
        ],
        "notes": "Healthcare content gained traction among Pharma executives."
    }
    return {"raw_metrics": sample}


def mock_summarize_metrics(ctx: Context) -> Dict[str, Any]:
    """Generate a concise summary and recommendations from mock data."""
    m = ctx.get("raw_metrics", {})
    conv_delta = m.get("week_over_week", {}).get("conv_rate", 0)
    summary = (
        f"Conversion rate rose {int(conv_delta*100)}% week-over-week. "
        f"Organic and LinkedIn remain leading channels. "
        f"Healthcare content continues to perform strongly."
    )
    key_insight = "Organic content is driving higher-quality engagement."
    recommendations = [
        "Increase LinkedIn outreach toward Pharma decision-makers.",
        "Repurpose top organic posts into short-form LinkedIn content.",
        "Test two creative variations focused on clinical impact."
    ]
    return {
        "summary": summary,
        "key_insight": key_insight,
        "recommendations": recommendations
    }


def mock_build_action_plan(ctx: Context) -> Dict[str, Any]:
    """Convert insights into a simple, trackable plan."""
    recs = ctx.get("recommendations", [])
    plan = [
        {"id": i + 1, "task": r, "owner": "marketing", "due": "EOW"}
        for i, r in enumerate(recs)
    ]
    return {"action_plan": plan}


def mock_send_email(ctx: Context) -> Dict[str, Any]:
    """Simulate emailing a summary report to the team."""
    payload = {
        "to": ["growth-leads@example.com"],
        "subject": f"[Daily Summary] {datetime.utcnow().strftime('%Y-%m-%d')}",
        "body": (
            f"Summary: {ctx.get('summary')}\n\n"
            f"Key Insight: {ctx.get('key_insight')}\n\n"
            f"Action Plan:\n"
            + "\n".join(
                f"- {p['task']} (owner: {p['owner']}, due: {p['due']})"
                for p in ctx.get('action_plan', [])
            )
        )
    }
    log.info(f"(mock) Email sent to {payload['to']}")
    return {"email_status": "sent", "email_payload": payload}


# ---------- Orchestrator ----------
class Orchestrator:
    def __init__(self, steps: List[Step]):
        self.steps = steps

    def run(self, ctx: Context) -> Context:
        for step in self.steps:
            step.run(ctx)
        return ctx


def build_default_workflow() -> Orchestrator:
    steps = [
        Step("pull_data", mock_pull_marketing_data),
        Step("summarize_metrics", mock_summarize_metrics),
        Step("build_action_plan", mock_build_action_plan),
        Step("send_email", mock_send_email),
    ]
    return Orchestrator(steps)


# ---------- CLI ----------
def main():
    parser = argparse.ArgumentParser(description="Workflow Orchestrator (demo)")
    parser.add_argument("--demo", action="store_true", help="Run the example workflow")
    parser.add_argument("--trace", type=str, default="trace.json", help="Save trace output to a file")
    args = parser.parse_args()

    if not args.demo:
        print("Use --demo to run the sample workflow.")
        return

    log.info("Starting demo workflow…")
    ctx = Context()
    orch = buil
