#!/usr/bin/env python3
"""
Resource Monitor for Paper Surfer
Monitor CPU, Memory, Network usage when running Paper Surfer
"""

import psutil
import time
import threading
import subprocess
import sys
from datetime import datetime

class ResourceMonitor:
    def __init__(self):
        self.monitoring = False
        self.process = None
        self.stats = {
            'cpu_samples': [],
            'memory_samples': [],
            'network_samples': [],
            'start_time': None,
            'end_time': None
        }
        
    def get_paper_surfer_process(self):
        """Find Paper Surfer process"""
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                if proc.info['name'] == 'python.exe' or proc.info['name'] == 'python':
                    cmdline = proc.info['cmdline']
                    if cmdline and 'main.py' in ' '.join(cmdline):
                        return proc
            except:
                continue
        return None
        
    def monitor_resources(self):
        """Monitor system resources"""
        print("📊 Starting resource monitoring...")
        print("Press Ctrl+C to stop monitoring")
        
        initial_network = psutil.net_io_counters()
        
        while self.monitoring:
            try:
                # System resources
                cpu_percent = psutil.cpu_percent(interval=1)
                memory = psutil.virtual_memory()
                network = psutil.net_io_counters()
                
                # Calculate network usage
                network_sent = network.bytes_sent - initial_network.bytes_sent
                network_recv = network.bytes_recv - initial_network.bytes_recv
                
                # Store samples
                self.stats['cpu_samples'].append(cpu_percent)
                self.stats['memory_samples'].append(memory.percent)
                self.stats['network_samples'].append({
                    'sent': network_sent,
                    'recv': network_recv
                })
                
                # Display current stats
                print(f"[{datetime.now().strftime('%H:%M:%S')}] "
                      f"CPU: {cpu_percent:5.1f}% | "
                      f"Memory: {memory.percent:5.1f}% | "
                      f"Network: ↑{network_sent/(1024*1024):6.1f}MB ↓{network_recv/(1024*1024):6.1f}MB")
                
                time.sleep(5)  # Monitor every 5 seconds
                
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"Error monitoring: {e}")
                break
                
    def run_with_monitoring(self):
        """Run Paper Surfer with resource monitoring"""
        self.monitoring = True
        self.stats['start_time'] = datetime.now()
        
        # Start monitoring in separate thread
        monitor_thread = threading.Thread(target=self.monitor_resources)
        monitor_thread.daemon = True
        monitor_thread.start()
        
        try:
            # Run Paper Surfer
            print("🚀 Starting Paper Surfer...")
            self.process = subprocess.Popen(
                [sys.executable, "main.py", "--once"],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True
            )
            
            # Wait for completion
            stdout, stderr = self.process.communicate()
            
            if stdout:
                print("\n📄 Paper Surfer Output:")
                print(stdout)
                
        except Exception as e:
            print(f"❌ Error running Paper Surfer: {e}")
        finally:
            self.monitoring = False
            self.stats['end_time'] = datetime.now()
            
    def analyze_results(self):
        """Analyze and display resource usage results"""
        if not self.stats['cpu_samples']:
            print("❌ No monitoring data available")
            return
            
        print("\n" + "="*60)
        print("📊 RESOURCE USAGE ANALYSIS")
        print("="*60)
        
        # Duration
        duration = self.stats['end_time'] - self.stats['start_time']
        print(f"⏱️  Duration: {duration.total_seconds():.1f} seconds")
        
        # CPU Usage
        cpu_samples = self.stats['cpu_samples']
        print(f"\n🖥️  CPU Usage:")
        print(f"   Average: {sum(cpu_samples)/len(cpu_samples):5.1f}%")
        print(f"   Maximum: {max(cpu_samples):5.1f}%")
        print(f"   Minimum: {min(cpu_samples):5.1f}%")
        
        # Memory Usage
        memory_samples = self.stats['memory_samples']
        print(f"\n💾 Memory Usage:")
        print(f"   Average: {sum(memory_samples)/len(memory_samples):5.1f}%")
        print(f"   Maximum: {max(memory_samples):5.1f}%")
        print(f"   Minimum: {min(memory_samples):5.1f}%")
        
        # Network Usage
        if self.stats['network_samples']:
            last_network = self.stats['network_samples'][-1]
            print(f"\n🌐 Network Usage:")
            print(f"   Total Sent: {last_network['sent']/(1024*1024):6.1f} MB")
            print(f"   Total Received: {last_network['recv']/(1024*1024):6.1f} MB")
            print(f"   Total Transfer: {(last_network['sent'] + last_network['recv'])/(1024*1024):6.1f} MB")
            
        # Resource Impact Assessment
        print(f"\n📈 Resource Impact Assessment:")
        avg_cpu = sum(cpu_samples)/len(cpu_samples)
        avg_memory = sum(memory_samples)/len(memory_samples)
        
        if avg_cpu < 5:
            cpu_impact = "🟢 Very Low"
        elif avg_cpu < 15:
            cpu_impact = "🟡 Low"
        elif avg_cpu < 30:
            cpu_impact = "🟠 Moderate"
        else:
            cpu_impact = "🔴 High"
            
        if avg_memory < 70:
            memory_impact = "🟢 Low"
        elif avg_memory < 85:
            memory_impact = "🟡 Moderate"
        else:
            memory_impact = "🔴 High"
            
        print(f"   CPU Impact: {cpu_impact}")
        print(f"   Memory Impact: {memory_impact}")
        
        # Recommendations
        print(f"\n💡 Recommendations:")
        if avg_cpu < 10:
            print("   ✅ Safe to run frequently - minimal CPU impact")
        elif avg_cpu < 20:
            print("   ⚠️  Moderate CPU usage - consider running during off-peak hours")
        else:
            print("   ⚠️  High CPU usage - limit frequency or optimize settings")
            
        if avg_memory < 80:
            print("   ✅ Memory usage is acceptable")
        else:
            print("   ⚠️  High memory usage - monitor system performance")

def main():
    monitor = ResourceMonitor()
    
    try:
        monitor.run_with_monitoring()
        monitor.analyze_results()
    except KeyboardInterrupt:
        print("\n⏹️  Monitoring stopped by user")
        monitor.monitoring = False
        if monitor.process:
            monitor.process.terminate()

if __name__ == "__main__":
    main() 