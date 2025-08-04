# Fraud Detection with Neo4j - Learning Lab

## 🎯 **Learning Objectives**

By the end of this lab, you will be able to:
- Understand how graph databases excel at fraud detection
- Implement various fraud detection algorithms using Neo4j
- Analyze complex relationships and patterns in financial data
- Build a comprehensive fraud detection system
- Apply graph-based analytics to real-world scenarios

---

## 📊 **Why Graph Databases for Fraud Detection?**

### **Traditional vs. Graph Approach**

| Traditional Databases | Graph Databases |
|----------------------|-----------------|
| ❌ Complex JOINs for relationships | ✅ Native relationship storage |
| ❌ Difficult pattern recognition | ✅ Built-in pattern matching |
| ❌ Slow multi-hop queries | ✅ Fast graph traversal |
| ❌ Limited network analysis | ✅ Rich network analytics |
| ❌ Rigid schema constraints | ✅ Flexible data model |

### **Key Advantages**

1. **Relationship-First Design**: Relationships are first-class citizens
2. **Pattern Recognition**: Natural detection of complex fraud schemes
3. **Network Analysis**: Identify fraud rings and connections
4. **Real-time Processing**: Fast traversal for live monitoring
5. **Scalability**: Efficient even with billions of relationships

---

## 🏗️ **Data Model Design**

### **Entities (Nodes)**

```cypher
// Users - People in the system
CREATE (u:User {
    id: "U001",
    name: "Alice Johnson",
    email: "alice@email.com",
    phone: "+1-555-0101",
    risk_score: 0.1,
    created_at: datetime()
})

// Devices - Computing devices
CREATE (d:Device {
    id: "D001",
    type: "laptop",
    ip: "192.168.1.100",
    location: "New York"
})

// Accounts - Bank accounts
CREATE (a:Account {
    id: "A001",
    bank: "Chase",
    account_type: "checking",
    balance: 5000
})

// Transactions - Financial transactions
CREATE (t:Transaction {
    id: "T001",
    amount: 100,
    type: "transfer",
    status: "completed",
    timestamp: datetime()
})
```

### **Relationships (Edges)**

```cypher
// User uses Device
CREATE (u:User {id: "U001"})-[:USES {since: datetime()}]->(d:Device {id: "D001"})

// User owns Account
CREATE (u:User {id: "U001"})-[:OWNS {since: datetime()}]->(a:Account {id: "A001"})

// Account sends Transaction to Account
CREATE (a1:Account {id: "A001"})-[:SENDS]->(t:Transaction {id: "T001"})-[:RECEIVES]->(a2:Account {id: "A002"})

// Suspicious relationships
CREATE (u1:User {id: "U101"})-[:SHARES_PHONE {phone: "+1-555-9999"}]->(u2:User {id: "U102"})
CREATE (u1:User {id: "U103"})-[:SIMILAR_EMAIL {pattern: "stolen.org"}]->(u2:User {id: "U104"})
```

---

## 🔍 **Fraud Detection Algorithms**

### **1. Device Sharing Detection**

**Problem**: Multiple users accessing the same device (potential account takeover)

**Cypher Query**:
```cypher
MATCH (u1:User)-[:USES]->(d:Device)<-[:USES]-(u2:User)
WHERE u1.id < u2.id  // Avoid duplicate pairs
WITH u1, u2, d, count(d) as shared_devices
WHERE shared_devices > 0
RETURN u1.name as user1, u2.name as user2, d.ip as device_ip, 
       u1.risk_score as risk1, u2.risk_score as risk2,
       (u1.risk_score + u2.risk_score) / 2 as avg_risk
ORDER BY avg_risk DESC
```

**Python Implementation**:
```python
def detect_device_sharing_fraud(self):
    """Detect users sharing the same device (potential account takeover)"""
    with self.driver.session() as session:
        result = session.run("""
            MATCH (u1:User)-[:USES]->(d:Device)<-[:USES]-(u2:User)
            WHERE u1.id < u2.id
            WITH u1, u2, d, count(d) as shared_devices
            WHERE shared_devices > 0
            RETURN u1.name as user1, u2.name as user2, d.ip as device_ip, 
                   u1.risk_score as risk1, u2.risk_score as risk2,
                   (u1.risk_score + u2.risk_score) / 2 as avg_risk
            ORDER BY avg_risk DESC
        """)
        return [dict(record) for record in result]
```

**Detection Logic**:
- Find devices connected to multiple users
- Calculate average risk score of users sharing each device
- Flag high-risk device sharing patterns

