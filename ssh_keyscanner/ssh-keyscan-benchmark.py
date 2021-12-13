import subprocess
import ipaddress
from time import time

net = ipaddress.IPv4Network('87.250.0.0/16')
hosts = [f'{host} {host}\n' for host in net.hosts()]
with open('../hosts.txt', 'w') as f:
    f.writelines(hosts)
start = time()

with open('../output0.txt', 'w') as out_f:
    with subprocess.Popen(
            f"ssh-keyscan -T 1 -p 22 -f ../hosts.txt",
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL) as p:
        out = p.stdout.read().decode('utf-8')
        out_f.write(f'{out}\n')

print(f'scan complete in {time() - start}s')
