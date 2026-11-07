# Workflow: Single-Part Modeling

Model one physical part from confirmed requirements to validated, optionally
packaged geometry. The workflow is role-structured. Roles 1 and 2 establish
the requirements and the stage plan; Roles 3 and 4 then run a strict,
stage-by-stage TDD loop; Role 5 exports only after every stage gate passes.

Standing discipline, binding for every role:

- **Serial stages, no bundling.** Do not prepare a later stage's model or
  verification artifact early. Finish the current stage gate before entering
  the next `S` stage.
- **Verifier before model.** For every stage, define and exercise the
  verification contract before editing the real part source. A model is not
  accepted because it builds; it is accepted only when the prepared checks
  pass.
- **⛔ BLOCKING means stop.** At a blocking gate, wait for the explicit user
  answer. Never decide on the user's behalf.
- **Image judgments are delegated.** Visual checks are planned by Role 3
  before the stage model is built; the render may be produced by Role 4
  afterward, but its acceptance verdict is supplied by an isolated subagent.
- **Standard parts first.** If the requirement can be satisfied by a
  standard part, or by a part based on one (gear, ring gear, rack,
  cycloidal disc, bearing, fastener), `scad.std.*` MUST be the basis —
  hand-modeling a standard shape is a defect, not a fallback. A single
  std part with no assembly context stays in this workflow via
  `domains/standard-parts.md`; a mechanism mating several std parts
  routes to `assembly-product-build.md`.
- **Sketch tier is the default part form.** Per the Feature Tree
  Convention, planar profiles and planar paths are sketch tier. When a
  stage's profiles are sketch tier, its verification contract includes
  the sketch gates: solve status and remaining DOF recorded before
  promotion, and promotion preserving measured geometry (closure, area,
  bounds compare). Plan entities and constraints with stable ids and
  evidence-backed constraints; intentional free DOF are recorded in the
  brief, never left silent. Capability detail:
  `domains/sketch-and-features.md`.
- **Feature Tree Convention.** Every part source is a marimo notebook
  (`references/docs/guides/notebook-runtime.md`) authored as
  block-structured features per `discipline/feature-tree-convention.md`
  (sketch → basic body op → bool → modifier, one feature per block and one
  block per cell, each with its boundary comment); read both before Role 4
  writes any model source, together with `discipline/notebook-cell-design.md`
  (where the cell boundaries go, when a number is a `Var`, and why).
- **Repair the owning artifact.** A failed verification reopens the current
  stage's verifier contract or model, whichever owns the failure. Never patch
  downstream symptoms or weaken a check to pass it.

## Role map

| # | Role | Reads (load before acting) | Produces | Exit gate |
| --- | --- | --- | --- | --- |
| 1 | Requirement Confirmer | `domains/requirement-refinement.md`, `discipline/requirement-and-cad-brief.md` | `<part-dir>/REQUIREMENTS.md` | ⛔ user consent received |
| 2 | Master Planner | `REQUIREMENTS.md`, `discipline/mechanical-modeling.md`, `discipline/datums-and-coordinate-systems.md` | `<part-dir>/BUILD_PLAN.md` + base TODOs | plan presented |
| 3 | Verifier Planner | `REQUIREMENTS.md`, `BUILD_PLAN.md`, `discipline/geometric-validation.md`, exact API/diagnostic pages used by the check | current-stage verification contract, hypothesis snippets, executable verification script, `plan verifier` and `run verifier` TODO items | verification artifact is ready before modeling |
| 4 | Detail Modeling Planner & Builder | current stage's verifier contract, `domains/part-modeling.md`, `discipline/feature-ordering.md`, `discipline/feature-tree-convention.md`, `discipline/notebook-cell-design.md`, exact modeling API pages | current-stage model, operation hypotheses, rendered evidence inputs | model runs and the prepared verifier passes |
| 5 | Exporter | `REQUIREMENTS.md` export rows, `domains/export-and-translation.md`, `domains/assembly-and-product.md` | `.scadpkg` + requested exports, readability check | artifacts re-open cleanly |

## Role-switch protocol

Before starting a role's work, output exactly:

```markdown
## [Role Switch: <Role Name>]
Reading: <role-owned files>
Artifact out: <path>
```

Then act only inside that role's scope. Roles 3 and 4 switch for each
Master-Planner stage as follows:

