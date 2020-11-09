#/usr/bin#/python
import boto3
import os
from elasticsearch import Elasticsearch 
from datetime import datetime, timezone, timedelta
import json

# Outra lambda para realizar o enrich do texto        
def comprehend_enrich_text(text):
    client = boto3.client('comprehend', region_name="us-east-1")
    if not text.get("descricaoTipo"):
        return

    response = client.detect_key_phrases(
        Text=text.get("ementa"),
        LanguageCode='pt'
    )

    key_phrases_list = []

    for key_phrases in response["KeyPhrases"]:
        key = key_phrases.get("Text")
        key_phrases_list.append(key)

    return key_phrases_list

def feed_data_into_es(es, data):
    index_name = "proposicoes"
    res = es.index(index=index_name,doc_type='_doc',id=data.get("id"),body=data)
    print(res)


def lambda_handler(event, context):
    
    es = Elasticsearch([{'host':os.getenv("ES_HOST", ""),
        'port':443}], 
        use_ssl = True,
        verify_certs = True
        )

    
    try:
        sqs_message = event["Records"][0]["body"].replace("\'", "\"")
        message_body = json.loads(sqs_message)
        datetime_now = datetime.utcnow()

        key_phrases_list = comprehend_enrich_text(message_body)
    
        message_body["key_phrases"] = key_phrases_list
        message_body["feed_date"] = datetime_now
        
        print(message_body)
        feed_data_into_es(es, message_body)
    except Exception as e:
        print(e)
        raise e