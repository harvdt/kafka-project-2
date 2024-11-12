from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.ml.feature import VectorAssembler, StringIndexer
from pyspark.ml.classification import RandomForestClassifier
from pyspark.ml.evaluation import MulticlassClassificationEvaluator
import os
import time

spark = SparkSession.builder \
    .appName("KafkaSparkML") \
    .getOrCreate()

current_dir = os.path.dirname(os.path.abspath(__file__))
batch_folder_path = os.path.join(current_dir, "../batch")
model_save_path = os.path.join(current_dir, "models")

def load_and_preprocess_data(batch_file_path):
    df = spark.read.csv(batch_file_path, header=True, inferSchema=True)
    label_indexer = StringIndexer(inputCol="loan_status", outputCol="label").fit(df)
    df = label_indexer.transform(df)

    categorical_columns = ['person_gender', 'person_education', 'person_home_ownership', 'loan_intent']
    indexers = [StringIndexer(inputCol=col, outputCol=col+"_index").fit(df) for col in categorical_columns]

    for indexer in indexers:
        df = indexer.transform(df)

    df = df.drop(*categorical_columns)

    feature_columns = [
        'person_age', 'person_income', 'person_emp_exp', 'loan_amnt',
        'loan_int_rate', 'loan_percent_income', 'cb_person_cred_hist_length',
        'credit_score', 'person_gender_index', 'person_education_index',
        'person_home_ownership_index', 'loan_intent_index'
    ]

    assembler = VectorAssembler(inputCols=feature_columns, outputCol='features')
    df = assembler.transform(df)
    df = df.select('features', 'label')
    return df

def train_and_save_model(df, model_name):
    train_data, test_data = df.randomSplit([0.8, 0.2], seed=1234)
    rf = RandomForestClassifier(featuresCol='features', labelCol='label', numTrees=100, seed=1)
    model = rf.fit(train_data)

    predictions = model.transform(test_data)
    evaluator = MulticlassClassificationEvaluator(labelCol="label", predictionCol="prediction", metricName="accuracy")
    accuracy = evaluator.evaluate(predictions)

    evaluator_f1 = MulticlassClassificationEvaluator(labelCol="label", predictionCol="prediction", metricName="f1")
    f1_score = evaluator_f1.evaluate(predictions)

    print(f"Model disimpan di {model_save_path}/{model_name}")
    print(f"Akurasi Model: {accuracy:.2f}")
    print(f"F1 Score: {f1_score:.2f}")

    model_dir = os.path.join(model_save_path, model_name)
    model.write().overwrite().save(model_dir)

def process_batches():
    batch_files = sorted(os.listdir(batch_folder_path))
    batch_count = 0

    for batch_file in batch_files:
        batch_file_path = os.path.join(batch_folder_path, batch_file)
        df = load_and_preprocess_data(batch_file_path)
        model_name = f"model_{batch_count + 1}"
        train_and_save_model(df, model_name)

        batch_count += 1
        print(f"Batch {batch_count} diproses dan model {model_name} telah dilatih")

        time.sleep(5)

if __name__ == "__main__":
    process_batches()
    spark.stop()
