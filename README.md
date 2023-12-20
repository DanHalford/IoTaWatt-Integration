# IoTaWatt-Integration

This project contains cross-platform Python and PowerShell scripts to pull data from the open source [IoTaWatt](https://iotawatt.com/) power monitoring device and push it into an [InfluxDB OSS](https://www.influxdata.com/products/influxdb/) instance. Consumption and power data is returned for each monitored circuit.

While IoTaWatt and Influx have data visualisation capabilities, [Grafana](https://grafana.com/) can be used to create interactive dashboards that show aggregate and per-cruit breakdowns, overall grid supply and demand, etc. The dashboard JSON files uploaded are specific to my home environment - circuit names, unit pricing, etc. - but can easily be modified to suit different environments.
