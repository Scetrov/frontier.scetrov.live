# Layout overrides

The layout files copied from `hugo-theme-relearn` are compatibility overrides based on theme commit `93d7f257d1a3`.
They replace Hugo APIs deprecated in v0.156.0 and v0.158.0 with `hugo.Sites`, `Language.Locale`, and
`Language.Direction`. Remove or refresh them after the upstream theme resolves
[McShelby/hugo-theme-relearn#1219](https://github.com/McShelby/hugo-theme-relearn/issues/1219) and related
language API deprecations.

Project-specific partials and shortcodes in this directory are not theme compatibility copies.
