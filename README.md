# IoTaWatt-Integration

This project contains cross-platform Python and PowerShell scripts to pull data from the open source [IoTaWatt](https://iotawatt.com/) power monitoring device and push it into an [InfluxDB OSS](https://www.influxdata.com/products/influxdb/) instance. Consumption and power data is returned for each monitored circuit.

While IoTaWatt and Influx have data visualisation capabilities, [Grafana](https://grafana.com/) can be used to create interactive dashboards that show aggregate and per-cruit breakdowns, overall grid supply and demand, etc. The dashboard JSON files uploaded are specific to my home environment - circuit names, unit pricing, etc. - but can easily be modified to suit different environments.

The carbon footprint component relies on the excellent [Electricity Maps](https://www.electricitymaps.com/) data. Assuming your home zone is covered, a free personal use tier should suffice for most visualisation requirements. Register and get an API key here: https://api-portal.electricitymaps.com/. 