```text
S1: Role 3 plan verifier -> Role 4 build -> Role 3 run/review verifier
S2: Role 3 plan verifier -> Role 4 build -> Role 3 run/review verifier
...
Sn: Role 3 plan verifier -> Role 4 build -> Role 3 run/review verifier
```

Role 3 may use hypotheses to design a check, but may not certify a model it
has not tested. Role 4 may use modeling hypotheses, but may not start a stage
until that stage's verification contract and script exist. A failed stage does
not advance the TODO; it appends or starts a `repair:` item for the owning
artifact and repeats the same Role 3/4 loop.

---

## Role 1 — Requirement Confirmer ⛔

Convert the request into `REQUIREMENTS.md`. No geometry, no probe builds,
no source-file writes before this role's gate closes.

Procedure:

1. Classify inputs (prose / reference images / drawings / mesh models ,etc.). For any image
   containing reference structure: write the interpreted shape region by
   region — overall form, visible features and locations, symmetry and
   orientation, anything hidden or uncertain. **Describing is not
   confirming:** the interpretation ends as part of ONE batched ask round
   that also covers the Ask-or-Record blocking table
   (`domains/requirement-refinement.md`). Shape-level facts are always
   confirmed; only dimension-level defaults may be assumed once a scale
   anchor exists.
   For provided models(most cases are mesh), use python code to render and inspect geometry information through something like sampling / fitting, which may provide useful geometry information for you to build similar stucture / rebuild same struction in brep through simplecadapi.
2. For undetermined parameters / geometry / function / performance, propose
   recommended assumptions as ask options (default first) so the user can
   accept or override in one round.

### Host binding: Role 1 blocking questions without a native ask tool (codex)

codex provides no structured interactive-question tool. Keep the ledger
discipline in plain conversation: after writing the region-by-region
interpretation and the Ask-or-Record ledger, send ONE message listing every
unresolved item that can block `REQUIREMENTS.md` — one numbered question per
decision, lettered mutually exclusive options each stating the operational
consequence, the conservative interpretation first and marked
`(recommended)`, and an explicit invitation to correct or type a different
answer. Then stop: make no further tool call until the user replies. Record
the reply verbatim in `REQUIREMENTS.md` under the same ledger keys, preserving
the user's wording for corrections. A partial answer or a general "sounds
good" does not answer the open rows: re-ask exactly those rows and keep the
gate blocked; never continue by silently selecting the recommended option.
The gate closes only when every blocking row has an explicit answer or an
explicitly recorded assumption permitted by the requirement discipline.

3. Fastened or load-bearing parts: the requirements contain the envelope
   arithmetic, not just values — head diameter + shaft + wall/clearance →
   minimum land diameter, boss thickness, edge distance, and lateral
   offset along the insertion path.
4. Write `REQUIREMENTS.md`:

```markdown
# Requirements: <part name>
- Inputs: <prose | images used | drawings>
- Functional goals: <what the part must do>
- Geometry targets: <confirmed shape description, region by region>
- Units / coordinate convention: <mm; origin, base plane, up axis>
- Named parameters (Var): <name = value | ASSUMED default>
- Fastening & mounting: <fastener, axis, head side, insertion path>
  Envelope math: <head+shaft+wall -> min land / boss / offset>
- Service conditions: <load direction and class | none stated>
- Export targets: .scadpkg always; STEP/STL/OBJ/MJCF/FCStd if requested
- Verification intent: <what the user's words require proving>
- Ask-or-Record ledger: | item | asked/assumed | answer/value |
```

Gate: the ask round returned answers, consent is recorded in the ledger, and
`REQUIREMENTS.md` exists. Entering Role 2 without this gate is the cardinal
violation.

## Role 2 — Master Planner

From `REQUIREMENTS.md` only — no API detail, no step-level modeling.

1. Choose the construction strategy (profile-driven vs block-and-feature)
   and fix the datum from the functional interface; one-paragraph rationale
   each.
2. Design the construction as numbered stages `S1..Sn`. For each stage state
   exactly what new substructure is complete at its output boundary and what
   later stages are not yet included. Pair every stage with its future
   verification target, but leave the executable verification design to Role
   3.
3. Write `BUILD_PLAN.md` with the stage output boundaries, datum, intended
   construction strategy, and the requirement-to-stage mapping. Role 3 adds
   verification contracts and Role 4 adds modeling hypotheses and source
   details while the loop runs.
4. Initialize the TODO tool with phases `Requirements / Plan / Build & Verify /
   Export`. For each stage create stable `plan verifier`, `model`, and `run
   verifier` items. The `run verifier` item is completed only after Role 3 has
   executed the prepared check against the Role 4 result. Mark Requirements
   done, Plan done, and start the first stage's `plan verifier` item.

