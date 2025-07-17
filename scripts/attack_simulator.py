#!/usr/bin/env python3
"""
OpenRAN Attack Pattern Simulator for Security Research
Simulates known attack patterns for Near-RT RIC intrusion detection research
"""

import json
import time
import random
from datetime import datetime, timedelta
from dataclasses import dataclass
from typing import Dict, List, Any
import threading

@dataclass
class AttackPattern:
    name: str
    description: str
    severity: str  # low, medium, high, critical
    target_component: str
    indicators: List[str]
    metrics_impact: Dict[str, Any]

class OpenRANAttackSimulator:
    def __init__(self):
        self.attack_patterns = self._define_attack_patterns()
        self.normal_metrics = self._load_baseline_metrics()
        self.attack_active = False
        self.current_attack = None
        self.attack_start_time = None
        
    def _define_attack_patterns(self) -> Dict[str, AttackPattern]:
        """Define known OpenRAN attack patterns"""
        return {
            "e2_message_flooding": AttackPattern(
                name="E2 Message Flooding",
                description="Overwhelming E2 termination with excessive messages",
                severity="high",
                target_component="E2 Interface",
                indicators=[
                    "Abnormally high E2 message rate",
                    "E2 processing latency increase",
                    "Memory/CPU spike on E2 termination"
                ],
                metrics_impact={
                    "e2_messages_total": {"multiplier": 10, "pattern": "spike"},
                    "e2_processing_latency": {"multiplier": 5, "pattern": "gradual_increase"},
                    "e2_error_rate": {"multiplier": 3, "pattern": "spike"},
                    "e2_connected_nodes": {"multiplier": 0.7, "pattern": "degradation"},
                    "connection_health": {"multiplier": 0, "pattern": "degradation"}
                }
            ),
            
            "malformed_e2_messages": AttackPattern(
                name="Malformed E2 Messages",
                description="Invalid ASN.1 encoding in E2 messages",
                severity="medium",
                target_component="E2 Interface",
                indicators=[
                    "E2 parsing errors",
                    "Dropped E2 messages",
                    "E2 service degradation"
                ],
                metrics_impact={
                    "e2_parse_errors": {"multiplier": 20, "pattern": "spike"},
                    "e2_dropped_messages": {"multiplier": 15, "pattern": "gradual_increase"},
                    "e2_service_availability": {"multiplier": 0.7, "pattern": "degradation"}
                }
            ),
            
            "subscription_hijacking": AttackPattern(
                name="Subscription Hijacking",
                description="Unauthorized subscription requests",
                severity="high",
                target_component="RIC Platform",
                indicators=[
                    "Unauthorized subscription attempts",
                    "Subscription from unknown sources",
                    "Data access violations"
                ],
                metrics_impact={
                    "ric_unauthorized_subscriptions": {"multiplier": 50, "pattern": "spike"},
                    "ric_subscription_requests_total": {"multiplier": 3, "pattern": "gradual_increase"},
                    "security_violations": {"multiplier": 10, "pattern": "spike"},
                    "connection_health": {"multiplier": 0, "pattern": "degradation"}
                }
            ),
            
            "rogue_xapp": AttackPattern(
                name="Rogue xApp Deployment",
                description="Unauthorized xApp installation and execution",
                severity="critical",
                target_component="xApp Platform",
                indicators=[
                    "Unauthorized xApp deployment",
                    "Excessive resource consumption",
                    "Abnormal xApp behavior"
                ],
                metrics_impact={
                    "xapp_unauthorized_deployments": {"multiplier": 5, "pattern": "spike"},
                    "xapp_cpu_usage": {"multiplier": 8, "pattern": "sustained_high"},
                    "xapp_memory_usage": {"multiplier": 6, "pattern": "sustained_high"},
                    "xapp_network_traffic": {"multiplier": 10, "pattern": "spike"},
                    "xapp_active_subscriptions": {"multiplier": 0.5, "pattern": "degradation"},
                    "xapp_ml_predictions_total": {"multiplier": 0.3, "pattern": "degradation"}
                }
            ),
            
            "ml_model_poisoning": AttackPattern(
                name="ML Model Poisoning",
                description="Corrupted training data affecting ML models",
                severity="high",
                target_component="xApp ML Models",
                indicators=[
                    "ML model accuracy degradation",
                    "Abnormal prediction patterns",
                    "Training data anomalies"
                ],
                metrics_impact={
                    "xapp_model_accuracy": {"multiplier": 0.6, "pattern": "degradation"},
                    "xapp_prediction_anomalies": {"multiplier": 25, "pattern": "spike"},
                    "xapp_training_errors": {"multiplier": 10, "pattern": "gradual_increase"},
                    "xapp_ml_predictions_total": {"multiplier": 0.4, "pattern": "degradation"}
                }
            ),
            
            "resource_exhaustion": AttackPattern(
                name="Resource Exhaustion Attack",
                description="Deliberate resource consumption to cause DoS",
                severity="critical",
                target_component="RIC Platform",
                indicators=[
                    "Abnormally high resource usage",
                    "Service response time degradation",
                    "Memory/CPU exhaustion"
                ],
                metrics_impact={
                    "ric_cpu_usage": {"multiplier": 9, "pattern": "sustained_high"},
                    "ric_memory_usage": {"multiplier": 8, "pattern": "sustained_high"},
                    "ric_response_time": {"multiplier": 10, "pattern": "gradual_increase"},
                    "ric_service_availability": {"multiplier": 0.5, "pattern": "degradation"},
                    "connection_health": {"multiplier": 0, "pattern": "degradation"},
                    "e2_connected_nodes": {"multiplier": 0.6, "pattern": "degradation"},
                    "xapp_active_subscriptions": {"multiplier": 0.3, "pattern": "degradation"}
                }
            )
        }
    
    def _load_baseline_metrics(self) -> Dict[str, float]:
        """Load baseline metrics for comparison"""
        return {
            # Original OpenRAN metrics that appear in the main dashboard
            "e2_messages_total": 50,
            "e2_connected_nodes": 5,
            "ric_subscription_requests_total": 15,
            "xapp_active_subscriptions": 12,
            "xapp_ml_predictions_total": 25,
            "xapp_model_accuracy": 0.92,
            "connection_health": 1,
            
            # Security-specific metrics
            "e2_processing_latency": 10,
            "e2_error_rate": 0.1,
            "e2_parse_errors": 0,
            "e2_dropped_messages": 0,
            "e2_service_availability": 99.9,
            "ric_unauthorized_subscriptions": 0,
            "security_violations": 0,
            "xapp_unauthorized_deployments": 0,
            "xapp_cpu_usage": 25,
            "xapp_memory_usage": 30,
            "xapp_network_traffic": 100,
            "xapp_prediction_anomalies": 0,
            "xapp_training_errors": 0,
            "ric_cpu_usage": 40,
            "ric_memory_usage": 35,
            "ric_response_time": 50,
            "ric_service_availability": 99.8
        }
    
    def start_attack(self, attack_name: str, duration_minutes: int = 10):
        """Start simulating an attack pattern"""
        if attack_name not in self.attack_patterns:
            raise ValueError(f"Unknown attack pattern: {attack_name}")
        
        self.current_attack = self.attack_patterns[attack_name]
        self.attack_active = True
        self.attack_start_time = datetime.now()
        
        print(f"🚨 ATTACK SIMULATION STARTED: {self.current_attack.name}")
        print(f"📋 Description: {self.current_attack.description}")
        print(f"⚠️  Severity: {self.current_attack.severity.upper()}")
        print(f"🎯 Target: {self.current_attack.target_component}")
        print(f"⏱️  Duration: {duration_minutes} minutes")
        print(f"🔍 Indicators to watch for:")
        for indicator in self.current_attack.indicators:
            print(f"   • {indicator}")
        
        # Start attack simulation thread
        attack_thread = threading.Thread(
            target=self._run_attack_simulation,
            args=(duration_minutes,),
            daemon=True
        )
        attack_thread.start()
    
    def _run_attack_simulation(self, duration_minutes: int):
        """Run the attack simulation for specified duration"""
        end_time = datetime.now() + timedelta(minutes=duration_minutes)
        
        while datetime.now() < end_time and self.attack_active:
            # Generate attack metrics
            attack_metrics = self._generate_attack_metrics()
            
            # Save attack data
            self._save_attack_data(attack_metrics)
            
            time.sleep(10)  # Update every 10 seconds
        
        self.stop_attack()
    
    def _generate_attack_metrics(self) -> Dict[str, Any]:
        """Generate metrics showing attack impact"""
        attack_metrics = self.normal_metrics.copy()
        
        if not self.current_attack:
            return attack_metrics
        
        # Calculate attack progression (0.0 to 1.0)
        elapsed = (datetime.now() - self.attack_start_time).total_seconds()
        progression = min(elapsed / 300.0, 1.0)  # 5 minute ramp-up
        
        # Apply attack patterns
        for metric, impact in self.current_attack.metrics_impact.items():
            base_value = self.normal_metrics.get(metric, 0)
            multiplier = impact["multiplier"]
            pattern = impact["pattern"]
            
            if pattern == "spike":
                # Immediate spike with some randomness
                attack_metrics[metric] = base_value * multiplier * (0.8 + random.uniform(0, 0.4))
            
            elif pattern == "gradual_increase":
                # Gradual increase over time
                attack_metrics[metric] = base_value * (1 + (multiplier - 1) * progression)
            
            elif pattern == "sustained_high":
                # Sustained high values
                attack_metrics[metric] = base_value * multiplier * (0.9 + random.uniform(0, 0.2))
            
            elif pattern == "degradation":
                # Service degradation (lower values)
                attack_metrics[metric] = base_value * multiplier * (0.9 + random.uniform(0, 0.2))
        
        return attack_metrics
    
    def _save_attack_data(self, metrics: Dict[str, Any]):
        """Save attack simulation data"""
        attack_data = {
            "timestamp": datetime.now().isoformat(),
            "attack_active": self.attack_active,
            "attack_name": self.current_attack.name if self.current_attack else None,
            "attack_severity": self.current_attack.severity if self.current_attack else None,
            "attack_target": self.current_attack.target_component if self.current_attack else None,
            "security_metrics": metrics,
            "data_source": "attack_simulator"
        }
        
        # Save to file for metrics exporter
        timestamp = int(time.time())
        filename = f"/tmp/openran_attack_data_{timestamp}.json"
        
        with open(filename, 'w') as f:
            json.dump(attack_data, f, indent=2)
    
    def stop_attack(self):
        """Stop the current attack simulation"""
        if self.attack_active:
            print(f"🛑 ATTACK SIMULATION STOPPED: {self.current_attack.name}")
            self.attack_active = False
            self.current_attack = None
            self.attack_start_time = None
    
    def get_available_attacks(self) -> List[str]:
        """Get list of available attack patterns"""
        return list(self.attack_patterns.keys())
    
    def get_attack_info(self, attack_name: str) -> AttackPattern:
        """Get information about a specific attack pattern"""
        return self.attack_patterns.get(attack_name)

def main():
    simulator = OpenRANAttackSimulator()
    
    print("🔒 OpenRAN Attack Simulator for Security Research")
    print("=" * 50)
    print("Available attack patterns:")
    
    for i, attack_name in enumerate(simulator.get_available_attacks(), 1):
        attack = simulator.get_attack_info(attack_name)
        print(f"{i}. {attack.name} ({attack.severity})")
        print(f"   Target: {attack.target_component}")
        print(f"   {attack.description}")
        print()
    
    # Interactive mode
    while True:
        try:
            choice = input("Enter attack number to simulate (or 'quit'): ").strip()
            
            if choice.lower() == 'quit':
                break
            
            attack_index = int(choice) - 1
            attack_names = simulator.get_available_attacks()
            
            if 0 <= attack_index < len(attack_names):
                attack_name = attack_names[attack_index]
                duration = int(input("Duration in minutes (default 10): ") or "10")
                simulator.start_attack(attack_name, duration)
                
                input("Press Enter to stop the attack...")
                simulator.stop_attack()
            else:
                print("Invalid choice. Please try again.")
                
        except (ValueError, KeyboardInterrupt):
            print("\nExiting...")
            break
    
    simulator.stop_attack()

if __name__ == "__main__":
    main()