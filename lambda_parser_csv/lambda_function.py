#/usr/bin#/python
import boto3
import os

# Enviar cada linha do CSV para uma fila SQS
def open_file(file_path):
    lines = None

    with open(file_path, "r+", encoding='utf-8-sig') as file:
        lines = file.readlines()
    
    return lines


# Realizar o parser de cada linha utilizando uma Lambda e trabalhar com DLQ
def csv_parser(lines):
    header = (lines[0]).split(";")
    json_list_parsed = []
    json_list = [] 
    for line in lines[1:]:
        line = line.split(";")
        json_parsed = {}
        for idx, value in enumerate(line):
            if len(header) != len(line):
                # Tentar tratar o erro posteriormente caso venha com alguma divergencia
                continue
            json_index = (header[idx].replace('"', "")).strip()
            value = (value.replace('"', "")).strip()

            if "keywords" in json_index:
                json_parsed[json_index] = value.split(",")
                continue

            json_parsed[json_index] = value
        json_list.append(json_parsed)
    return json_list


def send_to_amazon_sqs(sqs, json_list, queue_url):
    print("Seding messages to Amazon SQS")
    for item in json_list:
        if item:
            response = sqs.send_message(
                QueueUrl=queue_url,
                MessageBody=str(item),
            )
            print("Finished process of sending messages")


def download_s3_file(bucket_name, object_name, file_name):
    s3 = boto3.client('s3')
    s3.download_file(bucket_name, object_name, f"/tmp/{file_name}")
    print("Downloaded file")


def lambda_handler(event, context):

    try:
        file_path = event["Records"][0]["s3"]["object"]["key"]
        file_name = "tmp-01.csv"
        queue_url = os.getenv("SQS_URL", "")
        bucket_name = os.getenv("BUCBUCKET_NAMEKET_NAME", "")
        
        # Get file from s3
        download_s3_file(bucket_name, file_path, file_name)
        
        lines = open_file(f"/tmp/{file_name}")
        json_list = csv_parser(lines)

        client = boto3.client('sqs')
        send_to_amazon_sqs(client, json_list, queue_url)
    except Exception as e:
        print(e)