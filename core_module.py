import hashlib
import hmac
from collections import defaultdict

class CoreModule:
    def __init__(self, config):
        # Read processing config
        self.stateless_cfg = config["processing"]["stateless_tasks"]
        self.stateful_cfg = config["processing"]["stateful_tasks"]

        # Secret key for signature verification
        self.secret_key = self.stateless_cfg["secret_key"].encode()

        # Stateful tracking
        self.running_sums = defaultdict(float)
        self.counts = defaultdict(int)
        self.window_size = self.stateful_cfg.get("running_average_window_size", None)

    def verify_signature(self, packet):
        """
        Stateless task: Verify authenticity using PBKDF2 HMAC.
        """
        entity = packet["entity_name"].encode()
        timestamp = str(packet["time_period"]).encode()
        metric = str(packet["metric_value"]).encode()

        message = entity + b"|" + timestamp + b"|" + metric

        expected_hash = hashlib.pbkdf2_hmac(
            self.stateless_cfg["algorithm"],
            message,
            self.secret_key,
            self.stateless_cfg["iterations"]
        ).hex()

        return hmac.compare_digest(expected_hash, packet["security_hash"])

    def compute_running_average(self, packet):
        """
        Stateful task: Maintain running average per sensor.
        Supports optional window size.
        """
        sensor = packet["entity_name"]
        value = packet["metric_value"]

        self.running_sums[sensor] += value
        self.counts[sensor] += 1

        if self.window_size:
            # Sliding window approximation: reset after window size
            if self.counts[sensor] > self.window_size:
                self.running_sums[sensor] = value
                self.counts[sensor] = 1

        return self.running_sums[sensor] / self.counts[sensor]

    def run(self, raw_queue, processed_queue):
        """
        Main loop: verify, compute average, forward authentic packets.
        """
        while not raw_queue.empty():
            packet = raw_queue.get()

            # Stateless task
            if self.stateless_cfg["operation"] == "verify_signature":
                if not self.verify_signature(packet):
                    print(f"❌ Dropped spoofed packet: {packet}")
                    continue

            # Stateful task
            if self.stateful_cfg["operation"] == "running_average":
                avg = self.compute_running_average(packet)
                packet["running_avg"] = avg

            processed_queue.put(packet)