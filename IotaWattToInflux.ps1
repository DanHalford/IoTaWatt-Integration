$WarningPreference = "SilentlyContinue"

$iotaaddress = "<URL/IP Address of your IotaWatt device>"
$influxaddress = "<URL or IP Address:Port of your InfluxDB instance>"
$influxToken = "<InfluxDB API Token - must have write access to the bucket specified below>"
$bucket = "<InfluxDB Bucket>"
$org = "<InfluxDB Organisation ID>"
$influxqueryurl = "http://$influxaddress/api/v2/query?org=$org"
$influxurl = "http://$influxaddress/api/v2/write?org=$org&bucket=$bucket&precision=s"

Class Series {
    [System.String]$SeriesName
    [System.String]$Unit
}

Class Reading {
    [System.String]$ReadingType
    [System.String]$SeriesName
    [System.String]$Unit
    [System.Decimal]$Value
    [System.DateTimeOffset]$Timestamp

}

$series = @()
$drawReadings = @()
$consumeReadings = @()
$influxdata = @()

$seriesdata = Invoke-WebRequest -Uri "http://$iotaaddress/query?show=series"
($seriesdata | ConvertFrom-Json).Series | Where-Object { $_.unit -eq "Watts" } | ForEach-Object {
    $thisSeries = New-Object Series
    $thisSeries.SeriesName = $_.name
    $thisSeries.Unit = $_.unit
    $series += $thisSeries
}

$headers = @{"Authorization"="Token $influxToken"; "Accept"="application/csv"; "Content-type"="application/vnd.flux"}
$query = "from(bucket: ""$bucket"") |> range(start: -3h) |> last()"
$queryresult = Invoke-WebRequest -Method Post -Uri $influxqueryurl -Headers $headers -Body $query
$querydata = $queryresult.Content | ConvertFrom-Csv
if ($querydata -eq $null) {
    $lastrecord = "h-3h"
} else {
    $lastrecord = $querydata[0]._time
}

$drawSeries = $series | Join-String -Property SeriesName -Separator ","
$drawDataUri = "http://$iotaaddress/query?select=[time.iso,$drawSeries]&begin=$lastrecord&end=s&group=10s&format=json"
$drawData = Invoke-WebRequest -Uri $drawDataUri

$drawData | ConvertFrom-Json | ForEach-Object {
    $thisDataset = $_
    $timestamp = $thisDataset[0] #Timestamp is always the first value in the array
    for ($r = 1; $r -lt $thisDataset.Count; $r++) {
        $thisReading = New-Object Reading
        $thisReading.ReadingType = "draw"
        $thisReading.Timestamp = $timestamp
        $thisReading.SeriesName = $series[$r-1].SeriesName
        $thisReading.Unit = "W"
        $thisReading.Value = $thisDataset[$r]
        $drawReadings += $thisReading
    }
}

$consumeSeries = ($series | Join-String -Property SeriesName -Separator ".wh," ) + ".wh"
$consumeDataUri = "http://$iotaaddress/query?select=[time.iso,$consumeSeries]&begin=$lastrecord&end=s&group=m&format=json"
$consumeData = Invoke-WebRequest -Uri $consumeDataUri

$consumeData | ConvertFrom-Json | ForEach-Object {
    $thisDataset = $_
    $timestamp = $thisDataset[0] #Timestamp is always the first value in the array
    for ($r = 1; $r -lt $thisDataset.Count; $r++) {
        $thisReading = New-Object Reading
        $thisReading.ReadingType = "consumption"
        $thisReading.Timestamp = $timestamp
        $thisReading.SeriesName = $series[$r-1].SeriesName
        $thisReading.Unit = "Wh"
        $thisReading.Value = $thisDataset[$r]
        $consumeReadings += $thisReading
    }

    $influxdata = @()
$drawReadings | ForEach-Object {
    $thisReading = $_
    $influxdata += "$($thisReading.ReadingType),series=$($thisReading.SeriesName) value=$($thisReading.Value) $($thisReading.Timestamp.ToUnixTimeSeconds())"
}

$data = $influxdata | Join-String -Separator "`n"
$influxurl = "http://$influxaddress/api/v2/write?org=$org&bucket=$bucket&precision=s"
$result = Invoke-WebRequest -Method Post -Uri $influxurl -Headers @{"Authorization"="Token $influxToken"} -Body $data

$influxdata = @()
$consumeReadings | ForEach-Object {
    $thisReading = $_
    $influxdata += "$($thisReading.ReadingType),series=$($thisReading.SeriesName) value=$($thisReading.Value) $($thisReading.Timestamp.ToUnixTimeSeconds())"
}

$data = $influxdata | Join-String -Separator "`n"
$influxurl = "http://$influxaddress/api/v2/write?org=$org&bucket=$bucket&precision=s"
$result = Invoke-WebRequest -Method Post -Uri $influxurl -Headers @{"Authorization"="Token $influxToken"} -Body $data

Write-Output "$(Get-Date): Draw: $($drawReadings.Count), Consumption: $($consumeReadings.Count)"

