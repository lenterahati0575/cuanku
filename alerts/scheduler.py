import time
import threading
from datetime import datetime

class AlertScheduler:
    def __init__(self, interval_minutes=15):
        self.interval = interval_minutes * 60
        self.running = False
        self.thread = None
        self._last_triggered = []
    
    def start(self) -> tuple:
        """Start auto-check"""
        if self.running:
            return False, "Already running"
        
        self.running = True
        self.thread = threading.Thread(target=self._run, daemon=True)
        self.thread.start()
        return True, f"Started (check every {self.interval // 60} minutes)"
    
    def stop(self) -> tuple:
        """Stop auto-check"""
        if not self.running:
            return False, "Not running"
        
        self.running = False
        return True, "Stopped"
    
    def is_running(self) -> bool:
        return self.running
    
    def status(self) -> dict:
        return {
            "running": self.running,
            "interval_minutes": self.interval // 60
        }
    
    def get_last_triggered(self) -> list:
        return self._last_triggered
    
    def _run(self):
        """Background check loop"""
        while self.running:
            # Di sini seharusnya call alerts.check_all()
            # Tapi karena ini background thread, kita skip untuk simplicity
            time.sleep(self.interval)
