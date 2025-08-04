#!/usr/bin/env python3
"""
Fraud Detection Demo - A simplified demonstration of fraud detection concepts
using graph-based analysis without requiring Neo4j installation.
"""

import json
from collections import defaultdict
from datetime import datetime, timedelta
import random

class SimpleFraudDetector:
    """A simple in-memory fraud detection system to demonstrate concepts"""
    
    def __init__(self):
        self.users = {}
        self.devices = {}
        self.accounts = {}
        self.transactions = {}
        self.relationships = defaultdict(list)
        
    def add_user(self, user_id, name, email, phone, risk_score):
        """Add a user to the system"""
        self.users[user_id] = {
            'id': user_id,
            'name': name,
            'email': email,
            'phone': phone,
            'risk_score': risk_score
        }
    
    def add_device(self, device_id, device_type, ip, location):
        """Add a device to the system"""
        self.devices[device_id] = {
            'id': device_id,
            'type': device_type,
            'ip': ip,
            'location': location
        }
    
    def add_account(self, account_id, bank, account_type, balance):
        """Add a bank account to the system"""
        self.accounts[account_id] = {
            'id': account_id,
            'bank': bank,
            'account_type': account_type,
            'balance': balance
        }
    
    def add_transaction(self, transaction_id, from_account, to_account, amount, status, timestamp):
        """Add a transaction to the system"""
        self.transactions[transaction_id] = {
            'id': transaction_id,
            'from_account': from_account,
            'to_account': to_account,
            'amount': amount,
            'status': status,
            'timestamp': timestamp
        }
    
    def create_relationship(self, from_entity, to_entity, relationship_type, properties=None):
        """Create a relationship between entities"""
        if properties is None:
            properties = {}
        self.relationships[(from_entity, to_entity)].append({
            'type': relationship_type,
            'properties': properties
        })
    
    def detect_device_sharing(self):
        """Detect users sharing the same device"""
        device_users = defaultdict(list)
        
        # Find all user-device relationships
        for (from_entity, to_entity), rels in self.relationships.items():
            for rel in rels:
                if rel['type'] == 'USES':
                    if from_entity in self.users and to_entity in self.devices:
                        device_users[to_entity].append(from_entity)
        
        # Find devices with multiple users
        suspicious_devices = []
        for device_id, users in device_users.items():
            if len(users) > 1:
                device = self.devices[device_id]
                user_names = [self.users[user_id]['name'] for user_id in users]
                avg_risk = sum(self.users[user_id]['risk_score'] for user_id in users) / len(users)
                
                suspicious_devices.append({
                    'device_ip': device['ip'],
                    'users': user_names,
                    'avg_risk_score': avg_risk,
                    'risk_level': 'HIGH' if avg_risk > 0.5 else 'MEDIUM'
                })
        
        return suspicious_devices
    
    def detect_rapid_transfers(self):
        """Detect rapid transfer patterns"""
        account_transfers = defaultdict(list)
        
        # Group transactions by account pairs
        for transaction_id, transaction in self.transactions.items():
            key = (transaction['from_account'], transaction['to_account'])
            account_transfers[key].append(transaction)
        
        # Find suspicious patterns
        suspicious_patterns = []
        recent_time = datetime.now() - timedelta(minutes=30)
        
        for (from_acc, to_acc), transfers in account_transfers.items():
            recent_transfers = [t for t in transfers if t['timestamp'] > recent_time]
            
            if len(recent_transfers) >= 3:
                total_amount = sum(t['amount'] for t in recent_transfers)
                from_bank = self.accounts[from_acc]['bank']
                to_bank = self.accounts[to_acc]['bank']
                
                suspicious_patterns.append({
                    'from_account': from_acc,
                    'to_account': to_acc,
                    'from_bank': from_bank,
                    'to_bank': to_bank,
                    'transfer_count': len(recent_transfers),
                    'total_amount': total_amount,
                    'risk_level': 'HIGH' if total_amount > 100000 else 'MEDIUM'
                })
        
        return suspicious_patterns
    
    def detect_large_transactions(self):
        """Detect unusually large transactions"""
        large_transactions = []
        
        for transaction_id, transaction in self.transactions.items():
            if transaction['amount'] > 10000:
                from_account = self.accounts[transaction['from_account']]
                to_account = self.accounts[transaction['to_account']]
                
                # Find the user who owns the from_account
                user_name = "Unknown"
                for (from_entity, to_entity), rels in self.relationships.items():
                    for rel in rels:
                        if rel['type'] == 'OWNS' and to_entity == transaction['from_account']:
                            if from_entity in self.users:
                                user_name = self.users[from_entity]['name']
                                break
                
                large_transactions.append({
                    'user_name': user_name,
                    'amount': transaction['amount'],
                    'from_bank': from_account['bank'],
                    'to_bank': to_account['bank'],
                    'timestamp': transaction['timestamp'],
                    'risk_level': 'CRITICAL' if transaction['amount'] > 50000 else 'HIGH'
                })
        
        return sorted(large_transactions, key=lambda x: x['amount'], reverse=True)
    
    def detect_money_laundering_patterns(self):
        """Detect potential money laundering patterns"""
        # This is a simplified version - real implementation would be more complex
        laundering_patterns = []
        
        # Look for patterns of transfers through intermediate accounts
        for transaction_id, transaction in self.transactions.items():
            if transaction['amount'] > 50000:
                from_account = self.accounts[transaction['from_account']]
                to_account = self.accounts[transaction['to_account']]
                
                # Check if this is part of a laundering pattern
                if from_account['bank'] == 'Offshore Bank' or to_account['bank'] == 'Offshore Bank':
                    laundering_patterns.append({
                        'transaction_id': transaction_id,
                        'amount': transaction['amount'],
                        'from_bank': from_account['bank'],
                        'to_bank': to_account['bank'],
                        'risk_level': 'HIGH'
                    })
        
        return laundering_patterns
    
    def detect_account_takeover_indicators(self):
        """Detect potential account takeover indicators"""
        takeover_indicators = []
        
        for user_id, user in self.users.items():
            # Count devices per user
            device_count = 0
            unknown_location_devices = 0
            
            for (from_entity, to_entity), rels in self.relationships.items():
                for rel in rels:
                    if rel['type'] == 'USES' and from_entity == user_id:
                        device_count += 1
                        if to_entity in self.devices and self.devices[to_entity]['location'] == 'Unknown':
                            unknown_location_devices += 1
            
            # Count accounts per user
            account_count = 0
            for (from_entity, to_entity), rels in self.relationships.items():
                for rel in rels:
                    if rel['type'] == 'OWNS' and from_entity == user_id:
                        account_count += 1
            
            # Calculate risk score
            risk_score = device_count + account_count + unknown_location_devices
            
            if risk_score >= 5:
                takeover_indicators.append({
                    'user_name': user['name'],
                    'device_count': device_count,
                    'account_count': account_count,
                    'unknown_location_devices': unknown_location_devices,
                    'risk_score': risk_score,
                    'risk_level': 'CRITICAL' if risk_score >= 8 else 'HIGH'
                })
        
        return sorted(takeover_indicators, key=lambda x: x['risk_score'], reverse=True)

