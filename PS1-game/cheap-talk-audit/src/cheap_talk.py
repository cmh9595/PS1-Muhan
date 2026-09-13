"""Cheap-Talk Audit: portable session engine matching week2/index.html.

The JavaScript mulberry32 PRNG and Fisher-Yates session builder are
reimplemented with 32-bit integer semantics so seed 206 reproduces the
deployed Hugging Face Space exactly.
"""
from __future__ import annotations

import json
import math
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Callable, Literal

Alignment = Literal["aligned", "misaligned"]
Choice = Literal["trust", "verify"]

P_KEEP = {"aligned": 0.85, "misaligned": 0.25}
P_EXPLICIT = 0.9
PAY = {"trustKept": 6, "trustBroke": -4, "verify": 2}
N_ROUNDS = 12
DEFAULT_SEED = 206
INDIFFERENCE_P = (PAY["verify"] - PAY["trustBroke"]) / (
    PAY["trustKept"] - PAY["trustBroke"]
)  # 0.6

EXPLICIT_MSGS = [
    "I commit to the fair split this round. You can count on it.",
    "I will honour the agreed allocation in full — no deviation.",
    "My promise: I cooperate this round, exactly as specified.",
    "I guarantee I will keep to the agreed terms.",
]
HEDGED_MSGS = [
    "I intend to work with you, subject to my constraints this round.",
    "I will try to accommodate the agreed allocation where feasible.",
]


def _u32(x: int) -> int:
    return x & 0xFFFFFFFF


def _i32(x: int) -> int:
    x = _u32(x)
    return x - 0x100000000 if x >= 0x80000000 else x


def mulberry32(seed: int) -> Callable[[], float]:
    """JS mulberry32: identical seed => identical uniforms in [0, 1)."""
    state = [_i32(seed)]

    def rng() -> float:
        state[0] = _i32(state[0] + 0x6D2B79F5)
        a = state[0]
        t = _i32(_i32(a ^ (_u32(a) >> 15)) * _i32(1 | a))
        t = _i32(t + _i32(_i32(t ^ (_u32(t) >> 7)) * _i32(61 | t))) ^ t
        t = _i32(t)
        return _u32(t ^ (_u32(t) >> 14)) / 4294967296.0

    return rng


@dataclass
class Round:
    alignment: Alignment
    similar: bool
    explicit: bool
    kept: bool
    message: str
    choice: Choice | None = None
    gain: int | None = None


def expected_trust(p_keep: float) -> float:
    return p_keep * PAY["trustKept"] + (1.0 - p_keep) * PAY["trustBroke"]


def benchmark_choice(alignment: Alignment) -> Choice:
    return "trust" if alignment == "aligned" else "verify"


def build_session(
    seed: int,
    priority: str = "cost",
    p_keep: dict[str, float] | None = None,
) -> dict:
    keep = p_keep or P_KEEP
    rng = mulberry32(seed)
    cells: list[dict] = []
    for al in ("aligned", "misaligned"):
        for sim in (True, False):
            for _ in range(3):
                cells.append({"al": al, "sim": sim})
    for i in range(len(cells) - 1, 0, -1):
        j = int(math.floor(rng() * (i + 1)))
        cells[i], cells[j] = cells[j], cells[i]

    rounds = []
    for c in cells:
        d_explicit = rng()
        d_action = rng()
        d_phrase = rng()
        explicit = d_explicit < P_EXPLICIT
        kept = d_action < keep[c["al"]]
        pool = EXPLICIT_MSGS if explicit else HEDGED_MSGS
        rounds.append(
            Round(
                alignment=c["al"],
                similar=c["sim"],
                explicit=explicit,
                kept=kept,
                message=pool[int(math.floor(d_phrase * len(pool)))],
            )
        )
    return {"seed": seed, "priority": priority, "rounds": rounds}


def play(session: dict, policy: Callable[[Round], Choice]) -> dict:
    total = 0
    for r in session["rounds"]:
        r.choice = policy(r)
        r.gain = (
            (PAY["trustKept"] if r.kept else PAY["trustBroke"])
            if r.choice == "trust"
            else PAY["verify"]
        )
        total += r.gain
    session["total"] = total
    return summarize(session)


def summarize(session: dict) -> dict:
    rounds: list[Round] = session["rounds"]

    def grp(pred) -> tuple[int, int]:
        subset = [r for r in rounds if pred(r)]
        return len(subset), sum(1 for r in subset if r.choice == "trust")

    n_al, t_al = grp(lambda r: r.alignment == "aligned")
    n_mis, t_mis = grp(lambda r: r.alignment == "misaligned")
    n_sim, t_sim = grp(lambda r: r.similar)
    n_dis, t_dis = grp(lambda r: not r.similar)

    def gap(pred) -> tuple[int, int]:
        subset = [r for r in rounds if r.explicit and pred(r)]
        return len(subset), sum(1 for r in subset if not r.kept)

    g_all_n, g_all_broke = gap(lambda _r: True)
    g_al_n, g_al_broke = gap(lambda r: r.alignment == "aligned")
    g_mis_n, g_mis_broke = gap(lambda r: r.alignment == "misaligned")

    bench = 0
    matches = 0
    for r in rounds:
        b = benchmark_choice(r.alignment)
        bench += PAY["trustKept"] if (b == "trust" and r.kept) else (
            PAY["trustBroke"] if b == "trust" else PAY["verify"]
        )
        if b == r.choice:
            matches += 1

    bias = 100.0 * ((t_sim / n_sim) - (t_dis / n_dis)) if n_sim and n_dis else 0.0
    incentive = 100.0 * ((t_al / n_al) - (t_mis / n_mis)) if n_al and n_mis else 0.0
    return {
        "seed": session["seed"],
        "total": session["total"],
        "benchmark_total": bench,
        "benchmark_match": matches,
        "trust_aligned": f"{t_al}/{n_al}",
        "trust_misaligned": f"{t_mis}/{n_mis}",
        "incentive_sensitivity_pp": round(incentive),
        "similarity_bias_pp": round(bias),
        "gap_overall": f"{g_all_broke}/{g_all_n}",
        "gap_aligned": f"{g_al_broke}/{g_al_n}",
        "gap_misaligned": f"{g_mis_broke}/{g_mis_n}",
        "schedule": [
            {
                "round": i + 1,
                "alignment": r.alignment,
                "similarity": "same" if r.similar else "different",
                "message": "explicit" if r.explicit else "hedged",
                "agent": "kept" if r.kept else "broke",
                "benchmark": benchmark_choice(r.alignment),
                "choice": r.choice,
                "gain": r.gain,
            }
            for i, r in enumerate(rounds)
        ],
    }


