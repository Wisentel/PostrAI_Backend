from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
from typing import List, Optional

from helpers.user import hash_password, check_password
from models import User, UserSignup, UserResponse, UserLogin, AddUserTopics, TopicPreferenceResponse, GetUserTopics, GetUserTopicsResponse, AddUserDocuments, UserDocumentResponse, GetUserDocuments, GetUserDocumentsResponse, AddResearchPapersMetadata, ResearchPaperMetadataResponse, GetResearchPapersMetadata, AddComment, CommentResponse, GetComments, GetCommentsResponse, UpdateComment, SimpleCommentResponse
from database.mongodb import mongo_manager

app = FastAPI(title="PostrAI API", description="Backend API for PostrAI application")

# Configure CORS with more explicit settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080", "http://127.0.0.1:8080"],  # Include both localhost and 127.0.0.1
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "HEAD", "PATCH"],
    allow_headers=["Content-Type", "Authorization", "Accept", "Origin", "X-Requested-With", "*"],
    expose_headers=["*"],
    max_age=3600,
)

# Add middleware to log requests for debugging
@app.middleware("http")
async def log_requests(request, call_next):
    print(f"Request: {request.method} {request.url}")
    print(f"Headers: {dict(request.headers)}")
    
    response = await call_next(request)
    
    print(f"Response status: {response.status_code}")
    return response

# Health check endpoint
@app.get("/api/health")
async def health_check():
    return {"status": "ok", "message": "API is running"}

# Explicit OPTIONS handler for signup endpoint
@app.options("/api/signup")
async def signup_options():
    return {"message": "OK"}




@app.post("/api/signup")
async def signup(user_data: UserSignup):
    try:
        # Check if user already exists
        existing_user = mongo_manager.find_user_by_email(user_data.email)
        if existing_user:
            return {
                "success": False,
                "message": "Email is already registered. Please use a different email or login instead."
            }
        
        # Hash the password
        hashed_password = hash_password(user_data.password)
        
        # Prepare user data for database
        user_doc = {
            "firstName": user_data.firstName,
            "lastName": user_data.lastName,
            "email": user_data.email,
            "password": hashed_password  # Store hashed password
        }
        
        # Create user in database
        created_user = mongo_manager.create_user(user_doc)
        
        if not created_user:
            return {
                "success": False,
                "message": "Failed to create user account"
            }
        
        # Return successful response with user data
        return {
            "success": True,
            "message": "User registered successfully",
            "user": UserResponse(**created_user)
        }
        
    except ValueError as e:
        return {
            "success": False,
            "message": str(e)
        }
    except Exception as e:
        print(f"Signup error: {e}")
        return {
            "success": False,
            "message": "An error occurred during registration"
        }




@app.post("/api/login", response_model=UserResponse)
async def login(user_data: UserLogin):
    try:
        # Find user by email
        user = mongo_manager.find_user_by_email(user_data.email)
        if not user:
            raise HTTPException(status_code=401, detail="Invalid email or password")
        
        # Verify password
        if not check_password(user_data.password, user["password"]):
            raise HTTPException(status_code=401, detail="Invalid email or password")
        
        # Remove password from response
        user.pop("password", None)
        
        # Return user data
        return UserResponse(**user)
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Login error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")




@app.post("/api/add-user-topics")
async def add_user_topics(request_data: AddUserTopics):
    try:
        # Validate input
        if not request_data.topics:
            return {
                "success": False,
                "message": "At least one topic must be provided"
            }
        
        # Clean and validate topics
        clean_topics = []
        for topic in request_data.topics:
            topic_clean = topic.strip()
            if topic_clean and len(topic_clean) > 0:
                clean_topics.append(topic_clean)
        
        if not clean_topics:
            return {
                "success": False,
                "message": "No valid topics provided"
            }
        
        # Add topics for the user
        created_topics = mongo_manager.add_user_topics(request_data.user_id, clean_topics)
        
        # Convert to response format
        topic_responses = []
        for topic in created_topics:
            topic_responses.append(TopicPreferenceResponse(**topic))
        
        # Determine appropriate message based on results
        total_added = len(created_topics)
        total_skipped = len(clean_topics) - len(created_topics)
        
        if total_added == 0 and total_skipped > 0:
            # All topics already existed
            if total_skipped == 1:
                message = "Topic already exists for this user"
            else:
                message = f"All {total_skipped} topics already exist for this user"
        elif total_added > 0 and total_skipped == 0:
            # All topics were added successfully
            message = f"Successfully added {total_added} topics"
        else:
            # Some topics were added, some already existed
            message = f"Successfully added {total_added} topics, {total_skipped} already existed"
        
        return {
            "success": True,
            "message": message,
            "topics": topic_responses,
            "total_added": total_added,
            "skipped": total_skipped
        }
        
    except ValueError as e:
        return {
            "success": False,
            "message": str(e)
        }
    except Exception as e:
        print(f"Add topics error: {e}")
        return {
            "success": False,
            "message": "An error occurred while adding topics"
        }




