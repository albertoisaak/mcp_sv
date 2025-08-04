#!/usr/bin/env python3
"""
Fraud Detection with Neo4j - A comprehensive example showing how graph databases
can be used to detect various types of fraud through relationship analysis.
"""

from neo4j import GraphDatabase
import random
from datetime import datetime, timedelta
import json
from collections import defaultdict

class FraudDetectionSystem:
    """
    Fraud Detection System with Neo4j - A comprehensive example showing how graph databases
    can be used to detect various types of fraud through relationship analysis.
    """

    """
    Initialize the FraudDetectionSystem with Neo4j driver and credentials.

    Args:
        uri (str): The URI of the Neo4j database.
        user (str): The username for authentication.
        password (str): The password for authentication.
    """
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
        
    def close(self):
        self.driver.close()
        
    def clear_database(self):
        """Clear all data from the database"""
        with self.driver.session() as session:
            session.run("MATCH (n) DETACH DELETE n")
            print("Database cleared!")
    
    def create_fraud_detection_data(self):
        """Create sample data for fraud detection scenarios"""
        with self.driver.session() as session:
            # Create legitimate users
            legitimate_users = [
                {"id": "U001", "name": "Alice Johnson", "email": "alice@email.com", "phone": "+1-555-0101", "risk_score": 0.1},
                {"id": "U002", "name": "Bob Smith", "email": "bob@email.com", "phone": "+1-555-0102", "risk_score": 0.2},
                {"id": "U003", "name": "Carol Davis", "email": "carol@email.com", "phone": "+1-555-0103", "risk_score": 0.1},
                {"id": "U004", "name": "David Wilson", "email": "david@email.com", "phone": "+1-555-0104", "risk_score": 0.3},
                {"id": "U005", "name": "Eve Brown", "email": "eve@email.com", "phone": "+1-555-0105", "risk_score": 0.1}
            ]
            
            # Create suspicious users (potential fraudsters)
            suspicious_users = [
                {"id": "U101", "name": "Frank Fraud", "email": "frank@fake.com", "phone": "+1-555-9999", "risk_score": 0.9},
                {"id": "U102", "name": "Grace Scammer", "email": "grace@scam.net", "phone": "+1-555-9998", "risk_score": 0.8},
                {"id": "U103", "name": "Henry Thief", "email": "henry@stolen.org", "phone": "+1-555-9997", "risk_score": 0.7},
                {"id": "U104", "name": "Ivy Criminal", "email": "ivy@crime.com", "phone": "+1-555-9996", "risk_score": 0.9}
            ]
            
            # Create all users
            all_users = legitimate_users + suspicious_users
            for user in all_users:
                session.run("""
                    CREATE (u:User {
                        id: $id,
                        name: $name,
                        email: $email,
                        phone: $phone,
                        risk_score: $risk_score,
                        created_at: datetime()
                    })
                """, user)
            
            # Create devices
            devices = [
                {"id": "D001", "type": "laptop", "ip": "192.168.1.100", "location": "New York"},
                {"id": "D002", "type": "mobile", "ip": "192.168.1.101", "location": "San Francisco"},
                {"id": "D003", "type": "tablet", "ip": "192.168.1.102", "location": "Boston"},
                {"id": "D004", "type": "laptop", "ip": "10.0.0.50", "location": "Unknown"},  # Suspicious IP
                {"id": "D005", "type": "mobile", "ip": "10.0.0.51", "location": "Unknown"},  # Suspicious IP
                {"id": "D006", "type": "laptop", "ip": "10.0.0.52", "location": "Unknown"}   # Suspicious IP
            ]
            
            for device in devices:
                session.run("""
                    CREATE (d:Device {
                        id: $id,
                        type: $type,
                        ip: $ip,
                        location: $location
                    })
                """, device)
            
            # Create bank accounts
            accounts = [
                {"id": "A001", "bank": "Chase", "account_type": "checking", "balance": 5000},
                {"id": "A002", "bank": "Wells Fargo", "account_type": "savings", "balance": 15000},
                {"id": "A003", "bank": "Bank of America", "account_type": "checking", "balance": 3000},
                {"id": "A004", "bank": "Citibank", "account_type": "checking", "balance": 8000},
                {"id": "A005", "bank": "Chase", "account_type": "savings", "balance": 25000},
                # Suspicious accounts
                {"id": "A101", "bank": "Offshore Bank", "account_type": "checking", "balance": 100000},
                {"id": "A102", "bank": "Offshore Bank", "account_type": "savings", "balance": 500000},
                {"id": "A103", "bank": "Offshore Bank", "account_type": "checking", "balance": 75000}
            ]
            
            for account in accounts:
                session.run("""
                    CREATE (a:Account {
                        id: $id,
                        bank: $bank,
                        account_type: $account_type,
                        balance: $balance
                    })
                """, account)
            
            # Create transactions
            transactions = [
                # Legitimate transactions
                {"id": "T001", "amount": 100, "type": "transfer", "status": "completed", "timestamp": datetime.now() - timedelta(hours=2)},
                {"id": "T002", "amount": 250, "type": "payment", "status": "completed", "timestamp": datetime.now() - timedelta(hours=1)},
                {"id": "T003", "amount": 75, "type": "transfer", "status": "completed", "timestamp": datetime.now() - timedelta(minutes=30)},
                {"id": "T004", "amount": 500, "type": "payment", "status": "completed", "timestamp": datetime.now() - timedelta(minutes=15)},
                {"id": "T005", "amount": 1200, "type": "transfer", "status": "completed", "timestamp": datetime.now() - timedelta(minutes=5)},
                
                # Suspicious transactions
                {"id": "T101", "amount": 50000, "type": "transfer", "status": "pending", "timestamp": datetime.now() - timedelta(minutes=10)},
                {"id": "T102", "amount": 25000, "type": "transfer", "status": "pending", "timestamp": datetime.now() - timedelta(minutes=8)},
                {"id": "T103", "amount": 100000, "type": "transfer", "status": "pending", "timestamp": datetime.now() - timedelta(minutes=5)},
                {"id": "T104", "amount": 75000, "type": "transfer", "status": "pending", "timestamp": datetime.now() - timedelta(minutes=3)},
                {"id": "T105", "amount": 30000, "type": "transfer", "status": "pending", "timestamp": datetime.now() - timedelta(minutes=1)}
            ]
            
            for transaction in transactions:
                session.run("""
                    CREATE (t:Transaction {
                        id: $id,
                        amount: $amount,
                        type: $type,
                        status: $status,
                        timestamp: $timestamp
                    })
                """, transaction)
            
            # Create relationships
            
            # User-Device relationships (legitimate)
            user_device_legitimate = [
                ("U001", "D001"), ("U002", "D002"), ("U003", "D003"),
                ("U004", "D001"), ("U005", "D002")
            ]
            
            # User-Device relationships (suspicious - multiple users on same device)
            user_device_suspicious = [
                ("U101", "D004"), ("U102", "D004"), ("U103", "D005"), ("U104", "D005"),
                ("U101", "D006"), ("U102", "D006")  # Multiple devices per user
            ]
            
            for user_id, device_id in user_device_legitimate + user_device_suspicious:
                session.run("""
                    MATCH (u:User {id: $user_id}), (d:Device {id: $device_id})
                    CREATE (u)-[:USES {since: datetime()}]->(d)
                """, user_id=user_id, device_id=device_id)
            
            # User-Account relationships
            user_accounts = [
                ("U001", "A001"), ("U002", "A002"), ("U003", "A003"),
                ("U004", "A004"), ("U005", "A005"),
                # Suspicious: multiple accounts per user
                ("U101", "A101"), ("U101", "A102"), ("U102", "A103")
            ]
            
            for user_id, account_id in user_accounts:
                session.run("""
                    MATCH (u:User {id: $user_id}), (a:Account {id: $account_id})
                    CREATE (u)-[:OWNS {since: datetime()}]->(a)
                """, user_id=user_id, account_id=account_id)
            
            # Transaction relationships
            transaction_flows = [
                # Legitimate transactions
                ("A001", "T001", "A002"), ("A002", "T002", "A003"),
                ("A003", "T003", "A004"), ("A004", "T004", "A005"),
                ("A005", "T005", "A001"),
                
                # Suspicious transactions (large amounts, rapid transfers)
                ("A101", "T101", "A102"), ("A102", "T102", "A103"),
                ("A103", "T103", "A101"), ("A101", "T104", "A102"),
                ("A102", "T105", "A103")
            ]
            
            for from_account, transaction_id, to_account in transaction_flows:
                session.run("""
                    MATCH (from:Account {id: $from_account}), (t:Transaction {id: $transaction_id}), (to:Account {id: $to_account})
                    CREATE (from)-[:SENDS]->(t)-[:RECEIVES]->(to)
                """, from_account=from_account, transaction_id=transaction_id, to_account=to_account)
            
            # Create some shared phone numbers (suspicious)
            session.run("""
                MATCH (u1:User {id: 'U101'}), (u2:User {id: 'U102'})
                CREATE (u1)-[:SHARES_PHONE {phone: '+1-555-9999'}]->(u2)
            """)
            
            # Create some shared email patterns (suspicious)
            session.run("""
                MATCH (u1:User {id: 'U103'}), (u2:User {id: 'U104'})
                CREATE (u1)-[:SIMILAR_EMAIL {pattern: 'stolen.org'}]->(u2)
            """)
            
            print("Fraud detection data created successfully!")
    
    def detect_device_sharing_fraud(self):
        """Detect users sharing the same device (potential account takeover)"""
        with self.driver.session() as session:
            result = session.run("""
                MATCH (u1:User)-[:USES]->(d:Device)<-[:USES]-(u2:User)
                WHERE u1.id < u2.id  // Avoid duplicate pairs
                WITH u1, u2, d, count(d) as shared_devices
                WHERE shared_devices > 0
                RETURN u1.name as user1, u2.name as user2, d.ip as device_ip, 
                       u1.risk_score as risk1, u2.risk_score as risk2,
                       (u1.risk_score + u2.risk_score) / 2 as avg_risk
                ORDER BY avg_risk DESC
            """)
            
            return [dict(record) for record in result]
    
    def detect_rapid_transfer_patterns(self):
        """Detect rapid transfer patterns between accounts, which is a common indicator of fraud."""
        with self.driver.session() as session:
            result = session.run("""
                MATCH (a1:Account)-[:SENDS]->(t:Transaction)-[:RECEIVES]->(a2:Account)
                WHERE t.timestamp > datetime() - duration({minutes: 30})
                WITH a1, a2, count(t) as transfer_count, sum(t.amount) as total_amount
                WHERE transfer_count >= 3 OR total_amount > 100000
                RETURN a1.id as from_account, a2.id as to_account, 
                       transfer_count, total_amount,
                       CASE 
                           WHEN transfer_count >= 5 THEN 'HIGH'
                           WHEN transfer_count >= 3 THEN 'MEDIUM'
                           ELSE 'LOW'
                       END as risk_level
                ORDER BY total_amount DESC
            """)
            
            return [dict(record) for record in result]
    
    def detect_large_transaction_anomalies(self):
        """Detect unusually large transactions"""
        with self.driver.session() as session:
            result = session.run("""
                MATCH (a:Account)-[:SENDS]->(t:Transaction)-[:RECEIVES]->(a2:Account)
                WITH t, a, a2, t.amount as amount
                WHERE amount > 10000
                MATCH (u:User)-[:OWNS]->(a)
                RETURN u.name as user_name, u.risk_score as user_risk,
                       t.amount as amount, t.timestamp as timestamp,
                       a.bank as from_bank, a2.bank as to_bank,
                       CASE 
                           WHEN amount > 50000 THEN 'CRITICAL'
                           WHEN amount > 25000 THEN 'HIGH'
                           ELSE 'MEDIUM'
                       END as risk_level
                ORDER BY amount DESC
            """)
            
            return [dict(record) for record in result]
    
    def detect_network_connections(self):
        """Detect suspicious network connections between users"""
        with self.driver.session() as session:
            result = session.run("""
                MATCH (u1:User)-[:USES]->(d:Device)<-[:USES]-(u2:User)
                WHERE u1.id < u2.id
                OPTIONAL MATCH (u1)-[r1:SHARES_PHONE]->(u2)
                OPTIONAL MATCH (u1)-[r2:SIMILAR_EMAIL]->(u2)
                WITH u1, u2, count(d) as shared_devices,
                     CASE WHEN r1 IS NOT NULL THEN 1 ELSE 0 END as shares_phone,
                     CASE WHEN r2 IS NOT NULL THEN 1 ELSE 0 END as similar_email
                WHERE shared_devices > 0 OR shares_phone > 0 OR similar_email > 0
                RETURN u1.name as user1, u2.name as user2,
                       shared_devices, shares_phone, similar_email,
                       (shared_devices + shares_phone + similar_email) as connection_score,
                       CASE 
                           WHEN (shared_devices + shares_phone + similar_email) >= 3 THEN 'CRITICAL'
                           WHEN (shared_devices + shares_phone + similar_email) >= 2 THEN 'HIGH'
                           ELSE 'MEDIUM'
                       END as risk_level
                ORDER BY connection_score DESC
            """)
            
            return [dict(record) for record in result]
    
    def detect_money_laundering_patterns(self):
        """Detect potential money laundering patterns"""
        with self.driver.session() as session:
            result = session.run("""
                MATCH path = (start:Account)-[:SENDS]->(t1:Transaction)-[:RECEIVES]->(middle:Account)-[:SENDS]->(t2:Transaction)-[:RECEIVES]->(end:Account)
                WHERE start.id <> middle.id AND middle.id <> end.id AND start.id <> end.id
                AND t1.timestamp > datetime() - duration({hours: 24})
                AND t2.timestamp > t1.timestamp
                AND t2.timestamp < t1.timestamp + duration({minutes: 30})
                WITH start, middle, end, t1.amount as amount1, t2.amount as amount2,
                     (amount1 + amount2) as total_amount
                WHERE total_amount > 50000
                MATCH (u1:User)-[:OWNS]->(start)
                MATCH (u2:User)-[:OWNS]->(end)
                RETURN u1.name as origin_user, u2.name as destination_user,
                       start.bank as origin_bank, end.bank as destination_bank,
                       amount1, amount2, total_amount,
                       CASE 
                           WHEN total_amount > 100000 THEN 'CRITICAL'
                           WHEN total_amount > 75000 THEN 'HIGH'
                           ELSE 'MEDIUM'
                       END as risk_level
                ORDER BY total_amount DESC
            """)
            
            return [dict(record) for record in result]
    
    def detect_account_takeover_indicators(self):
        """Detect potential account takeover indicators"""
        with self.driver.session() as session:
            result = session.run("""
                MATCH (u:User)-[:USES]->(d:Device)
                WITH u, count(d) as device_count
                WHERE device_count > 2
                
                MATCH (u)-[:OWNS]->(a:Account)
                WITH u, device_count, count(a) as account_count
                
                MATCH (u)-[:USES]->(d:Device)
                WHERE d.location = 'Unknown'
                WITH u, device_count, account_count, count(d) as unknown_location_devices
                
                RETURN u.name as user_name, u.risk_score as user_risk,
                       device_count, account_count, unknown_location_devices,
                       (device_count + account_count + unknown_location_devices) as risk_score,
                       CASE 
                           WHEN (device_count + account_count + unknown_location_devices) >= 8 THEN 'CRITICAL'
                           WHEN (device_count + account_count + unknown_location_devices) >= 5 THEN 'HIGH'
                           ELSE 'MEDIUM'
                       END as risk_level
                ORDER BY risk_score DESC
            """)
            
            return [dict(record) for record in result]
    
    def get_fraud_risk_summary(self):
        """Get overall fraud risk summary"""
        with self.driver.session() as session:
            # Count high-risk users
            high_risk_users = session.run("""
                MATCH (u:User)
                WHERE u.risk_score > 0.7
                RETURN count(u) as high_risk_count
            """).single()["high_risk_count"]
            
            # Count suspicious transactions
            suspicious_transactions = session.run("""
                MATCH (t:Transaction)
                WHERE t.amount > 10000 OR t.status = 'pending'
                RETURN count(t) as suspicious_count
            """).single()["suspicious_count"]
            
            # Count device sharing
            device_sharing = session.run("""
                MATCH (u1:User)-[:USES]->(d:Device)<-[:USES]-(u2:User)
                WHERE u1.id < u2.id
                RETURN count(*) as sharing_count
            """).single()["sharing_count"]
            
            # Count offshore accounts
            offshore_accounts = session.run("""
                MATCH (a:Account)
                WHERE a.bank = 'Offshore Bank'
                RETURN count(a) as offshore_count
            """).single()["offshore_count"]
            
            return {
                "high_risk_users": high_risk_users,
                "suspicious_transactions": suspicious_transactions,
                "device_sharing_incidents": device_sharing,
                "offshore_accounts": offshore_accounts,
                "total_risk_score": (high_risk_users * 0.3 + suspicious_transactions * 0.2 + 
                                   device_sharing * 0.3 + offshore_accounts * 0.2)
            }

