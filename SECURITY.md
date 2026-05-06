# Security Policy

## Supported Versions

KYNODE Pediatric is currently a pre-pilot alpha. Security fixes are handled on the `main` branch and released with the next tagged alpha or beta.

## Reporting a Vulnerability

Please report security concerns privately to:

```text
opensource@kynode.io
```

Do not open a public issue for vulnerabilities involving patient privacy, deployment configuration or clinical data handling.

## Privacy Boundary

The standalone packages in this repo do not require cloud access, databases or external APIs.

The demo uses synthetic data only.

The intended deployment boundary is:

```text
PHI stays inside the clinic. Only aggregated zone-level signal leaves the node.
```
