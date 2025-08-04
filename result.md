(mcp_sv) alberto@Jorges-MacBook-Air-3 mcp_sv % /Users/alberto/Desktop/mcp_sv/.venv/bin/python /Users/a
lberto/Desktop/mcp_sv/fraud_detection_example.py
=== Fraud Detection System with Neo4j ===

1. Setting up fraud detection data...
Database cleared!
Fraud detection data created successfully!

2. Fraud Risk Summary:
   High Risk Users: 3
   Suspicious Transactions: 5
   Device Sharing Incidents: 5
   Offshore Accounts: 3
   Total Risk Score: 4.0

3. Device Sharing Fraud Detection:
   Frank Fraud and Grace Scammer share device 10.0.0.50
     Average risk score: 0.85
   Frank Fraud and Grace Scammer share device 10.0.0.52
     Average risk score: 0.85
   Henry Thief and Ivy Criminal share device 10.0.0.51
     Average risk score: 0.80
   Alice Johnson and David Wilson share device 192.168.1.100
     Average risk score: 0.20
   Bob Smith and Eve Brown share device 192.168.1.101
     Average risk score: 0.15

4. Rapid Transfer Pattern Detection:

5. Large Transaction Anomaly Detection:
   Grace Scammer: $100,000 transfer
     From Offshore Bank to Offshore Bank - Risk: CRITICAL
   Frank Fraud: $75,000 transfer
     From Offshore Bank to Offshore Bank - Risk: CRITICAL
   Frank Fraud: $50,000 transfer
     From Offshore Bank to Offshore Bank - Risk: HIGH
   Frank Fraud: $30,000 transfer
     From Offshore Bank to Offshore Bank - Risk: HIGH
   Frank Fraud: $25,000 transfer
     From Offshore Bank to Offshore Bank - Risk: MEDIUM

6. Suspicious Network Connection Detection:
   Frank Fraud and Grace Scammer have 3 connections
     Shared devices: 2, Shared phone: 1, Similar email: 0
     Risk level: CRITICAL
   Henry Thief and Ivy Criminal have 2 connections
     Shared devices: 1, Shared phone: 0, Similar email: 1
     Risk level: HIGH
   Alice Johnson and David Wilson have 1 connections
     Shared devices: 1, Shared phone: 0, Similar email: 0
     Risk level: MEDIUM
   Bob Smith and Eve Brown have 1 connections
     Shared devices: 1, Shared phone: 0, Similar email: 0
     Risk level: MEDIUM

7. Money Laundering Pattern Detection:

8. Account Takeover Indicator Detection:

=== Fraud Detection Analysis Complete! ===

Key Insights:
• Graph databases excel at detecting complex fraud patterns
• Relationship analysis reveals hidden connections
• Pattern recognition across multiple entities
• Real-time fraud detection capabilities
(mcp_sv) alberto@Jorges-MacBook-Air-3 mcp_sv % 