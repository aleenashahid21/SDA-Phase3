import time
import pandas as pd
import queue

class TelemetryStream:
    def __init__(self, config, raw_queue: queue.Queue):
        self.config = config
        self.raw_queue = raw_queue
        self.delay = config["pipeline_dynamics"]["input_delay_seconds"]

        # Load dataset
        dataset_path = config["dataset_path"]
        self.df = pd.read_excel(dataset_path)

        # Schema mapping
        self.schema = config["schema_mapping"]["columns"]

    def stream(self):
        """
        Continuously stream packets into raw_queue with delay.
        Stop manually with Ctrl+C.
        """
        print(" Starting telemetry stream... Press Ctrl+C to stop.")
        try:
            for _, row in self.df.iterrows():
                packet = {}
                for col in self.schema:
                    source = col["source_name"]
                    internal = col["internal_mapping"]
                    dtype = col["data_type"]

                    if dtype == "string":
                        packet[internal] = str(row[source])
                    elif dtype == "integer":
                        packet[internal] = int(row[source])
                    elif dtype == "float":
                        packet[internal] = float(row[source])
                    else:
                        packet[internal] = row[source]

                # Push packet into queue
                self.raw_queue.put(packet)
                print(f" Streamed packet: {packet}")

                # Delay between packets
                time.sleep(self.delay)

        except KeyboardInterrupt:
            print("\n Telemetry stream stopped by user.")