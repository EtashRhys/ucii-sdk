# Security and Publication Boundary

This repository is the public UCII Python SDK surface.

It intentionally excludes the private UCII server implementation and all secret-bearing or operationally sensitive material.

## Public material allowed here

- thin `/v1/*` HTTP client code;
- public request/response contracts;
- public error models;
- provider-neutral signing interfaces;
- local policy/adoption/provenance data contracts intended for SDK consumers;
- public examples and tests that use non-secret fixtures;
- packaging and developer documentation.

## Material that must remain private

Do not publish any of the following from the private UCII repository or production environment:

- private signing keys, seed material, recovery secrets, controller-authority secrets, or reusable payment proofs;
- production credentials, tokens, API keys, database contents, host configuration, or deployment secrets;
- private server-side authorization, custody, lifecycle, settlement, anti-abuse, or enforcement implementation details that are not required by the SDK contract;
- autonomous fleet internals, Mission Control internals, private prompts, operational policies, deployment topology, or production runbooks;
- vulnerability details that would materially weaken production UCII before remediation;
- private implementation history simply because a public interface depends on it.

## SDK custody rule

The SDK does not own or persist private signing keys. Applications provide their own authorized signing/custody implementation through public provider contracts.

## Reporting

If you believe public SDK code or documentation exposes sensitive UCII implementation detail, do not include secrets in a public issue. Contact the repository owner through an appropriate private channel first.
