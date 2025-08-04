#!/usr/bin/env python3
"""
Neo4j Concepts Demo - A simple demonstration of graph database concepts
This script shows how Neo4j works without requiring a Neo4j installation.
"""

import json
from collections import defaultdict
from datetime import datetime
import random

class SimpleGraphDB:
    """A simple in-memory graph database to demonstrate Neo4j concepts"""
    
    def __init__(self):
        self.nodes = {}  # node_id -> node_data
        self.relationships = defaultdict(list)  # (from_id, to_id) -> [relationship_data]
        self.node_counter = 0
        
    def create_node(self, labels, properties):
        """Create a node with labels and properties"""
        node_id = self.node_counter
        self.node_counter += 1
        self.nodes[node_id] = {
            'id': node_id,
            'labels': labels,
            'properties': properties
        }
        return node_id
    
    def create_relationship(self, from_id, to_id, rel_type, properties=None):
        """Create a relationship between two nodes"""
        if properties is None:
            properties = {}
        self.relationships[(from_id, to_id)].append({
            'type': rel_type,
            'properties': properties
        })
    
    def query(self, cypher_like):
        """Simple query simulation - not a real Cypher parser"""
        if "MATCH (p:Person)" in cypher_like and "RETURN" in cypher_like:
            return self._query_persons()
        elif "MATCH ()-[r:KNOWS]->()" in cypher_like:
            return self._query_relationships()
        elif "shortestPath" in cypher_like:
            return self._find_shortest_path()
        return []
    
    def _query_persons(self):
        """Query all Person nodes"""
        persons = []
        for node_id, node_data in self.nodes.items():
            if 'Person' in node_data['labels']:
                persons.append(node_data['properties'])
        return persons
    
    def _query_relationships(self):
        """Query all KNOWS relationships"""
        relationships = []
        for (from_id, to_id), rels in self.relationships.items():
            for rel in rels:
                if rel['type'] == 'KNOWS':
                    from_node = self.nodes[from_id]['properties']
                    to_node = self.nodes[to_id]['properties']
                    relationships.append({
                        'person1': from_node['name'],
                        'person2': to_node['name'],
                        'since': rel['properties'].get('since', 'unknown')
                    })
        return relationships
    
    def _find_shortest_path(self):
        """Find shortest path between nodes (simplified)"""
        # This is a simplified version - real Neo4j uses sophisticated algorithms
        return ["Alice", "Bob", "Charlie"]

def create_social_network():
    """Create a sample social network"""
    db = SimpleGraphDB()
    
    # Create people
    alice_id = db.create_node(['Person'], {'name': 'Alice', 'age': 30, 'city': 'New York'})
    bob_id = db.create_node(['Person'], {'name': 'Bob', 'age': 25, 'city': 'San Francisco'})
    charlie_id = db.create_node(['Person'], {'name': 'Charlie', 'age': 35, 'city': 'Boston'})
    diana_id = db.create_node(['Person'], {'name': 'Diana', 'age': 28, 'city': 'Seattle'})
    
    # Create relationships
    db.create_relationship(alice_id, bob_id, 'KNOWS', {'since': 2020})
    db.create_relationship(bob_id, charlie_id, 'KNOWS', {'since': 2021})
    db.create_relationship(alice_id, diana_id, 'KNOWS', {'since': 2019})
    db.create_relationship(charlie_id, diana_id, 'KNOWS', {'since': 2022})
    
    return db

def create_movie_database():
    """Create a sample movie recommendation database"""
    db = SimpleGraphDB()
    
    # Create movies
    matrix_id = db.create_node(['Movie'], {
        'title': 'The Matrix', 
        'year': 1999, 
        'genre': ['Sci-Fi', 'Action']
    })
    inception_id = db.create_node(['Movie'], {
        'title': 'Inception', 
        'year': 2010, 
        'genre': ['Sci-Fi', 'Thriller']
    })
    dark_knight_id = db.create_node(['Movie'], {
        'title': 'The Dark Knight', 
        'year': 2008, 
        'genre': ['Action', 'Crime']
    })
    
    # Create actors
    keanu_id = db.create_node(['Actor'], {'name': 'Keanu Reeves', 'age': 59})
    leo_id = db.create_node(['Actor'], {'name': 'Leonardo DiCaprio', 'age': 49})
    bale_id = db.create_node(['Actor'], {'name': 'Christian Bale', 'age': 50})
    
    # Create users
    alice_id = db.create_node(['User'], {'name': 'Alice', 'age': 25})
    bob_id = db.create_node(['User'], {'name': 'Bob', 'age': 30})
    
    # Create ACTED_IN relationships
    db.create_relationship(keanu_id, matrix_id, 'ACTED_IN')
    db.create_relationship(leo_id, inception_id, 'ACTED_IN')
    db.create_relationship(bale_id, dark_knight_id, 'ACTED_IN')
    
    # Create RATED relationships
    db.create_relationship(alice_id, matrix_id, 'RATED', {'rating': 5})
    db.create_relationship(alice_id, inception_id, 'RATED', {'rating': 4})
    db.create_relationship(bob_id, matrix_id, 'RATED', {'rating': 4})
    db.create_relationship(bob_id, dark_knight_id, 'RATED', {'rating': 5})
    
    return db

