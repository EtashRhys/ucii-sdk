# UCII SDK Publication Audit

This document records the publication boundary used to move the sanctioned Python SDK out of the private UCII repository and into this public repository.

## Decision classes

### PUBLIC CONTRACT
Approved public interoperability surface in this repository.

- `src/ucii/__init__.py`
- `src/ucii/_transport.py`
- `src/ucii/client.py`
- `src/ucii/credentials.py`
- `src/ucii/errors.py`
- `src/ucii/identity.py`
- `src/ucii/participant.py`
- `src/ucii/service_entitlement.py`
- `src/ucii/signing.py`
- `src/ucii/verification.py`
- `src/ucii/x402.py`
- `pyproject.toml`

These files define the publication-approved HTTP client behavior and public
interoperability contracts. The x402 module is intentionally limited to
read-only service discovery/metadata and pricing. These files do not contain
the UCII server implementation, production secrets, private-key custody
material, database access, deployment topology, Mission Control/fleet
internals, settlement machinery, or private enforcement machinery.

### KEEP PRIVATE
The following modules and categories remain private unless a future,
independently justified interoperability requirement establishes a narrower
public contract. They must not be copied here merely because UCII internally
uses them or the public SDK interoperates with related service capabilities:

- `auth.py`;
- `policy.py`;
- `peer_auth.py`;
- `peer_trust.py`;
- `adoption.py`;
- `provenance.py`;
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
- Provenance is not part of the current public SDK surface.
- x402 exposes read-only public service discovery/metadata and pricing only; settlement projections, receipt history, verification, replay protection, adapters, and settlement enforcement machinery remain outside the public SDK.
- Authorization is exposed only as the non-executing `client.authorization.check()` public boundary. Execution, delegated-authority management, policy, permission derivation, and related server-side authority evaluation and enforcement machinery remain private.

## Publication rule

The public SDK may explain how to call UCII and how to construct sanctioned public requests. It must not explain or reproduce how the private UCII service internally establishes, stores, enforces, rotates, settles, or operationalizes trust and authority beyond what the public API contract requires.

Any future SDK synchronization from the private UCII repository must repeat this boundary review before publishing new modules or fields.
