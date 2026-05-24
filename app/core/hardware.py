import psutil
import subprocess

class HardwareManager:
    @staticmethod
    def get_capabilities():
        capabilities = {
            "cpu_cores": psutil.cpu_count(logical=True),
            "ram_gb": round(psutil.virtual_memory().total / (1024**3), 2),
            "has_nvidia_gpu": False,
            "vram_gb": 0,
            "optimal_provider": "google_ai"
        }
        try:
            nvidia_smi = subprocess.check_output(["nvidia-smi", "--query-gpu=memory.total", "--format=csv,noheader,nounits"], encoding='utf-8')
            capabilities["has_nvidia_gpu"] = True
            capabilities["vram_gb"] = int(nvidia_smi.strip()) / 1024
            if capabilities["vram_gb"] >= 8: capabilities["optimal_provider"] = "ollama"
        except: pass
        return capabilities
