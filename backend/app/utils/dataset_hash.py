import hashlib

def generate_dataset_hash(df):
    df_sorted = df.sort_values(by=["timestamp"])

    data_str = df_sorted.to_json()

    return hashlib.md5(data_str.encode()).hexdigest()