@app.post("/api/get-user-topics")
async def get_user_topics(request_data: GetUserTopics):
    try:
        # Get all topics for the user
        user_topics = mongo_manager.get_user_topics(request_data.user_id)
        
        # Extract just the topic names
        topic_names = [topic["topic_name"] for topic in user_topics]
        
        return {
            "success": True,
            "user_id": request_data.user_id,
            "topics": topic_names
        }
        
    except Exception as e:
        print(f"Get user topics error: {e}")
        return {
            "success": False,
            "user_id": request_data.user_id,
            "topics": []
        }




@app.post("/api/add-user-documents")
async def add_user_documents(request_data: AddUserDocuments):
    try:
        # Validate input
        if not request_data.document_ids:
            return {
                "success": False,
                "message": "At least one document ID must be provided"
            }
        
        # Clean and validate document IDs
        clean_document_ids = []
        for doc_id in request_data.document_ids:
            doc_id_clean = doc_id.strip()
            if doc_id_clean and len(doc_id_clean) > 0:
                clean_document_ids.append(doc_id_clean)
        
        if not clean_document_ids:
            return {
                "success": False,
                "message": "No valid document IDs provided"
            }
        
        # Add documents for the user
        created_documents = mongo_manager.add_user_documents(
            request_data.user_id, 
            clean_document_ids,
            request_data.folder,
            request_data.is_favorite
        )
        
        # Convert to response format
        document_responses = []
        for doc in created_documents:
            document_responses.append(UserDocumentResponse(**doc))
        
        # Determine appropriate message based on results
        total_added = len(created_documents)
        total_skipped = len(clean_document_ids) - len(created_documents)
        
        if total_added == 0 and total_skipped > 0:
            # All documents already existed
            if total_skipped == 1:
                message = "Document already exists for this user"
            else:
                message = f"All {total_skipped} documents already exist for this user"
        elif total_added > 0 and total_skipped == 0:
            # All documents were added successfully
            message = f"Successfully added {total_added} documents"
        else:
            # Some documents were added, some already existed
            message = f"Successfully added {total_added} documents, {total_skipped} already existed"
        
        return {
            "success": True,
            "message": message,
            "documents": document_responses,
            "total_added": total_added,
            "skipped": total_skipped
        }
        
    except ValueError as e:
        return {
            "success": False,
            "message": str(e)
        }
    except Exception as e:
        print(f"Add documents error: {e}")
        return {
            "success": False,
            "message": "An error occurred while adding documents"
        }




@app.post("/api/get-user-documents")
async def get_user_documents(request_data: GetUserDocuments):
    try:
        # Get all documents for the user
        user_documents = mongo_manager.get_user_documents(request_data.user_id)
        
        # Extract just the document IDs
        document_ids = [doc["document_id"] for doc in user_documents]
        
        return {
            "success": True,
            "user_id": request_data.user_id,
            "document_ids": document_ids
        }
        
    except Exception as e:
        print(f"Get user documents error: {e}")
        return {
            "success": False,
            "user_id": request_data.user_id,
            "document_ids": []
        }




