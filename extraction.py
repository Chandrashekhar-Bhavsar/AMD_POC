

data = {
    "Requests/sec": 133572.71,
    "Transfer/sec": "160.76MB"
}

result_info = {
    "resultinfo": {
        "Statistics": {
            i: {
                "MetricName": metric_name,
                "MetricValue": metric_value
            }
            for i, (metric_name, metric_value) in enumerate(data.items())
        }
    }
}

print(result_info)
