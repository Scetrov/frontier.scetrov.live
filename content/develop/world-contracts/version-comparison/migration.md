+++
title = "Migration guidance"
weight = 60
+++

Do not reuse v0 package/type identities, object layouts, `OwnerCap` assumptions, fixed-assembly calls, or v0 event schemas with v1. Start by mapping the integration's concrete v0 domain to the [coverage state](../domain-coverage/), then decide whether it has an active module, a redesigned equivalent, only partial platform support, or no active port.

For active modules, create or locate the deterministic Entity, install/configure the module through its typed request, supply and consume requirements in order, and complete the request. Update PTB code to the [SDK builders](../developer-experience/), rework indexers from active event sources, and make authorization/location/bridge checks explicit in tests.

There is no reviewed universal data migration or extension compatibility layer. Archived v0 extension examples are historical reference, not compatible active extension seams. For gameplay domains still archive-only, retain v0 integration or design a new module/action/requirement surface; do not claim an automatic migration path.