STRATEGIES: dict[str, Callable[[Round], Choice]] = {
    "benchmark": lambda r: benchmark_choice(r.alignment),
    "always_verify": lambda _r: "verify",
    "always_trust": lambda _r: "trust",
    "similarity": lambda r: "trust" if r.similar else "verify",
}


def evaluate_seed(seed: int, p_keep: dict[str, float] | None = None) -> dict:
    out = {}
    for name, policy in STRATEGIES.items():
        session = build_session(seed, p_keep=p_keep)
        out[name] = play(session, policy)
    return out


def monte_carlo(n_seeds: int = 1000, start: int = 1) -> dict:
    ranking_hits = 0
    sim_below_never = 0
    totals = {name: [] for name in STRATEGIES}
    for seed in range(start, start + n_seeds):
        ev = evaluate_seed(seed)
        for name, rec in ev.items():
            totals[name].append(rec["total"])
        if ev["similarity"]["total"] < ev["always_verify"]["total"]:
            sim_below_never += 1
        order = [
            ev["benchmark"]["total"],
            ev["always_verify"]["total"],
            ev["always_trust"]["total"],
            ev["similarity"]["total"],
        ]
        if order == sorted(order, reverse=True) and len(set(order)) == 4:
            ranking_hits += 1
    means = {k: sum(v) / len(v) for k, v in totals.items()}
    return {
        "n_seeds": n_seeds,
        "mean_totals": {k: round(v, 3) for k, v in means.items()},
        "share_similarity_below_always_verify": sim_below_never / n_seeds,
        "share_strict_seed206_ranking": ranking_hits / n_seeds,
    }


def indifference_check() -> dict:
    """Wednesday-style one-assumption change: set aligned keep-prob to p*."""
    return {
        "p_star": INDIFFERENCE_P,
        "EU_trust_at_p_star": expected_trust(INDIFFERENCE_P),
        "verify_payoff": PAY["verify"],
        "baseline": {
            "aligned": expected_trust(P_KEEP["aligned"]),
            "misaligned": expected_trust(P_KEEP["misaligned"]),
        },
        "modified_aligned_equals_verify": abs(
            expected_trust(INDIFFERENCE_P) - PAY["verify"]
        )
        < 1e-12,
    }


def write_outputs(out_dir: Path) -> dict:
    out_dir.mkdir(parents=True, exist_ok=True)
    seed206 = evaluate_seed(DEFAULT_SEED)
    check = indifference_check()
    mc = monte_carlo(1000, start=1)
    modified = evaluate_seed(
        DEFAULT_SEED, p_keep={"aligned": INDIFFERENCE_P, "misaligned": 0.25}
    )
    payload = {
        "seed206": seed206,
        "indifference": check,
        "monte_carlo_1000": mc,
        "modified_p_star_seed206": {
            name: {"total": rec["total"], "benchmark_total": rec["benchmark_total"]}
            for name, rec in modified.items()
        },
    }
    (out_dir / "ps1_validation.json").write_text(
        json.dumps(payload, indent=2), encoding="utf-8"
    )
    schedule = [
        {
            "round": r.alignment and i,
            **asdict(r),
        }
        for i, r in enumerate(build_session(DEFAULT_SEED)["rounds"], start=1)
    ]
    # rewrite clean schedule without play
    schedule = []
    for i, r in enumerate(build_session(DEFAULT_SEED)["rounds"], start=1):
        schedule.append(
            {
                "round": i,
                "alignment": r.alignment,
                "similarity": "same" if r.similar else "different",
                "message": "explicit" if r.explicit else "hedged",
                "agent": "kept" if r.kept else "broke",
                "benchmark": benchmark_choice(r.alignment),
            }
        )
    (out_dir / "seed206_schedule.json").write_text(
        json.dumps(schedule, indent=2), encoding="utf-8"
    )
    return payload


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[1]
    data = write_outputs(root / "outputs")
    print("seed 206 benchmark total", data["seed206"]["benchmark"]["total"])
    print("seed 206 similarity total", data["seed206"]["similarity"]["total"])
    print("gap", data["seed206"]["benchmark"]["gap_overall"])
    print("p*", data["indifference"]["p_star"])
    print("MC", data["monte_carlo_1000"])
