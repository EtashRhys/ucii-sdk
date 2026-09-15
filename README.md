# UCII Python SDK

The official public Python SDK for Universal Cryptographic Identity Infrastructure (UCII).

The SDK provides a thin developer-facing client boundary over the UCII `/v1/*` API for identity, credentials, authentication, verification, authorization, delegated authority, provenance, service entitlement, and x402 interactions.

## Install from GitHub

```bash
pip install git+https://github.com/EtashRhys/ucii-sdk.git
```

## Basic client

```python
from ucii import UCIIClient

client = UCIIClient(base_url="https://ucii.sportgen-ai.com")

status = client.verification.status()
print(status)

client.close()
```

Async usage is available through `AsyncUCIIClient`.

## Public boundary

This repository contains the sanctioned public SDK surface only. It does not contain the UCII server implementation, private custody material, controller secrets, production infrastructure, fleet internals, or other private UCII implementation details.

Applications integrate with UCII through the public API boundary rather than importing private server code.

## Capability domains

The SDK exposes public client and contract surfaces for:

- identities;
- credentials and credential verification;
- authentication compatibility flows;
- authorization checks and execution;
- delegated-authority checks, grants, and revocation;
- verification status;
- x402 discovery, pricing, and settlement information;
- service-entitlement proofs as an alternative economic-access mechanism where applicable;
- participant context and provider-neutral signing boundaries;
- peer authentication and peer-trust contracts;
- provenance events;
- agent policy and adoption-state contracts.

## Authority separation

UCII intentionally separates identity, credential verification, authority, economic access, and execution.

A verified identity does not automatically possess action authority. Payment or service entitlement does not create controller or execution authority. Local policy may further restrict behavior but cannot expand authority granted by UCII.

## Python

Python >= 3.11

## Distribution

`ucii-sdk`

## License

Apache License 2.0
