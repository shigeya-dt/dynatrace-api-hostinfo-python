# Dynatrace Host Information Collector

A Python script that collects host information from Dynatrace and exports it to a CSV file. Currently, it collects hostname, CPU cores, and total memory for each host.

## Prerequisites

- Python 3.x
- Dynatrace environment
- Dynatrace API token with the following permissions:
  - `entities.read` (for host information)
  - `metrics.read` (for memory metrics)

## Setup

Install required packages:
```bash
pip install requests
```

## Configuration

1. Copy `config.py.template` to `config.py`:
   ```bash
   cp config.py.template config.py
   ```

2. Edit `config.py` and set your Dynatrace environment details:
   - `DYNATRACE_API_URL`: Your Dynatrace environment URL
   - `DYNATRACE_API_TOKEN`: Your Dynatrace API token

## Usage

Run the script:
```bash
python dynatrace_host_info.py
```

The script will:
1. Connect to your Dynatrace environment
2. Fetch host information and metrics
3. Generate a CSV file named `dynatrace_hosts_YYYYMMDD_HHMMSS.csv`

## Output

The CSV file contains the following columns:
- Hostname
- CPU Cores
- Memory (GB)

Example output:

| Hostname    | CPU Cores | Memory (GB) |
|------------|-----------|-------------|
| st-linux-01| 4         | 15.5        |
| st-win-01  | 14        | 31.7        |

## Adding New Attributes

To add new attributes to the CSV output, follow these steps:

1. Identify the attribute in the Dynatrace API response:
   - For entity properties, check the [Dynatrace Entity API v1](https://www.dynatrace.com/support/help/dynatrace-api/environment-api/entity-v1)
   - For metrics, check the [Dynatrace Metrics API v2](https://www.dynatrace.com/support/help/dynatrace-api/environment-api/metric-v2)

2. Add a new method in the `DynatraceHostInfo` class if needed:
```python
def get_new_metric(self, host_id):
    """Fetch new metric for a specific host"""
    endpoint = f'{self.tenant_url}/api/v2/metrics/query'
    params = {
        'metricSelector': 'your.metric.key',
        'entitySelector': f'entityId({host_id})',
        'resolution': '1h',
        'timeFrame': 'last5mins'
    }
    # ... handle the API call and return the value
```

3. Modify the `save_to_csv` method:
```python
def save_to_csv(self, hosts_data):
    # ... existing code ...
    # Add new column to header
    writer.writerow(['Hostname', 'CPU Cores', 'Memory (GB)', 'New Column'])
    
    for host in hosts_data:
        hostname = host.get('displayName', 'N/A')
        cpu_cores = host.get('cpuCores', 'N/A')
        memory_gb = self.get_host_memory(host.get('entityId'))
        # Add new value
        new_value = host.get('newAttribute') or self.get_new_metric(host.get('entityId'))
        writer.writerow([hostname, cpu_cores, memory_gb, new_value])
```

## Debug Mode

The script includes a debug mode that can be enabled to show detailed information:

```python
debug_mode = True  # in main()
```

This will print additional information like API response samples and error messages.

## Notes

- CSV files are automatically excluded from git commits
- Memory values are rounded to one decimal place
- The script uses the most recent data available from Dynatrace
