# Azure live-deployment acceptance

This branch adds deployment-ready infrastructure source. It does **not** claim a completed Azure deployment.

Do not add Azure/Terraform/production-cloud claims to the CV until:
- terraform fmt/validate/plan pass;
- resources are provisioned in a personal/developer Azure subscription;
- GitHub Actions uses Azure OIDC;
- tests + synthetic evaluation pass;
- dependency and container scans pass;
- an image is pushed to ACR and deployed to Container Apps;
- /health passes;
- Application Insights shows latency/errors/traces;
- rollback is demonstrated;
- evidence records commit SHA, image digest and deployment receipt without secrets.

Current blocker: no Azure subscription/tenant credentials are connected to this task.