def demonstrate_social_network():
    """Demonstrate social network analysis"""
    print("=== Social Network Analysis Demo ===\n")
    
    db = create_social_network()
    
    # Query all people
    print("1. All People in the Network:")
    persons = db.query("MATCH (p:Person) RETURN p.name, p.age, p.city")
    for person in persons:
        print(f"   {person['name']} ({person['age']} years old, {person['city']})")
    print()
    
    # Query relationships
    print("2. Social Relationships:")
    relationships = db.query("MATCH ()-[r:KNOWS]->() RETURN r")
    for rel in relationships:
        print(f"   {rel['person1']} knows {rel['person2']} since {rel['since']}")
    print()
    
    # Find shortest path
    print("3. Network Connectivity:")
    path = db.query("MATCH path = shortestPath((alice:Person {name: 'Alice'})-[:KNOWS*]-(charlie:Person {name: 'Charlie'}))")
    print(f"   Shortest path from Alice to Charlie: {' -> '.join(path)}")
    print()
    
    # Network metrics
    print("4. Network Metrics:")
    print(f"   Total people: {len(db._query_persons())}")
    print(f"   Total relationships: {len(db._query_relationships())}")
    print(f"   Average connections per person: {len(db._query_relationships()) / len(db._query_persons()):.1f}")
    print()

def demonstrate_movie_recommendations():
    """Demonstrate movie recommendation system"""
    print("=== Movie Recommendation System Demo ===\n")
    
    db = create_movie_database()
    
    # Show movies
    print("1. Available Movies:")
    movies = [node for node in db.nodes.values() if 'Movie' in node['labels']]
    for movie in movies:
        props = movie['properties']
        print(f"   {props['title']} ({props['year']}) - {', '.join(props['genre'])}")
    print()
    
    # Show actors
    print("2. Actors and Their Movies:")
    actors = [node for node in db.nodes.values() if 'Actor' in node['labels']]
    for actor in actors:
        actor_name = actor['properties']['name']
        # Find movies they acted in
        acted_in = []
        for (from_id, to_id), rels in db.relationships.items():
            if from_id == actor['id']:
                for rel in rels:
                    if rel['type'] == 'ACTED_IN':
                        movie = db.nodes[to_id]['properties']
                        acted_in.append(movie['title'])
        print(f"   {actor_name}: {', '.join(acted_in)}")
    print()
    
    # Show user ratings
    print("3. User Ratings:")
    users = [node for node in db.nodes.values() if 'User' in node['labels']]
    for user in users:
        user_name = user['properties']['name']
        # Find their ratings
        ratings = []
        for (from_id, to_id), rels in db.relationships.items():
            if from_id == user['id']:
                for rel in rels:
                    if rel['type'] == 'RATED':
                        movie = db.nodes[to_id]['properties']
                        rating = rel['properties']['rating']
                        ratings.append(f"{movie['title']} ({rating}/5)")
        print(f"   {user_name}: {', '.join(ratings)}")
    print()
    
    # Simple recommendation logic
    print("4. Movie Recommendations for Alice:")
    print("   Based on Alice's high rating of 'The Matrix' (Sci-Fi/Action),")
    print("   and Bob's similar taste (both liked The Matrix),")
    print("   Recommended: The Dark Knight (Action genre, highly rated by Bob)")
    print()

