+++
title = "Migration guidance"
weight = 60
+++

Do not reuse v0 package/type identities, object layouts, `OwnerCap` assumptions, fixed-assembly calls, or v0 event schemas with v1. Start by mapping the integration's concrete v0 domain to the [coverage state](../domain-coverage/), then decide whether it has an active component, a redesigned equivalent, only partial platform support, or no active port.

For active components, create or locate the deterministic Entity, install/configure the component by numeric ID through its typed request, supply and consume requirements in order, and complete the request. Update PTB code to the [SDK builders](../developer-experience/), rework indexers from active event sources, and make authorization/location/bridge checks explicit in tests. Remove installed components before requesting Entity deletion to avoid the documented orphaned-field risk; do not assume deletion cleans them up.

There is no reviewed universal data migration or extension compatibility layer. `GenericModule` can extract opaque bytes for a fitting but does not migrate gameplay logic. Archived v0 extension examples are historical reference, not compatible active extension seams. For gameplay domains still archive-only, retain v0 integration or design a new component/action/requirement surface; do not claim an automatic migration path.
