+++
title = "v0 and modular v1 comparison"
type = "chapter"
weight = 1
comparison_schema = 1
upstream_repository = "evefrontier/world-contracts"
comparison_mode = "tip-to-tip"
v0_ref = "main"
v0_reviewed_commit = "843f706efe74b0c5b818d4282587f4a58893107c"
v1_ref = "dev"
v1_reviewed_commit = "485740eae181638f494bd574e18a10ba0c991303"
merge_base_commit = "db577cf9fd85c2310f6449a1cf42a4a84ba9d20b"
reviewed_at = "2026-08-10T18:00:00Z"
review_status = "complete"
+++

## Scope

This chapter compares the reviewed `main` tree (**v0**) with the modular architecture in the reviewed `dev` tree (**v1 architecture**). These are divergent development branches—not a linear release history, semantic-version promise, production-readiness statement, or evidence that either source tree is deployed or active in game. The candidates have 16 `main`-only and 28 `dev`-only commits after their merge base.

The existing World Contracts pages remain v0/`main` material. They are not relocated by this comparison.

## Executive summary

v0's active `world` package uses fixed shared assemblies and dedicated domain objects. v1's active source is split into `core`, `character`, and `inventory`; v0 packages are retained below `contracts/archive/`. v1 composes deterministic `Entity` objects from installed modules and gates lifecycle work through typed, transaction-scoped requests and requirements. That is an incompatible integration model, not a complete port of the archived gameplay surface.

The comparison is source and test review only. Manifests establish only the artifacts they name; neither source presence nor a passing source review proves deployment or runtime behavior. [Architecture](architecture/) explains the model; [coverage](domain-coverage/) prevents archive code from being mistaken for active v1 code; [evidence](evidence/) records limitations and contradictions.

## Method and provenance

Every upstream factual link uses one of the immutable commits in this page's metadata. Review three relationships: recorded v0 to `main`, recorded v1 to `dev`, and the pinned tips against each other. The sole cursor is here so child pages cannot drift. The initial review found 26 v0 source modules and 21 v0 Move tests, plus 13 active v1 source modules, 31 v1 Move tests, and 45 archived v1 source modules. Tests and archive paths are not counted as active source coverage.

{{% children sort="weight" %}}
