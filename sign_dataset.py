import pandas as pd
import hashlib

def generate_signature(entity, timestamp, value, secret_key, iterations=100000):
    message = f"{entity}|{timestamp}|{value}".encode()
    return hashlib.pbkdf2_hmac(
        "sha256",                # digest algorithm
        message,                 # data to hash
        secret_key.encode(),     # secret key
        iterations               # iteration count
    ).hex()

def main():
    dataset_path = "data/sample_sensor_data.xlsx"   # adjust path if needed
    df = pd.read_excel(dataset_path)

    secret_key = "sda_spring_2026_secure_key"

    df["Auth_Signature"] = df.apply(
        lambda row: generate_signature(
            row["Sensor_ID"],
            row["Timestamp"],
            row["Raw_Value"],
            secret_key
        ),
        axis=1
    )

    output_path = "data/signed_sensor_data.xlsx"
    df.to_excel(output_path, index=False)
    print(f"✅ Signed dataset saved to {output_path}")

if __name__ == "__main__":
    main()