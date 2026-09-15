# UCII SDK Publication Audit

This document records the publication boundary used to move the sanctioned Python SDK out of the private UCII repository and into this public repository.

## Decision classes

### PUBLIC CONTRACT
Safe to publish when unchanged from the reviewed private SDK source.

- `src/ucii/__init__.py`
- `src/ucii/_transport.py`
- `src/ucii/adoption.py`
- `src/ucii/auth.py`
- `src/ucii/authorization.py`
- `src/ucii/client.py`
- `src/ucii/credentials.py`
- `src/ucii/errors.py`
- `src/ucii/identity.py`
- `src/ucii/participant.py`
- `src/ucii/peer_auth.py`
- `src/ucii/peer_trust.py`
- `src/ucii/policy.py`
- `src/ucii/provenance.py`
- `src/ucii/service_entitlement.py`
- `src/ucii/signing.py`
- `src/ucii/verification.py`
- `src/ucii/x402.py`
- `pyproject.toml`

These files define thin public HTTP client behavior and public data/contracts. They do not contain the UCII server implementation, production secrets, private-key custody material, database access, deployment topology, Mission Control/fleet internals, or private enforcement machinery.

### KEEP PRIVATE
The following categories remain in the private UCII repository and must not be copied here merely because the SDK interoperates with them:

- server-side authorization/enforcement internals;
- credential/controller lifecycle implementation internals;
- private custody and signing implementations;
- settlement processing internals and reusable payment material;
- production configuration, databases, host/service configuration, deployment runbooks, and credentials;
- autonomous fleet, Scout, Ambassador, Guardian private integration machinery, Mission Control, private prompts, and operational policy;
- internal security findings and exploit-enabling details that are not required for safe public interoperability;
- private tests or fixtures containing operational assumptions, internal topology, secrets, or implementation-specific assertions.

## Review findings

- Public HTTP transport contains no hard-coded production credentials or private host paths.
- The public client accepts caller-provided `base_url` and optional API token; it does not contain production tokens.
- The signing boundary is provider-neutral and does not own or persist private keys.
- Service entitlement exposes only the public proof format and explicitly does not create controller, authorization, revocation, or execution authority.
- Provenance exposes descriptive event envelopes only; durable storage, retention, append-only persistence, and tamper-evidence implementation remain outside the SDK.
- x402 exposes public service metadata, pricing, and settlement projections, not private settlement implementation.
- Delegated-authority methods expose the sanctioned public API surface; server-side authority evaluation and enforcement remain private.

## Publication rule

The public SDK may explain how to call UCII and how to construct sanctioned public requests. It must not explain or reproduce how the private UCII service internally establishes, stores, enforces, rotates, settles, or operationalizes trust and authority beyond what the public API contract requires.

Any future SDK synchronization from the private UCII repository must repeat this boundary review before publishing new modules or fields.