def create_sample_fraud_data():
    """Create sample data for fraud detection demonstration"""
    detector = SimpleFraudDetector()
    
    # Add legitimate users
    detector.add_user("U001", "Alice Johnson", "alice@email.com", "+1-555-0101", 0.1)
    detector.add_user("U002", "Bob Smith", "bob@email.com", "+1-555-0102", 0.2)
    detector.add_user("U003", "Carol Davis", "carol@email.com", "+1-555-0103", 0.1)
    
    # Add suspicious users
    detector.add_user("U101", "Frank Fraud", "frank@fake.com", "+1-555-9999", 0.9)
    detector.add_user("U102", "Grace Scammer", "grace@scam.net", "+1-555-9998", 0.8)
    detector.add_user("U103", "Henry Thief", "henry@stolen.org", "+1-555-9997", 0.7)
    
    # Add devices
    detector.add_device("D001", "laptop", "192.168.1.100", "New York")
    detector.add_device("D002", "mobile", "192.168.1.101", "San Francisco")
    detector.add_device("D003", "tablet", "192.168.1.102", "Boston")
    detector.add_device("D004", "laptop", "10.0.0.50", "Unknown")  # Suspicious
    detector.add_device("D005", "mobile", "10.0.0.51", "Unknown")  # Suspicious
    
    # Add accounts
    detector.add_account("A001", "Chase", "checking", 5000)
    detector.add_account("A002", "Wells Fargo", "savings", 15000)
    detector.add_account("A003", "Bank of America", "checking", 3000)
    detector.add_account("A101", "Offshore Bank", "checking", 100000)  # Suspicious
    detector.add_account("A102", "Offshore Bank", "savings", 500000)   # Suspicious
    
    # Add transactions
    now = datetime.now()
    detector.add_transaction("T001", "A001", "A002", 100, "completed", now - timedelta(hours=2))
    detector.add_transaction("T002", "A002", "A003", 250, "completed", now - timedelta(hours=1))
    detector.add_transaction("T003", "A003", "A001", 75, "completed", now - timedelta(minutes=30))
    
    # Add suspicious transactions
    detector.add_transaction("T101", "A101", "A102", 50000, "pending", now - timedelta(minutes=10))
    detector.add_transaction("T102", "A102", "A101", 25000, "pending", now - timedelta(minutes=8))
    detector.add_transaction("T103", "A101", "A102", 100000, "pending", now - timedelta(minutes=5))
    
    # Create relationships
    # User-Device relationships
    detector.create_relationship("U001", "D001", "USES")
    detector.create_relationship("U002", "D002", "USES")
    detector.create_relationship("U003", "D003", "USES")
    
    # Suspicious device sharing
    detector.create_relationship("U101", "D004", "USES")
    detector.create_relationship("U102", "D004", "USES")  # Same device
    detector.create_relationship("U103", "D005", "USES")
    
    # User-Account relationships
    detector.create_relationship("U001", "A001", "OWNS")
    detector.create_relationship("U002", "A002", "OWNS")
    detector.create_relationship("U003", "A003", "OWNS")
    detector.create_relationship("U101", "A101", "OWNS")
    detector.create_relationship("U102", "A102", "OWNS")
    
    return detector

