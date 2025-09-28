import psutil
import xgboost as xgb
import numpy as np

class MonitorAgent:
def init(self):
self.thresholds = {"cpu": 80, "memory": 80, "disk": 90}
self.model = xgb.XGBClassifier() # For anomaly detection

def check_health(self):
    try:
        cpu = psutil.cpu_percent()
        memory = psutil.virtual_memory().percent
        disk = psutil.disk_usage("/").percent
        details = {"cpu": cpu, "memory": memory, "disk": disk}
        if any(details[k] > self.thresholds[k] for k in self.thresholds):
            orchestrator.log_action("monitor_alert", "warning", details)
            return {"status": "warning", "details": details}
        return {"status": "healthy", "details": details}
    except Exception as e:
        return {"status": "error", "error": str(e)}
