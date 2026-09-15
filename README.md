# UCII Python SDK

The official public Python SDK for Universal Cryptographic Identity Infrastructure (UCII).

This repository contains a deliberately narrow, developer-facing client boundary for the UCII public API. It is intended to give external developers the minimum interface needed to integrate with UCII without exposing the private UCII server implementation or sensitive internal trust and authority machinery.

## Install from GitHub

```bash
pip install git+https://github.com/EtashRhys/ucii-sdk.git
```

## Current public SDK surface

The currently published SDK includes public client support for:

- identity creation, retrieval, and listing;
- credential registration, retrieval, verification, revocation, and recovery;
- verification status;
- x402 service discovery/metadata and pricing through `client.x402.info()` and `client.x402.pricing()`;
- service-entitlement proof construction for supported economic-access flows;
- synchronous and asynchronous HTTP transport;
- public SDK error handling.

Additional UCII capabilities may exist behind the public API, but they are not part of this repository unless and until they pass a separate publication and competitive-IP review.

## Public boundary

This repository contains sanctioned public interoperability code only. It does not contain the UCII server implementation, private custody material, controller secrets, production infrastructure, databases, autonomous fleet internals, Mission Control internals, private operational policy, or private enforcement logic.

Applications integrate with UCII through the public API boundary rather than importing private server code.

## Authority separation

UCII intentionally separates identity, credential verification, authority, economic access, and execution.

A verified identity does not automatically possess action authority. Payment or service entitlement does not create controller or execution authority. Public SDK interfaces may present evidence or requests to UCII, but authoritative trust and enforcement decisions remain inside the private UCII service.

## Base URL

Provide the UCII base URL supplied for the environment you are integrating with:

```python
from ucii import UCIIClient

client = UCIIClient(base_url="https://<your-ucii-endpoint>")
```

Read x402 service metadata or pricing through the same client:

```python
info = client.x402.info()
pricing = client.x402.pricing()
```

The public SDK intentionally does not expose settlement history, receipt verification, settlement adapters, or private settlement enforcement machinery.

The public repository intentionally does not treat any deployment hostname as authoritative unless that endpoint has been explicitly approved for public documentation.

## Python

Python >= 3.11

## Distribution

`ucii-sdk`

## License

Apache License 2.0
