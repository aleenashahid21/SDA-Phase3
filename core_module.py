import hashlib
import hmac
import time
import queue
from collections import defaultdict


class CoreModule:
    def __init__(self, config):
        self.stateless_cfg = config["processing"]["stateless_tasks"]
        self.stateful_cfg = config["processing"]["stateful_tasks"]

        # Cryptographic parameters
        self.secret_key = self.stateless_cfg["secret_key"]
        self.iterations = int(self.stateless_cfg.get("iterations", 100000))

        # Running‑average state
        self.running_sums = defaultdict(float)
        self.counts = defaultdict(int)
        self.window_size = self.stateful_cfg.get("running_average_window_size", 10)

    # ------------------------------------------------------------------
    # Verification identical to sign_dataset.py
    # ------------------------------------------------------------------
    def verify_signature(self, packet):
        """
        Verify authenticity using PBKDF2‑HMAC‑SHA256.
        The original generator hashed f"{entity}|{timestamp}|{value}" as password
        and used the secret key as the salt.
        """
        entity = packet["entity_name"]
        timestamp = packet["time_period"]
        value = packet["metric_value"]
        secret_key = self.secret_key

        message = f"{entity}|{timestamp}|{value}".encode()

        derived_hash = hashlib.pbkdf2_hmac(
            "sha256",
            password=message,             # same message string as generator
            salt=secret_key.encode(),     # secret key as salt
            iterations=self.iterations,
        ).hex()

        ok = hmac.compare_digest(derived_hash, packet["security_hash"])
        if ok:
            print("✅ Verified:", entity, timestamp, value)
        else:
            print("❌ Signature mismatch:", entity, timestamp, value)
        return ok

    # ------------------------------------------------------------------
    # Stateful running average
    # ------------------------------------------------------------------
    def compute_running_average(self, packet):
        sensor = packet["entity_name"]
        value = packet["metric_value"]

        self.running_sums[sensor] += value
        self.counts[sensor] += 1

        if self.window_size and self.counts[sensor] > self.window_size:
            self.running_sums[sensor] = value
            self.counts[sensor] = 1

        return self.running_sums[sensor] / self.counts[sensor]

    # ------------------------------------------------------------------
    # Continuous, non‑blocking processing loop
    # ------------------------------------------------------------------
    def run(self, raw_queue, processed_queue):
        print("CoreModule started.")
        while True:
            try:
                if raw_queue.empty():
                    time.sleep(0.05)
                    continue

                packet = raw_queue.get()

                # Stateless verification
                if self.stateless_cfg.get("operation") == "verify_signature":
                    if not self.verify_signature(packet):
                        continue

                # Stateful computation
                if self.stateful_cfg.get("operation") == "running_average":
                    packet["running_avg"] = self.compute_running_average(packet)

                # Safe enqueue
                try:
                    processed_queue.put(packet, timeout=1)
                except queue.Full:
                    print("⚠️ processed_queue full — dropping packet.")
                    continue

            except Exception as e:
                import traceback
                print("💥 CoreModule error:", e)
                traceback.print_exc()
                time.sleep(0.05)
