from kafka import KafkaConsumer
from json import loads

consumer = KafkaConsumer(
    'kafka-server',
    bootstrap_servers=['localhost:9092'],
    auto_offset_reset='earliest',
    enable_auto_commit=True,
    group_id='my-group',
    value_deserializer=lambda x: loads(x.decode('utf-8'))
)

message_buffer = []
buffer_size = 15000 # Jumlah data per batch, bisa disesuaikan
batch = 0
counter = 0

header = 'person_age,person_gender,person_education,person_income,person_emp_exp,person_home_ownership,loan_amnt,loan_intent,loan_int_rate,loan_percent_income,cb_person_cred_hist_length,credit_score,previous_loan_defaults_on_file,loan_status\n'

for message in consumer:
    if counter == 0:
        output = open(f'../batch/batch{batch}.csv', 'w', encoding='utf-8')
        output.write(header)

    data = message.value
    row = ','.join(str(data.get(col, '')) for col in header.strip().split(',')) + '\n'
    output.write(row)
    print(data)
    counter += 1

    if counter >= buffer_size:
        output.close()
        counter = 0
        batch += 1