Present the plan in ≤10 lines. No approval gate; enter the Role 3/4 loop.

### Host binding: TODO tool (codex)

Tool name: `update_plan`. One operation: submit the whole plan as
`plan=[{step, status}]` with statuses `pending / in_progress / completed`.
Every call rewrites the full plan, so start, done, drop, and append are all
expressed by including every current step with its updated status in the next
call. Contract: batch the rewrite with real work in the same turn; `step`
strings are the stable identifiers — quote them exactly (`S1 plan verifier`,
`repair: S1 verifier collision check`); keep exactly one step `in_progress`
at a time; mark a step `completed` only at its actual gate, never
speculatively. There is no `blocked` status: a blocked step stays `pending`
or `in_progress` and a follow-up `repair:` step records the blocker. Keep the
current stage's `model` step pending until its `plan verifier` artifact
exists. A failed `run verifier` reopens the owning verifier or model through
a `repair:` step; never advance the stage while either owner is open. If
`update_plan` is unavailable in the current session, keep the same list as a
checklist section in `BUILD_PLAN.md`, update it in the same turn as the work
it gates, and quote the current checklist state when reporting a gate
decision.

## Role 3 — Verifier Planner

Role 3 runs before every stage's modeling work and owns the stage's
verification contract. It is the modeling equivalent of writing tests before
implementation.

For the current `S` stage, in order:

1. Identify the stage output: name the substructure that must be complete,
   its datum/coordinate relationship, and the existing geometry it may touch.
   State what is deliberately out of scope until later stages.
2. Translate the requirements into acceptance criteria for that output:
   dimensions and tolerances; required faces, holes, axes, or features;
   interfaces and fit with already-built geometry; collision and clearance;
   fastener insertion and tool access; assembly reachability; demolding or
   manufacturing access when relevant; absence of unintended interference;
   BREP validity and single-solid expectations. Include visual criteria when
3. Turn every criterion into a deterministic check. Iterate through small
   hypothesis code snippets or probes in the available execution environment:
   deliberately good and bad probes must show that the proposed measurement,
   collision test, topology query, or visual review contract distinguishes pass
   from fail. Reject a check that merely prints a plausible value without
   testing the requirement.
4. Produce the executable verification script or function for this stage,
   including explicit pass/fail assertions, named measurements, and small
   evidence prints. Append to `BUILD_PLAN.md`:
   `Verifier contract: <output> / Criteria: <...> / Script: <path or symbol>`
   plus the hypothesis results and known-bad proof.
5. Update TODO before modeling: complete the current `plan verifier` item
   after the contract, executable check, hypothesis evidence, and known-bad
   proof are recorded. The `model` item may then start. After Role 4 produces
   the stage result, start `run verifier` and execute the exact prepared
   function or script against that result; only its passing output closes the
   stage.

Role 3 may prepare visual verification here. It defines named render views,
close-ups, comparison regions, and the structured verdict required from an
isolated reviewer. It does not treat a render it produced as its own visual
acceptance.

### Host binding: file-based hypothesis loop and plan state machine for Verifier Planner (codex)

codex has no persistent REPL. Python runs through the shell tool and every
invocation is a fresh process: names do not survive between calls. Keep each
hypothesis snippet, known-bad probe, and final check as a numbered script
file under the part directory (e.g. `<part-dir>/verify/s1_hypothesis.py`,
`s1_known_bad.py`, `s1_verify.py`), run it with `python` through the shell,
and persist intermediate state in files (JSON, pickle, or a captured package)
reloaded by the next script. The script file is the evidence: do not hide an
unproven check in a throwaway one-shot command whose text is lost. Use
`update_plan` to make the current stage's verification contract a real gate,
not a note.

Role 2 creates the stable stage steps in the `Build & Verify` phase in the
order `S1 plan verifier`, `S1 model`, `S1 run verifier`, then `S2 ...`, and
so on. Use the exact step strings in every `update_plan` call. When Role 3
enters a stage, submit the full plan with that step as the only `in_progress`
entry. If a stage is added after the original initialization, add its three
steps as one ordered batch in the next rewrite before starting the first one;
do not add a later stage's steps while the current stage is still open. A
`repair:` step for the current stage is the exception: add it next to the
owning step and keep the stage open.

