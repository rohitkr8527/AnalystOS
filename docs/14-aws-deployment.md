# AWS EC2 deployment architecture — design only

One EC2 Linux host runs Docker Compose for the portfolio deployment. Nginx terminates HTTPS and routes `/api` to FastAPI and `/` to Next.js. PostgreSQL, Redis, workers, MCP and Dagster stay on the internal Docker network. LangSmith is external. Deploy only after production/security gates pass.

```text
Internet → security group 443 → Nginx → web / API
                                      API → Redis → worker → MCP → warehouse
                                      API → application DB
EC2 encrypted EBS → PostgreSQL volume, evidence, backup staging
```

Security group inbound: 443 public; 80 only for certificate issuance/HTTPS redirect if required. No public 5432, 6379, MCP, Dagster or Grafana. Administration uses SSM Session Manager or restricted administrator IP SSH if SSM is unavailable. Require IMDSv2 and least-privilege instance IAM. Use encrypted EBS, TLS certificates with renewal monitoring and host security updates.

GitHub Actions tests and builds immutable image tags; an approved deployment pulls the tag and runs health/readiness checks. Back up before migrations. A failed release rolls back application images; database migrations need an explicit backward-compatible or restore plan. Do not auto-run schema-destructive resets.

Initial target RPO 24 hours and RTO 4 hours. Nightly encrypted pg_dump backups for both databases must be copied off the EC2 host (operator-managed encrypted storage is sufficient; S3 optional), retained for 7 days, and restore-tested before launch and monthly. A same-disk snapshot is not an off-host backup. Alert on failed backups or renewal.

Start sizing only after measuring warehouse and worker memory; no resources are provisioned in this milestone. Use budget alerts and bounded agent spend. Single host is an accepted availability ceiling for the portfolio; split managed databases and app hosts if availability or load demands it.

Reference: [EC2 security groups](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ec2-security-groups.html).

