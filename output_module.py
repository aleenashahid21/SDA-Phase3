import pandas as pd

class OutputModule:
    @staticmethod
    def run(config, processed_queue):
        output_mode = config["output"]["mode"]   # "print" or "excel"
        output_path = config["output"]["path"]   # path for Excel export

        results = []

        # Drain the processed queue
        while not processed_queue.empty():
            packet = processed_queue.get()
            results.append(packet)

        if not results:
            return  # nothing to output

        if output_mode == "print":
            for packet in results:
                print(f" Sensor: {packet['entity_name']}, "
                      f"Timestamp: {packet['time_period']}, "
                      f"Value: {packet['metric_value']}, "
                      f"Running Avg: {packet.get('running_avg', 'N/A')}")
        
        elif output_mode == "excel":
            df = pd.DataFrame(results)
            df.to_excel(output_path, index=False)
            print(f" Output saved to {output_path}")