### **2. Rapid Transfer Pattern Detection**

**Problem**: Unusual frequency of transfers between accounts

**Cypher Query**:
```cypher
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
```

**Risk Thresholds**:
- **Time Window**: Last 30 minutes
- **Frequency Threshold**: 3+ transfers between same accounts
- **Amount Threshold**: $100,000+ total
- **Risk Levels**: LOW, MEDIUM, HIGH based on transfer count

### **3. Large Transaction Anomaly Detection**

**Problem**: Unusually large transactions that deviate from normal patterns

**Cypher Query**:
```cypher
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
```

**Risk Levels**:
- **CRITICAL**: > $50,000
- **HIGH**: $25,000 - $50,000
- **MEDIUM**: $10,000 - $25,000

### **4. Money Laundering Pattern Detection**

**Problem**: Complex transaction chains designed to hide money origins

**Cypher Query**:
```cypher
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
```

**Money Laundering Detection**:
- **Pattern**: Account A → Account B → Account C (layering)
- **Time Window**: 24 hours, with 30-minute gaps
- **Amount Threshold**: $50,000+ total
- **Purpose**: Hide money origins through multiple transfers

### **5. Account Takeover Indicator Detection**

**Problem**: Unusual account activity patterns

**Cypher Query**:
```cypher
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
```

**Account Takeover Indicators**:
- **Multiple devices**: > 2 devices per user
- **Multiple accounts**: High account count
- **Unknown locations**: Devices from suspicious locations
- **Risk scoring**: Combined score determines risk level

---

## 🎮 **Hands-On Exercise**

### **Step 1: Setup**

```bash
# Install dependencies
pip install neo4j matplotlib networkx pandas

# Start Neo4j (if using local installation)
neo4j start
```

### **Step 2: Run the Demo**

```bash
# Run the standalone demo (no Neo4j required)
python fraud_detection_demo.py

# Run the full Neo4j example
python fraud_detection_example.py
```

### **Step 3: Explore the Data**

```cypher
// View all users
MATCH (u:User) RETURN u.name, u.risk_score ORDER BY u.risk_score DESC

// View all transactions
MATCH (t:Transaction) RETURN t.amount, t.status ORDER BY t.amount DESC

// View device sharing
MATCH (u1:User)-[:USES]->(d:Device)<-[:USES]-(u2:User)
WHERE u1.id < u2.id
RETURN u1.name, u2.name, d.ip
```

### **Step 4: Custom Queries**

Try these custom queries to explore the data:

```cypher
// Find high-risk users with multiple accounts
MATCH (u:User)-[:OWNS]->(a:Account)
WHERE u.risk_score > 0.7
WITH u, count(a) as account_count
WHERE account_count > 1
RETURN u.name, u.risk_score, account_count
ORDER BY account_count DESC

// Find transactions from offshore banks
MATCH (a:Account)-[:SENDS]->(t:Transaction)
WHERE a.bank = 'Offshore Bank'
RETURN t.amount, t.timestamp
ORDER BY t.amount DESC

// Find users with unknown location devices
MATCH (u:User)-[:USES]->(d:Device)
WHERE d.location = 'Unknown'
RETURN u.name, count(d) as unknown_devices
ORDER BY unknown_devices DESC
```

---

## 🔧 **Advanced Patterns**

### **Multi-hop Path Finding**

```cypher
// Find paths between users through devices
MATCH path = (u1:User)-[:USES]->(d:Device)<-[:USES]-(u2:User)
WHERE u1.id <> u2.id
RETURN u1.name, u2.name, length(path) as path_length
ORDER BY path_length
```

### **Temporal Analysis**

```cypher
// Find recent suspicious activity
MATCH (t:Transaction)
WHERE t.timestamp > datetime() - duration({hours: 1})
AND t.amount > 10000
RETURN t.amount, t.timestamp
ORDER BY t.timestamp DESC
```

### **Network Centrality**

```cypher
// Find most connected users
MATCH (u:User)-[:USES]->(d:Device)
WITH u, count(d) as device_count
MATCH (u)-[:OWNS]->(a:Account)
WITH u, device_count, count(a) as account_count
RETURN u.name, device_count + account_count as total_connections
ORDER BY total_connections DESC
```

---

## 📈 **Real-World Applications**

### **Banking & Financial Services**

| Use Case | Detection Method | Benefits |
|----------|------------------|----------|
| **Transaction Monitoring** | Amount thresholds, velocity checks | Regulatory compliance, fraud prevention |
| **Account Takeover** | Device sharing, location anomalies | Customer protection, loss prevention |
| **Money Laundering** | Multi-hop transaction analysis | AML compliance, risk mitigation |
| **Credit Card Fraud** | Spending patterns, geographic anomalies | Real-time detection, reduced losses |