@app.post("/api/add-research-papers-metadata")
async def add_research_papers_metadata(request_data: AddResearchPapersMetadata):
    try:
        # Validate input
        if not request_data.research_papers_metadata:
            return {
                "success": False,
                "message": "At least one research paper metadata must be provided"
            }
        
        # Validate each paper metadata
        valid_papers = []
        for paper in request_data.research_papers_metadata:
            # Convert Pydantic model to dict for database operations
            paper_dict = paper.dict()
            
            # Validate required fields
            required_fields = ["document_id", "title", "authors", "published_date", "source", "abstract"]
            missing_fields = [field for field in required_fields if not paper_dict.get(field)]
            
            if missing_fields:
                return {
                    "success": False,
                    "message": f"Missing required fields for paper '{paper_dict.get('document_id', 'unknown')}': {', '.join(missing_fields)}"
                }
            
            # Clean and validate data
            paper_dict["document_id"] = paper_dict["document_id"].strip()
            paper_dict["title"] = paper_dict["title"].strip()
            paper_dict["source"] = paper_dict["source"].strip()
            paper_dict["abstract"] = paper_dict["abstract"].strip()
            
            # Clean summary if provided
            if paper_dict.get("summary"):
                paper_dict["summary"] = paper_dict["summary"].strip()
            
            # Clean PDF URL if provided
            if paper_dict.get("pdf_url"):
                paper_dict["pdf_url"] = paper_dict["pdf_url"].strip()
            
            # Ensure authors is a list
            if isinstance(paper_dict["authors"], str):
                paper_dict["authors"] = [paper_dict["authors"]]
            
            # Clean author names
            paper_dict["authors"] = [author.strip() for author in paper_dict["authors"] if author.strip()]
            
            if not paper_dict["authors"]:
                return {
                    "success": False,
                    "message": f"At least one author must be provided for paper '{paper_dict['document_id']}'"
                }
            
            # Handle labels field
            if paper_dict.get("labels"):
                if isinstance(paper_dict["labels"], str):
                    # If labels is a string, convert to list
                    paper_dict["labels"] = [paper_dict["labels"]]
                elif isinstance(paper_dict["labels"], list):
                    # Clean label names and remove empty ones
                    paper_dict["labels"] = [label.strip() for label in paper_dict["labels"] if label and label.strip()]
                else:
                    # Invalid labels format
                    return {
                        "success": False,
                        "message": f"Labels must be a string or list of strings for paper '{paper_dict['document_id']}'"
                    }
                
                # Remove labels field if empty after cleaning
                if not paper_dict["labels"]:
                    paper_dict["labels"] = None
            
            valid_papers.append(paper_dict)
        
        if not valid_papers:
            return {
                "success": False,
                "message": "No valid research papers metadata provided"
            }
        
        # Add research papers metadata to database
        created_papers = mongo_manager.add_research_papers_metadata(valid_papers)
        
        # Convert to response format
        paper_responses = []
        for paper in created_papers:
            paper_responses.append(ResearchPaperMetadataResponse(**paper))
        
        # Determine appropriate message based on results
        total_processed = len(valid_papers)
        total_added = len(created_papers)
        
        if total_added == total_processed:
            message = f"Successfully processed {total_added} research papers"
        else:
            message = f"Successfully processed {total_added} research papers, {total_processed - total_added} were updated"
        
        return {
            "success": True,
            "message": message,
            "papers": paper_responses,
            "total_processed": total_processed,
            "total_added_or_updated": total_added
        }
        
    except Exception as e:
        print(f"Add research papers metadata error: {e}")
        return {
            "success": False,
            "message": "An error occurred while adding research papers metadata"
        }




@app.post("/api/get-research-papers-metadata")
async def get_research_papers_metadata(request_data: GetResearchPapersMetadata):
    try:
        # Validate input
        if not request_data.document_ids:
            return {
                "success": False,
                "message": "At least one document ID must be provided"
            }
        
        # Clean and validate document IDs
        clean_document_ids = []
        for doc_id in request_data.document_ids:
            doc_id_clean = doc_id.strip()
            if doc_id_clean and len(doc_id_clean) > 0:
                clean_document_ids.append(doc_id_clean)
        
        if not clean_document_ids:
            return {
                "success": False,
                "message": "No valid document IDs provided"
            }
        
        # Get research papers metadata from database
        papers_metadata = mongo_manager.get_research_papers_metadata(clean_document_ids)
        
        # Convert to response format
        paper_responses = []
        for paper in papers_metadata:
            paper_responses.append(ResearchPaperMetadataResponse(**paper))
        
        # Determine which document IDs were found and which were not
        found_document_ids = [paper["document_id"] for paper in papers_metadata]
        not_found_document_ids = [doc_id for doc_id in clean_document_ids if doc_id not in found_document_ids]
        
        return {
            "success": True,
            "message": f"Retrieved metadata for {len(paper_responses)} papers",
            "papers": paper_responses,
            "total_requested": len(clean_document_ids),
            "total_found": len(paper_responses),
            "not_found": not_found_document_ids
        }
        
    except Exception as e:
        print(f"Get research papers metadata error: {e}")
        return {
            "success": False,
            "message": "An error occurred while retrieving research papers metadata"
        }




