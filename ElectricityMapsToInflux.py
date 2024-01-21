import requests
from dateutil import parser
import datetime

class Reading:
    def __init__(self, series, reading, timestamp):
        self.series = series
        self.reading = reading
        self.timestamp = int(parser.parse(timestamp).timestamp())

def SendDataToInflux(type, data):
    postData = f"{type},series={data.series} value={data.reading} {data.timestamp}"
    headers = {"Authorization": f"Token {influxToken}"}
    response = requests.post(influxUri, headers=headers, data=postData)
    return response

nfluxaddress = "<URL/IP Address:Port of your Influx instance>"
influxToken = "<Influx API Token - must have write access to the bucket specified below>"
bucket = "<Influx Bucket>"
org = "<Influx Organisation ID>"
influxUri = f"http://{influxaddress}/api/v2/write?org={org}&bucket={bucket}&precision=s"
influxHeaders = {"Authorization": f"Token {influxToken}", "Accept": "application/csv", "Content-type": "application/vnd.flux"}

electricityMapsZone = "<Your zone - list all zones by calling https://api.electricitymap.org/v3/zones>"
powerBreakdownUri = f"https://api-access.electricitymaps.com/free-tier/power-breakdown/latest?zone={electricityMapsZone}"
carbonFootprintUri = f"https://api-access.electricitymaps.com/free-tier/carbon-intensity/latest?zone={electricityMapsZone}"
electricityMapsToken = "<Your electricity maps API token - register here>"
electricityMapsHeaders = {"auth-token": f"{electricityMapsToken}"}

powerBreakdownInfo = requests.get(powerBreakdownUri, headers=electricityMapsHeaders ).json()
carbonFootprintInfo = requests.get(carbonFootprintUri, headers=electricityMapsHeaders ).json()

powerBreakdown = Reading("renewable", powerBreakdownInfo['fossilFreePercentage'], powerBreakdownInfo['datetime'])
carbonIntensity = Reading("carbon", carbonFootprintInfo['carbonIntensity'], carbonFootprintInfo['datetime'])

SendDataToInflux("renewable", powerBreakdown)
SendDataToInflux("carbon", carbonIntensity)

print(f'{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")} - C Footprint: {carbonFootprintInfo["carbonIntensity"]} - % Renewable: {powerBreakdownInfo["fossilFreePercentage"]}')
