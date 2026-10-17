# Multi-provider AI backend support

Status: Approved

## Problem

ai-cli is hardcoded to OpenAI: `OpenAIClient` is instantiated directly in
`commands.py`, there's no provider abstraction, and the only persisted
setting is a single API key in the OS keyring. Users want to use Claude or
OpenRouter instead.

## Decision summary

- Purely additive. Zero-config existing OpenAI users see no behavior change
  until they explicitly re-run `ai setup` and pick a different provider.
- Exactly one active provider and one active model at a time — no
  multi-provider fallback, no per-request override beyond what's configured.
  Switching providers overwrites the previous selection (one slot, not saved
  profiles you toggle between).
- Non-secret state (active provider, active model) lives in a new config
  file at `~/.config/ai-cli/config.json`. The API key itself stays in the
  OS keyring, stored under the same keyring service/username as today
  (`ai-cli` / `openai-api-key`) regardless of which provider is active —
  this avoids any migration for existing users; the config file is what
  actually says which provider the stored key belongs to.
- Env var fallback extends to all three providers (`ANTHROPIC_API_KEY`,
  `OPENROUTER_API_KEY`, alongside the existing `OPENAI_API_KEY`), same
  fallback-only-if-no-stored-key semantics as today.
- `ai setup` stays interactive by default: pick provider → enter key →
  optionally override model (pre-filled with that provider's *currently
  configured* model if one exists, else a hardcoded cheap/fast default).
  Also accepts `--provider`, `--model`, `--api-key` flags for
  non-interactive/scripted use.
- Key validation: a cheap local prefix/shape check per provider, then a
  live test call; a failed live call (e.g. network down) warns but doesn't
  block saving.
- OpenRouter's model field is free text (vendor-prefixed slugs, e.g.
  `anthropic/claude-haiku-4.5`) — no fixed allowlist; a bad id surfaces as
  an API error at call time.
- `ai status` reports active provider + model + "key present," with no
  live API call — instant, no network dependency.
- `ai reset` wipes the whole configuration (provider + model + key), same
  full-reset semantics as today.
- Introduce a minimal common client interface (`BaseAIClient`, matching
  the existing `get_terminal_command()` call shape) implemented by
  `OpenAIClient`, new `ClaudeClient`, new `OpenRouterClient`, with a small
  factory (`create_client`) selecting the right one from the active
  provider — replacing the hardcoded `OpenAIClient` reference in
  `commands.py`.

See [docs/adr/0001-multi-provider-ai-backend.md](../../docs/adr/0001-multi-provider-ai-backend.md)
for the architectural rationale and [GLOSSARY.md](../../GLOSSARY.md) for
the "provider" / "active provider" vocabulary this introduces.

## Out of scope

- Storing multiple providers' keys simultaneously / switching without
  re-entering a key.
- A fixed model allowlist for any provider.
- Live-validating the stored key on every `ai status` call.
