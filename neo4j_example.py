from neo4j import GraphDatabase
import random
from datetime import datetime, timedelta
import json

class SocialNetworkAnalyzer:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
        
    def close(self):
        self.driver.close()
        
    def clear_database(self):
        """Clear all data from the database"""
        with self.driver.session() as session:
            session.run("MATCH (n) DETACH DELETE n")
            print("Database cleared!")
    
    def create_sample_data(self):
        """Create a sample social network with users, posts, and relationships"""
        with self.driver.session() as session:
            # Create users with different interests
            users_data = [
                {"name": "Alice", "age": 28, "city": "New York", "interests": ["AI", "Machine Learning", "Python"]},
                {"name": "Bob", "age": 32, "city": "San Francisco", "interests": ["Data Science", "Neo4j", "Graph Theory"]},
                {"name": "Charlie", "age": 25, "city": "Boston", "interests": ["Web Development", "JavaScript", "React"]},
                {"name": "Diana", "age": 30, "city": "Seattle", "interests": ["AI", "Neural Networks", "Python"]},
                {"name": "Eve", "age": 27, "city": "Austin", "interests": ["Data Science", "Python", "Statistics"]},
                {"name": "Frank", "age": 35, "city": "New York", "interests": ["Graph Theory", "Algorithms", "Neo4j"]},
                {"name": "Grace", "age": 29, "city": "San Francisco", "interests": ["Machine Learning", "AI", "Python"]},
                {"name": "Henry", "age": 31, "city": "Boston", "interests": ["Web Development", "Python", "Django"]}
            ]
            
            # Create users
            for user_data in users_data:
                session.run("""
                    CREATE (u:User {
                        name: $name,
                        age: $age,
                        city: $city,
                        interests: $interests,
                        created_at: datetime()
                    })
                """, user_data)
            
            # Create posts
            posts_data = [
                {"title": "Introduction to Graph Databases", "content": "Graph databases are amazing for complex relationships...", "tags": ["Neo4j", "Graph Theory"]},
                {"title": "Machine Learning with Python", "content": "Here's how to get started with ML...", "tags": ["Python", "Machine Learning"]},
                {"title": "Building Social Networks", "content": "How to model social connections...", "tags": ["Social Networks", "Graph Theory"]},
                {"title": "AI Trends 2024", "content": "The latest developments in AI...", "tags": ["AI", "Machine Learning"]},
                {"title": "Web Development Best Practices", "content": "Modern web development techniques...", "tags": ["Web Development", "JavaScript"]},
                {"title": "Data Science Workflow", "content": "From data collection to insights...", "tags": ["Data Science", "Python"]}
            ]
            
            for post_data in posts_data:
                session.run("""
                    CREATE (p:Post {
                        title: $title,
                        content: $content,
                        tags: $tags,
                        created_at: datetime(),
                        likes: 0
                    })
                """, post_data)
            
            # Create friendships (FOLLOWS relationships)
            friendships = [
                ("Alice", "Bob"), ("Alice", "Diana"), ("Alice", "Grace"),
                ("Bob", "Charlie"), ("Bob", "Frank"), ("Bob", "Eve"),
                ("Charlie", "Diana"), ("Charlie", "Henry"),
                ("Diana", "Eve"), ("Diana", "Grace"),
                ("Eve", "Frank"), ("Eve", "Grace"),
                ("Frank", "Grace"), ("Frank", "Henry"),
                ("Grace", "Henry")
            ]
            
            for friend1, friend2 in friendships:
                session.run("""
                    MATCH (u1:User {name: $name1}), (u2:User {name: $name2})
                    CREATE (u1)-[:FOLLOWS {since: datetime()}]->(u2)
                """, name1=friend1, name2=friend2)
            
            # Create LIKES relationships
            likes = [
                ("Alice", "Introduction to Graph Databases"),
                ("Bob", "Machine Learning with Python"),
                ("Charlie", "Web Development Best Practices"),
                ("Diana", "AI Trends 2024"),
                ("Eve", "Data Science Workflow"),
                ("Frank", "Building Social Networks"),
                ("Grace", "Machine Learning with Python"),
                ("Henry", "Web Development Best Practices")
            ]
            
            for user_name, post_title in likes:
                session.run("""
                    MATCH (u:User {name: $user_name}), (p:Post {title: $post_title})
                    CREATE (u)-[:LIKES {timestamp: datetime()}]->(p)
                    SET p.likes = p.likes + 1
                """, user_name=user_name, post_title=post_title)
            
            # Create AUTHOR relationships
            authors = [
                ("Alice", "Introduction to Graph Databases"),
                ("Bob", "Machine Learning with Python"),
                ("Charlie", "Web Development Best Practices"),
                ("Diana", "AI Trends 2024"),
                ("Eve", "Data Science Workflow"),
                ("Frank", "Building Social Networks")
            ]
            
            for user_name, post_title in authors:
                session.run("""
                    MATCH (u:User {name: $user_name}), (p:Post {title: $post_title})
                    CREATE (u)-[:AUTHOR]->(p)
                """, user_name=user_name, post_title=post_title)
            
            print("Sample data created successfully!")
    
    def find_mutual_friends(self, user1_name, user2_name):
        """Find mutual friends between two users"""
        with self.driver.session() as session:
            result = session.run("""
                MATCH (u1:User {name: $user1})-[:FOLLOWS]->(mutual:User)<-[:FOLLOWS]-(u2:User {name: $user2})
                RETURN mutual.name as mutual_friend, mutual.city as city
                ORDER BY mutual.name
            """, user1=user1_name, user2=user2_name)
            
            mutual_friends = [record["mutual_friend"] for record in result]
            return mutual_friends
    
    def find_influencers(self, min_followers=2):
        """Find users with the most followers (influencers)"""
        with self.driver.session() as session:
            result = session.run("""
                MATCH (influencer:User)<-[:FOLLOWS]-(follower:User)
                WITH influencer, count(follower) as follower_count
                WHERE follower_count >= $min_followers
                RETURN influencer.name as name, 
                       follower_count as followers,
                       influencer.city as city,
                       influencer.interests as interests
                ORDER BY follower_count DESC
            """, min_followers=min_followers)
            
            return [dict(record) for record in result]
    
    def find_common_interests(self, user1_name, user2_name):
        """Find common interests between two users"""
        with self.driver.session() as session:
            result = session.run("""
                MATCH (u1:User {name: $user1}), (u2:User {name: $user2})
                RETURN [interest IN u1.interests WHERE interest IN u2.interests] as common_interests
            """, user1=user1_name, user2=user2_name)
            
            record = result.single()
            return record["common_interests"] if record else []
    
    def recommend_friends(self, user_name, limit=3):
        """Recommend friends based on common interests and mutual connections"""
        with self.driver.session() as session:
            result = session.run("""
                MATCH (user:User {name: $user_name})
                MATCH (potential:User)
                WHERE potential.name <> $user_name
                AND NOT (user)-[:FOLLOWS]->(potential)
                
                // Calculate common interests
                WITH user, potential, 
                     size([interest IN user.interests WHERE interest IN potential.interests]) as common_interests
                
                // Calculate mutual friends
                OPTIONAL MATCH (user)-[:FOLLOWS]->(mutual:User)<-[:FOLLOWS]-(potential)
                WITH user, potential, common_interests, count(mutual) as mutual_friends
                
                // Calculate recommendation score
                WITH potential, common_interests, mutual_friends,
                     (common_interests * 2) + mutual_friends as score
                
                RETURN potential.name as name,
                       potential.city as city,
                       potential.interests as interests,
                       common_interests,
                       mutual_friends,
                       score
                ORDER BY score DESC
                LIMIT $limit
            """, user_name=user_name, limit=limit)
            
            return [dict(record) for record in result]
    
    def find_popular_posts(self, min_likes=1):
        """Find the most popular posts"""
        with self.driver.session() as session:
            result = session.run("""
                MATCH (post:Post)
                WHERE post.likes >= $min_likes
                OPTIONAL MATCH (author:User)-[:AUTHOR]->(post)
                RETURN post.title as title,
                       post.likes as likes,
                       post.tags as tags,
                       author.name as author,
                       post.created_at as created_at
                ORDER BY post.likes DESC
            """, min_likes=min_likes)
            
            return [dict(record) for record in result]
    
    def find_shortest_path(self, user1_name, user2_name):
        """Find the shortest path between two users through follows relationships"""
        with self.driver.session() as session:
            result = session.run("""
                MATCH path = shortestPath(
                    (u1:User {name: $user1})-[:FOLLOWS*]-(u2:User {name: $user2})
                )
                RETURN [node IN nodes(path) WHERE node:User | node.name] as path
            """, user1=user1_name, user2=user2_name)
            
            record = result.single()
            return record["path"] if record else None
    
    def analyze_network_metrics(self):
        """Analyze overall network metrics"""
        with self.driver.session() as session:
            # Total users and posts
            stats = session.run("""
                MATCH (u:User)
                WITH count(u) as total_users
                MATCH (p:Post)
                WITH total_users, count(p) as total_posts
                MATCH ()-[r:FOLLOWS]->()
                WITH total_users, total_posts, count(r) as total_follows
                MATCH ()-[l:LIKES]->()
                WITH total_users, total_posts, total_follows, count(l) as total_likes
                RETURN total_users, total_posts, total_follows, total_likes
            """).single()
            
            # Average followers per user
            avg_followers = session.run("""
                MATCH (u:User)
                OPTIONAL MATCH (u)<-[:FOLLOWS]-(follower:User)
                WITH u, count(follower) as follower_count
                RETURN avg(follower_count) as avg_followers
            """).single()["avg_followers"]
            
            # Most active city
            active_city = session.run("""
                MATCH (u:User)
                WITH u.city as city, count(u) as user_count
                ORDER BY user_count DESC
                LIMIT 1
                RETURN city, user_count
            """).single()
            
            return {
                "total_users": stats["total_users"],
                "total_posts": stats["total_posts"],
                "total_follows": stats["total_follows"],
                "total_likes": stats["total_likes"],
                "avg_followers_per_user": round(avg_followers, 2),
                "most_active_city": active_city["city"],
                "users_in_most_active_city": active_city["user_count"]
            }

