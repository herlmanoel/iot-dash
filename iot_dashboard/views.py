from django.shortcuts import render
from django.http import HttpResponse
import requests
# from datetime import datetime
import pandas as pd
import numpy as np
import json
import csv
# import json
from prophet import Prophet

# Create your views here.


def home(request):
    return render(request, 'index.html')


def getData(request):
    channelId = '196384'
    numResults = '500'
    tratandoOsDados(channelId, '1', numResults)
    tratandoOsDados(channelId, '2', numResults)
    return HttpResponse({'status': 'ok'})

def getJsonComum():
    channelId = '196384'
    numResults = '500'
    fieldNumber = '1'
    arrayComplet = returnDataDsYDataFrameMediaDesvio(channelId, fieldNumber, numResults)
    df = arrayComplet[0]
    media = arrayComplet[1]
    desvio = arrayComplet[2]
    print(df)
    result = df.to_json(orient="values")
    parsed = json.loads(result)
    jsonCompleto = json.dumps(parsed, indent=4)
    

    return HttpResponse(jsonCompleto)



# def getTemperaturePrevision(request):
#     fieldNumber = request.GET.get("id", '1')
    
#     channelId = '196384'
#     numResults = '1500'
#     tratandoOsDados(channelId, fieldNumber, numResults)
#     return HttpResponse({'status': 'ok'})

def getJson(request):
    id = request.GET.get("id", '1')
    f = open('data_'+id+'.json')
    return HttpResponse(f)

def getJsonPrev(request):
    id = request.GET.get("id", '1')
    f = open('data_prev_'+id+'.json')
    return HttpResponse(f)
# ===================================================================


def getDataJsonThingspeak(channelId, fieldNumber, numResults):
    URL = 'https://api.thingspeak.com/channels/'+channelId +'/fields/'+fieldNumber+'.json?results='+numResults
    print(URL)
    response = requests.get(url=URL)
    feedsJson = response.json()["feeds"]
    return feedsJson

def returnDataDsYDataFrameMediaDesvio(channelId, fieldNumber, numResults):
    jsonData = getDataJsonThingspeak(channelId, fieldNumber, numResults)
    df = pd.json_normalize(jsonData)
    df.drop('entry_id', axis=1, inplace=True)
    df['created_at'] = pd.to_datetime(
        df['created_at'], format="%Y-%m-%d %H:%M")
    df['created_at'] = df['created_at'].dt.tz_convert(None)
    df.rename(columns={'created_at': 'ds', 'field' + fieldNumber: 'y'}, inplace=True)
    media = df['y'].mean()
    desvioPadrao = df['y'].std()
    array = [df, media, desvioPadrao]
    return array

def tratandoOsDados(channelId, fieldNumber, numResults):
    jsonData = getDataJsonThingspeak(channelId, fieldNumber, numResults)
    df = pd.json_normalize(jsonData)
    df.drop('entry_id', axis=1, inplace=True)
    df['created_at'] = pd.to_datetime(
        df['created_at'], format="%Y-%m-%d %H:%M")
    df['created_at'] = df['created_at'].dt.tz_convert(None)
    df.rename(columns={'created_at': 'ds', 'field' +
                       fieldNumber: 'y'}, inplace=True)
    
    # escrevendo json e csv nos arquivos de previsão e normal

    nomeArquivo = 'data_'+fieldNumber
    escreverJsonCsv(df, nomeArquivo)

    nomeArquivoPrevisao = 'data_prev_'+fieldNumber
    dfPrevivisao = previsionData(df)
    escreverJsonCsv(dfPrevivisao, nomeArquivoPrevisao)

def escreverJsonCsv(df, nomeDoArquivo):
    df.to_csv(nomeDoArquivo+'.csv', index=False)
    convertCsvToJson(nomeDoArquivo)

def convertCsvToJson(nomeDoArquivo):
    file = nomeDoArquivo+'.csv'
    json_file = nomeDoArquivo+'.json'

    # Read CSV File
    def read_CSV(file, json_file):
        csv_rows = []
        with open(file) as csvfile:
            reader = csv.DictReader(csvfile)
            field = reader.fieldnames
            for row in reader:
                csv_rows.extend([{field[i]:row[field[i]]
                                  for i in range(len(field))}])
            convert_write_json(csv_rows, json_file)

    # Convert csv data into json

    def convert_write_json(data, json_file):
        with open(json_file, "w") as f:
            f.write(json.dumps(data, sort_keys=False, indent=4,
                               separators=(',', ': ')))  # for pretty
            # f.write(json.dumps(data))

    read_CSV(file, json_file)


def previsionData(df):
    m = Prophet()
    m.fit(df)

    # ultimoIndex = df.count
    inicio = df.loc[499]['ds']
    print('-------------------')
    print(inicio)

    data_futuro = pd.date_range(
        start=inicio, periods=500, freq="5s")
    df_data_futuro = pd.DataFrame(data_futuro)
    df_data_futuro.columns = ['ds']
    df_data_futuro
    previsao = m.predict(df_data_futuro)
    previsao = previsao[['ds', 'yhat']]
    print(previsao.loc[0])
    return previsao
