from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from pymongo.errors import ConnectionFailure, DuplicateKeyError
from typing import Dict, List, Optional, Any
import os
from datetime import datetime
import uuid

class MongoDBManager:
    def __init__(self):
        # MongoDB connection URI - should be stored in environment variables
        self.uri = os.getenv("MONGODB_URI", "mongodb+srv://athishrajesh:89GaXb80iCkmJ4QX@wisentel.4aeym5h.mongodb.net/?retryWrites=true&w=majority&appName=Wisentel")
        self.client = None
        self.db = None
        self.connect()

    def connect(self):
        """Connect to MongoDB"""
        try:
            # Connection options to handle SSL issues in cloud environments
            connection_options = {
                'server_api': ServerApi('1'),
                'ssl': True,
                'tlsAllowInvalidCertificates': True,
                'tlsAllowInvalidHostnames': True,
                'connectTimeoutMS': 30000,
                'socketTimeoutMS': 30000,
                'serverSelectionTimeoutMS': 30000,
                'maxPoolSize': 10,
                'retryWrites': True,
                'w': 'majority'
            }
            
            self.client = MongoClient(self.uri, **connection_options)
            
            # Test the connection
            self.client.admin.command('ping')
            print("Successfully connected to MongoDB!")
            
            # Select database
            self.db = self.client["PostrAI_db"]
            
            # Create indexes for better performance
            self.create_indexes()
            
        except ConnectionFailure as e:
            print(f"Failed to connect to MongoDB: {e}")
            raise

    def create_indexes(self):
        """Create database indexes for better performance"""
        try:
            # Create unique index on email for user_profile collection
            self.db.user_profile.create_index("email", unique=True)
            
            # Create indexes for topic_preferences collection
            self.db.topic_preferences.create_index([("user_id", 1), ("topic_name", 1)], unique=True)
            self.db.topic_preferences.create_index("user_id")
            
            # Create indexes for user_documents collection
            self.db.user_documents.create_index([("user_id", 1), ("document_id", 1)], unique=True)
            self.db.user_documents.create_index("user_id")
            self.db.user_documents.create_index("document_id")
            self.db.user_documents.create_index("folder")
            
            # Create indexes for research_papers_metadata collection
            self.db.research_papers_metadata.create_index("document_id", unique=True)
            self.db.research_papers_metadata.create_index("source")
            self.db.research_papers_metadata.create_index("published_date")
            self.db.research_papers_metadata.create_index("title")
            
            # Create indexes for comments collection
            self.db.comments.create_index("comment_id", unique=True)
            self.db.comments.create_index("document_id")
            self.db.comments.create_index("user_id")
            self.db.comments.create_index("created_at")
            self.db.comments.create_index([("document_id", 1), ("created_at", -1)])  # For efficient comment retrieval
            
            print("Database indexes created successfully")
        except Exception as e:
            print(f"Error creating indexes: {e}")

    def close_connection(self):
        """Close MongoDB connection"""
        if self.client:
            self.client.close()
            print("MongoDB connection closed")

    # User Profile Operations
    def create_user(self, user_data: Dict) -> Dict:
        """Create a new user in the database"""
        try:
            # Add metadata
            user_data["user_id"] = str(uuid.uuid4())[:6]  # 6-character user ID
            user_data["created_at"] = datetime.now().isoformat()
            user_data["updated_at"] = datetime.now().isoformat()
            
            # Insert user
            result = self.db.user_profile.insert_one(user_data)
            
            # Return the created user (without password)
            created_user = self.db.user_profile.find_one({"_id": result.inserted_id})
            if created_user:
                created_user.pop("password", None)  # Remove password from response
                created_user["id"] = str(created_user.pop("_id"))  # Convert ObjectId to string
            
            return created_user
            
        except DuplicateKeyError:
            raise ValueError("Email already exists")
        except Exception as e:
            print(f"Error creating user: {e}")
            raise

    def find_user_by_email(self, email: str) -> Optional[Dict]:
        """Find user by email"""
        try:
            user = self.db.user_profile.find_one({"email": email})
            if user:
                user["id"] = str(user.pop("_id"))  # Convert ObjectId to string
            return user
        except Exception as e:
            print(f"Error finding user by email: {e}")
            return None

    def find_user_by_id(self, user_id: str) -> Optional[Dict]:
        """Find user by user_id"""
        try:
            user = self.db.user_profile.find_one({"user_id": user_id})
            if user:
                user["id"] = str(user.pop("_id"))  # Convert ObjectId to string
            return user
        except Exception as e:
            print(f"Error finding user by ID: {e}")
            return None

    def update_user(self, user_id: str, update_data: Dict) -> bool:
        """Update user information"""
        try:
            update_data["updated_at"] = datetime.now().isoformat()
            result = self.db.user_profile.update_one(
                {"user_id": user_id},
                {"$set": update_data}
            )
            return result.modified_count > 0
        except Exception as e:
            print(f"Error updating user: {e}")
            return False

    def delete_user(self, user_id: str) -> bool:
        """Delete user by user_id"""
        try:
            result = self.db.user_profile.delete_one({"user_id": user_id})
            return result.deleted_count > 0
        except Exception as e:
            print(f"Error deleting user: {e}")
            return False

    def get_all_users(self, limit: int = 100, skip: int = 0) -> List[Dict]:
        """Get all users with pagination"""
        try:
            users = list(self.db.user_profile.find({}, {"password": 0}).limit(limit).skip(skip))
            for user in users:
                user["id"] = str(user.pop("_id"))  # Convert ObjectId to string
            return users
        except Exception as e:
            print(f"Error getting all users: {e}")
            return []

    # Topic Preference Operations
    def add_user_topics(self, user_id: str, topics: List[str]) -> List[Dict]:
        """Add topics for a user"""
        try:
            # Check if user exists
            user = self.find_user_by_id(user_id)
            if not user:
                raise ValueError("User not found")
            
            created_topics = []
            for topic_name in topics:
                try:
                    # Prepare topic document
                    topic_doc = {
                        "user_id": user_id,
                        "topic_name": topic_name.strip(),
                        "status": "not_scraped",
                        "created_at": datetime.now().isoformat(),
                        "updated_at": datetime.now().isoformat()
                    }
                    
                    # Insert topic (will fail if duplicate due to unique index)
                    result = self.db.topic_preferences.insert_one(topic_doc)
                    
                    # Get the created topic
                    created_topic = self.db.topic_preferences.find_one({"_id": result.inserted_id})
                    if created_topic:
                        created_topic["id"] = str(created_topic.pop("_id"))
                        created_topics.append(created_topic)
                        
                except DuplicateKeyError:
                    # Topic already exists for this user, skip it
                    print(f"Topic '{topic_name}' already exists for user {user_id}")
                    continue
                    
            return created_topics
            
        except ValueError:
            raise
        except Exception as e:
            print(f"Error adding user topics: {e}")
            raise

    def get_user_topics(self, user_id: str) -> List[Dict]:
        """Get all topics for a user"""
        try:
            topics = list(self.db.topic_preferences.find({"user_id": user_id}))
            for topic in topics:
                topic["id"] = str(topic.pop("_id"))
            return topics
        except Exception as e:
            print(f"Error getting user topics: {e}")
            return []

    def update_topic_status(self, user_id: str, topic_name: str, status: str) -> bool:
        """Update topic status for a user"""
        try:
            result = self.db.topic_preferences.update_one(
                {"user_id": user_id, "topic_name": topic_name},
                {"$set": {"status": status, "updated_at": datetime.now().isoformat()}}
            )
            return result.modified_count > 0
        except Exception as e:
            print(f"Error updating topic status: {e}")
            return False

    def delete_user_topic(self, user_id: str, topic_name: str) -> bool:
        """Delete a specific topic for a user"""
        try:
            result = self.db.topic_preferences.delete_one(
                {"user_id": user_id, "topic_name": topic_name}
            )
            return result.deleted_count > 0
        except Exception as e:
            print(f"Error deleting user topic: {e}")
            return False

    # User Document Operations
    def add_user_documents(self, user_id: str, document_ids: List[str], folder: str = "my_papers", is_favorite: bool = False) -> List[Dict]:
        """Add documents for a user"""
        try:
            # Check if user exists
            user = self.find_user_by_id(user_id)
            if not user:
                raise ValueError("User not found")
            
            # Validate folder value
            valid_folders = ["public", "private", "my_papers"]
            if folder not in valid_folders:
                raise ValueError(f"Invalid folder. Must be one of: {', '.join(valid_folders)}")
            
            created_documents = []
            for document_id in document_ids:
                try:
                    # Prepare document relationship
                    doc_relation = {
                        "user_id": user_id,
                        "document_id": document_id.strip(),
                        "folder": folder,
                        "is_favorite": is_favorite,
                        "created_at": datetime.now().isoformat(),
                        "updated_at": datetime.now().isoformat()
                    }
                    
                    # Insert document relationship (will fail if duplicate due to unique index)
                    result = self.db.user_documents.insert_one(doc_relation)
                    
                    # Get the created document relationship
                    created_doc = self.db.user_documents.find_one({"_id": result.inserted_id})
                    if created_doc:
                        created_doc["id"] = str(created_doc.pop("_id"))
                        created_documents.append(created_doc)
                        
                except DuplicateKeyError:
                    # Document already exists for this user, skip it
                    print(f"Document '{document_id}' already exists for user {user_id}")
                    continue
                    
            return created_documents
            
        except ValueError:
            raise
        except Exception as e:
            print(f"Error adding user documents: {e}")
            raise

    def get_user_documents(self, user_id: str, folder: Optional[str] = None) -> List[Dict]:
        """Get all documents for a user, optionally filtered by folder"""
        try:
            query = {"user_id": user_id}
            if folder:
                query["folder"] = folder
                
            documents = list(self.db.user_documents.find(query))
            for doc in documents:
                doc["id"] = str(doc.pop("_id"))
            return documents
        except Exception as e:
            print(f"Error getting user documents: {e}")
            return []

    def update_user_document(self, user_id: str, document_id: str, update_data: Dict) -> bool:
        """Update user document relationship"""
        try:
            update_data["updated_at"] = datetime.now().isoformat()
            result = self.db.user_documents.update_one(
                {"user_id": user_id, "document_id": document_id},
                {"$set": update_data}
            )
            return result.modified_count > 0
        except Exception as e:
            print(f"Error updating user document: {e}")
            return False

    def delete_user_document(self, user_id: str, document_id: str) -> bool:
        """Delete a specific document relationship for a user"""
        try:
            result = self.db.user_documents.delete_one(
                {"user_id": user_id, "document_id": document_id}
            )
            return result.deleted_count > 0
        except Exception as e:
            print(f"Error deleting user document: {e}")
            return False

    def get_user_favorites(self, user_id: str) -> List[Dict]:
        """Get all favorite documents for a user"""
        try:
            documents = list(self.db.user_documents.find({"user_id": user_id, "is_favorite": True}))
            for doc in documents:
                doc["id"] = str(doc.pop("_id"))
            return documents
        except Exception as e:
            print(f"Error getting user favorites: {e}")
            return []

    # Research Papers Metadata Operations
    def add_research_papers_metadata(self, papers_metadata: List[Dict]) -> List[Dict]:
        """Add research papers metadata to the database"""
        try:
            created_papers = []
            for paper_data in papers_metadata:
                try:
                    # Prepare paper metadata document
                    paper_doc = {
                        "document_id": paper_data["document_id"],
                        "title": paper_data["title"],
                        "authors": paper_data["authors"],
                        "published_date": paper_data["published_date"],
                        "source": paper_data["source"],
                        "pdf_url": paper_data.get("pdf_url"),
                        "abstract": paper_data["abstract"],
                        "summary": paper_data.get("summary"),
                        "labels": paper_data.get("labels"),  # Add labels field
                        "created_at": datetime.now().isoformat(),
                        "updated_at": datetime.now().isoformat()
                    }
                    
                    # Insert paper metadata (will fail if duplicate due to unique index on document_id)
                    result = self.db.research_papers_metadata.insert_one(paper_doc)
                    
                    # Get the created paper metadata
                    created_paper = self.db.research_papers_metadata.find_one({"_id": result.inserted_id})
                    if created_paper:
                        created_paper["id"] = str(created_paper.pop("_id"))
                        created_papers.append(created_paper)
                        
                except DuplicateKeyError:
                    # Paper already exists, try to update it instead
                    print(f"Paper '{paper_data['document_id']}' already exists, updating...")
                    
                    update_data = {
                        "title": paper_data["title"],
                        "authors": paper_data["authors"],
                        "published_date": paper_data["published_date"],
                        "source": paper_data["source"],
                        "pdf_url": paper_data.get("pdf_url"),
                        "abstract": paper_data["abstract"],
                        "summary": paper_data.get("summary"),
                        "labels": paper_data.get("labels"),  # Add labels field
                        "updated_at": datetime.now().isoformat()
                    }
                    
                    # Update existing paper
                    result = self.db.research_papers_metadata.update_one(
                        {"document_id": paper_data["document_id"]},
                        {"$set": update_data}
                    )
                    
                    if result.modified_count > 0:
                        # Get the updated paper
                        updated_paper = self.db.research_papers_metadata.find_one({"document_id": paper_data["document_id"]})
                        if updated_paper:
                            updated_paper["id"] = str(updated_paper.pop("_id"))
                            created_papers.append(updated_paper)
                    
            return created_papers
            
        except Exception as e:
            print(f"Error adding research papers metadata: {e}")
            raise

    def get_research_papers_metadata(self, document_ids: List[str]) -> List[Dict]:
        """Get research papers metadata by document IDs"""
        try:
            papers = list(self.db.research_papers_metadata.find({"document_id": {"$in": document_ids}}))
            for paper in papers:
                paper["id"] = str(paper.pop("_id"))
            return papers
        except Exception as e:
            print(f"Error getting research papers metadata: {e}")
            return []

    def get_research_paper_by_id(self, document_id: str) -> Optional[Dict]:
        """Get a single research paper metadata by document ID"""
        try:
            paper = self.db.research_papers_metadata.find_one({"document_id": document_id})
            if paper:
                paper["id"] = str(paper.pop("_id"))
            return paper
        except Exception as e:
            print(f"Error getting research paper by ID: {e}")
            return None

    def update_research_paper_metadata(self, document_id: str, update_data: Dict) -> bool:
        """Update research paper metadata"""
        try:
            update_data["updated_at"] = datetime.now().isoformat()
            result = self.db.research_papers_metadata.update_one(
                {"document_id": document_id},
                {"$set": update_data}
            )
            return result.modified_count > 0
        except Exception as e:
            print(f"Error updating research paper metadata: {e}")
            return False

    def delete_research_paper_metadata(self, document_id: str) -> bool:
        """Delete research paper metadata"""
        try:
            result = self.db.research_papers_metadata.delete_one({"document_id": document_id})
            return result.deleted_count > 0
        except Exception as e:
            print(f"Error deleting research paper metadata: {e}")
            return False

    def search_research_papers(self, query: str, limit: int = 50) -> List[Dict]:
        """Search research papers by title, abstract, authors, or labels"""
        try:
            # Create text search query
            search_query = {
                "$or": [
                    {"title": {"$regex": query, "$options": "i"}},
                    {"abstract": {"$regex": query, "$options": "i"}},
                    {"authors": {"$regex": query, "$options": "i"}},
                    {"summary": {"$regex": query, "$options": "i"}},
                    {"labels": {"$regex": query, "$options": "i"}}  # Add labels to search
                ]
            }
            
            papers = list(self.db.research_papers_metadata.find(search_query).limit(limit))
            for paper in papers:
                paper["id"] = str(paper.pop("_id"))
            return papers
        except Exception as e:
            print(f"Error searching research papers: {e}")
            return []

    # Comments Operations
    def add_comment(self, document_id: str, user_id: str, comment_text: str) -> Dict:
        """Add a comment to a research paper"""
        try:
            # Check if user exists
            user = self.find_user_by_id(user_id)
            if not user:
                raise ValueError("User not found")
            
            # Check if research paper exists
            paper = self.get_research_paper_by_id(document_id)
            if not paper:
                raise ValueError("Research paper not found")
            
            # Generate unique comment ID
            comment_id = str(uuid.uuid4())
            
            # Prepare comment document
            comment_doc = {
                "comment_id": comment_id,
                "document_id": document_id,
                "user_id": user_id,
                "comment_text": comment_text.strip(),
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
            }
            
            # Insert comment
            result = self.db.comments.insert_one(comment_doc)
            
            # Get the created comment
            created_comment = self.db.comments.find_one({"_id": result.inserted_id})
            if created_comment:
                created_comment["id"] = str(created_comment.pop("_id"))
            
            return created_comment
            
        except ValueError:
            raise
        except Exception as e:
            print(f"Error adding comment: {e}")
            raise

    def get_comments_by_document(self, document_id: str, limit: int = 100, skip: int = 0) -> List[Dict]:
        """Get all comments for a specific research paper"""
        try:
            comments = list(
                self.db.comments.find({"document_id": document_id})
                .sort("created_at", -1)  # Sort by newest first
                .limit(limit)
                .skip(skip)
            )
            for comment in comments:
                comment["id"] = str(comment.pop("_id"))
            return comments
        except Exception as e:
            print(f"Error getting comments by document: {e}")
            return []

    def get_comments_by_user(self, user_id: str, limit: int = 100, skip: int = 0) -> List[Dict]:
        """Get all comments by a specific user"""
        try:
            comments = list(
                self.db.comments.find({"user_id": user_id})
                .sort("created_at", -1)  # Sort by newest first
                .limit(limit)
                .skip(skip)
            )
            for comment in comments:
                comment["id"] = str(comment.pop("_id"))
            return comments
        except Exception as e:
            print(f"Error getting comments by user: {e}")
            return []

    def update_comment(self, comment_id: str, user_id: str, comment_text: str) -> bool:
        """Update a comment (only by the original author)"""
        try:
            result = self.db.comments.update_one(
                {"comment_id": comment_id, "user_id": user_id},  # Ensure user can only update their own comments
                {"$set": {"comment_text": comment_text.strip(), "updated_at": datetime.now().isoformat()}}
            )
            return result.modified_count > 0
        except Exception as e:
            print(f"Error updating comment: {e}")
            return False

    def delete_comment(self, comment_id: str, user_id: str) -> bool:
        """Delete a comment (only by the original author)"""
        try:
            result = self.db.comments.delete_one(
                {"comment_id": comment_id, "user_id": user_id}  # Ensure user can only delete their own comments
            )
            return result.deleted_count > 0
        except Exception as e:
            print(f"Error deleting comment: {e}")
            return False

    def get_comment_by_id(self, comment_id: str) -> Optional[Dict]:
        """Get a single comment by comment ID"""
        try:
            comment = self.db.comments.find_one({"comment_id": comment_id})
            if comment:
                comment["id"] = str(comment.pop("_id"))
            return comment
        except Exception as e:
            print(f"Error getting comment by ID: {e}")
            return None

    def count_comments_by_document(self, document_id: str) -> int:
        """Count total comments for a specific research paper"""
        try:
            return self.db.comments.count_documents({"document_id": document_id})
        except Exception as e:
            print(f"Error counting comments by document: {e}")
            return 0

    # Generic collection operations
    def insert_document(self, collection_name: str, document: Dict) -> str:
        """Insert a document into any collection"""
        try:
            document["created_at"] = datetime.now().isoformat()
            result = self.db[collection_name].insert_one(document)
            return str(result.inserted_id)
        except Exception as e:
            print(f"Error inserting document: {e}")
            raise

    def find_documents(self, collection_name: str, query: Dict = None, limit: int = 100) -> List[Dict]:
        """Find documents in any collection"""
        try:
            query = query or {}
            documents = list(self.db[collection_name].find(query).limit(limit))
            for doc in documents:
                doc["id"] = str(doc.pop("_id"))  # Convert ObjectId to string
            return documents
        except Exception as e:
            print(f"Error finding documents: {e}")
            return []

    def update_document(self, collection_name: str, query: Dict, update_data: Dict) -> bool:
        """Update document in any collection"""
        try:
            update_data["updated_at"] = datetime.now().isoformat()
            result = self.db[collection_name].update_one(query, {"$set": update_data})
            return result.modified_count > 0
        except Exception as e:
            print(f"Error updating document: {e}")
            return False

    def delete_document(self, collection_name: str, query: Dict) -> bool:
        """Delete document from any collection"""
        try:
            result = self.db[collection_name].delete_one(query)
            return result.deleted_count > 0
        except Exception as e:
            print(f"Error deleting document: {e}")
            return False

# Global MongoDB manager instance
mongo_manager = MongoDBManager() 