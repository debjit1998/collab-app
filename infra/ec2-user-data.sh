#!/bin/bash
# EC2 first-boot bootstrap for the collab-api host.
# Paste this into the "User data" field when launching a t3.micro Amazon Linux 2023.
#
# Prerequisites baked into this script:
#   - The instance role (collab-ec2-role) has ECR pull + SSM core attached.
#   - Account ID / region are hardcoded — change if you move accounts.

set -euxo pipefail

# --- Docker ---
dnf update -y
dnf install -y docker
systemctl enable --now docker
usermod -aG docker ec2-user

# --- Docker Compose v2 (not included in AL2023's docker package) ---
mkdir -p /usr/libexec/docker/cli-plugins
curl -SL https://github.com/docker/compose/releases/latest/download/docker-compose-linux-x86_64 \
  -o /usr/libexec/docker/cli-plugins/docker-compose
chmod +x /usr/libexec/docker/cli-plugins/docker-compose

# --- App directory + compose file ---
mkdir -p /opt/collab
cat > /opt/collab/docker-compose.yml <<'YAML'
services:
  redis:
    image: redis:7-alpine
    restart: unless-stopped
    networks:
      - collab-net
    volumes:
      - redis-data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 3s
      retries: 3

  api:
    image: 182399698691.dkr.ecr.ap-south-1.amazonaws.com/collab-api:latest
    restart: unless-stopped
    ports:
      - "8000:8000"
    environment:
      REDIS_URL: redis://redis:6379/0
    depends_on:
      redis:
        condition: service_healthy
    networks:
      - collab-net

networks:
  collab-net:

volumes:
  redis-data:
YAML
chown -R ec2-user:ec2-user /opt/collab

# --- ECR login + first pull as ec2-user ---
sudo -u ec2-user bash <<'EOF'
set -e
aws ecr get-login-password --region ap-south-1 \
  | docker login --username AWS \
    --password-stdin 182399698691.dkr.ecr.ap-south-1.amazonaws.com
cd /opt/collab
docker compose pull
docker compose up -d
EOF
