# Dynatrace ホスト情報コレクター

Dynatraceからホスト情報を収集してCSVファイルにエクスポートするPythonスクリプトです。現在、各ホストのホスト名、CPUコア数、および総メモリを収集します。

## 前提条件

- Python 3.x
- Dynatrace環境
- 以下の権限を持つDynatrace APIトークン：
  - `entities.read`（ホスト情報用）
  - `metrics.read`（メモリメトリクス用）

## セットアップ

1. 必要なパッケージをインストール：
```bash
pip install requests
```

2. Dynatraceの認証情報を含む`config.py`ファイルを作成：
```python
TENANT_URL = "https://your-tenant-url"
API_TOKEN = "your-api-token"
```

3. 認証情報を公開しないように`config.py`を`.gitignore`に含めてください。

## 使用方法

スクリプトの実行：
```bash
python dynatrace_host_info.py
```

スクリプトは以下を実行します：
1. Dynatrace環境に接続
2. ホスト情報とメトリクスを取得
3. `dynatrace_hosts_YYYYMMDD_HHMMSS.csv`という名前のCSVファイルを生成

## 出力

CSVファイルには以下の列が含まれます：
- ホスト名
- CPUコア数
- メモリ（GB）

## 新しい属性の追加

CSV出力に新しい属性を追加するには、以下の手順に従ってください：

1. Dynatrace APIレスポンスで属性を特定：
   - エンティティプロパティについては、[Dynatrace Entity API v1](https://www.dynatrace.com/support/help/dynatrace-api/environment-api/entity-v1)を確認
   - メトリクスについては、[Dynatrace Metrics API v2](https://www.dynatrace.com/support/help/dynatrace-api/environment-api/metric-v2)を確認

2. 必要に応じて`DynatraceHostInfo`クラスに新しいメソッドを追加：
```python
def get_new_metric(self, host_id):
    """特定のホストの新しいメトリクスを取得"""
    endpoint = f'{self.tenant_url}/api/v2/metrics/query'
    params = {
        'metricSelector': 'your.metric.key',
        'entitySelector': f'entityId({host_id})',
        'resolution': '1h',
        'timeFrame': 'last5mins'
    }
    # ... API呼び出しを処理して値を返す
```

3. `save_to_csv`メソッドを修正：
```python
def save_to_csv(self, hosts_data):
    # ... 既存のコード ...
    # ヘッダーに新しい列を追加
    writer.writerow(['Hostname', 'CPU Cores', 'Memory (GB)', '新しい列'])
    
    for host in hosts_data:
        hostname = host.get('displayName', 'N/A')
        cpu_cores = host.get('cpuCores', 'N/A')
        memory_gb = self.get_host_memory(host.get('entityId'))
        # 新しい値を追加
        new_value = host.get('newAttribute') or self.get_new_metric(host.get('entityId'))
        writer.writerow([hostname, cpu_cores, memory_gb, new_value])
```

## デバッグモード

スクリプトには詳細情報を表示するデバッグモードが含まれています：

```python
debug_mode = True  # main()内で設定
```

これにより、APIレスポンスのサンプルやエラーメッセージなどの追加情報が表示されます。

## 注意事項

- CSVファイルはgitコミットから自動的に除外されます
- メモリ値は小数点第1位に丸められます
- スクリプトはDynatraceから入手可能な最新のデータを使用します 