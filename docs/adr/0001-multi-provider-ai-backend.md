# 0001: Multi-provider AI backend support

## Status

Accepted

## Context

ai-cli converts natural-language questions into terminal commands. Until
now it has been hardcoded to OpenAI: `commands.py` constructs a concrete
`OpenAIClient` directly, there is no provider abstraction, and the only
persisted setting is a single API key in the OS keyring
(`keyring.get_password("ai-cli", "openai-api-key")`), with `OPENAI_API_KEY`
as an environment-variable fallback.

Users want to configure Claude (Anthropic) or OpenRouter as alternatives.
OpenRouter in particular is not itself a model — it's a gateway that
proxies to many vendors' models by slug (e.g.
`anthropic/claude-3.5-haiku`), so "provider" and "model" are necessarily
separate axes once more than one provider exists.

## Decision

1. **One active provider, one active model, at a time.** No per-request
   provider switching and no stored set of provider profiles to toggle
   between. Running `ai setup` again for a different provider overwrites
   the previous selection.

2. **Split state by secrecy, not by provider.** The API key (secret)
   continues to live in the OS keyring, under the *same* service/username
   it always has (`ai-cli` / `openai-api-key`) — this is what lets
   existing OpenAI-only users upgrade with zero migration. Non-secret
   state — which provider is active, which model is active — moves to a
   new JSON file at `~/.config/ai-cli/config.json`, since cramming
   non-secret state into more keyring entries would be an abuse of what
   the keyring is for.

3. **A minimal common client interface**, `BaseAIClient`, with
   `validate_api_key()` and `get_terminal_command(question, system_info,
   model)` — the same shape `OpenAIClient` already exposed. `ClaudeClient`
   and `OpenRouterClient` implement it; a small `create_client(provider,
   api_key)` factory replaces the hardcoded `OpenAIClient(...)`
   construction in `commands.py`. OpenRouter reuses the `openai` SDK
   pointed at OpenRouter's OpenAI-compatible `chat.completions` endpoint
   rather than pulling in a separate client library.

4. **Model is always free text.** No fixed allowlist per provider —
   OpenRouter's catalog changes independently of this codebase, and a bad
   model id already surfaces as a clear API error at call time.

5. **No live validation on `ai status`.** Status reporting stays instant
   and offline; the live test call happens once, at `ai setup` time.

## Consequences

- Adding a fourth provider later means: add a `ProviderSpec` entry in
  `config.py`, add a client class implementing `BaseAIClient`, register it
  in `client_factory.py`. No changes needed to the config-file schema or
  to `commands.py`'s control flow.
- Because the keyring slot is shared across providers, only one provider's
  key can be stored at a time — switching providers requires re-entering
  that provider's key. This was an explicit simplicity trade-off, not an
  oversight (see spec's "Out of scope").
- `ai_cli/openai_client.py`'s validation/error-handling style (string
  matching on "authentication"/"unauthorized" in the exception message,
  rather than catching SDK-specific exception types) is intentionally
  repeated in `ClaudeClient` and `OpenRouterClient` for consistency with
  the existing codebase, not because it's the most robust approach
  available.

See [.scratch/multi-provider-support/spec.md](../../.scratch/multi-provider-support/spec.md)
for the full decision record this ADR formalizes, and
[GLOSSARY.md](../../GLOSSARY.md) for the "provider" / "active provider"
terms this introduces.
