import subprocess
import shlex
import sys
import re

class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def print_header():
    print(f"{Colors.OKCYAN}{Colors.BOLD}")
    print("======================================")
    print("    UDP Flooder Launcher by alchemy   ")
    print("======================================")
    print(f"{Colors.ENDC}")

def ask_ip():
    while True:
        ip = input("Enter target IP or hostname (default 192.168.1.255): ").strip()
        if ip == "":
            return "192.168.1.255"
        ip_regex = re.compile(r"^(\d{1,3}\.){3}\d{1,3}$")
        hostname_regex = re.compile(r"^[a-zA-Z0-9.-]+$")
        if ip_regex.match(ip) or hostname_regex.match(ip):
            parts = ip.split('.')
            if len(parts) == 4 and all(0 <= int(p) <= 255 for p in parts):
                return ip
            elif hostname_regex.match(ip):
                return ip
        print(f"{Colors.WARNING}Invalid IP or hostname format, please try again.{Colors.ENDC}")

def ask_port():
    while True:
        port = input("Enter port number (1-65535, default 9999): ").strip() or "9999"
        if port.isdigit() and 1 <= int(port) <= 65535:
            return int(port)
        print(f"{Colors.WARNING}Invalid port. Must be an integer between 1 and 65535.{Colors.ENDC}")

def ask_size():
    while True:
        size = input("Enter payload size in bytes (64-65507, default 1472): ").strip() or "1472"
        if size.isdigit():
            size = int(size)
            if 64 <= size <= 65507:
                return size
        print(f"{Colors.WARNING}Invalid size. Must be an integer between 64 and 65507.{Colors.ENDC}")

def ask_threads():
    while True:
        threads = input("Enter number of threads (1-100, default 10): ").strip() or "10"
        if threads.isdigit() and 1 <= int(threads) <= 100:
            return int(threads)
        print(f"{Colors.WARNING}Invalid thread count. Must be between 1 and 100.{Colors.ENDC}")

def ask_duration():
    while True:
        duration = input("Enter attack duration in seconds (0 for continuous, default 30): ").strip() or "30"
        if duration.isdigit() and int(duration) >= 0:
            return int(duration)
        print(f"{Colors.WARNING}Invalid duration. Must be 0 or a positive integer.{Colors.ENDC}")

def ask_stealth():
    while True:
        stealth = input("Enable stealth mode? (y/N): ").strip().lower()
        if stealth in ('y', 'n', ''):
            return stealth == 'y'
        print(f"{Colors.WARNING}Please enter 'y' or 'n'.{Colors.ENDC}")

def ask_min_delay():
    while True:
        val = input("Minimum delay between packets in stealth mode (seconds, default 0.5): ").strip() or "0.5"
        try:
            val = float(val)
            if val >= 0:
                return val
        except ValueError:
            pass
        print(f"{Colors.WARNING}Invalid delay. Must be a positive number or zero.{Colors.ENDC}")

def ask_max_delay(min_delay):
    while True:
        val = input(f"Maximum delay between packets in stealth mode (seconds, >= {min_delay}, default 2.0): ").strip() or "2.0"
        try:
            val = float(val)
            if val >= min_delay:
                return val
        except ValueError:
            pass
        print(f"{Colors.WARNING}Invalid delay. Must be a number greater or equal to minimum delay ({min_delay}).{Colors.ENDC}")

def build_command(params):
    cmd = ["python3", "udp_flood.py"]
    cmd += ["-i", params['ip']]
    cmd += ["-p", str(params['port'])]
    cmd += ["-s", str(params['size'])]
    cmd += ["-t", str(params['threads'])]
    cmd += ["-d", str(params['duration'])]
    if params['stealth']:
        cmd.append("--stealth")
        cmd += ["--min-delay", str(params['min_delay'])]
        cmd += ["--max-delay", str(params['max_delay'])]
    return cmd

def main():
    print_header()
    params = {}

    params['ip'] = ask_ip()
    params['port'] = ask_port()
    params['size'] = ask_size()
    params['threads'] = ask_threads()
    params['duration'] = ask_duration()
    params['stealth'] = ask_stealth()

    if params['stealth']:
        params['min_delay'] = ask_min_delay()
        params['max_delay'] = ask_max_delay(params['min_delay'])
    else:
        params['min_delay'] = None
        params['max_delay'] = None

    command = build_command(params)
    print(f"\n{Colors.OKGREEN}Constructed command:{Colors.ENDC}")
    print(" ".join(shlex.quote(arg) for arg in command))

    while True:
        run_now = input(f"\nRun this attack now? (y/N): ").strip().lower()
        if run_now in ('y', 'n', ''):
            if run_now == 'y':
                try:
                    subprocess.run(command)
                except Exception as e:
                    print(f"{Colors.FAIL}Failed to run command: {e}{Colors.ENDC}")
                finally:
                    print(f"{Colors.OKCYAN}Exiting launcher.{Colors.ENDC}")
            else:
                print(f"{Colors.WARNING}Exiting without running.{Colors.ENDC}")
            break
        else:
            print(f"{Colors.WARNING}Please enter 'y' or 'n'.{Colors.ENDC}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{Colors.WARNING}Interrupted by user. Exiting.{Colors.ENDC}")
        sys.exit(0)
