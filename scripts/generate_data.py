#!/usr/bin/env python3
"""
OpenRAN Data Generator
Generates realistic OpenRAN metrics and data for testing and demonstration
"""

import time
import random
import json
import requests
import threading
from datetime import datetime, timedelta
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class OpenRANDataGenerator:
    def __init__(self):
        self.running = False
        self.metrics = {
            'e2_messages_total': 0,
            'e2_connected_nodes': random.randint(3, 8),
            'ric_subscription_requests_total': 0,
            'ric_control_requests_total': 0,
            'xapp_control_actions_total': 0,
            'xapp_active_subscriptions': random.randint(5, 15),
            'xapp_ml_predictions_total': 0,
            'xapp_model_accuracy': random.uniform(0.85, 0.98)
        }
        
        # RAN Node data
        self.ran_nodes = [
            {'id': f'gnb_{i}', 'cell_id': f'cell_{i}', 'status': 'active'} 
            for i in range(1, self.metrics['e2_connected_nodes'] + 1)
        ]
        
        # UE data
        self.ues = [
            {
                'ue_id': f'ue_{i}',
                'imsi': f'001010000000{i:03d}',
                'rsrp': random.randint(-120, -70),
                'rsrq': random.randint(-20, -5),
                'throughput_dl': random.randint(10, 100),
                'throughput_ul': random.randint(5, 50)
            }
            for i in range(1, 51)  # 50 UEs
        ]

    def generate_e2_messages(self):
        """Generate E2 interface messages"""
        message_types = ['subscription_request', 'subscription_response', 
                        'indication', 'control_request', 'control_response']
        
        while self.running:
            # Generate E2 messages
            for _ in range(random.randint(5, 15)):
                self.metrics['e2_messages_total'] += 1
                if random.choice(message_types) == 'subscription_request':
                    self.metrics['ric_subscription_requests_total'] += 1
                elif random.choice(message_types) == 'control_request':
                    self.metrics['ric_control_requests_total'] += 1
            
            # Update connected nodes (simulate nodes joining/leaving)
            if random.random() < 0.05:  # 5% chance of change
                change = random.choice([-1, 1])
                new_count = max(1, min(10, self.metrics['e2_connected_nodes'] + change))
                self.metrics['e2_connected_nodes'] = new_count
            
            time.sleep(1)

    def generate_xapp_data(self):
        """Generate xApp ML/AI data"""
        while self.running:
            # Generate ML predictions
            if random.random() < 0.7:  # 70% chance of prediction
                self.metrics['xapp_ml_predictions_total'] += 1
                
            # Generate control actions
            if random.random() < 0.3:  # 30% chance of control action
                self.metrics['xapp_control_actions_total'] += 1
            
            # Update model accuracy (slowly drift)
            accuracy_change = random.uniform(-0.001, 0.001)
            new_accuracy = self.metrics['xapp_model_accuracy'] + accuracy_change
            self.metrics['xapp_model_accuracy'] = max(0.5, min(1.0, new_accuracy))
            
            # Update active subscriptions
            if random.random() < 0.1:  # 10% chance of change
                change = random.choice([-1, 1])
                new_subs = max(1, min(20, self.metrics['xapp_active_subscriptions'] + change))
                self.metrics['xapp_active_subscriptions'] = new_subs
            
            time.sleep(2)

    def generate_ue_data(self):
        """Generate UE (User Equipment) data"""
        while self.running:
            for ue in self.ues:
                # Update signal quality (RSRP, RSRQ)
                ue['rsrp'] += random.randint(-5, 5)
                ue['rsrp'] = max(-130, min(-60, ue['rsrp']))
                
                ue['rsrq'] += random.randint(-2, 2)
                ue['rsrq'] = max(-25, min(-3, ue['rsrq']))
                
                # Update throughput based on signal quality
                signal_factor = (ue['rsrp'] + 130) / 70  # Normalize RSRP
                base_dl = 50 * signal_factor
                base_ul = 25 * signal_factor
                
                ue['throughput_dl'] = max(1, int(base_dl + random.randint(-20, 20)))
                ue['throughput_ul'] = max(1, int(base_ul + random.randint(-10, 10)))
            
            time.sleep(5)

    def export_metrics(self):
        """Export metrics in Prometheus format"""
        prometheus_metrics = []
        
        # Basic counters
        prometheus_metrics.append(f"e2_messages_total {self.metrics['e2_messages_total']}")
        prometheus_metrics.append(f"e2_connected_nodes {self.metrics['e2_connected_nodes']}")
        prometheus_metrics.append(f"ric_subscription_requests_total {self.metrics['ric_subscription_requests_total']}")
        prometheus_metrics.append(f"ric_control_requests_total {self.metrics['ric_control_requests_total']}")
        prometheus_metrics.append(f"xapp_control_actions_total {self.metrics['xapp_control_actions_total']}")
        prometheus_metrics.append(f"xapp_active_subscriptions {self.metrics['xapp_active_subscriptions']}")
        prometheus_metrics.append(f"xapp_ml_predictions_total {self.metrics['xapp_ml_predictions_total']}")
        prometheus_metrics.append(f"xapp_model_accuracy {self.metrics['xapp_model_accuracy']:.4f}")
        
        # UE metrics aggregates
        avg_rsrp = sum(ue['rsrp'] for ue in self.ues) / len(self.ues)
        avg_rsrq = sum(ue['rsrq'] for ue in self.ues) / len(self.ues)
        total_dl = sum(ue['throughput_dl'] for ue in self.ues)
        total_ul = sum(ue['throughput_ul'] for ue in self.ues)
        
        prometheus_metrics.append(f"ran_ue_avg_rsrp {avg_rsrp:.2f}")
        prometheus_metrics.append(f"ran_ue_avg_rsrq {avg_rsrq:.2f}")
        prometheus_metrics.append(f"ran_total_throughput_dl {total_dl}")
        prometheus_metrics.append(f"ran_total_throughput_ul {total_ul}")
        prometheus_metrics.append(f"ran_active_ues {len(self.ues)}")
        
        return "\n".join(prometheus_metrics)

    def save_data_to_file(self):
        """Save generated data to JSON files for analysis"""
        while self.running:
            timestamp = datetime.now().isoformat()
            
            # Save metrics snapshot
            data = {
                'timestamp': timestamp,
                'metrics': self.metrics.copy(),
                'ran_nodes': self.ran_nodes.copy(),
                'ues': self.ues.copy()
            }
            
            filename = f"/tmp/openran_data_{int(time.time())}.json"
            try:
                with open(filename, 'w') as f:
                    json.dump(data, f, indent=2)
                logger.info(f"Data saved to {filename}")
            except Exception as e:
                logger.error(f"Failed to save data: {e}")
            
            time.sleep(60)  # Save every minute

    def start(self):
        """Start data generation"""
        logger.info("Starting OpenRAN data generation...")
        self.running = True
        
        # Start generation threads
        threads = [
            threading.Thread(target=self.generate_e2_messages),
            threading.Thread(target=self.generate_xapp_data),
            threading.Thread(target=self.generate_ue_data),
            threading.Thread(target=self.save_data_to_file)
        ]
        
        for thread in threads:
            thread.daemon = True
            thread.start()
        
        return threads

    def stop(self):
        """Stop data generation"""
        logger.info("Stopping data generation...")
        self.running = False

    def get_status(self):
        """Get current status and metrics"""
        return {
            'running': self.running,
            'metrics': self.metrics,
            'connected_nodes': len(self.ran_nodes),
            'active_ues': len(self.ues)
        }

def main():
    generator = OpenRANDataGenerator()
    
    try:
        threads = generator.start()
        
        logger.info("Data generation started. Press Ctrl+C to stop.")
        logger.info("Metrics will be saved to /tmp/openran_data_*.json files")
        logger.info("Access points:")
        logger.info("- Grafana: http://localhost:3000 (admin/admin)")
        logger.info("- Prometheus: http://localhost:9090")
        logger.info("- Kibana: http://localhost:5601")
        
        # Keep the main thread alive
        while True:
            time.sleep(10)
            status = generator.get_status()
            logger.info(f"Status: {status['connected_nodes']} nodes, {status['active_ues']} UEs, "
                       f"E2 messages: {status['metrics']['e2_messages_total']}")
            
    except KeyboardInterrupt:
        logger.info("Received interrupt signal")
    finally:
        generator.stop()
        logger.info("Data generation stopped")

if __name__ == "__main__":
    main()
