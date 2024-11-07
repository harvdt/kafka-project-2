# Apache Kafka Study Case

Kelompok:

- Samuel Yuma Krismata (5027221029)
- Muhammad Harvian Dito Syahputra (5027221039)
- Naufan Zaki Luqmanulhakim (5027221065)

# Requirement

Jalankan command berikut untuk install requirement library python

```bash
pip install -r requirements.txt
```

## Setup Apache Kafka dan Zookeeper

Installasi Apache Kafka dan Zookeeper dilakukan dengan menggunakan docker. Berikut file `docker-compose.yaml`.

```yaml
services:
  zookeeper:
    image: "bitnami/zookeeper:latest"
    container_name: zookeeper
    environment:
      - ALLOW_ANONYMOUS_LOGIN=yes
    ports:
      - "2181:2181"

  kafka:
    image: "bitnami/kafka:latest"
    container_name: kafka
    environment:
      - KAFKA_BROKER_ID=1
      - KAFKA_ZOOKEEPER_CONNECT=zookeeper:2181
      - ALLOW_PLAINTEXT_LISTENER=yes
      - KAFKA_LISTENERS=PLAINTEXT://:9092
      - KAFKA_ADVERTISED_LISTENERS=PLAINTEXT://localhost:9092
    ports:
      - "9092:9092"
    depends_on:
      - zookeeper
```

Langkah pertama adalah menjalankan command berikut untuk melakukan build docker

```bash
docker-compose up --build
```

Setelah docker container berhasil dibuat, maka langkah selanjutnya adalah membuat topic kafka

## Membuat Topik Kafka

Untuk membuat topic, bisa menggunakan command berikut untuk masuk ke container kafka

```bash
docker exec -it kafka bash
```

Setelah masuk ke dalam container kafka, maka langkah selanjutnya adalah membuat topic. Nama topic bebas dan menyesuaikan, di sini kami menggunakan topic dengan nama 'kafka-server'

```bash
kafka-topics.sh --create --topic kafka-server --bootstrap-server localhost:9092 --partitions 1 --replication-factor 1
```

Kemudian dapat melakukan command berikut untuk check apakah topic sudah terbuat atau belum

```bash
kafka-topics.sh --list --bootstrap-server localhost:9092
```

Jika topic sudah terbuat, maka seharusnya akan muncul nama topic

## Menjalankan Kafka Producer dan Consumer

**Disarankan menggunakan WSL**
Masuk ke folder Kafka. Kemudian menjalankan program producer

```bash
python3 kafka_producer.py
```

Menjalankan program consumer di terminal lain

```bash
python3 kafka_consumer.py
```

Hasil output file batch akan muncul pada folder Batch sesuai dengan jumlah data

Berikut ini adalah lanjutan dokumentasi untuk bagian Spark ML dan petunjuk bagi teman Anda yang bertugas membuat API. Dokumentasi ini juga akan membantu pengguna yang ingin clone dan menjalankan keseluruhan proyek ini.

---

## Spark ML Pipeline - Clustering Model

Bagian ini berfokus pada pemrosesan data menggunakan Spark ML untuk melatih model clustering (contohnya KMeans) berdasarkan data batch yang disimpan dari Kafka Consumer. Model ini akan disimpan dan kemudian diakses oleh API untuk melayani permintaan pengguna.

### Persiapan Lingkungan

