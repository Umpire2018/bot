import psutil
import os

def monitor_memory():
    process = psutil.Process(os.getpid())
    memory = process.memory_info()
    
    mem_used = memory.rss / 1024 / 1024
    
    return mem_used


