import time
import pandas as pd

class InputModule:
    @staticmethod
    def run(config, raw_queue):
        dataset_path = config["dataset_path"]
        delay = config["pipeline_dynamics"]["input_delay_seconds"]
        schema = config["schema_mapping"]["columns"]

        # Load dataset
        df = pd.read_excel(dataset_path)

        print("📥 Input Module: Reading packets from dataset...")

        for _, row in df.iterrows():
            packet = {}

            # Apply schema mapping
            for col in schema:
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
            raw_queue.put(packet)
            print(f"➡️ Input Module queued packet: {packet}")

            # Delay between packets (simulates telemetry)
            time.sleep(delay)

        print("✅ Input Module finished reading dataset.")