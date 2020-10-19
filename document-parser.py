#/usr/bin#/python
import boto3
from elasticsearch import Elasticsearch 

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
            

# Outra lambda para realizar o enrich do texto        
def comprehend_enrich_text(text):
    client = boto3.client('comprehend', region_name="us-east-1")
    if not text.get("descricaoTipo"):
        return

    response = client.detect_key_phrases(
        Text=text.get("descricaoTipo"),
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


def main():
    file_path = "data/proposicoes-2020.csv"
    es = Elasticsearch([{'host':'search-es-for-demo-o7wbu5722qanrtbbula3lglv4e.us-east-1.es.amazonaws.com',
        'port':443}], 
        use_ssl = True,
        verify_certs = True
        )

    lines = open_file(file_path)
    json_list = csv_parser(lines)
    
    for value in json_list:
        if value:
            print("-"*20)
            key_phrases_list = comprehend_enrich_text(value)
            value["key_phrases"] = key_phrases_list

            feed_data_into_es(es, value)

if __name__ == "__main__":
    main()