1. **Buat Virtual Environment** (opsional tetapi direkomendasikan):
   - Gunakan virtual environment untuk memastikan instalasi paket tidak mengganggu sistem Python.
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```


### Menjalankan Training Model Spark ML

1. Pastikan data batch telah disimpan di folder `Batch/` setelah menjalankan Kafka Consumer.
2. Skrip **`train_model.py`** yang ada di folder `spark_ml/` akan membaca setiap file batch, melakukan preprocessing, melatih model clustering, dan menyimpan model tersebut ke folder `models/`.

   **Jalankan perintah berikut untuk melatih model**:
   ```bash
   python3 spark_ml/train_model.py
   ```

3. Setiap model yang dilatih akan disimpan di folder `spark_ml/models/` dengan nama unik, misalnya `model_1`, `model_2`, dst., berdasarkan batch yang diproses.

4. Setelah skrip ini selesai, model siap digunakan oleh API.

### Struktur Folder untuk Spark ML (ini dibikinin sama GPT yum, buat bantu kamu aja supaya lebih ngerti sama modelnya. kalo dah kelar apus aja wkwkwkw)

```
kafka-project-2/
├── Batch/                  # Folder untuk file batch dari Kafka Consumer
├── Kafka/                  # Folder untuk skrip Kafka Producer dan Consumer
├── spark_ml/               # Folder untuk komponen Spark ML
│   ├── models/             # Folder untuk menyimpan model yang telah dilatih
│   ├── train_model.py      # Skrip utama untuk pelatihan model
│   └── requirements.txt    # Dependensi untuk Spark ML
```

## Petunjuk untuk Tim API

Bagian ini berisi instruksi untuk anggota tim yang bertanggung jawab pada bagian API. API ini akan digunakan untuk mengakses model clustering yang telah dilatih agar pengguna bisa mendapatkan hasil clustering atau rekomendasi berdasarkan data mereka.

### Membuat API untuk Mengakses Model

1. **Framework API**: Disarankan menggunakan Flask atau FastAPI untuk membuat API. Berikut adalah contoh sederhana menggunakan Flask.

2. **Struktur Folder API**:
   - Buat folder `api/` di dalam `kafka-project-2/` untuk menyimpan file API, misalnya `app.py` sebagai server utama dan subfolder `endpoints/` jika diperlukan untuk endpoint spesifik.

   ```plaintext
   kafka-project-2/
   ├── api/
   │   ├── app.py            # Skrip utama untuk API server
   │   └── endpoints/
   │       ├── clustering.py # Contoh endpoint untuk clustering
   ```

3. **Contoh Skrip API `app.py`**:

   Berikut adalah contoh skrip `app.py` untuk membuat endpoint clustering menggunakan Flask. Endpoint ini akan memuat model dari folder `models/` dan memberikan hasil clustering.

   ```python
   from flask import Flask, request, jsonify
   from pyspark.ml.clustering import KMeansModel
   from pyspark.ml.linalg import Vectors
   import os

   app = Flask(__name__)

   # Path ke folder model
   MODEL_PATH = "spark_ml/models/"

   # Fungsi untuk memuat model dari folder
   def load_model(model_name):
       model_path = os.path.join(MODEL_PATH, model_name)
       return KMeansModel.load(model_path)

   # Endpoint untuk clustering
   @app.route("/clustering", methods=["POST"])
   def clustering():
       # Ambil data input dari request JSON
       data = request.json
       input_vector = Vectors.dense(data["features"])  # Contoh input features

       # Muat model terbaru (misalnya model terakhir)
       model_name = "model_3"  # Ganti sesuai kebutuhan
       model = load_model(model_name)

       # Prediksi cluster
       prediction = model.predict(input_vector)
       return jsonify({"cluster": int(prediction)})

   if __name__ == "__main__":
       app.run(debug=True)
   ```

4. **Menjalankan API**:
   - Jalankan API menggunakan perintah berikut:
   ```bash
   python api/app.py
   ```
   - API akan berjalan di `localhost:5000`, dan Anda bisa mengakses endpoint `/clustering` dengan mengirim data fitur dalam format JSON.

5. **Contoh Request untuk Endpoint Clustering**:
   - Berikut adalah contoh untuk mengirim request menggunakan `curl` atau Postman:

   ```bash
   curl -X POST http://localhost:5000/clustering -H "Content-Type: application/json" -d '{"features": [22.0, 71948.0, 0, 35000.0, 16.02, 0.49, 3.0, 561, 0, 1, 0, 1]}'
   ```

   - Output akan berupa JSON yang menunjukkan cluster di mana data input diklasifikasikan:
     ```json
     {
       "cluster": 1
     }
     ```

### Petunjuk untuk Clone dan Menjalankan Project

Berikut adalah langkah-langkah untuk menjalankan keseluruhan proyek dari awal:

1. **Clone Repository**:
   ```bash
   git clone https://github.com/harvdt/kafka-project-2.git
   cd kafka-project-2
   ```

2. **Setup Docker untuk Kafka dan Zookeeper**:
   - Jalankan perintah berikut untuk memulai layanan Kafka dan Zookeeper:
   ```bash
   docker-compose up --build
   ```

3. **Membuat Kafka Topic**:
   - Buat topic Kafka dengan masuk ke container dan jalankan perintah yang sesuai (lihat instruksi di atas).

4. **Jalankan Kafka Producer dan Consumer**:
   - Jalankan `kafka_producer.py` dan `kafka_consumer.py` untuk mulai mengirim dan menerima data.

5. **Jalankan Skrip Spark ML untuk Melatih Model**:
   - Setelah data batch tersedia di folder `Batch/`, jalankan skrip berikut untuk melatih model clustering:
   ```bash
   python3 spark_ml/train_model.py
   ```

6. **Jalankan API**:
   - Setelah model tersedia di folder `models/`, jalankan API dengan:
   ```bash
   python api/app.py
   ```

7. **Mengakses API**:
   - Kirim request ke API menggunakan Postman atau `curl` untuk mendapatkan hasil clustering.

Dengan mengikuti dokumentasi ini, pengguna bisa mengimplementasikan Kafka, Spark ML, dan API secara terintegrasi dalam proyek ini. Jika ada pertanyaan, silakan tanyakan kepada anggota tim terkait.