After the verifier contract, executable check, hypothesis evidence, and
known-bad proof are recorded in `BUILD_PLAN.md`, close the planning gate and
open the modeling gate in one rewrite: `S1 plan verifier` -> `completed`,
`S1 model` -> `in_progress`. Role 4 owns the model step; it must not be
`in_progress` while `S1 plan verifier` is unfinished. After Role 4's source
run completes, mark `S1 model` completed, set `S1 run verifier`
`in_progress`, and execute the exact prepared script named in that step.

On a passing verification, record the output/evidence and mark `S1 run
verifier` completed; only then may `S2 plan verifier` become `in_progress`.
On a failed check, do not flip statuses merely to clear the list: identify
the owner, add a stable `repair:` step, make it the `in_progress` step, and
after the repair return to the current stage's `run verifier`; never advance
to `S2`. Batch each rewrite with the real shell, file, or verification work
in the same turn.

## Role 4 — Detail Modeling Planner & Builder

Role 4 starts only after Role 3's current-stage verifier contract and
executable check exist. It owns the detailed construction of the current
stage, not the acceptance definition.

For the current stage:

1. Read the verifier contract, then choose a construction strategy from the
   geometry and the controlling dimensions. The categories below are a design
   ladder, **not an API whitelist**: select the operations that express the
   current stage's design intent, then read the exact documentation page for
   every operation before its first call. A method absent from its page does
   not exist.

   - **Profile and sketch first when they control the shape.** Analyze the
     required 2D sections, symmetry, datum planes, and dimensional relations.
     Use `make_sketch_rsketch` with the applicable `constrain_*` APIs and
     `inspect_sketch_rsketchresult` when a constrained sketch carries design
     intent; promote it through `make_wire_from_sketch_rwire` or
     `make_face_from_sketch_rface`. Build solids from that intent with
     `extrude_rsolid`, `revolve_rsolid`, `loft_rsolid`, `sweep_rsolid`, or a
     helical sweep when the feature is genuinely helical. A closed profile is
     preferred when its parameters directly represent the requirement.
   - **Primitives are an alternative for genuinely regular base forms.** Use a
     box, cylinder, cone, sphere, or other documented primitive when it maps
     directly to the controlled form; do not force a sketch only because one
     exists. Keep the controlling dimensions as named parameters either way.
   - **Build named feature solids, then combine them deliberately.** Start
     from a named base solid, create each additive boss/rib/flange or
     subtractive bore/pocket/opening as a separately named solid or tool, then
     use `union_rsolid`, `cut_rsolid`, or `intersect_rsolid` to obtain the next
     single Solid. Repeat construct-feature -> Boolean -> verify for each
     required feature group; ensure intentional positive overlap for unions
     and tool overshoot for cuts. Do not assemble an opaque final shape in one
     expression.
   - **Use advanced features only after the prototype feature is proven.**
     Validate one representative feature before `linear_pattern_rsolidlist` or
     `radial_pattern_rsolidlist`; use documented transforms or mirrors for
     symmetry. Apply `fillet_rsolid`, `chamfer_rsolid`, `shell_rsolid`, and
     similar topology-sensitive features after their supporting geometry and
     selectors are stable.
   - **Use surface construction when the requirement is surface-led.**
     Consider documented ruled, patch, Bezier, Gordon, cylindrical, trimmed,
     sewn, or lofted surfaces; turn a closed, valid shell into a Solid only
     when that is the required topology. Do not approximate a freeform or
     transition surface with arbitrary primitives merely because booleans are
     familiar.

2. Name every meaningful construction step before it is used: source variables,
   helper functions, exposed parameters, and tags must identify the part role
   or feature rather than its creation order. Prefer names such as
   `mounting_base`, `port_bore_tool`, `front_flange`, and
   `feature.mounting_bore` over `shape2`, `cut1`, or numeric topology indexes.
   Attach semantic tags with `apply_tag(shape=..., tag=...)`, inspect them with
   `list_tags(shape=...)`, and use tag-aware QL selection where later features
   or verification need stable intent. Use `role.*`, `feature.*`, and `tool.*`
   namespaces; keep numeric facts in metadata rather than tags.

3. Use small hypothesis code snippets or probes in the available execution
   environment to test the proposed construction sequence on minimal solids.
   Print types, counts, volumes, bounds, tag/selection cards, and other facts
   required by the verifier contract. Adopt an operation only when its evidence
   shows that it can produce the required shape. Append
   `Hypothesis: ... / Result: ... / Adopted: ...` under the current stage in
   `BUILD_PLAN.md`.
