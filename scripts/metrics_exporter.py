#!/usr/bin/env python3
"""
OpenRAN Metrics Exporter for Prometheus
Reads JSON data files and exposes them as Prometheus metrics
"""

import json
import glob
import time
import os
from http.server import HTTPServer, BaseHTTPRequestHandler
from datetime import datetime
import threading

class MetricsExporter:
    def __init__(self):
        self.latest_metrics = {}
        self.latest_ue_aggregates = {}
        
    def load_latest_data(self):
        """Load the most recent data file"""
        try:
            # Load normal OpenRAN data
            json_files = glob.glob("/tmp/openran_data_*.json")
            if json_files:
                latest_file = max(json_files, key=os.path.getctime)
                with open(latest_file, 'r') as f:
                    data = json.load(f)
                
                self.latest_metrics = data.get('metrics', {})
                
                # Calculate UE aggregates
                ues = data.get('ues', [])
                if ues:
                    self.latest_ue_aggregates = {
                        'ue_count': len(ues),
                        'avg_rsrp': sum(ue.get('rsrp', 0) for ue in ues) / len(ues),
                        'avg_rsrq': sum(ue.get('rsrq', 0) for ue in ues) / len(ues),
                        'total_dl_throughput': sum(ue.get('throughput_dl', 0) for ue in ues),
                        'total_ul_throughput': sum(ue.get('throughput_ul', 0) for ue in ues),
                        'avg_dl_throughput': sum(ue.get('throughput_dl', 0) for ue in ues) / len(ues),
                        'avg_ul_throughput': sum(ue.get('throughput_ul', 0) for ue in ues) / len(ues)
                    }
            
            # Load security/attack data
            attack_files = glob.glob("/tmp/openran_attack_data_*.json")
            if attack_files:
                latest_attack_file = max(attack_files, key=os.path.getctime)
                with open(latest_attack_file, 'r') as f:
                    attack_data = json.load(f)
                
                # Merge security metrics
                security_metrics = attack_data.get('security_metrics', {})
                self.latest_metrics.update(security_metrics)
                
                # Add attack status metrics
                self.latest_metrics['attack_active'] = 1 if attack_data.get('attack_active', False) else 0
                self.latest_metrics['attack_severity'] = self._severity_to_numeric(attack_data.get('attack_severity', 'none'))
            
            return len(json_files) > 0 or len(attack_files) > 0
            
        except Exception as e:
            print(f"Error loading data: {e}")
            return False
    
    def generate_prometheus_metrics(self):
        """Generate Prometheus-formatted metrics"""
        metrics = []
        
        # Basic OpenRAN metrics
        for key, value in self.latest_metrics.items():
            if isinstance(value, (int, float)):
                metric_name = f"openran_{key}"
                metrics.append(f"{metric_name} {value}")
        
        # UE aggregated metrics
        for key, value in self.latest_ue_aggregates.items():
            if isinstance(value, (int, float)):
                # Fix metric naming - remove duplicate "ue" prefix
                if key == 'ue_count':
                    metric_name = "openran_ue_count"
                else:
                    metric_name = f"openran_ue_{key}"
                metrics.append(f"{metric_name} {value:.2f}")
        
        # Add derived metrics
        if self.latest_metrics:
            # Connection health (1 if >= 3 nodes, 0 otherwise)
            nodes = self.latest_metrics.get('e2_connected_nodes', 0)
            metrics.append(f"openran_connection_health {1 if nodes >= 3 else 0}")
            
            # Model performance category (0=poor, 1=good, 2=excellent)
            accuracy = self.latest_metrics.get('xapp_model_accuracy', 0)
            if accuracy >= 0.95:
                perf = 2
            elif accuracy >= 0.85:
                perf = 1
            else:
                perf = 0
            metrics.append(f"openran_model_performance_category {perf}")
        
        # Add histogram metrics for latency (simulated buckets)
        latency_ms = self.latest_metrics.get('e2_message_latency_ms', 15.0)
        metrics.extend(self._generate_latency_histogram('e2_message_latency', latency_ms))
        
        # Add counter metrics without "openran_" prefix for dashboard compatibility
        e2_messages = self.latest_metrics.get('e2_messages_total', 0)
        ric_subs = self.latest_metrics.get('ric_subscription_requests_total', 0)
        ric_ctrl = self.latest_metrics.get('ric_control_requests_total', 0)
        xapp_actions = self.latest_metrics.get('xapp_control_actions_total', 0)
        xapp_predictions = self.latest_metrics.get('xapp_ml_predictions_total', 0)
        
        # Add raw counter metrics for rate calculations
        metrics.append(f"e2_messages_total {e2_messages}")
        metrics.append(f"ric_subscription_requests_total {ric_subs}")
        metrics.append(f"ric_control_requests_total {ric_ctrl}")
        metrics.append(f"xapp_control_actions_total {xapp_actions}")
        metrics.append(f"xapp_ml_predictions_total {xapp_predictions}")
        
        # Add node count for sum() queries
        nodes = self.latest_metrics.get('e2_connected_nodes', 0)
        metrics.append(f"e2_connected_nodes {nodes}")
        
        # Add xApp metrics
        xapp_subs = self.latest_metrics.get('xapp_active_subscriptions', 0)
        metrics.append(f"xapp_active_subscriptions {xapp_subs}")
        
        # Add timestamp
        metrics.append(f"openran_last_update {int(time.time())}")
        
        return "\n".join(metrics) + "\n"
    
    def _severity_to_numeric(self, severity: str) -> int:
        """Convert severity string to numeric value"""
        severity_map = {
            'none': 0,
            'low': 1,
            'medium': 2,
            'high': 3,
            'critical': 4
        }
        return severity_map.get(severity.lower(), 0)
    
    def _generate_latency_histogram(self, metric_name: str, current_latency: float) -> list:
        """Generate histogram buckets for latency metrics"""
        buckets = [5.0, 10.0, 15.0, 20.0, 25.0, 30.0, 50.0, 100.0, 200.0, 500.0, 1000.0]
        histogram_metrics = []
        
        # Generate cumulative counts for each bucket
        total_count = 100  # Simulated total observations
        for bucket in buckets:
            if current_latency <= bucket:
                # If current latency is within this bucket, include most observations
                count = int(total_count * 0.8)
            else:
                # If current latency exceeds this bucket, include fewer observations
                count = int(total_count * 0.2)
            
            histogram_metrics.append(f'{metric_name}_bucket{{le="{bucket}"}} {count}')
        
        # Add +Inf bucket
        histogram_metrics.append(f'{metric_name}_bucket{{le="+Inf"}} {total_count}')
        
        # Add sum and count
        histogram_metrics.append(f'{metric_name}_sum {current_latency * total_count}')
        histogram_metrics.append(f'{metric_name}_count {total_count}')
        
        return histogram_metrics

