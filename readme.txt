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

SECRET_KEY = "sda_spring_2026_secure_key"
ITERATIONS = 100000
raw_value = sensor data rounded to two decimal places

def generate_signature(raw_value_str: str, key: str, iterations: int) -> str:
    """
    Generates a PBKDF2 HMAC SHA-256 signature for the given value.
    Treats the secret key as the password and the raw value as the salt.
    """
    password_bytes = key.encode('utf-8')
    salt_bytes = raw_value_str.encode('utf-8')
    
    # Generate the hash
    hash_bytes = hashlib.pbkdf2_hmac(
        hash_name='sha256', 
        password=password_bytes, 
        salt=salt_bytes, 
        iterations=iterations
    )
    return hash_bytes.hex()
