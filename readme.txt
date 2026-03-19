This is the file structure 
Phase-3/
├── config.json          # Configuration (algorithm, iterations, secret key, dataset path)
├── main.py              # Entry point: starts telemetry, core, and output modules
├── telemetry.py         # Streams packets from dataset into raw queue
├── core_module.py       # Verifies signatures, drops spoofed packets, computes averages
├── output_module.py     # Prints or saves processed packets
├── sign_dataset.py      # Utility script to regenerate valid signatures
├── data/
│   ├── sample_sensor_data.xlsx   # Original dataset
│   └── signed_sensor_data.xlsx   # Corrected dataset with valid signatures

