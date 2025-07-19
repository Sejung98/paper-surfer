#!/usr/bin/env python3
"""
Background Runner for Paper Surfer
Runs Paper Surfer in background with minimal resource usage
"""

import os
import sys
import time
import logging
import subprocess
import psutil
from datetime import datetime
import signal
import threading

class BackgroundRunner:
    def __init__(self):
        self.running = False
        self.process = None
        self.log_file = "./logs/background_runner.log"
        self.pid_file = "./logs/background_runner.pid"
        self.setup_logging()
        
    def setup_logging(self):
        """Setup logging for background runner"""
        os.makedirs(os.path.dirname(self.log_file), exist_ok=True)
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(self.log_file, encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger('BackgroundRunner')
        
    def save_pid(self):
        """Save process ID to file"""
        os.makedirs(os.path.dirname(self.pid_file), exist_ok=True)
        with open(self.pid_file, 'w') as f:
            f.write(str(os.getpid()))
            
    def remove_pid(self):
        """Remove PID file"""
        if os.path.exists(self.pid_file):
            os.remove(self.pid_file)
            
    def is_running(self):
        """Check if background runner is already running"""
        if not os.path.exists(self.pid_file):
            return False
            
        try:
            with open(self.pid_file, 'r') as f:
                pid = int(f.read().strip())
            return psutil.pid_exists(pid)
        except:
            return False
            
    def stop_existing(self):
        """Stop existing background runner"""
        if not os.path.exists(self.pid_file):
            return
            
        try:
            with open(self.pid_file, 'r') as f:
                pid = int(f.read().strip())
            
            if psutil.pid_exists(pid):
                os.kill(pid, signal.SIGTERM)
                self.logger.info(f"Stopped existing background runner (PID: {pid})")
                time.sleep(2)
        except Exception as e:
            self.logger.error(f"Error stopping existing runner: {e}")
            
    def get_system_resources(self):
        """Get current system resource usage"""
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        return {
            'cpu_percent': cpu_percent,
            'memory_percent': memory.percent,
            'memory_available_gb': memory.available / (1024**3),
            'disk_percent': disk.percent,
            'disk_free_gb': disk.free / (1024**3)
        }
        
    def run_paper_surfer(self):
        """Run Paper Surfer scheduler"""
        try:
            self.logger.info("Starting Paper Surfer scheduler...")
            
            # Monitor resources before starting
            resources_before = self.get_system_resources()
            self.logger.info(f"System resources before: CPU {resources_before['cpu_percent']:.1f}%, "
                           f"Memory {resources_before['memory_percent']:.1f}%, "
                           f"Disk {resources_before['disk_percent']:.1f}%")
            
            # Start Paper Surfer in scheduler mode
            self.process = subprocess.Popen(
                [sys.executable, "main.py", "--scheduler"],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
            )
            
            # Monitor the process
            while self.running and self.process.poll() is None:
                time.sleep(30)  # Check every 30 seconds
                
                # Log resource usage periodically
                if int(time.time()) % 300 == 0:  # Every 5 minutes
                    resources = self.get_system_resources()
                    self.logger.info(f"Resource usage: CPU {resources['cpu_percent']:.1f}%, "
                                   f"Memory {resources['memory_percent']:.1f}%, "
                                   f"Available Memory {resources['memory_available_gb']:.1f}GB")
            
            if self.process.poll() is not None:
                self.logger.warning(f"Paper Surfer process exited with code: {self.process.returncode}")
                
        except Exception as e:
            self.logger.error(f"Error running Paper Surfer: {e}")
            
    def start(self):
        """Start background runner"""
        if self.is_running():
            print("Background runner is already running!")
            return
            
        self.running = True
        self.save_pid()
        
        # Set up signal handlers
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        
        self.logger.info("Background runner started")
        
        # Reduce process priority to use less CPU
        try:
            if os.name == 'nt':  # Windows
                import win32process
                win32process.SetPriorityClass(-1, win32process.BELOW_NORMAL_PRIORITY_CLASS)
            else:  # Unix-like
                os.nice(10)
        except:
            pass
            
        # Run Paper Surfer
        self.run_paper_surfer()
        
    def stop(self):
        """Stop background runner"""
        self.running = False
        if self.process:
            self.process.terminate()
            self.process.wait()
        self.remove_pid()
        self.logger.info("Background runner stopped")
        
    def signal_handler(self, signum, frame):
        """Handle termination signals"""
        self.logger.info(f"Received signal {signum}, stopping...")
        self.stop()
        sys.exit(0)
        
    def status(self):
        """Show background runner status"""
        if self.is_running():
            print("✅ Background runner is running")
            if os.path.exists(self.pid_file):
                with open(self.pid_file, 'r') as f:
                    pid = f.read().strip()
                print(f"   PID: {pid}")
                
                # Show resource usage
                try:
                    resources = self.get_system_resources()
                    print(f"   System Resources:")
                    print(f"   - CPU: {resources['cpu_percent']:.1f}%")
                    print(f"   - Memory: {resources['memory_percent']:.1f}% "
                          f"(Available: {resources['memory_available_gb']:.1f}GB)")
                    print(f"   - Disk: {resources['disk_percent']:.1f}% "
                          f"(Free: {resources['disk_free_gb']:.1f}GB)")
                except Exception as e:
                    print(f"   Error getting resources: {e}")
        else:
            print("❌ Background runner is not running")

def main():
    runner = BackgroundRunner()
    
    if len(sys.argv) < 2:
        print("Usage: python background_runner.py [start|stop|restart|status]")
        return
        
    command = sys.argv[1].lower()
    
    if command == "start":
        print("🚀 Starting Paper Surfer in background...")
        runner.start()
    elif command == "stop":
        print("⏹️  Stopping background runner...")
        runner.stop_existing()
        print("✅ Background runner stopped")
    elif command == "restart":
        print("🔄 Restarting background runner...")
        runner.stop_existing()
        time.sleep(2)
        runner.start()
    elif command == "status":
        runner.status()
    else:
        print("Invalid command. Use: start, stop, restart, or status")

if __name__ == "__main__":
    main() 