### **E-commerce**

| Use Case | Detection Method | Benefits |
|----------|------------------|----------|
| **Payment Fraud** | Device fingerprinting, velocity checks | Revenue protection, customer experience |
| **Account Creation** | IP reputation, device patterns | Bot detection, fake account prevention |
| **Purchase Patterns** | Behavioral analysis, network connections | Personalized security, reduced false positives |

### **Insurance**

| Use Case | Detection Method | Benefits |
|----------|------------------|----------|
| **Claim Fraud** | Provider networks, temporal patterns | Cost reduction, risk assessment |
| **Policy Fraud** | Identity verification, relationship mapping | Fraud prevention, accurate pricing |

---

## 🚀 **Performance Considerations**

### **Indexing Strategy**

```cypher
// Create indexes for better performance
CREATE INDEX user_id_index FOR (u:User) ON (u.id)
CREATE INDEX transaction_timestamp_index FOR (t:Transaction) ON (t.timestamp)
CREATE INDEX device_ip_index FOR (d:Device) ON (d.ip)
CREATE INDEX account_bank_index FOR (a:Account) ON (a.bank)
```

### **Query Optimization**

1. **Use specific labels**: `MATCH (u:User)` instead of `MATCH (u)`
2. **Limit result sets**: `LIMIT 100` for large datasets
3. **Use parameters**: `$user_id` instead of hardcoded values
4. **Avoid cartesian products**: Use proper WHERE clauses

### **Scaling Considerations**

- **Partitioning**: Split data by time periods or regions
- **Caching**: Cache frequently accessed patterns
- **Batch processing**: Process large datasets in chunks
- **Real-time vs. batch**: Choose appropriate processing model

---

## 🎯 **Best Practices**

### **Data Quality**

1. **Consistent naming**: Use standardized entity and relationship names
2. **Data validation**: Validate data before insertion
3. **Regular cleanup**: Remove stale or invalid data
4. **Audit trails**: Track data changes and access

### **Security**

1. **Access control**: Implement role-based access
2. **Data encryption**: Encrypt sensitive data
3. **Audit logging**: Log all queries and changes
4. **Network security**: Secure database connections

### **Monitoring**

1. **Query performance**: Monitor slow queries
2. **System health**: Track database metrics
3. **Fraud alerts**: Set up automated alerting
4. **False positives**: Continuously tune detection rules

---

## 📚 **Additional Resources**

### **Documentation**
- [Neo4j Cypher Manual](https://neo4j.com/docs/cypher-manual/current/)
- [Neo4j Python Driver](https://neo4j.com/docs/python-manual/current/)
- [Neo4j Graph Data Science](https://neo4j.com/docs/graph-data-science/current/)

### **Tutorials**
- [Neo4j Getting Started](https://neo4j.com/developer/get-started/)
- [Cypher Query Language](https://neo4j.com/developer/cypher/)
- [Graph Algorithms](https://neo4j.com/docs/graph-data-science/current/algorithms/)

### **Community**
- [Neo4j Community](https://community.neo4j.com/)
- [Stack Overflow](https://stackoverflow.com/questions/tagged/neo4j)
- [Neo4j Blog](https://neo4j.com/blog/)

---

## 🎓 **Assessment Questions**

### **Beginner**
1. What are the main advantages of using graph databases for fraud detection?
2. Explain the difference between nodes and relationships in Neo4j.
3. Write a simple Cypher query to find all users with risk scores above 0.5.

### **Intermediate**
1. How would you detect users who share multiple devices?
2. Explain the money laundering detection algorithm.
3. What are the key performance considerations for large-scale fraud detection?

### **Advanced**
1. Design a fraud detection system for a new domain (e.g., healthcare, education).
2. How would you implement real-time fraud detection with streaming data?
3. What machine learning techniques could be combined with graph-based fraud detection?

---

## 🔗 **Code Repository**

All code examples and demos are available in:
- `fraud_detection_example.py` - Complete Neo4j implementation
- `fraud_detection_demo.py` - Standalone demo
- `neo4j.ipynb` - Interactive Jupyter notebook

---

## 📞 **Support & Questions**

For questions about this learning lab:
- Check the documentation links above
- Join the Neo4j community forums
- Review the code examples in the repository
- Practice with the hands-on exercises

---

*Happy learning! 🚀*