def main():
    # Connect to Neo4j (update these credentials as needed)
    uri = "neo4j+s://3bf0ff2c.databases.neo4j.io"
    user = "neo4j"
    password = "QrIQolzO5EvFK-ObdlsKTroOPeVQkfUJOM3-4ts6JZI"
    
    fraud_system = FraudDetectionSystem(uri, user, password)
    
    try:
        print("=== Fraud Detection System with Neo4j ===\n")
        
        # Clear existing data and create sample data
        print("1. Setting up fraud detection data...")
        fraud_system.clear_database()
        fraud_system.create_fraud_detection_data()
        print()
        
        # Overall risk summary
        print("2. Fraud Risk Summary:")
        summary = fraud_system.get_fraud_risk_summary()
        for key, value in summary.items():
            print(f"   {key.replace('_', ' ').title()}: {value}")
        print()
        
        # Device sharing detection
        print("3. Device Sharing Fraud Detection:")
        device_sharing = fraud_system.detect_device_sharing_fraud()
        for incident in device_sharing:
            print(f"   {incident['user1']} and {incident['user2']} share device {incident['device_ip']}")
            print(f"     Average risk score: {incident['avg_risk']:.2f}")
        print()
        
        # Rapid transfer patterns
        print("4. Rapid Transfer Pattern Detection:")
        rapid_transfers = fraud_system.detect_rapid_transfer_patterns()
        for pattern in rapid_transfers:
            print(f"   {pattern['transfer_count']} transfers between {pattern['from_account']} and {pattern['to_account']}")
            print(f"     Total amount: ${pattern['total_amount']:,} - Risk: {pattern['risk_level']}")
        print()
        
        # Large transaction anomalies
        print("5. Large Transaction Anomaly Detection:")
        large_transactions = fraud_system.detect_large_transaction_anomalies()
        for transaction in large_transactions:
            print(f"   {transaction['user_name']}: ${transaction['amount']:,} transfer")
            print(f"     From {transaction['from_bank']} to {transaction['to_bank']} - Risk: {transaction['risk_level']}")
        print()
        
        # Network connections
        print("6. Suspicious Network Connection Detection:")
        network_connections = fraud_system.detect_network_connections()
        for connection in network_connections:
            print(f"   {connection['user1']} and {connection['user2']} have {connection['connection_score']} connections")
            print(f"     Shared devices: {connection['shared_devices']}, Shared phone: {connection['shares_phone']}, Similar email: {connection['similar_email']}")
            print(f"     Risk level: {connection['risk_level']}")
        print()
        
        # Money laundering patterns
        print("7. Money Laundering Pattern Detection:")
        money_laundering = fraud_system.detect_money_laundering_patterns()
        for pattern in money_laundering:
            print(f"   {pattern['origin_user']} -> {pattern['destination_user']}")
            print(f"     Via {pattern['origin_bank']} -> {pattern['destination_bank']}")
            print(f"     Amounts: ${pattern['amount1']:,} + ${pattern['amount2']:,} = ${pattern['total_amount']:,}")
            print(f"     Risk level: {pattern['risk_level']}")
        print()
        
        # Account takeover indicators
        print("8. Account Takeover Indicator Detection:")
        account_takeover = fraud_system.detect_account_takeover_indicators()
        for indicator in account_takeover:
            print(f"   {indicator['user_name']}: {indicator['device_count']} devices, {indicator['account_count']} accounts")
            print(f"     Unknown location devices: {indicator['unknown_location_devices']}")
            print(f"     Risk level: {indicator['risk_level']}")
        print()
        
        print("=== Fraud Detection Analysis Complete! ===")
        print("\nKey Insights:")
        print("• Graph databases excel at detecting complex fraud patterns")
        print("• Relationship analysis reveals hidden connections")
        print("• Pattern recognition across multiple entities")
        print("• Real-time fraud detection capabilities")
        
    except Exception as e:
        print(f"Error: {e}")
        print("\nMake sure Neo4j is running and the credentials are correct.")
    
    finally:
        fraud_system.close()

if __name__ == "__main__":
    main() 