#!/usr/bin/env python3
"""Check network for call connectivity"""

import socket
import subprocess

print("Checking network configuration for calls...")
print("-" * 50)

# Check if UDP is available
try:
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(1)
    sock.sendto(b'test', ('8.8.8.8', 53))
    print("✅ UDP outbound: Working")
    sock.close()
except:
    print("❌ UDP outbound: Blocked")

# Check local IP
import socket
hostname = socket.gethostname()
local_ip = socket.gethostbyname(hostname)
print(f"Local IP: {local_ip}")

# Check if behind NAT
if local_ip.startswith('192.168.') or local_ip.startswith('10.'):
    print("⚠️ Behind NAT - may need port forwarding")

print("\nFor Telegram calls to work:")
print("1. UDP ports 16384-32768 should be open")
print("2. STUN/TURN should be accessible")
print("3. Firewall should allow WebRTC")
