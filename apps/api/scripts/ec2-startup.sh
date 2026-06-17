#!/bin/bash
set -euxo pipefail

# Update + install Docker
dnf update -y
dnf install -y docker

# Start Docker, enable on boot
systemctl enable --now docker

# Allow ec2-user to run docker without sudo (convenience for SSM shells)
usermod -aG docker ec2-user

# systemd unit for the collab-api container.
# Pulls latest from ECR on every start; deploy step will trigger restart.
cat > /etc/systemd/system/collab-api.service <<'EOF'
[Unit]
Description=Collab API container
After=docker.service network-online.target
Requires=docker.service
Wants=network-online.target

[Service]
Type=simple
Restart=always
RestartSec=5
TimeoutStartSec=120

ExecStartPre=/bin/bash -c '/usr/bin/aws ecr get-login-password --region ap-south-1 | /usr/bin/docker login --username AWS --password-stdin 182399698691.dkr.ecr.ap-south-1.amazonaws.com'
ExecStartPre=-/usr/bin/docker stop collab-api
ExecStartPre=-/usr/bin/docker rm collab-api
ExecStartPre=/usr/bin/docker pull 182399698691.dkr.ecr.ap-south-1.amazonaws.com/collab-api:latest

ExecStart=/usr/bin/docker run --name collab-api --rm -p 8000:8000 182399698691.dkr.ecr.ap-south-1.amazonaws.com/collab-api:latest

ExecStop=/usr/bin/docker stop collab-api

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload