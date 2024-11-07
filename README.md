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