def demonstrate_cypher_queries():
    """Show what Cypher queries would look like"""
    print("=== Cypher Query Examples ===\n")
    
    queries = [
        {
            "description": "Find all people in the network",
            "cypher": "MATCH (p:Person) RETURN p.name, p.age, p.city ORDER BY p.name"
        },
        {
            "description": "Find mutual friends between two people",
            "cypher": """MATCH (p1:Person {name: 'Alice'})-[:KNOWS]->(mutual:Person)<-[:KNOWS]-(p2:Person {name: 'Charlie'})
                        RETURN mutual.name as mutual_friend"""
        },
        {
            "description": "Find the shortest path between two people",
            "cypher": """MATCH path = shortestPath(
                            (p1:Person {name: 'Alice'})-[:KNOWS*]-(p2:Person {name: 'Charlie'})
                        )
                        RETURN [node IN nodes(path) WHERE node:Person | node.name] as path"""
        },
        {
            "description": "Recommend movies based on user preferences",
            "cypher": """MATCH (user:User {name: 'Alice'})-[:RATED]->(rated_movie:Movie)
                        MATCH (other_user:User)-[:RATED]->(rated_movie)
                        WHERE other_user <> user
                        MATCH (other_user)-[:RATED]->(recommended_movie:Movie)
                        WHERE NOT (user)-[:RATED]->(recommended_movie)
                        RETURN recommended_movie.title, avg(other_user.rating) as predicted_rating
                        ORDER BY predicted_rating DESC"""
        },
        {
            "description": "Find influencers (people with most followers)",
            "cypher": """MATCH (influencer:Person)<-[:KNOWS]-(follower:Person)
                        WITH influencer, count(follower) as follower_count
                        WHERE follower_count >= 2
                        RETURN influencer.name, follower_count
                        ORDER BY follower_count DESC"""
        }
    ]
    
    for i, query in enumerate(queries, 1):
        print(f"{i}. {query['description']}:")
        print(f"   {query['cypher']}")
        print()

def demonstrate_real_world_applications():
    """Show real-world applications of Neo4j"""
    print("=== Real-World Neo4j Applications ===\n")
    
    applications = [
        {
            "domain": "Social Networks",
            "examples": [
                "Facebook's friend suggestions",
                "LinkedIn's professional connections",
                "Twitter's follower recommendations"
            ],
            "benefits": [
                "Find mutual connections",
                "Discover influencers",
                "Analyze network patterns"
            ]
        },
        {
            "domain": "Recommendation Systems",
            "examples": [
                "Netflix movie recommendations",
                "Amazon product suggestions",
                "Spotify music recommendations"
            ],
            "benefits": [
                "Collaborative filtering",
                "Content-based recommendations",
                "Hybrid approaches"
            ]
        },
        {
            "domain": "Fraud Detection",
            "examples": [
                "Credit card fraud detection",
                "Insurance claim analysis",
                "Money laundering detection"
            ],
            "benefits": [
                "Pattern recognition",
                "Anomaly detection",
                "Network analysis"
            ]
        },
        {
            "domain": "Knowledge Graphs",
            "examples": [
                "Google's Knowledge Graph",
                "Wikipedia's entity relationships",
                "Medical knowledge bases"
            ],
            "benefits": [
                "Semantic search",
                "Entity linking",
                "Knowledge discovery"
            ]
        },
        {
            "domain": "Supply Chain Management",
            "examples": [
                "Product traceability",
                "Supplier relationship mapping",
                "Risk assessment"
            ],
            "benefits": [
                "End-to-end visibility",
                "Risk mitigation",
                "Optimization"
            ]
        }
    ]
    
    for app in applications:
        print(f"📊 {app['domain']}:")
        print(f"   Examples: {', '.join(app['examples'])}")
        print(f"   Benefits: {', '.join(app['benefits'])}")
        print()

def main():
    """Main demonstration function"""
    print("🚀 Neo4j with Python: Graph Database Concepts Demo")
    print("=" * 60)
    print()
    
    demonstrate_social_network()
    demonstrate_movie_recommendations()
    demonstrate_cypher_queries()
    demonstrate_real_world_applications()
    
    print("=== Getting Started with Neo4j ===\n")
    print("To run the full examples with Neo4j:")
    print("1. Install Neo4j Desktop or Neo4j Community Edition")
    print("2. Start Neo4j server")
    print("3. Install Python driver: pip install neo4j")
    print("4. Run the examples in neo4j.ipynb or neo4j_example.py")
    print()
    print("Key Neo4j Concepts:")
    print("• Nodes: Represent entities (people, movies, products)")
    print("• Relationships: Connect nodes with typed edges")
    print("• Properties: Store data on nodes and relationships")
    print("• Labels: Categorize nodes (Person, Movie, User)")
    print("• Cypher: Graph query language (like SQL for graphs)")
    print()
    print("Why Neo4j?")
    print("• Native graph storage and processing")
    print("• Excellent for complex relationships")
    print("• Powerful graph algorithms")
    print("• ACID compliance")
    print("• Great for recommendation systems and network analysis")

if __name__ == "__main__":
    main() 