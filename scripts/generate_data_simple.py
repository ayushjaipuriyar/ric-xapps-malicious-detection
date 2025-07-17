#!/usr/bin/env python3
"""
Simple OpenRAN Data Generator (No External Dependencies)
Generates basic OpenRAN metrics without requiring requests library
"""

import json
import time
import random
import os
from datetime import datetime

class SimpleOpenRANGenerator:
    def __init__(self):
        self.metrics = {
            'e2_messages_total': 0,
            'e2_connected_nodes': 5,
            'ric_subscription_requests_total': 0,
            'ric_control_requests_total': 0,
            'xapp_control_actions_total': 0,
            'xapp_active_subscriptions': 10,
            'xapp_ml_predictions_total': 0,
            'xapp_model_accuracy': 0.92
        }
        
        # Ensure tmp directory exists
        os.makedirs('/tmp', exist_ok=True)
        
    def generate_sample_data(self):
        """Generate one sample of OpenRAN data"""
        
        # Update counters
        self.metrics['e2_messages_total'] += random.randint(5, 15)
        self.metrics['ric_subscription_requests_total'] += random.randint(0, 3)
        self.metrics['ric_control_requests_total'] += random.randint(0, 5)
        self.metrics['xapp_control_actions_total'] += random.randint(0, 2)
        self.metrics['xapp_ml_predictions_total'] += random.randint(1, 8)
        
        # Slowly varying metrics
        self.metrics['e2_connected_nodes'] += random.choice([-1, 0, 0, 0, 1])
        self.metrics['e2_connected_nodes'] = max(3, min(8, self.metrics['e2_connected_nodes']))
        
        self.metrics['xapp_active_subscriptions'] += random.choice([-1, 0, 0, 1])
        self.metrics['xapp_active_subscriptions'] = max(5, min(20, self.metrics['xapp_active_subscriptions']))
        
        self.metrics['xapp_model_accuracy'] += random.uniform(-0.005, 0.005)
        self.metrics['xapp_model_accuracy'] = max(0.8, min(1.0, self.metrics['xapp_model_accuracy']))
        
        # Generate UE data
        ues = []
        for i in range(random.randint(15, 25)):
            ue = {
                'ue_id': f'ue_{i+1}',
                'imsi': f'001010000000{i+1:03d}',
                'rsrp': random.randint(-120, -70),
                'rsrq': random.randint(-20, -5),
                'throughput_dl': random.randint(10, 100),
                'throughput_ul': random.randint(5, 50)
            }
            ues.append(ue)
        
        # Create complete data entry
        data_entry = {
            'timestamp': datetime.now().isoformat(),
            'metrics': self.metrics.copy(),
            'ran_nodes': [
                {'id': f'gnb_{i}', 'cell_id': f'cell_{i}', 'status': 'active'}
                for i in range(1, self.metrics['e2_connected_nodes'] + 1)
            ],
            'ues': ues
        }
        
        return data_entry
    
    def save_data(self, data):
        """Save data to JSON file"""
        timestamp = int(time.time())
        filename = f'/tmp/openran_data_{timestamp}.json'
        
        try:
            with open(filename, 'w') as f:
                json.dump(data, f, indent=2)
            print(f"✅ Data saved to {filename}")
            return True
        except Exception as e:
            print(f"❌ Error saving data: {e}")
            return False
    
    def run_continuous(self, interval=30):
        """Run continuous data generation"""
        print("🚀 Starting Simple OpenRAN Data Generator...")
        print(f"📊 Generating data every {interval} seconds")
        print("📁 Data files saved to /tmp/openran_data_*.json")
        print("⏹️  Press Ctrl+C to stop\n")
        
        try:
            while True:
                data = self.generate_sample_data()
                success = self.save_data(data)
                
                if success:
                    print(f"📈 Stats: {data['metrics']['e2_messages_total']} E2 msgs, "
                          f"{data['metrics']['e2_connected_nodes']} nodes, "
                          f"{len(data['ues'])} UEs, "
                          f"Model: {data['metrics']['xapp_model_accuracy']:.3f}")
                
                time.sleep(interval)
                
        except KeyboardInterrupt:
            print("\n🛑 Data generation stopped by user")
        except Exception as e:
            print(f"\n❌ Error in data generation: {e}")

def main():
    generator = SimpleOpenRANGenerator()
    
    print("Simple OpenRAN Data Generator")
    print("=" * 40)
    
    # Generate a few sample files immediately
    print("Generating initial sample data...")
    for i in range(3):
        data = generator.generate_sample_data()
        generator.save_data(data)
        time.sleep(1)
    
    print(f"\n✅ Initial data generated!")
    print("\nTo run continuous generation:")
    print("python3 scripts/generate_data_simple.py")
    
    # Ask if user wants to continue with continuous generation
    try:
        choice = input("\nStart continuous generation? (y/n): ").strip().lower()
        if choice in ['y', 'yes']:
            generator.run_continuous(30)  # Generate every 30 seconds
    except (KeyboardInterrupt, EOFError):
        print("\nExiting...")

if __name__ == "__main__":
    main()