def demonstrate_fraud_detection():
    """Demonstrate various fraud detection techniques"""
    print("=== Fraud Detection System Demo ===\n")
    
    # Create sample data
    detector = create_sample_fraud_data()
    
    # 1. Device Sharing Detection
    print("1. Device Sharing Fraud Detection:")
    device_sharing = detector.detect_device_sharing()
    for incident in device_sharing:
        print(f"   Device {incident['device_ip']} shared by: {', '.join(incident['users'])}")
        print(f"     Average risk score: {incident['avg_risk_score']:.2f} - Risk: {incident['risk_level']}")
    print()
    
    # 2. Rapid Transfer Pattern Detection
    print("2. Rapid Transfer Pattern Detection:")
    rapid_transfers = detector.detect_rapid_transfers()
    for pattern in rapid_transfers:
        print(f"   {pattern['transfer_count']} transfers between {pattern['from_account']} and {pattern['to_account']}")
        print(f"     Banks: {pattern['from_bank']} -> {pattern['to_bank']}")
        print(f"     Total amount: ${pattern['total_amount']:,} - Risk: {pattern['risk_level']}")
    print()
    
    # 3. Large Transaction Detection
    print("3. Large Transaction Anomaly Detection:")
    large_transactions = detector.detect_large_transactions()
    for transaction in large_transactions:
        print(f"   {transaction['user_name']}: ${transaction['amount']:,} transfer")
        print(f"     From {transaction['from_bank']} to {transaction['to_bank']} - Risk: {transaction['risk_level']}")
    print()
    
    # 4. Money Laundering Detection
    print("4. Money Laundering Pattern Detection:")
    laundering_patterns = detector.detect_money_laundering_patterns()
    for pattern in laundering_patterns:
        print(f"   Transaction {pattern['transaction_id']}: ${pattern['amount']:,}")
        print(f"     From {pattern['from_bank']} to {pattern['to_bank']} - Risk: {pattern['risk_level']}")
    print()
    
    # 5. Account Takeover Detection
    print("5. Account Takeover Indicator Detection:")
    takeover_indicators = detector.detect_account_takeover_indicators()
    for indicator in takeover_indicators:
        print(f"   {indicator['user_name']}: {indicator['device_count']} devices, {indicator['account_count']} accounts")
        print(f"     Unknown location devices: {indicator['unknown_location_devices']}")
        print(f"     Risk level: {indicator['risk_level']}")
    print()

def show_real_world_applications():
    """Show real-world fraud detection applications"""
    print("=== Real-World Fraud Detection Applications ===\n")
    
    applications = [
        {
            "domain": "Credit Card Fraud",
            "patterns": [
                "Unusual spending patterns",
                "Geographic anomalies",
                "Velocity checks",
                "Device fingerprinting"
            ],
            "benefits": [
                "Real-time detection",
                "Reduced false positives",
                "Pattern recognition",
                "Network analysis"
            ]
        },
        {
            "domain": "Insurance Fraud",
            "patterns": [
                "Claim pattern analysis",
                "Provider network analysis",
                "Temporal anomalies",
                "Relationship mapping"
            ],
            "benefits": [
                "Cost reduction",
                "Risk assessment",
                "Network visualization",
                "Predictive analytics"
            ]
        },
        {
            "domain": "Banking Fraud",
            "patterns": [
                "Account takeover detection",
                "Money laundering patterns",
                "Transaction velocity",
                "Device sharing detection"
            ],
            "benefits": [
                "Regulatory compliance",
                "Risk mitigation",
                "Customer protection",
                "Operational efficiency"
            ]
        },
        {
            "domain": "E-commerce Fraud",
            "patterns": [
                "Bot detection",
                "Account creation patterns",
                "Purchase behavior analysis",
                "IP reputation analysis"
            ],
            "benefits": [
                "Revenue protection",
                "Customer experience",
                "Automated detection",
                "Scalable solutions"
            ]
        }
    ]
    
    for app in applications:
        print(f"🔍 {app['domain']}:")
        print(f"   Patterns: {', '.join(app['patterns'])}")
        print(f"   Benefits: {', '.join(app['benefits'])}")
        print()

