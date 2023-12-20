
import requests
import datetime
import json
import os
import csv

iotaaddress = "<URL/IP Address of your IotaWatt device>"
influxaddress = "<URL/IP Address:Port of your Influx instance>"
influxToken = "<Influx API Token - must have write access to the bucket specified below>"
bucket = "<Influx Bucket>"
org = "<Influx Organisation ID>"
influxQueryUri = f"http://{influxaddress}/api/v2/query?org={org}"
influxUri = f"http://{influxaddress}/api/v2/write?org={org}&bucket={bucket}&precision=s"

class Reading:
    def __init__(self, series, reading, timestamp):
        self.series = series
        self.reading = reading
        self.timestamp = int(datetime.datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%S").timestamp())

def SendDataToInflux(type, data):
    influxData = []
    for r in data:
        influxData.append(f"{type},series={r.series} value={r.reading} {r.timestamp}")
    postData = "\n".join(influxData)
    headers = {"Authorization": f"Token {influxToken}"}
    response = requests.post(influxUri, headers=headers, data=postData)
    return response

circuits = []
drawReadings = []
consumeReadings = []

influxHeaders = {"Authorization": f"Token {influxToken}", "Accept": "application/csv", "Content-type": "application/vnd.flux"}
influxQuery = f'from(bucket: "{bucket}") |> range(start: -3h) |> last()'
influxData = requests.post(influxQueryUri, headers=influxHeaders, data=influxQuery)
influxDataReader = csv.DictReader(list(filter(None, influxData.text.split("\r\n"))))
lastrecord = ""
for row in influxDataReader:
    rowtime = row['_time']
    if rowtime > lastrecord:
        lastrecord = rowtime
if lastrecord == '':
    lastrecord = "h-5m"

seriesData = requests.get(f"http://{iotaaddress}/query?show=series")
for series in filter(lambda x: x['unit'] == 'Watts', seriesData.json()['series']):
    circuits.append(series['name'])

drawSeries = ','.join(circuits)
drawQueryUri = f"http://{iotaaddress}/query?select=[time.iso,{drawSeries}]&begin={lastrecord}&end=s&group=10s&format=json"
drawData = requests.get(drawQueryUri)
for reading in drawData.json():
    timestamp = reading[0]
    for count in range(1, len(reading)):
        r = Reading(circuits[count-1], reading[count], timestamp)
        drawReadings.append(r)

consumeSeries = '.wh,'.join(circuits) + '.wh'
consumeQueryUri = f"http://{iotaaddress}/query?select=[time.iso,{consumeSeries}]&begin={lastrecord}&end=s&group=m&format=json"
consumeData = requests.get(consumeQueryUri)
for reading in consumeData.json():
    timestamp = reading[0]
    for count in range(1, len(reading)):
        r = Reading(circuits[count-1], reading[count], timestamp)
        consumeReadings.append(r)

drawResponse = SendDataToInflux('draw', drawReadings)
consumeResponse = SendDataToInflux('consumption', consumeReadings)

print(f'{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")} - Draw: {len(drawReadings)} entries - Consume: {len(consumeReadings)} entries')
