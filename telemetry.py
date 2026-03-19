import time
import pandas as pd
import queue


class TelemetryStream:
    def __init__(self, config, raw_queue: queue.Queue):
        self.config = config
        self.raw_queue = raw_queue
        self.delay = config["pipeline_dynamics"]["input_delay_seconds"]
        self.max_size = config["pipeline_dynamics"]["stream_queue_max_size"]

        # Load dataset
        dataset_path = config["dataset_path"]
        self.df = pd.read_excel(dataset_path)

        # Schema mapping
        self.schema = config["schema_mapping"]["columns"]

    def stream(self):
        """Continuously stream packets into raw_queue with adaptive pacing."""
        print("Starting telemetry stream... Press Ctrl+C to stop.")
        try:
            for i, row in self.df.iterrows():
                packet = {}
                for col in self.schema:
                    source = col["source_name"]
                    internal = col["internal_mapping"]
                    dtype = col["data_type"]
                    val = row[source]

                    if dtype == "string":
                        packet[internal] = str(val)
                    elif dtype == "integer":
                        packet[internal] = int(val)
                    elif dtype == "float":
                        packet[internal] = float(val)
                    else:
                        packet[internal] = val

                # Adaptive backpressure
                if self.raw_queue.qsize() > self.max_size * 0.8:
                    print("Raw queue nearly full — taking a short pause.")
                    time.sleep(self.delay * 3)

                # Non‑blocking enqueue
                try:
                    self.raw_queue.put(packet, timeout=1)
                except queue.Full:
                    print("⚠️ raw_queue full — skipping packet.")
                    continue

                if i % 20 == 0:
                    print(f"Streamed {i} packets so far...")

                time.sleep(self.delay)

        except KeyboardInterrupt:
            print("\nTelemetry stream stopped by user.")