def show_cypher_examples():
    """Show Cypher query examples for fraud detection"""
    print("=== Cypher Query Examples for Fraud Detection ===\n")
    
    queries = [
        {
            "description": "Find users sharing the same device",
            "cypher": """MATCH (u1:User)-[:USES]->(d:Device)<-[:USES]-(u2:User)
                        WHERE u1.id < u2.id
                        RETURN u1.name, u2.name, d.ip, d.location"""
        },
        {
            "description": "Detect rapid transfer patterns",
            "cypher": """MATCH (a1:Account)-[:SENDS]->(t:Transaction)-[:RECEIVES]->(a2:Account)
                        WHERE t.timestamp > datetime() - duration({minutes: 30})
                        WITH a1, a2, count(t) as transfer_count, sum(t.amount) as total_amount
                        WHERE transfer_count >= 3 OR total_amount > 100000
                        RETURN a1.id, a2.id, transfer_count, total_amount"""
        },
        {
            "description": "Find money laundering patterns",
            "cypher": """MATCH path = (start:Account)-[:SENDS]->(t1:Transaction)-[:RECEIVES]->(middle:Account)-[:SENDS]->(t2:Transaction)-[:RECEIVES]->(end:Account)
                        WHERE t1.timestamp > datetime() - duration({hours: 24})
                        AND t2.timestamp > t1.timestamp
                        AND t2.timestamp < t1.timestamp + duration({minutes: 30})
                        RETURN start.bank, end.bank, t1.amount + t2.amount as total_amount"""
        },
        {
            "description": "Detect account takeover indicators",
            "cypher": """MATCH (u:User)-[:USES]->(d:Device)
                        WITH u, count(d) as device_count
                        WHERE device_count > 2
                        MATCH (u)-[:OWNS]->(a:Account)
                        WITH u, device_count, count(a) as account_count
                        WHERE device_count + account_count >= 5
                        RETURN u.name, device_count, account_count"""
        },
        {
            "description": "Find high-risk user networks",
            "cypher": """MATCH (u1:User)-[:USES]->(d:Device)<-[:USES]-(u2:User)
                        WHERE u1.risk_score > 0.7 AND u2.risk_score > 0.7
                        OPTIONAL MATCH (u1)-[:SHARES_PHONE]->(u2)
                        RETURN u1.name, u2.name, count(d) as shared_devices"""
        }
    ]
    
    for i, query in enumerate(queries, 1):
        print(f"{i}. {query['description']}:")
        print(f"   {query['cypher']}")
        print()

def main():
    """Main demonstration function"""
    print("🚀 Fraud Detection with Graph Databases Demo")
    print("=" * 60)
    print()
    
    demonstrate_fraud_detection()
    show_real_world_applications()
    show_cypher_examples()
    
    print("=== Why Graph Databases for Fraud Detection? ===\n")
    print("✅ Relationship Analysis:")
    print("   • Discover hidden connections between entities")
    print("   • Identify fraud rings and networks")
    print("   • Map complex transaction flows")
    print()
    print("✅ Pattern Recognition:")
    print("   • Detect multi-hop fraud patterns")
    print("   • Identify temporal anomalies")
    print("   • Find behavioral patterns")
    print()
    print("✅ Real-time Processing:")
    print("   • Fast graph traversal algorithms")
    print("   • Efficient relationship queries")
    print("   • Scalable pattern matching")
    print()
    print("✅ Network Analysis:")
    print("   • Centrality analysis for key players")
    print("   • Community detection for fraud rings")
    print("   • Influence propagation analysis")
    print()
    print("=== Getting Started ===")
    print("1. Install Neo4j: https://neo4j.com/download/")
    print("2. Install Python driver: pip install neo4j")
    print("3. Run the full example: python fraud_detection_example.py")
    print("4. Explore the Jupyter notebook: neo4j.ipynb")

if __name__ == "__main__":
    main() 