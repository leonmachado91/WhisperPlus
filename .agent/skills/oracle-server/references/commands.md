# Oracle Server Commands Reference

## Docker

```bash
# Listar containers
docker ps

# Logs
docker logs n8n --tail 100
docker logs caddy --tail 100
docker logs -f n8n  # tempo real

# Restart
docker restart n8n
docker restart caddy

# Stats
docker stats --no-stream
```

## Sistema

```bash
# Status geral
uptime
free -h
df -h

# Processos
htop
ps aux | grep node

# Rede
netstat -tlpn
curl -I https://leon8n.duckdns.org/
```

## n8n Específico

```bash
# Diretório n8n
cd /home/ubuntu/n8n

# Docker compose
docker compose ps
docker compose logs n8n
docker compose restart n8n

# Backup database
docker cp n8n:/home/node/.n8n/database.sqlite ./backup/
```

## Caddy

```bash
# Verificar config
docker exec caddy caddy validate --config /etc/caddy/Caddyfile

# Reload config
docker exec caddy caddy reload --config /etc/caddy/Caddyfile

# Certificados
docker exec caddy caddy trust
```

## Tailscale

```bash
# Status
tailscale status

# IP
tailscale ip -4
```
