# Glossary

Domain vocabulary for ai-cli. See `docs/agents/domain.md` for how this
file is meant to be used, and `docs/adr/` for the decisions that
introduced these terms.

## Provider

An AI backend ai-cli can send a question to in order to get back a
terminal command: `openai`, `claude` (Anthropic), or `openrouter`. Each
provider has a `ProviderSpec` (`ai_cli/config.py`) describing its label,
default model, API key prefix, environment variable name, and
where-to-get-a-key URL.

Don't use "backend" or "vendor" for this — the code and the CLI flags
(`--provider`) both say "provider."

## Active provider

The single provider ai-cli is currently configured to use. There is
always exactly one — no per-request override and no stored set of
provider profiles to switch between. Set by `ai setup`; stored (along
with the active model) in `~/.config/ai-cli/config.json`; read via
`ProviderConfigManager.get_active_provider()`.

Switching the active provider overwrites whichever one was active before,
including the API key stored for it — see
[ADR-0001](adr/0001-multi-provider-ai-backend.md).

## Active model

The model id ai-cli will ask the active provider for. Free text — there
is no fixed allowlist, since OpenRouter's catalog of model slugs (e.g.
`anthropic/claude-haiku-4.5`) changes independently of this codebase. Each
provider has a default model used when the user hasn't overridden it.
