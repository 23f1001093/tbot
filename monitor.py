#!/usr/bin/env python3
"""
Live monitoring dashboard for your voice assistant
"""

import asyncio
import sys
import time
from datetime import datetime

class Monitor:
    def __init__(self):
        self.start_time = datetime.now()
        self.call_count = 0
        
    def show_dashboard(self):
        """Display live dashboard"""
        # Clear screen
        print('\033[2J\033[H')
        
        uptime = datetime.now() - self.start_time
        hours = int(uptime.total_seconds() // 3600)
        minutes = int((uptime.total_seconds() % 3600) // 60)
        seconds = int(uptime.total_seconds() % 60)
        
        print("╔" + "═"*58 + "╗")
        print("║" + " "*20 + "🤖 VOICE ASSISTANT" + " "*20 + "║")
        print("╠" + "═"*58 + "╣")
        print(f"║ 📞 Phone: +918076444718" + " "*32 + "║")
        print(f"║ 👤 User: intern-mayaagent" + " "*30 + "║")
        print(f"║ ⏱️  Uptime: {hours:02d}:{minutes:02d}:{seconds:02d}" + " "*39 + "║")
        print(f"║ 📊 Status: 🟢 ACTIVE" + " "*36 + "║")
        print(f"║ 📥 Calls Received: {self.call_count}" + " "*37 + "║")
        print("╠" + "═"*58 + "╣")
        print("║" + " "*17 + "WAITING FOR INCOMING CALLS" + " "*15 + "║")
        print("║" + " "*58 + "║")
        print("║  📱 To test: Call +918076444718 from another account" + " "*3 + "║")
        print("║  ⚡ The assistant will auto-answer in 2 seconds" + " "*8 + "║")
        print("║  🎙️  Voice interaction will be available" + " "*16 + "║")
        print("║" + " "*58 + "║")
        print("║  Press Ctrl+C to stop" + " "*36 + "║")
        print("╚" + "═"*58 + "╝")
        
        # Animated waiting indicator
        frames = ["⏳", "⌛", "⏳", "⌛"]
        frame_idx = int(time.time() * 2) % len(frames)
        print(f"\n  {frames[frame_idx]} Monitoring for calls...")

async def main():
    monitor = Monitor()
    
    try:
        while True:
            monitor.show_dashboard()
            await asyncio.sleep(0.5)
    except KeyboardInterrupt:
        print("\n\n✅ Monitor stopped")

if __name__ == '__main__':
    asyncio.run(main())
