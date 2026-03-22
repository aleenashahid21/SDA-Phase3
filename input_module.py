import time
import pandas as pd

class InputModule:
    @staticmethod
    def run(config, raw_queue):
        dataset_path = config["dataset_path"]
        delay = config["pipeline_dynamics"]["input_delay_seconds"]
        schema = config["schema_mapping"]["columns"]
        try:
            #detects extension and picks the right function
            if path.endswith('.xlsx') or path.endswith('.xls'):
                df = pd.read_excel(path)
            else:
                df = pd.read_csv(path)

            #iterate through rows and apply your generic mapping
            for _, row in df.iterrows():
                packet = {}
                for col in schema:
                    src, internal, dtype = col["source_name"], col["internal_mapping"], col["data_type"]
                    val = row.get(src)
                    
                    #casting to correct primitive types
                    try:
                        if dtype == "float": packet[internal] = float(val)
                        elif dtype == "integer": packet[internal] = int(val)
                        else: packet[internal] = str(val)
                    except:
                        packet[internal] = None

                raw_stream.put(packet)
                time.sleep(delay)
                
        except Exception as e:
            print(f"Input Error: {e}")
        finally:
            raw_stream.put(None)



       
