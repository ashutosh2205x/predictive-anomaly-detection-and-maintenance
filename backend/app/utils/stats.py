mean_temp = None
std_temp = None
mean_pressure = None
std_pressure = None
mean_vibration = None
std_vibration = None


def update_stats(df):
    global mean_temp, std_temp

    mean_temp = df["temperature"].mean()
    std_temp = df["temperature"].std()
    mean_pressure = df["pressure"].mean()
    std_pressure = df["pressure"].std()
    mean_vibration = df["vibration"].mean()
    std_vibration = df["vibration"].std()


def compute_z(temp):
    if std_temp == 0 or std_temp is None:
        return 0.0
    return (temp - mean_temp) / std_temp