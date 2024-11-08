# Apache Kafka Study Case

Anggota Kelompok:

| Nama                            | NRP        |
| ------------------------------- | ---------- |
| Samuel Yuma Krismata            | 5027221029 |
| Muhammad Harvian Dito Syahputra | 5027221039 |
| Naufan Zaki Luqmanulhakim       | 5027221065 |

# Requirement

Jalankan command berikut untuk melakukan instalasi requirement library python:

```bash
pip install -r requirements.txt
```

## Setup Apache Kafka dan Zookeeper

Instalasi dapat dilakukan dengan menggunakan file `docker-compose.yml` dengan konfigurasi sebagai berikut:

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

Gunakan command berikut untuk menjalankan container pada aplikasi Docker:

```bash
docker-compose up -d
```

### Membuat Topik Kafka

Untuk membuat topik baru, gunakan command berikut untuk masuk ke container kafka:

```bash
docker exec -it kafka bash
```

Selanjutnya, buat topik baru (nama topik bebas dan menyesuaikan) yang mana disini kami membuat topik dengan nama `kafka-server`:

```bash
kafka-topics.sh --create --topic kafka-server --bootstrap-server localhost:9092 --partitions 1 --replication-factor 1
```

Kemudian, jalankan command berikut untuk mengecek apakah topik `kafka-server` sudah terbuat atau belum:

```bash
kafka-topics.sh --list --bootstrap-server localhost:9092
```

## Setup Kafka Producer dan Consumer

**NB: Disarankan untuk menggunakan WSL**

Masuk ke folder `kafka` dan gunakan command berikut untuk menjalankan producer:

```bash
python3 kafka/kafka_producer.py
```

Buat terminal baru dan gunakan command berikut untuk menjalankan producer:

```bash
python3 kafka/kafka_consumer.py
```

Hasil output file batch akan muncul pada folder `batch` sesuai dengan jumlah data

## Spark ML Pipeline - Clustering Model

### Persiapan Environment

1. **Buat Virtual Environment** (opsional tetapi direkomendasikan):
    - Gunakan virtual environment untuk memastikan instalasi paket tidak mengganggu sistem Python.
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

### Menjalankan Training Model Spark ML

1. Pastikan data batch telah disimpan di folder `batch/` setelah menjalankan Kafka Consumer.
2. Script **`train_model.py`** yang ada di folder `spark_ml/` akan membaca setiap file batch, melakukan preprocessing, melatih model clustering, dan menyimpan model tersebut ke folder `models/`.

    **Jalankan perintah berikut untuk melatih model**:

    ```bash
    python3 spark_ml/train_model.py
    ```

3. Setiap model yang dilatih akan disimpan di folder `spark_ml/models/` dengan nama unik, misalnya `model_1`, `model_2`, dst., berdasarkan batch yang diproses.

## Endpoint API

Untuk dapat melakukan request dan response dengan api, jalankan command berikut:

```bash
python3 api/app.py
```

Aplikasi tersebut akan berjalan pada `localhost:5000` dan endpoint yang dapat diakses adalah `/...` dengan format request sebagai berikut:

```JSON
{
    ...
}
```

Contoh request:

```bash
...
```

Contoh response

```JSON
...
```
