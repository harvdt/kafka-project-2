from flask import Flask, request, jsonify
from pyspark.ml.classification import RandomForestClassificationModel
from pyspark.ml.evaluation import MulticlassClassificationEvaluator
from pyspark.ml.feature import VectorAssembler
from pyspark.ml.linalg import Vectors
from pyspark.sql import SparkSession
import os

app = Flask(__name__)

spark = SparkSession.builder \
    .appName("FlaskSparkMLApp") \
    .master("local[*]") \
    .getOrCreate()

MODEL_PATH = "spark_ml/models/"
TEST_DATA_PATH = "loan_data.csv"

prediction_history = []

def load_model(model_name):
    model_path = os.path.join(MODEL_PATH, model_name)
    if os.path.exists(model_path):
        return RandomForestClassificationModel.load(model_path)
    else:
        return None

def prepare_features(data):
    features = [
        data.get("person_age", 0),
        data.get("person_income", 0),
        data.get("person_emp_exp", 0),
        data.get("loan_amnt", 0),
        data.get("loan_int_rate", 0),
        data.get("loan_percent_income", 0),
        data.get("cb_person_cred_hist_length", 0),
        data.get("credit_score", 0),
        data.get("person_gender_index", 0),
        data.get("person_education_index", 0),
        data.get("person_home_ownership_index", 0),
        data.get("loan_intent_index", 0)
    ]
    return Vectors.dense(features)

@app.route("/predict-model/<model_id>", methods=["POST"])
def predict(model_id):
    data = request.json
    input_vector = prepare_features(data)

    model_name = 'model_' + model_id
    model = load_model(model_name)

    if not model:
        return jsonify({"error": f"Model {model_id} tidak ditemukan"}), 404

    prediction = model.predict(input_vector)
    prediction_history.append({"model_id": model_id, "input": data, "prediction": int(prediction)})

    return jsonify({"model": int(model_id), "loan_status": int(prediction)})

@app.route("/history", methods=["GET"])
def get_prediction_history():
    return jsonify(prediction_history)

@app.route("/batch-predict/<model_id>", methods=["POST"])
def batch_predict(model_id):
    data_list = request.json.get("data", [])
    model_name = 'model_' + model_id
    model = load_model(model_name)

    if not model:
        return jsonify({"error": f"Model {model_id} tidak ditemukan"}), 404

    predictions = []
    for data in data_list:
        input_vector = prepare_features(data)
        prediction = model.predict(input_vector)
        result = {
            "input": data,
            "loan_status": int(prediction)
        }
        predictions.append(result)

    return jsonify({
        "model": model_id,
        "predictions": predictions
    })

if __name__ == "__main__":
    app.run(debug=True)

    spark.stop()