# Case: User microService Recovery Runbook

## Purpose
Diagnose and restore availability of critical Glow microservices in Similprod, specifically `ms user-service` to recover user login and portal functionality.

## Trigger
- Login to Glow fails at `https://glow-similprod.corp.globant.com/#/`.
- Backend Portal logs (tomcat.log) shows authentication or globers-related errors.
- microService instances are missing or unhealthy in Eureka Server at `http://nglo220dxu315.eqx.corp.globant.com:8761/`.

## Steps to Diagnose

1. Attempt login in Glow and confirm failure.
2. Check Backend Portal logs "catalina.out" y confirme que si se han registrado en los últimos minutos el siguiente error `org.springframework.web.client.HttpServerErrorException$InternalServerError: 500 Internal Server Error" para el endpoint "http://nglo220dxu315.egx.corp.globant.com:8765/glow/userservice/user/roles`
3. Open Eureka (`http://nglo220dxu315.eqx.corp.globant.com:8761/`) and search for `users` microservice are not UP.
4. If absent or unhealthy, SSH to the target hosts and check container status:
   - Hosts: `nglo220dxu338.globant.com` and `nglo220dxu339.globant.com`.
   - Run: `docker ps | grep user-service` (as `tomcat`).

## Steps to Fix

1. On each host, restart the service container (as `tomcat`):
   - `docker start user-service` or `docker restart user-service`
2. Ensure the instance binds to `users:8606` and re-registers with Eureka.
3. If restart fails, check logs:
   - `docker logs user-service --tail 200`

## Verifications
- Eureka shows all expected instances as healthy:
  - User Service: `nglo220dxu338.globant.com:users:8606`, `nglo220dxu339.globant.com:users:8606` are UP, mediante el comando `curl -s -H "Accept: application/json" http://nglo220dxu315.eqx.corp.globant.com:8761/eureka/apps | jq -r '.applications.application[] | .instance[] | select(.instanceId|test("users:8606"))|"\(.instanceId) \(.status)"'`
- Login to Glow succeeds; portal no longer displays the previous errors.

## References
- Portal: `https://glow-similprod.corp.globant.com/#/`
- Eureka Discovery: `http://nglo220dxu315.eqx.corp.globant.com:8761/`
