#!/bin/bash
# setup_port_redirect.sh
#
# Redirects real port 22 traffic to Cowrie's port 2222 using iptables NAT,
# and moves the REAL sshd off port 22 first so admin access is preserved.
# Run as a sudo-capable user. Reference script -- review before running.

set -e

echo "== 1. Move real sshd off port 22 (systemd socket activation) =="
echo "Run: sudo systemctl edit ssh.socket"
echo "Add:"
echo "[Socket]"
echo "ListenStream="
echo "ListenStream=22222"
echo ""
echo "Then:"
echo "sudo systemctl daemon-reload"
echo "sudo systemctl restart ssh.socket"
echo "sudo systemctl restart ssh.service"
echo ""
echo "VERIFY before continuing: ss -tlnp | grep 22222"
echo "Confirm you can log in on the new port from a SEPARATE session:"
echo "  ssh -p 22222 <your_user>@localhost"
read -p "Press Enter once real SSH access on 22222 is confirmed working..."

echo "== 2. Redirect port 22 -> Cowrie's port 2222 =="
sudo iptables -t nat -A PREROUTING -p tcp --dport 22 -j REDIRECT --to-port 2222
# Also needed if you want to test from the same machine (localhost):
sudo iptables -t nat -A OUTPUT -p tcp -o lo --dport 22 -j REDIRECT --to-port 2222

echo "== 3. Persist the rules across reboots =="
sudo apt install -y iptables-persistent
sudo netfilter-persistent save

echo "Done. Verify with:"
echo "  sudo iptables -t nat -L PREROUTING -n"
echo "  ssh -p 22 root@localhost   # should hit Cowrie, not real sshd"