class MetricsHandler(BaseHTTPRequestHandler):
    def __init__(self, exporter, *args, **kwargs):
        self.exporter = exporter
        super().__init__(*args, **kwargs)
    
    def do_GET(self):
        if self.path == '/metrics':
            # Load latest data
            self.exporter.load_latest_data()
            
            # Generate metrics
            metrics_text = self.exporter.generate_prometheus_metrics()
            
            # Send response
            self.send_response(200)
            self.send_header('Content-Type', 'text/plain; charset=utf-8')
            self.end_headers()
            self.wfile.write(metrics_text.encode('utf-8'))
        else:
            self.send_response(404)
            self.end_headers()
    
    def log_message(self, format, *args):
        pass  # Suppress default logging

def run_metrics_server(port=9091):
    """Run the metrics server"""
    exporter = MetricsExporter()
    
    def handler(*args, **kwargs):
        return MetricsHandler(exporter, *args, **kwargs)
    
    server = HTTPServer(('0.0.0.0', port), handler)
    print(f"🚀 OpenRAN Metrics Exporter running on port {port}")
    print(f"📊 Metrics available at: http://localhost:{port}/metrics")
    print("⏹️  Press Ctrl+C to stop")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Metrics server stopped")
        server.shutdown()

if __name__ == "__main__":
    run_metrics_server()
