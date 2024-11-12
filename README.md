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
docker-compose up --build
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
python3 kafka_producer.py
```

Buat terminal baru dan gunakan command berikut untuk menjalankan producer:

```bash
python3 kafka_consumer.py
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

## Setup dan Cara Mengakses API

Untuk dapat melakukan request dan response dengan api, jalankan command berikut:

```bash
python3 api/app.py
```

Aplikasi tersebut akan berjalan pada `localhost:5000` dan berikut adalah endpoint yang dapat diakses:

### Endpoint `/predict-model/<model_id>`

- Digunakan untuk memprediksi `loan_status` berdasarkan payload yang dikirim menggunakan `<model_id>` yang dipilih 

- `model_id` tersedia dari 1-3 (karena ada 3 model yang dilatih)

- Contoh request menggunakan `curl`:

	```bash
	curl -X POST http://localhost:5000/predict-model/3  \
	-H "Content-Type: application/json"               \
	-d '{
			"person_age": 42,
			"person_income": 60000,
			"person_emp_exp": 12,
			"loan_amnt": 4000,
			"loan_int_rate": 0.10,
			"loan_percent_income": 0.3,
			"cb_person_cred_hist_length": 20,
			"credit_score": 750,
			"person_gender_index": 1,
			"person_education_index": 2,
			"person_home_ownership_index": 1,
			"loan_intent_index": 1
		}'
	```

- Contoh response:

	```JSON
	{
		"loan_status": 1,
		"model": 3
	}
	```

### Endpoint `/history`

- Digunakan untuk melihat riwayat payload serta hasil prediksi yang telah dilakukan sebelumnya

- Contoh request menggunakan `curl`:

```bash
curl -X GET http://localhost:5000/history 
```

- Contoh response:

```bash
[
  {
    "input": {
      "cb_person_cred_hist_length": 20,
      "credit_score": 750,
      "loan_amnt": 4000,
      "loan_int_rate": 0.1,
      "loan_intent_index": 1,
      "loan_percent_income": 0.3,
      "person_age": 42,
      "person_education_index": 2,
      "person_emp_exp": 12,
      "person_gender_index": 1,
      "person_home_ownership_index": 1,
      "person_income": 60000
    },
    "model_id": "3",
    "prediction": 0
  }
]
```

### Endpoint `/batch-predict/<model_id>`

- Digunakan untuk memprediksi beberapa `loan_status` berdasarkan beberapa payload yang dikirim dalam bentuk array `[]` menggunakan `<model_id>` yang dipilih

- `model_id` tersedia dari 1-3 (karena ada 3 model yang dilatih)

- Contoh request menggunakan `curl`:

```bash
curl -X POST http://localhost:5000/batch-predict/1 \
    -H "Content-Type: application/json" \
    -d '{
          "data": [
              {
                  "person_age": 25,
                  "person_income": 30000,
                  "person_emp_exp": 2,
                  "loan_amnt": 2000,
                  "loan_int_rate": 0.05,
                  "loan_percent_income": 0.1,
                  "cb_person_cred_hist_length": 10,
                  "credit_score": 600,
                  "person_gender_index": 1,
                  "person_education_index": 1,
                  "person_home_ownership_index": 1,
                  "loan_intent_index": 1
              },
              {
                  "person_age": 35,
                  "person_income": 50000,
                  "person_emp_exp": 7,
                  "loan_amnt": 5000,
                  "loan_int_rate": 0.2,
                  "loan_percent_income": 0.2,
                  "cb_person_cred_hist_length": 12,
                  "credit_score": 650,
                  "person_gender_index": 0,
                  "person_education_index": 2,
                  "person_home_ownership_index": 0,
                  "loan_intent_index": 2
              }
          ]
        }'
```

- Contoh response:

```bash
{
  "model": "1",
  "predictions": [
    {
      "input": {
        "cb_person_cred_hist_length": 10,
        "credit_score": 600,
        "loan_amnt": 2000,
        "loan_int_rate": 0.05,
        "loan_intent_index": 1,
        "loan_percent_income": 0.1,
        "person_age": 25,
        "person_education_index": 1,
        "person_emp_exp": 2,
        "person_gender_index": 1,
        "person_home_ownership_index": 1,
        "person_income": 30000,
      },
      "loan_status": 1
    },
    {
      "input": {
        "cb_person_cred_hist_length": 12,
        "credit_score": 650,
        "loan_amnt": 5000,
        "loan_int_rate": 0.2,
        "loan_intent_index": 2,
        "loan_percent_income": 0.2,
        "person_age": 35,
        "person_education_index": 2,
        "person_emp_exp": 7,
        "person_gender_index": 0,
        "person_home_ownership_index": 0,
        "person_income": 50000
      },
      "loan_status": 0
    }
  ]
}
```