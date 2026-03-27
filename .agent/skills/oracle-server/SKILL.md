---
name: oracle-server
description: Gerenciamento do servidor Oracle Cloud Always Free via MCP oracle-ssh. Use quando precisar executar comandos no servidor, verificar status de serviços (n8n, Caddy, Docker), troubleshooting, ou gerenciar containers.
---

# Oracle Server Management

Skill para gerenciamento do servidor Oracle Cloud via MCP `oracle-ssh`.

## Informações do Servidor

| Propriedade | Valor |
|-------------|-------|
| **IP** | `146.235.57.174` |
| **User** | `ubuntu` |
| **OS** | Ubuntu 22.04 |
| **Region** | São Paulo |

## Serviços

| Serviço | URL/Info |
|---------|----------|
| **n8n** | https://leon8n.duckdns.org/ |
| **Caddy** | Reverse proxy + HTTPS |
| **Docker** | Container runtime |

## Uso

Use o MCP `oracle-ssh` para executar comandos:

```
mcp_oracle-ssh_exec({ command: "docker ps" })
mcp_oracle-ssh_sudo-exec({ command: "systemctl status docker" })
```

## Comandos Frequentes

Ver [references/commands.md](references/commands.md) para lista completa.

### Quick Reference

```bash
# Status
docker ps
docker logs n8n --tail 50
uptime && free -h && df -h

# Restart
docker restart n8n
docker restart caddy

# Logs em tempo real
docker logs -f n8n
```
