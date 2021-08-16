# Monitoring-Lab
PoC for monitoring python application with Prometheus and EFK

# Ideas

- Learning how to write python (Flask) applications with Prometheus metrics exporting
- Creating application which simulates some failures and warnings
- Monitoring applications and containerized infrastructure with Prometheus
- Collecting logs with EFK
- Configuring alerting

# Application

```MonApp``` is a Flask application created for learning how to build monitoring systems.

## Logs

Every 10 seconds the application prints a log entry in console. 

```
Mon, 16 Aug 2021 15:04:12 - INFO - dynauend whoilt wuoy
Mon, 16 Aug 2021 15:04:22 - INFO - gnaiantz psycheerly viaob
Mon, 16 Aug 2021 15:04:32 - ERROR - twoand twouc snoarr
Mon, 16 Aug 2021 15:04:42 - WARNING - sriaontz gills cycloech
Mon, 16 Aug 2021 15:04:51 - INFO - hyiaoght mckews blaiarry
Mon, 16 Aug 2021 15:05:02 - WARNING - wauefy dioutch mcciur
Mon, 16 Aug 2021 15:05:12 - INFO - schwoink psychong phantz
Mon, 16 Aug 2021 15:05:22 - INFO - groiats hiidy kosm
```
## Metrics 

```http://{IP}:5000/metrics```
The application exposes some metrics about warehouses effectiveness:
```
# HELP monapp_position_in_stock Position in stock (1000 tons)
# TYPE monapp_position_in_stock gauge
monapp_position_in_stock{position="Rice"} 15.3699
monapp_position_in_stock{position="Corn"} 11.3835
```

## Alert

```http://{IP}:5000/alert```
```MonApp``` can work as a web hook for your AlertManager. It will show requests from AlertManager amd print them in console in raw format.

## Mocking

There are two URIs for testing CPU and RAM load.

```http://{IP}:5000/cpu_task```
This task will create a thread which will use as much CPU resources as possible during next 30 seconds.
```http://{IP}:5000/ram_task```
This task will create a thread which will use as much RAM as possible until the application is killed by docker.


# Infrastructure for monitoring

## Tools

- Prometheus and AlertManager
- ElasticSearch
- Kibana
- Grafana
- Fluentd
- cAdvisor
- Docker

![Diagram](/docs/diagram.png)


# About monitoring

## Logs

```http://{IP}:5601/```
Logs are collected by ```Fluentd``` using Docker ```fluentd``` driver. ```Fluentd``` filters out only **critical**, **error** and **warning** messages and redirects them to ```ElasticSearch```. All other messages will be ignored.
Collected logs are exposed using ```Kibana```. Dashboards for ```Kibana``` you can find [here](/kibana/MonApp.ndjson) (they will not be uploaded automatically during deployment).

## Metrics

```http://{IP}:3000/```
All the metrics are collected by ```Prometheus``` and exposed in ```Grafana```. Find specially created dashboards in there.

## Alerting

```Alertmanager``` is configured to fire up an alert if it finds that ```monapp_position_in_stock``` metric is below 10 or greater than 20. In this case it will send a request to a webhook ```http://{IP}:5000/alert```.

## Infrastructure Monitoring

For infrastructure monitoring ```cAdvisor``` container is added and configured. All metrics from ```cAdvisor``` are collected by ```Prometheus`` and exposed in ```Grafana``` dashboards.

# Mocking

```MonApp``` has some mocking tools which can help you to test you monitoring infrastructure.
