import hashlib
import multiprocessing
import time

class ComputeWorker:
    """
    Stateless Parallelism: Authenticates packets.
    Matches the README and CSV format exactly.
    """
    @staticmethod
    def run(config, raw_stream, processed_stream):
        settings = config["processing"]["stateless_tasks"]
        secret_key = settings["secret_key"]
        iterations = settings["iterations"]

        while True:
            packet = raw_stream.get()
            if packet is None:
                processed_stream.put(None)
                break

            # 1. Prepare Salt (Must match CSV string exactly)
            # Using :.2f ensures 44.3 in Python matches "44.30" in your CSV
            raw_val = packet.get("metric_value", 0.0)
            salt_str = f"{float(raw_val):.2f}"
            
            expected_hash = packet.get("security_hash", "")

            # 2. Compute PBKDF2 (Key=Password, Value=Salt)
            dk = hashlib.pbkdf2_hmac(
                'sha256', 
                password=secret_key.encode('utf-8'), 
                salt=salt_str.encode('utf-8'), 
                iterations=iterations
            )
            generated_hash = dk.hex()

            # 3. Verification
            if generated_hash == expected_hash:
                # Authentic data moves to the "Core Queue"
                processed_stream.put(packet)
            else:
                # Tampered data is dropped (This satisfies the security requirement)
                print(f"[-] SECURITY ALERT: Dropped spoofed packet from {packet.get('entity_name')}")

class AggregatorWorker:
    """
    Stateful Aggregator: 
    Calculates the running average for the Red Line on your graph.
    """
    @staticmethod
    def run(config, processed_stream, final_output_stream):
        window = config["processing"]["stateful_tasks"]["running_average_window_size"]
        history = []

        while True:
            packet = processed_stream.get()
            time.sleep(0.1)
            if packet is None:
                final_output_stream.put(None)
                break

            # Functional Core: Pure state transformation
            history, avg = AggregatorWorker._pure_average(history, packet["metric_value"], window)
            
            packet["computed_metric"] = avg
            final_output_stream.put(packet)

    @staticmethod
    def _pure_average(history, new_val, window):
        new_history = (history + [new_val])[-window:]
        return new_history, sum(new_history) / len(new_history)
