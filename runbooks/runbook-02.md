# Case: Globers microService Recovery Runbook

## Purpose

Diagnose and restore availability of critical Glow microservices in Similprod, specifically `ms glow-globers`, to recover user login and portal functionality.

## Trigger

- Login to Glow fails at `https://glow-similprod.corp.globant.com/#/`.
- Backend Portal logs (catalina.out) shows authentication or globers-related errors.
- microService are instances missing or unhealthy in Eureka Server at `http://nglo220dxu315.eqx.corp.globant.com:8761/`.

## Steps to Diagnose

1. Review Backend Portal logs file (catalina.out) and check if there are any error at the last minutes like `ERROR 1742970 --- [nio-8080-exec-7] c.g.b.service.impl.GatewayServiceImpl : error org.springframework.web.client.HttpServerErrorException: 503 Service Unavailable`.
2. Open Eureka and search for `globers` microservice are not UP.
3. If absent or unhealthy, SSH to the target hosts and check container status:
   - Hosts: `nglo220dxu338`, `nglo220dxu332`, `nglo220dxu330`, `nglo220dxu333`, `nglo220dxu339`.
   - Run: `docker ps | grep globers` (as `tomcat`).

## Steps to Fix

1. On each host, restart the globers service container (as `tomcat`):
   - Example: `docker restart globers` (use the actual container name for `globers`).
2. Ensure the instance binds to `globers:8602` and re-registers with Eureka.
3. If restart fails, check logs:
   - `docker logs globers --tail 200`

## Verifications

- Eureka shows all expected instances as healthy:
  - Globers microService: `nglo220dxu338/332/330/333/339.globant.com:globers:8602` are UP, mediante el comando: `curl -s -H "Accept: application/json" http://nglo220dxu315.eqx.corp.globant.com:8761/eureka/apps | jq -r '.applications.application[] | .instance[] | select(.instanceId|test("globers:8602"))|"\(.instanceId) \(.status)"'`
- Login to Glow succeeds; portal no longer displays the previous errors.

## References

- Portal: `https://glow-similprod.corp.globant.com/#/`
- Eureka Discovery: `http://nglo220dxu315.eqx.corp.globant.com:8761/`
