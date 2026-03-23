import pandas as pd
import time
from typing import List, Dict, Any
from contracts import IStream

class InputWorker:
   
    @staticmethod
    def run(path: str, delay: float, schema: List[Dict], raw_stream: IStream):
        try:
            # 1. DYNAMIC LOADER: Handles both CSV and Excel based on extension
            if path.endswith(('.xlsx', '.xls')):
                df = pd.read_excel(path)
            else:
                df = pd.read_csv(path)

            #converts domain-specific columns to generic keys
            for _, row in df.iterrows():
                packet = {}
                for col in schema:
                    src = col["source_name"]
                    internal = col["internal_mapping"]
                    dtype = col["data_type"]
                    
                    val = row.get(src)
                    
                    #cast based on config.json
                    try:
                        if dtype == "float": 
                            packet[internal] = float(val)
                        elif dtype == "integer": 
                            packet[internal] = int(val)
                        else: 
                            packet[internal] = str(val)
                    except (ValueError, TypeError):
                        packet[internal] = None

                #backpressure is call will block if raw_stream is full
                raw_stream.put(packet)
                time.sleep(delay)
                
        except Exception as e:
            print(f"[!] Input Error: {e}")
        finally:
            #signal to the scatter pool that input has ended
            raw_stream.put(None)
