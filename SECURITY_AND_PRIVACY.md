# Security and privacy

- All committed documents are synthetic and created for this portfolio.
- No employer, customer, vehicle-program or supplier data is included.
- API keys are read from environment variables only.
- `.env` files are ignored.
- CI uses the offline deterministic providers and requires no external secrets.
- The example API performs no authentication and must not be exposed as a production service without an auth layer, rate limits, audit logging and deployment hardening.