@app.post("/api/add-comment")
async def add_comment(request_data: AddComment):
    try:
        # Validate input
        if not request_data.document_id or not request_data.document_id.strip():
            return {
                "success": False,
                "message": "Document ID is required"
            }
        
        if not request_data.user_id or not request_data.user_id.strip():
            return {
                "success": False,
                "message": "User ID is required"
            }
        
        if not request_data.comment_text or not request_data.comment_text.strip():
            return {
                "success": False,
                "message": "Comment text is required"
            }
        
        # Clean input data
        document_id = request_data.document_id.strip()
        user_id = request_data.user_id.strip()
        comment_text = request_data.comment_text.strip()
        
        # Validate comment length
        if len(comment_text) > 2000:  # Set reasonable limit
            return {
                "success": False,
                "message": "Comment text is too long (maximum 2000 characters)"
            }
        
        # Add comment to database
        created_comment = mongo_manager.add_comment(document_id, user_id, comment_text)
        
        if not created_comment:
            return {
                "success": False,
                "message": "Failed to add comment"
            }
        
        # Convert to response format
        comment_response = CommentResponse(**created_comment)
        
        return {
            "success": True,
            "message": "Comment added successfully",
            "comment": comment_response
        }
        
    except ValueError as e:
        return {
            "success": False,
            "message": str(e)
        }
    except Exception as e:
        print(f"Add comment error: {e}")
        return {
            "success": False,
            "message": "An error occurred while adding the comment"
        }




@app.post("/api/get-comments")
async def get_comments(request_data: GetComments):
    try:
        # Validate input
        if not request_data.user_id or not request_data.user_id.strip():
            return {
                "success": False,
                "message": "User ID is required"
            }
        
        if not request_data.document_id or not request_data.document_id.strip():
            return {
                "success": False,
                "message": "Document ID is required"
            }
        
        # Clean input data
        user_id = request_data.user_id.strip()
        document_id = request_data.document_id.strip()
        
        # Verify user exists
        user = mongo_manager.find_user_by_id(user_id)
        if not user:
            return {
                "success": False,
                "message": "User not found"
            }
        
        # Get all comments for the document
        comments_data = mongo_manager.get_comments_by_document(document_id)
        
        # Convert to simplified response format
        comments_list = []
        for comment in comments_data:
            simple_comment = SimpleCommentResponse(
                comment_id=comment["comment_id"],
                user_id=comment["user_id"],
                document_id=comment["document_id"],
                comment_text=comment["comment_text"]
            )
            comments_list.append(simple_comment.dict())
        
        return {
            "comments": comments_list
        }
        
    except Exception as e:
        print(f"Get comments error: {e}")
        return {
            "comments": []
        }




@app.post("/api/update-comment")
async def update_comment(request_data: UpdateComment):
    try:
        # Validate input
        if not request_data.user_id or not request_data.user_id.strip():
            return {
                "success": False,
                "message": "User ID is required"
            }
        
        if not request_data.document_id or not request_data.document_id.strip():
            return {
                "success": False,
                "message": "Document ID is required"
            }
        
        if not request_data.comment_id or not request_data.comment_id.strip():
            return {
                "success": False,
                "message": "Comment ID is required"
            }
        
        if not request_data.comment_text or not request_data.comment_text.strip():
            return {
                "success": False,
                "message": "Comment text is required"
            }
        
        # Clean input data
        user_id = request_data.user_id.strip()
        document_id = request_data.document_id.strip()
        comment_id = request_data.comment_id.strip()
        comment_text = request_data.comment_text.strip()
        
        # Validate comment length
        if len(comment_text) > 2000:  # Set reasonable limit
            return {
                "success": False,
                "message": "Comment text is too long (maximum 2000 characters)"
            }
        
        # Check if the comment exists and belongs to the user
        existing_comment = mongo_manager.get_comment_by_id(comment_id)
        if not existing_comment:
            return {
                "success": False,
                "message": "Comment not found"
            }
        
        # Verify the comment belongs to the user
        if existing_comment["user_id"] != user_id:
            return {
                "success": False,
                "message": "You can only update your own comments"
            }
        
        # Verify the comment belongs to the specified document
        if existing_comment["document_id"] != document_id:
            return {
                "success": False,
                "message": "Comment does not belong to the specified document"
            }
        
        # Update the comment in the database
        update_success = mongo_manager.update_comment(comment_id, user_id, comment_text)
        
        if not update_success:
            return {
                "success": False,
                "message": "Failed to update comment"
            }
        
        # Get the updated comment
        updated_comment = mongo_manager.get_comment_by_id(comment_id)
        
        if not updated_comment:
            return {
                "success": False,
                "message": "Comment was updated but could not retrieve updated data"
            }
        
        # Convert to response format
        comment_response = CommentResponse(**updated_comment)
        
        return {
            "success": True,
            "message": "Comment updated successfully",
            "comment": comment_response
        }
        
    except Exception as e:
        print(f"Update comment error: {e}")
        return {
            "success": False,
            "message": "An error occurred while updating the comment"
        }




@app.post("/api/scraper/master-scraper")
async def master_scraper(arxiv_url: str):
    pass

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app_main:app", host="0.0.0.0", port=8000, reload=True)