import paramiko
import random
import time

SCENARIOS = [
    ["whoami", "uname -a", "cat /etc/passwd", "exit"],
    ["wget https://www.wikipedia.org -O w.html", "ls -la", "exit"],
    ["cat /etc/passwd", "echo 'ssh-rsa AAAAB3Nzatest' >> ~/.ssh/authorized_keys", "exit"],
    ["crontab -l", "crontab -e", "exit"],
    ["sudo su -", "chmod 777 /etc/shadow", "exit"],
    ["wget https://en.wikipedia.org/wiki/Special:Random -O r.html", "history -c", "exit"],
    ["apt-get install -y nmap", "nmap -sV localhost", "exit"],
    ["ls", "pwd", "date", "exit"],
]


def run_session(commands):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    username = f"user{random.randint(1,999)}"
    password = f"pass{random.randint(1,999)}"

    try:
        client.connect(
            "localhost", port=2222,
            username=username, password=password,
            timeout=10, banner_timeout=10, auth_timeout=10,
            look_for_keys=False, allow_agent=False
        )
        shell = client.invoke_shell()
        time.sleep(1)

        for cmd in commands:
            shell.send(cmd + "\n")
            time.sleep(random.uniform(1, 2))

        time.sleep(1)
        client.close()
    except Exception as e:
        print(f"  (session error: {e})")


if __name__ == "__main__":
    for i in range(15):
        scenario = random.choice(SCENARIOS)
        print(f"Session {i+1}: {scenario[0]}...")
        run_session(scenario)
        time.sleep(random.uniform(2, 4))
    print("Done simulating traffic.")
