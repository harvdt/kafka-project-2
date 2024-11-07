from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.ml.feature import VectorAssembler, StringIndexer
from pyspark.ml.clustering import KMeans
import os
import time

spark = SparkSession.builder \
    .appName("KafkaSparkML") \
    .getOrCreate()

current_dir = os.path.dirname(os.path.abspath(__file__))
batch_folder_path = os.path.join(current_dir, "../Batch")
model_save_path = os.path.join(current_dir, "models")

# load dan preprocessing
def load_and_preprocess_data(batch_file_path):
    # Membaca file batch
    df = spark.read.csv(batch_file_path, header=True, inferSchema=True)
    
    # Melakukan encoding pada kolom kategorikal
    categorical_columns = ['person_gender', 'person_education', 'person_home_ownership', 'loan_intent']
    indexers = [StringIndexer(inputCol=col, outputCol=col+"_index").fit(df) for col in categorical_columns]
    
    for indexer in indexers:
        df = indexer.transform(df)

    # Menghapus kolom asli setelah encoding
    df = df.drop(*categorical_columns)
    
    # Menentukan kolom fitur untuk vektorisasi
    feature_columns = [
        'person_age', 'person_income', 'person_emp_exp', 'loan_amnt', 
        'loan_int_rate', 'loan_percent_income', 'cb_person_cred_hist_length', 
        'credit_score', 'person_gender_index', 'person_education_index', 
        'person_home_ownership_index', 'loan_intent_index'
    ]
    
    # Menggabungkan fitur ke dalam satu kolom vektor
    assembler = VectorAssembler(inputCols=feature_columns, outputCol='features')
    df = assembler.transform(df)
    
    # Memilih kolom 'features' saja untuk pemodelan
    df = df.select('features')
    return df

# training dan save model
def train_and_save_model(df, model_name):
    # Mendefinisikan dan melatih model KMeans
    kmeans = KMeans(k=3, seed=1)
    model = kmeans.fit(df)
    
    # Simpan model
    model_dir = os.path.join(model_save_path, model_name)
    model.write().overwrite().save(model_dir)
    print(f"Model disimpan di {model_dir}")

# Fungsi untuk memproses setiap file batch
def process_batches():
    batch_files = sorted(os.listdir(batch_folder_path))
    batch_count = 0
    
    for batch_file in batch_files:
        batch_file_path = os.path.join(batch_folder_path, batch_file)
        
        # Memuat dan memproses data
        df = load_and_preprocess_data(batch_file_path)
        
        # Melatih dan menyimpan model
        model_name = f"model_{batch_count + 1}"
        train_and_save_model(df, model_name)
        
        batch_count += 1
        print(f"Batch {batch_count} diproses dan model {model_name} telah dilatih")
        
        # Opsional: Tambahkan jeda jika diperlukan untuk simulasi
        time.sleep(5)  # Atur durasi jeda sesuai kebutuhan

if __name__ == "__main__":
    process_batches()
    spark.stop()