def main():
    # Connect to Neo4j (update these credentials as needed)
    uri = "bolt://localhost:7687"
    user = "neo4j"
    password = "password"  # Change this to your actual password
    
    analyzer = SocialNetworkAnalyzer(uri, user, password)
    
    try:
        print("=== Social Network Analysis with Neo4j ===\n")
        
        # Clear existing data and create sample data
        print("1. Setting up sample data...")
        analyzer.clear_database()
        analyzer.create_sample_data()
        print()
        
        # Network metrics
        print("2. Network Overview:")
        metrics = analyzer.analyze_network_metrics()
        for key, value in metrics.items():
            print(f"   {key.replace('_', ' ').title()}: {value}")
        print()
        
        # Find influencers
        print("3. Top Influencers (users with most followers):")
        influencers = analyzer.find_influencers(min_followers=2)
        for influencer in influencers:
            print(f"   {influencer['name']} ({influencer['city']}): {influencer['followers']} followers")
            print(f"     Interests: {', '.join(influencer['interests'])}")
        print()
        
        # Mutual friends
        print("4. Mutual Friends Analysis:")
        mutual_friends = analyzer.find_mutual_friends("Alice", "Bob")
        print(f"   Mutual friends between Alice and Bob: {', '.join(mutual_friends) if mutual_friends else 'None'}")
        print()
        
        # Common interests
        print("5. Common Interests Analysis:")
        common_interests = analyzer.find_common_interests("Alice", "Diana")
        print(f"   Common interests between Alice and Diana: {', '.join(common_interests) if common_interests else 'None'}")
        print()
        
        # Friend recommendations
        print("6. Friend Recommendations for Alice:")
        recommendations = analyzer.recommend_friends("Alice", limit=3)
        for rec in recommendations:
            print(f"   {rec['name']} ({rec['city']}) - Score: {rec['score']}")
            print(f"     Common interests: {rec['common_interests']}, Mutual friends: {rec['mutual_friends']}")
        print()
        
        # Popular posts
        print("7. Most Popular Posts:")
        popular_posts = analyzer.find_popular_posts(min_likes=1)
        for post in popular_posts:
            print(f"   '{post['title']}' by {post['author']} - {post['likes']} likes")
            print(f"     Tags: {', '.join(post['tags'])}")
        print()
        
        # Shortest path
        print("8. Network Connectivity:")
        path = analyzer.find_shortest_path("Alice", "Henry")
        if path:
            print(f"   Shortest path from Alice to Henry: {' -> '.join(path)}")
        else:
            print("   No path found between Alice and Henry")
        print()
        
        print("=== Analysis Complete! ===")
        
    except Exception as e:
        print(f"Error: {e}")
        print("\nMake sure Neo4j is running and the credentials are correct.")
        print("You can start Neo4j with: neo4j start")
        print("Default credentials are usually neo4j/neo4j (you'll be prompted to change on first run)")
    
    finally:
        analyzer.close()

if __name__ == "__main__":
    main() 