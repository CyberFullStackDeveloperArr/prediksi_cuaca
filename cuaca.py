import xml.etree.ElementTree as ET
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter
from scipy.interpolate import interp1d

# Membaca file XML
tree = ET.parse('data.xml')
root = tree.getroot()

# Fungsi untuk mengambil data parameter dari XML
def ambil_data_parameter(tempat, parameter_id):
    datetime_values = []
    parameter_values = []

    for area in root.findall(".//area"):
        description = area.attrib['description']
        if tempat.lower() in description.lower():
            for param_elem in area.findall("parameter"):
                if param_elem.attrib['id'] == parameter_id:
                    for timerange in param_elem.findall("timerange"):
                        datetime = timerange.attrib['datetime']
                        value = float(timerange.find("value").text)
                        
                        datetime_values.append(datetime)
                        parameter_values.append(value)
    
    return datetime_values, parameter_values

# Fungsi untuk menampilkan grafik cuaca berdasarkan tempat yang diinput pengguna
def tampilkan_grafik_cuaca(tempat):
    # Mengambil data untuk masing-masing parameter
    datetime_temp, temp_values = ambil_data_parameter(tempat, "t")  # Temperature
    datetime_hu, hum_values = ambil_data_parameter(tempat, "hu")   # Humidity
    datetime_ws, ws_values = ambil_data_parameter(tempat, "ws")    # Wind speed

    # Konversi ke dalam DataFrame untuk mempermudah plot
    data = {
        'Datetime': datetime_temp,
        'Temperature (°C)': temp_values,
        'Humidity (%)': hum_values,
        'Wind Speed (knots)': ws_values
    }
    weather_df = pd.DataFrame(data)
    weather_df['Datetime'] = pd.to_datetime(weather_df['Datetime'])

    # Plotting menggunakan Matplotlib
    fig, axes = plt.subplots(nrows=3, figsize=(12, 12), sharex=True)

    axes[0].plot(weather_df['Datetime'], weather_df['Temperature (°C)'], marker='o', linestyle='-', color='b')
    axes[0].set_title(f"Temperature in {tempat}", fontsize=14)
    axes[0].set_ylabel('Temperature (°C)')
    axes[0].grid(True, linestyle='--', alpha=0.7)
    axes[0].xaxis.set_major_formatter(DateFormatter('%Y-%m-%d %H:%M'))

    axes[1].plot(weather_df['Datetime'], weather_df['Humidity (%)'], marker='o', linestyle='--', color='g')
    axes[1].set_title(f"Humidity in {tempat}", fontsize=14)
    axes[1].set_ylabel('Humidity (%)')
    axes[1].grid(True, linestyle='--', alpha=0.7)
    axes[1].xaxis.set_major_formatter(DateFormatter('%Y-%m-%d %H:%M'))

    axes[2].plot(weather_df['Datetime'], weather_df['Wind Speed (knots)'], marker='o', linestyle='-.', color='r')
    axes[2].set_title(f"Wind Speed in {tempat}", fontsize=14)
    axes[2].set_ylabel('Wind Speed (knots)')
    axes[2].grid(True, linestyle='--', alpha=0.7)
    axes[2].xaxis.set_major_formatter(DateFormatter('%Y-%m-%d %H:%M'))

    # Penyesuaian tambahan untuk tampilan grafik
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.subplots_adjust(hspace=0.4)  # Menambahkan ruang vertikal antara subplot
    plt.show()

