import requests
import csv
from datetime import datetime
import os
from config import TENANT_URL, API_TOKEN

class DynatraceHostInfo:
    def __init__(self, tenant_url, api_token, debug=False):
        self.tenant_url = tenant_url.rstrip('/')
        self.api_token = api_token
        self.debug = debug
        self.headers = {
            'Authorization': f'Api-Token {api_token}',
            'Accept': 'application/json'
        }

    def get_hosts(self):
        """Fetch host information from Dynatrace API"""
        endpoint = f'{self.tenant_url}/api/v1/entity/infrastructure/hosts'
        
        try:
            response = requests.get(endpoint, headers=self.headers)
            response.raise_for_status()
            data = response.json()
            # Debug print
            if self.debug:
                print(f"First host data sample: {data[0] if data else 'No data'}")
            return data
        except requests.exceptions.RequestException as e:
            print(f"Error fetching host information: {e}")
            return None

    def get_host_memory(self, host_id):
        """Fetch memory metrics for a specific host"""
        endpoint = f'{self.tenant_url}/api/v2/metrics/query'
        params = {
            'metricSelector': 'builtin:host.mem.total',
            'entitySelector': f'entityId({host_id})',
            'resolution': '1h',  # Get hourly data
            'timeFrame': 'last5mins'  # Get recent data
        }
        
        try:
            response = requests.get(endpoint, headers=self.headers, params=params)
            response.raise_for_status()
            data = response.json()
            
            # Extract the memory value from the response
            if data.get('result', []) and data['result'][0].get('data', []):
                # Get the most recent value
                memory_bytes = data['result'][0]['data'][0].get('values', [None])[0]
                if memory_bytes is not None:
                    # Convert bytes to GB and round to one decimal place
                    memory_gb = memory_bytes / (1024 * 1024 * 1024)
                    return round(memory_gb, 1)
            return 'N/A'
        except requests.exceptions.RequestException as e:
            if self.debug:
                print(f"Error fetching memory metrics for host {host_id}: {e}")
            return 'N/A'

    def save_to_csv(self, hosts_data):
        """Save host information to CSV file"""
        if not hosts_data:
            print("No data to save")
            return

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'dynatrace_hosts_{timestamp}.csv'

        try:
            with open(filename, 'w', newline='') as csvfile:
                writer = csv.writer(csvfile)
                # Write header
                writer.writerow(['Hostname', 'CPU Cores', 'Memory (GB)'])
                
                # Write host data
                for host in hosts_data:
                    hostname = host.get('displayName', 'N/A')
                    cpu_cores = host.get('cpuCores', 'N/A')
                    # Get memory for each host
                    memory_gb = self.get_host_memory(host.get('entityId'))
                    writer.writerow([hostname, cpu_cores, memory_gb])

            print(f"Data successfully saved to {filename}")
        except Exception as e:
            print(f"Error saving to CSV: {e}")

def main():
    # Create DynatraceHostInfo instance using config values
    debug_mode = False  # Set to True to enable debug output
    dt_info = DynatraceHostInfo(TENANT_URL, API_TOKEN, debug=debug_mode)

    # Fetch host information
    hosts_data = dt_info.get_hosts()

    # Save to CSV
    if hosts_data:
        dt_info.save_to_csv(hosts_data)
    else:
        print("Failed to fetch host information")

if __name__ == "__main__":
    main() 