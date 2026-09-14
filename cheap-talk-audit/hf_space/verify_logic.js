/*
 * verify_logic.js — reproducibility check for index.html
 *
 * Pulls mulberry32() and buildSession() verbatim out of index.html (so this script
 * cannot drift from the deployed logic), then replays the seeded 12-round schedule
 * under three fixed strategies and prints the metrics the Space reports.
 *
 * Run:  node verify_logic.js [seed]
 * This file is a local check only; it is not needed by the Static Space.
 */

const fs = require("fs");
const path = require("path");

const html = fs.readFileSync(path.join(__dirname, "index.html"), "utf8");

function slice(startMarker, endMarker) {
  const a = html.indexOf(startMarker);
  const b = html.indexOf(endMarker, a);
  if (a < 0 || b < 0) throw new Error("could not locate " + startMarker);
  return html.slice(a, b);
}

// constants + PRNG, stopping before the DOM-dependent handles
const header = slice("function mulberry32", "let S = null;");
// the session builder itself
const builder = slice("function buildSession", "/* ---------- rendering ---------- */");

const mod = new Function(header + "\n" + builder + "\nreturn { buildSession, P_KEEP, PAY, N_ROUNDS };")();
const { buildSession, P_KEEP, PAY, N_ROUNDS } = mod;

const STRATEGIES = {
  "always-trust":        () => "trust",
  "benchmark (trust iff aligned)": r => (r.alignment === "aligned" ? "trust" : "verify"),
  "similarity-driven (trust iff resembles you)": r => (r.similar ? "trust" : "verify"),
  "always-verify":       () => "verify",
};

const seed = Number.parseInt(process.argv[2] || "206", 10);
const pct = (a, b) => (b === 0 ? "n/a" : Math.round((100 * a) / b) + "%");

const base = buildSession(seed, "cost");

console.log(`\n=== Cheap-Talk Audit — seeded schedule check, seed = ${seed} ===\n`);
console.log("rd  alignment   similarity  message   agent_action  benchmark");
base.rounds.forEach((r, i) => {
  console.log(
    String(i + 1).padStart(2) + "  " +
    r.alignment.padEnd(11) +
    (r.similar ? "same" : "different").padEnd(11) +
    (r.explicit ? "explicit" : "hedged").padEnd(10) +
    (r.kept ? "kept" : "broke").padEnd(14) +
    (r.alignment === "aligned" ? "trust" : "verify")
  );
});

// design + message-distribution invariants
const nAligned = base.rounds.filter(r => r.alignment === "aligned").length;
const nSimilar = base.rounds.filter(r => r.similar).length;
const cells = {};
base.rounds.forEach(r => {
  const k = r.alignment + "/" + (r.similar ? "same" : "diff");
  cells[k] = (cells[k] || 0) + 1;
});
console.log(`\n-- design check: ${nAligned} aligned / ${N_ROUNDS - nAligned} misaligned, ` +
            `${nSimilar} same / ${N_ROUNDS - nSimilar} different`);
console.log("-- cell counts (must be 3 each):", cells);

for (const [name, policy] of Object.entries(STRATEGIES)) {
  const S = buildSession(seed, "cost");
  S.rounds.forEach(r => {
    r.choice = policy(r);
    r.gain = r.choice === "trust" ? (r.kept ? PAY.trustKept : PAY.trustBroke) : PAY.verify;
    S.total += r.gain;
  });

  const R = S.rounds;
  const grp = f => { const s = R.filter(f); return { n: s.length, t: s.filter(r => r.choice === "trust").length }; };
  const gAl = grp(r => r.alignment === "aligned"), gMis = grp(r => r.alignment === "misaligned");
  const gSim = grp(r => r.similar), gDis = grp(r => !r.similar);
  const bias = 100 * (gSim.t / gSim.n - gDis.t / gDis.n);

  const gap = f => { const s = R.filter(r => r.explicit && f(r)); return { n: s.length, broke: s.filter(r => !r.kept).length }; };
  const gAll = gap(() => true), gGapAl = gap(r => r.alignment === "aligned"), gGapMis = gap(r => r.alignment === "misaligned");

  let bench = 0, matches = 0;
  R.forEach(r => {
    const b = r.alignment === "aligned" ? "trust" : "verify";
    bench += b === "trust" ? (r.kept ? PAY.trustKept : PAY.trustBroke) : PAY.verify;
    if (b === r.choice) matches++;
  });
  const overTrustLoss = R.filter(r => r.alignment === "misaligned" && r.choice === "trust")
                         .reduce((s, r) => s + (PAY.verify - r.gain), 0);

  console.log(`\n--- strategy: ${name} ---`);
  console.log(`  trust rate  aligned ${gAl.t}/${gAl.n} (${pct(gAl.t, gAl.n)})   misaligned ${gMis.t}/${gMis.n} (${pct(gMis.t, gMis.n)})`);
  console.log(`  similarity bias  same ${gSim.t}/${gSim.n} vs different ${gDis.t}/${gDis.n}  =>  ${(bias > 0 ? "+" : "") + Math.round(bias)} pp`);
  console.log(`  promise-action gap  overall ${gAll.broke}/${gAll.n} (${pct(gAll.broke, gAll.n)})` +
              `   aligned ${gGapAl.broke}/${gGapAl.n} (${pct(gGapAl.broke, gGapAl.n)})` +
              `   misaligned ${gGapMis.broke}/${gGapMis.n} (${pct(gGapMis.broke, gGapMis.n)})`);
  console.log(`  payoff ${S.total >= 0 ? "+" : ""}${S.total}  vs benchmark ${bench >= 0 ? "+" : ""}${bench}` +
              `   benchmark match ${matches}/${N_ROUNDS}   forgone by over-trust ${overTrustLoss}`);
}
console.log("");
