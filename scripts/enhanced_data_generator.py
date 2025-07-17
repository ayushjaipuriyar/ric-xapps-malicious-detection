#!/usr/bin/env python3
"""
Enhanced OpenRAN Data Generator with Public Dataset Integration
Uses realistic datasets to generate more accurate OpenRAN metrics
"""

import json
import os
import time
import random
from datetime import datetime, timedelta
import pandas as pd

class EnhancedDataGenerator:
    def __init__(self):
        self.datasets_path = "/tmp/openran_datasets"
        self.output_path = "/tmp"
        
        # Load datasets if available
        self.cell_towers = self.load_dataset("cell_towers.json")
        self.ue_traces = self.load_dataset("ue_traces.json") 
        self.network_kpis = self.load_dataset("network_kpis.json")
        self.ml_data = self.load_dataset("ml_training_data.json")
        
        # Current simulation state
        self.current_time = datetime.now()
        self.metrics = {
            'e2_messages_total': 0,
            'e2_connected_nodes': 5,
            'ric_subscription_requests_total': 0,
            'ric_control_requests_total': 0,
            'xapp_control_actions_total': 0,
            'xapp_active_subscriptions': 12,
            'xapp_ml_predictions_total': 0,
            'xapp_model_accuracy': 0.92,
            # Add missing metrics for RIC Performance dashboard
            'e2_message_latency_ms': 15.0,
            'e2_message_processing_time_ms': 8.0,
            'ric_cpu_usage_percent': 45.0,
            'ric_memory_usage_percent': 38.0,
            'ric_response_time_ms': 25.0,
            # Add missing metrics for xApp Analytics dashboard
            'xapp_cpu_usage_percent': 30.0,
            'xapp_memory_usage_mb': 256.0,
            'xapp_network_bytes_sent': 0,
            'xapp_network_bytes_received': 0,
            'xapp_prediction_accuracy': 0.88,
            'xapp_training_iterations': 0
        }
        
        print(f"📊 Enhanced OpenRAN Data Generator Initialized")
        print(f"🗂️  Datasets loaded: {self.get_loaded_datasets()}")
        
    def load_dataset(self, filename):
        """Load a dataset file if it exists"""
        filepath = os.path.join(self.datasets_path, filename)
        try:
            if os.path.exists(filepath):
                with open(filepath, 'r') as f:
                    return json.load(f)
        except Exception as e:
            print(f"⚠️  Could not load {filename}: {e}")
        return None
    
    def get_loaded_datasets(self):
        """Return list of successfully loaded datasets"""
        datasets = []
        if self.cell_towers: datasets.append("cell_towers")
        if self.ue_traces: datasets.append("ue_traces") 
        if self.network_kpis: datasets.append("network_kpis")
        if self.ml_data: datasets.append("ml_data")
        return datasets
    
    def get_realistic_ue_data(self):
        """Generate UE data based on real traces or realistic patterns"""
        ues = []
        
        if self.ue_traces:
            # Use actual trace data
            current_hour = self.current_time.hour
            
            # Filter traces for similar time
            relevant_traces = [
                trace for trace in self.ue_traces 
                if datetime.fromisoformat(trace['timestamp']).hour == current_hour
            ]
            
            if relevant_traces:
                # Sample from real traces
                selected_traces = random.sample(
                    relevant_traces, 
                    min(len(relevant_traces), random.randint(20, 50))
                )
                
                for trace in selected_traces:
                    ue = {
                        'ue_id': trace['ue_id'],
                        'ue_type': trace.get('ue_type', 'mobile'),
                        'rsrp': trace['rsrp'] + random.uniform(-2, 2),  # Add small variation
                        'rsrq': trace['rsrq'] + random.uniform(-1, 1),
                        'throughput_dl': max(1, trace['throughput_dl'] + random.uniform(-5, 5)),
                        'throughput_ul': max(0.5, trace['throughput_ul'] + random.uniform(-2, 2)),
                        'speed_kmh': trace.get('speed_kmh', 10)
                    }
                    ues.append(ue)
        
        # If no traces or need more UEs, generate additional ones
        while len(ues) < 25:  # Ensure minimum UE count
            ue_id = f"ue_{len(ues)+1:03d}"
            
            # Generate based on time of day patterns
            hour = self.current_time.hour
            if 6 <= hour <= 22:  # Daytime - better conditions
                rsrp_base = -85
                throughput_factor = 1.0
            else:  # Nighttime - fewer users, potentially better signal
                rsrp_base = -80
                throughput_factor = 1.2
            
            ue = {
                'ue_id': ue_id,
                'ue_type': random.choice(['pedestrian', 'vehicle', 'stationary']),
                'rsrp': rsrp_base + random.uniform(-20, 10),
                'rsrq': -10 + random.uniform(-8, 5),
                'throughput_dl': (30 + random.uniform(-15, 40)) * throughput_factor,
                'throughput_ul': (15 + random.uniform(-8, 20)) * throughput_factor,
                'speed_kmh': random.uniform(0, 80)
            }
            ues.append(ue)
        
        return ues
    
    def get_network_conditions(self):
        """Determine current network conditions based on time and patterns"""
        hour = self.current_time.hour
        day_of_week = self.current_time.weekday()  # 0=Monday, 6=Sunday
        
        # Load patterns from dataset or use defaults
        if self.network_kpis:
            peak_hours = self.network_kpis.get('peak_hours', [8, 9, 12, 13, 17, 18, 19, 20])
            weekend_factor = self.network_kpis.get('weekend_factor', 0.7)
            night_factor = self.network_kpis.get('night_factor', 0.3)
        else:
            peak_hours = [8, 9, 12, 13, 17, 18, 19, 20]
            weekend_factor = 0.7
            night_factor = 0.3
        
        # Calculate load factor
        load_factor = 1.0
        
        if hour in peak_hours:
            load_factor *= 1.5  # Higher load during peak hours
        elif 22 <= hour or hour <= 6:
            load_factor *= night_factor  # Lower load at night
        
        if day_of_week >= 5:  # Weekend
            load_factor *= weekend_factor
        
        return {
            'load_factor': load_factor,
            'is_peak': hour in peak_hours,
            'is_weekend': day_of_week >= 5,
            'hour': hour
        }
    
    def get_ml_model_performance(self, network_conditions, ue_data):
        """Calculate ML model performance based on current conditions"""
        
        # Base accuracy from training data if available
        if self.ml_data:
            # Sample from training data to get realistic accuracy
            sample = random.choice(self.ml_data)
            base_accuracy = 0.85 + random.uniform(0, 0.15)  # 85-100% range
        else:
            base_accuracy = 0.90
        
        # Adjust based on network conditions
        accuracy = base_accuracy
        
        # Model performs worse under high load
        if network_conditions['load_factor'] > 1.3:
            accuracy *= 0.95
        
        # Model performs better with more stable conditions
        avg_rsrp = sum(ue['rsrp'] for ue in ue_data) / len(ue_data)
        if avg_rsrp > -90:  # Good signal conditions
            accuracy *= 1.02
        elif avg_rsrp < -110:  # Poor signal conditions
            accuracy *= 0.93
        
        # Add some random variation
        accuracy += random.uniform(-0.01, 0.01)
        
        return max(0.7, min(1.0, accuracy))
    
    def update_metrics(self, network_conditions, ue_data):
        """Update OpenRAN metrics based on current conditions"""
        
        # E2 messages scale with load and UE count
        base_rate = 10
        message_increment = int(base_rate * network_conditions['load_factor'] * (len(ue_data) / 25))
        self.metrics['e2_messages_total'] += message_increment
        
        # Subscription and control requests
        sub_increment = max(1, int(message_increment * 0.3))
        control_increment = max(1, int(message_increment * 0.2))
        
        self.metrics['ric_subscription_requests_total'] += sub_increment
        self.metrics['ric_control_requests_total'] += control_increment
        
        # xApp predictions and actions
        predictions = int(len(ue_data) * network_conditions['load_factor'] * random.uniform(0.1, 0.3))
        actions = max(1, int(predictions * 0.15))
        
        self.metrics['xapp_ml_predictions_total'] += predictions
        self.metrics['xapp_control_actions_total'] += actions
        
        # Update model accuracy
        self.metrics['xapp_model_accuracy'] = self.get_ml_model_performance(network_conditions, ue_data)
        
        # Connected nodes (simulate occasional changes)
        if random.random() < 0.05:  # 5% chance of change
            change = random.choice([-1, 0, 1])
            self.metrics['e2_connected_nodes'] = max(3, min(8, self.metrics['e2_connected_nodes'] + change))
        
        # Active subscriptions
        if random.random() < 0.1:  # 10% chance of change
            change = random.choice([-1, 0, 1])
            self.metrics['xapp_active_subscriptions'] = max(5, min(25, self.metrics['xapp_active_subscriptions'] + change))
        
        # Update performance metrics based on load
        load_factor = network_conditions['load_factor']
        
        # E2 latency increases with load
        base_latency = 15.0
        self.metrics['e2_message_latency_ms'] = base_latency * (1 + load_factor * 0.5) + random.uniform(-2, 2)
        self.metrics['e2_message_processing_time_ms'] = self.metrics['e2_message_latency_ms'] * 0.6
        
        # RIC resource usage
        self.metrics['ric_cpu_usage_percent'] = min(95, 45 + (load_factor * 30) + random.uniform(-5, 5))
        self.metrics['ric_memory_usage_percent'] = min(90, 38 + (load_factor * 25) + random.uniform(-3, 3))
        self.metrics['ric_response_time_ms'] = 25 + (load_factor * 15) + random.uniform(-3, 3)
        
        # xApp metrics
        self.metrics['xapp_cpu_usage_percent'] = min(85, 30 + (predictions * 0.5) + random.uniform(-3, 3))
        self.metrics['xapp_memory_usage_mb'] = 256 + (predictions * 2) + random.uniform(-10, 10)
        
        # Network activity
        self.metrics['xapp_network_bytes_sent'] += predictions * 1024 + random.randint(0, 2048)
        self.metrics['xapp_network_bytes_received'] += predictions * 512 + random.randint(0, 1024)
        
        # ML training progress
        if random.random() < 0.1:  # 10% chance of training iteration
            self.metrics['xapp_training_iterations'] += 1
            # Prediction accuracy slowly improves with training
            self.metrics['xapp_prediction_accuracy'] = min(0.98, 
                self.metrics['xapp_prediction_accuracy'] + random.uniform(-0.01, 0.02))
    
    def generate_enhanced_data(self):
        """Generate one comprehensive data sample"""
        
        # Get current network conditions
        network_conditions = self.get_network_conditions()
        
        # Generate UE data
        ue_data = self.get_realistic_ue_data()
        
        # Update metrics
        self.update_metrics(network_conditions, ue_data)
        
        # Get cell information if available
        ran_nodes = []
        if self.cell_towers:
            # Sample a few cells
            selected_cells = random.sample(self.cell_towers, min(len(self.cell_towers), self.metrics['e2_connected_nodes']))
            for cell in selected_cells:
                node = {
                    'id': cell['cell_id'],
                    'city': cell.get('city', 'Unknown'),
                    'technology': cell.get('technology', '5G'),
                    'frequency': cell.get('frequency', 3500),
                    'status': 'active'
                }
                ran_nodes.append(node)
        else:
            # Generate basic node info
            for i in range(self.metrics['e2_connected_nodes']):
                node = {
                    'id': f'gnb_{i+1}',
                    'cell_id': f'cell_{i+1}',
                    'status': 'active'
                }
                ran_nodes.append(node)
        
        # Create complete data entry
        data_entry = {
            'timestamp': self.current_time.isoformat(),
            'metrics': self.metrics.copy(),
            'network_conditions': network_conditions,
            'ran_nodes': ran_nodes,
            'ues': ue_data,
            'data_source': 'enhanced_generator_with_datasets'
        }
        
        return data_entry
    
    def save_data(self, data):
        """Save data to JSON file"""
        timestamp = int(time.time())
        filename = f'{self.output_path}/openran_data_{timestamp}.json'
        
        try:
            with open(filename, 'w') as f:
                json.dump(data, f, indent=2)
            return filename
        except Exception as e:
            print(f"❌ Error saving data: {e}")
            return None
    
    def run_continuous(self, interval=30):
        """Run continuous enhanced data generation"""
        print("🚀 Starting Enhanced OpenRAN Data Generator...")
        print(f"📊 Using datasets: {', '.join(self.get_loaded_datasets())}")
        print(f"⏱️  Generating data every {interval} seconds")
        print("⏹️  Press Ctrl+C to stop\n")
        
        try:
            while True:
                # Generate data
                data = self.generate_enhanced_data()
                filename = self.save_data(data)
                
                if filename:
                    conditions = data['network_conditions']
                    print(f"📈 {self.current_time.strftime('%H:%M:%S')} | "
                          f"Load: {conditions['load_factor']:.2f} | "
                          f"UEs: {len(data['ues'])} | "
                          f"Nodes: {data['metrics']['e2_connected_nodes']} | "
                          f"Accuracy: {data['metrics']['xapp_model_accuracy']:.3f}")
                
                # Advance time
                self.current_time += timedelta(seconds=interval)
                time.sleep(interval)
                
        except KeyboardInterrupt:
            print("\n🛑 Enhanced data generation stopped")

def main():
    generator = EnhancedDataGenerator()
    
    if not generator.get_loaded_datasets():
        print("⚠️  No datasets found. Run dataset_integrator.py first to download datasets.")
        print("Falling back to basic generation...")
    
    generator.run_continuous(30)

if __name__ == "__main__":
    main()