def prediksi_cuaca_1_hari_ke_depan(tempat):
    # Mengambil data temperatur, kelembaban, dan kecepatan angin untuk interpolasi
    datetime_temp, temp_values = ambil_data_parameter(tempat, "t")
    datetime_hu, hum_values = ambil_data_parameter(tempat, "hu")
    datetime_ws, ws_values = ambil_data_parameter(tempat, "ws")

    # Konversi datetime menjadi waktu dalam satuan jam
    times_temp = pd.to_datetime(datetime_temp)
    times_hum = pd.to_datetime(datetime_hu)
    times_ws = pd.to_datetime(datetime_ws)
    
    times_temp_start = times_temp[0]  # Waktu awal dalam Timestamp

    # Hitung selisih waktu dalam satuan jam dari waktu awal
    hours_since_start = (times_temp - times_temp_start) / pd.Timedelta(hours=1)

    # Fungsi interpolasi untuk temperatur, kelembaban, dan kecepatan angin
    interpolate_temp = interp1d(hours_since_start, temp_values, kind='linear', fill_value="extrapolate")
    interpolate_hum = interp1d(hours_since_start, hum_values, kind='linear', fill_value="extrapolate")
    interpolate_ws = interp1d(hours_since_start, ws_values, kind='linear', fill_value="extrapolate")

    # Waktu saat ini dalam bentuk Timestamp
    current_time = pd.Timestamp.now()

    # Prediksi cuaca 1 jam ke depan
    prediction_time = current_time + pd.Timedelta(hours=1)

    # Hitung waktu prediksi dalam satuan jam sejak waktu awal
    hours_prediction = (prediction_time - times_temp_start) / pd.Timedelta(hours=1)

    # Prediksi temperatur, kelembaban, dan kecepatan angin pada waktu prediksi
    predicted_temp = interpolate_temp(hours_prediction)
    predicted_hum = interpolate_hum(hours_prediction)
    predicted_ws = interpolate_ws(hours_prediction)

    # Kategori prediksi cuaca berdasarkan temperatur, kelembaban, dan kecepatan angin
    if predicted_temp < 20 and predicted_hum > 80 and predicted_ws < 10:
        kategori_cuaca = 3  # Berawan / Mostly Cloudy
    elif predicted_temp >= 20 and predicted_temp < 30 and predicted_hum > 60 and predicted_ws < 15:
        kategori_cuaca = 1  # Cerah Berawan / Partly Cloudy
    elif predicted_temp >= 20 and predicted_temp < 30 and predicted_hum > 70 and predicted_ws < 20:
        kategori_cuaca = 60  # Hujan Ringan / Light Rain
    elif predicted_temp >= 25 and predicted_temp < 35 and predicted_hum > 80 and predicted_ws < 25:
        kategori_cuaca = 61  # Hujan Sedang / Rain
    else:
        kategori_cuaca = 63  # Hujan Lebat / Heavy Rain

    # Output prediksi
    print(f"Prediksi temperatur pada {prediction_time} di {tempat}: {predicted_temp:.2f} °C")
    print(f"Prediksi kelembaban pada {prediction_time} di {tempat}: {predicted_hum:.2f} %")
    print(f"Prediksi kecepatan angin pada {prediction_time} di {tempat}: {predicted_ws:.2f} knots")
    print(f"Kategori cuaca pada {prediction_time}: {kategori_cuaca} - {keterangan_cuaca(kategori_cuaca)}")


# Fungsi untuk memberikan keterangan cuaca berdasarkan kode cuaca
def keterangan_cuaca(kode_cuaca):
    cuaca_dict = {
        0: "Cerah / Clear Skies",
        1: "Cerah Berawan / Partly Cloudy",
        2: "Cerah Berawan / Partly Cloudy",
        3: "Berawan / Mostly Cloudy",
        4: "Berawan Tebal / Overcast",
        5: "Udara Kabur / Haze",
        10: "Asap / Smoke",
        45: "Kabut / Fog",
        60: "Hujan Ringan / Light Rain",
        61: "Hujan Sedang / Rain",
        63: "Hujan Lebat / Heavy Rain",
        80: "Hujan Lokal / Isolated Shower",
        95: "Hujan Petir / Severe Thunderstorm",
        97: "Hujan Petir / Severe Thunderstorm"
    }
    return cuaca_dict.get(kode_cuaca, "Unknown")

# Fungsi untuk menampilkan daftar kota yang tersedia
def tampilkan_daftar_kota():
    kota_set = set()
    for area in root.findall(".//area"):
        description = area.attrib['description']
        kota_set.add(description)
    
    kota_list = sorted(kota_set)
    
    print("Daftar kota yang tersedia:")
    max_len = max(len(kota_list[i]) for i in range(0, len(kota_list), 2))
    for i in range(0, len(kota_list), 2):
        if i + 1 < len(kota_list):
            print(f"{i+1}. {kota_list[i]:<{max_len}}  {i+2}. {kota_list[i+1]}")
        else:
            print(f"{i+1}. {kota_list[i]}")

# Tampilkan daftar kota yang tersedia
tampilkan_daftar_kota()

# Input dari pengguna
tempat_input = input("Masukkan nama tempat yang ingin dilihat cuacanya (pilih nomor kota): ")

# Cek apakah input pengguna valid
kota_list = sorted(set(area.attrib['description'] for area in root.findall(".//area")))

try:
    tempat_input = kota_list[int(tempat_input) - 1]
except (ValueError, IndexError):
    print("Input tidak valid. Silakan masukkan nomor kota yang sesuai.")
    exit()

# Tampilkan grafik cuaca
tampilkan_grafik_cuaca(tempat_input)

# Lakukan prediksi cuaca 1 jam ke depan
prediksi_cuaca_1_hari_ke_depan(tempat_input)