4. Edit the part source only after the operation hypotheses pass. Use keyword
   arguments, named parameters, role/feature/tool tags, and QL fact prints;
   include selection cards before every fillet/chamfer.
5. Run the source and hand the resulting stage geometry to Role 3. Role 3
   executes the exact prepared verification script. The stage passes only when
   all assertions, measurements, fit/access checks, and required visual
   verdicts pass. A visual verdict comes from the isolated reviewer contract
   planned by Role 3.
5. On failure, do not weaken the check. Determine whether the verifier
   contract or the model owns the defect, add a `repair:` TODO to that owner,
   and repeat Role 3/4 for the same stage. Start the next stage only after the
   current stage's `model` and `run verifier` items are both complete.

### Host binding: file-based hypothesis loop for Detail Modeling Planner & Builder (codex)

codex has no persistent REPL; run incremental construction hypotheses as
numbered scripts under the part directory (e.g.
`<part-dir>/hypotheses/s1_base_probe.py`) through the shell tool. Names do
not survive between runs: carry intermediate geometry between probes by
writing it to a file (pickle, JSON, or a captured package) and reloading, or
by re-materializing from the part source. Keep the real source run in the
shell too. Never use a modeling success message as the verification result:
invoke the prepared verifier script and record its output in the stage
evidence.

## Verifier contract patterns

Role 3 selects the applicable checks per stage; it does not mechanically run
every pattern. A contract may combine:

- dimensional measurements with explicit tolerance bounds;
- topology, axis, and face-location queries for required features;
- BREP closure, positive volume, and solid-count checks;
- swept insertion envelopes for screws, tools, or assembly access, with a
  zero-collision criterion;
- clearance and interference checks against already-built substructures;
- demolding or tool-direction access checks when manufacturing intent requires;
- named renders and isolated per-region visual verdicts;
- functional motion or clearance checks when the part has moving interfaces;
- FEM only when service conditions are stated in `REQUIREMENTS.md`.

Every selected pattern needs a deterministic pass/fail condition and a
known-bad hypothesis proof before the current stage is modeled.

### Host binding: mandatory isolated image review (codex)

When Role 3 selects visual verification, any image-based acceptance judgment
must come from a context that did not produce the render; the modeling
context cannot certify it. Role 3 defines the visual contract before Role 4
builds: reference/render paths, named views, regions, required verdict
fields, and the reviewer input description.

- codex has no subagent spawn mechanism. The fallback reviewer is the user:
  present the render together with the written visual contract (views,
  regions, and the verdict fields you need) in one message, then stop and
  wait. Record the user's verdict verbatim in the stage evidence as the
  review record; a partial verdict is `unreviewable` for the uncovered
  regions.
- If the user cannot review in this round, the visual gate remains open and
  the stage cannot pass; do not substitute the modeling context's own
  judgment for the review.
- A mismatch cannot be overridden by the modeling context. Repair the owning
  model, render again, and repeat the review.

## Role 5 — Exporter

Read the export rows from `REQUIREMENTS.md`. Durable canonical delivery is
`sca run <part>.py --out out/<part>.scadpkg` (or
`capture(run.definition, ...)` after `run_notebook`); external formats go through
`domains/export-and-translation.md` capabilities. Post-export gate:
re-open the package in a fresh process (`validate_product_package` /
definition materialization) and confirm definition/solid counts; list every
produced file with size.

Final delivery ⛔: evidence pack + artifact list + assumptions made +
checks not run, and record the user's verdict. A rejection here routes back
through the role map to the owning artifact.

---

## Failure routes

- Boolean fails or yields multiple bodies → `domains/part-modeling.md`
  boolean discipline (overlap, overshoot tools, isolate the pair).
- Fillet/chamfer fails → smaller radius, narrower selection, later order;
  selection problems follow the edge-selection defaults.
- Dimension mismatch → re-measure against `REQUIREMENTS.md`; fix the named
  parameter, not the symptom.
- Repeated dead ends → `discipline/failure-and-repair.md`; reconsider the
  BUILD_PLAN stage, not the same retry.

Part notebook, `REQUIREMENTS.md`, `BUILD_PLAN.md` with stage output
boundaries, verifier contracts, executable verification scripts, modeling
hypotheses, and method proofs; evidence pack paths; image verdicts quoted
from isolated subagent reviews; package/exports with sizes; assumptions made;
and checks not run.
