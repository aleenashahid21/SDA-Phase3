import hashlib
from typing import List, Tuple, Dict
from contracts import IStream
import time

class CoreLogic:
    @staticmethod
    def verify_signature(packet: Dict, secret_key: str, iterations: int) -> bool:
        raw_val = f"{float(packet.get('metric_value', 0)):.2f}".encode('utf-8')
        dk = hashlib.pbkdf2_hmac('sha256', secret_key.encode('utf-8'), raw_val, iterations)
        return dk.hex() == packet.get("security_hash")

    @staticmethod
    def calculate_average(history: List[float], new_val: float, window: int) -> Tuple[List[float], float]:
        new_history = (history + [new_val])[-window:]
        return new_history, sum(new_history) / len(new_history)

class ComputeWorker:
    @staticmethod
    def run(settings: Dict, raw_stream: IStream, proc_stream: IStream):
        key, iters = settings["secret_key"], settings["iterations"]
        while True:
            packet = raw_stream.get()
            if packet is None:
                proc_stream.put(None)
                break
            if CoreLogic.verify_signature(packet, key, iters):
                proc_stream.put(packet)

class AggregatorWorker:
    @staticmethod
    def run(window: int, proc_stream: IStream, final_stream: IStream):
        history = []
        while True:
            packet = proc_stream.get()
            time.sleep(0.2)
            if packet is None:
                final_stream.put(None)
                break
            history, avg = CoreLogic.calculate_average(history, packet["metric_value"], window)
            packet["computed_metric"] = avg
            final_stream.put(packet)
