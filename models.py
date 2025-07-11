from pydantic import BaseModel, EmailStr
from typing import Optional, List

# Data model for user signup
class UserSignup(BaseModel):
    firstName: str
    lastName: str
    email: EmailStr
    password: str

# Data model for user stored in database (without password)
class User(BaseModel):
    id: str
    user_id: str
    firstName: str
    lastName: str
    email: EmailStr
    created_at: str
    updated_at: Optional[str] = None

# Data model for user login
class UserLogin(BaseModel):
    email: EmailStr
    password: str

# Data model for user response (what we send back to frontend)
class UserResponse(BaseModel):
    id: str
    user_id: str
    firstName: str
    lastName: str
    email: EmailStr
    created_at: str

# Data model for adding user topics
class AddUserTopics(BaseModel):
    user_id: str
    topics: List[str]

# Data model for getting user topics request
class GetUserTopics(BaseModel):
    user_id: str

# Data model for getting user topics response
class GetUserTopicsResponse(BaseModel):
    success: bool
    user_id: str
    topics: List[str]

# Data model for getting user documents request
class GetUserDocuments(BaseModel):
    user_id: str

# Data model for getting user documents response
class GetUserDocumentsResponse(BaseModel):
    success: bool
    user_id: str
    document_ids: List[str]

# Data model for adding user documents
class AddUserDocuments(BaseModel):
    user_id: str
    document_ids: List[str]
    folder: Optional[str] = "my_papers"  # Default folder
    is_favorite: Optional[bool] = False  # Default not favorite

# Data model for user document stored in database
class UserDocument(BaseModel):
    id: str
    user_id: str
    document_id: str
    folder: str = "my_papers"
    is_favorite: bool = False
    created_at: str
    updated_at: Optional[str] = None

# Data model for user document response
class UserDocumentResponse(BaseModel):
    id: str
    user_id: str
    document_id: str
    folder: str
    is_favorite: bool
    created_at: str
    updated_at: Optional[str] = None

# Data model for topic preference stored in database
class TopicPreference(BaseModel):
    id: str
    user_id: str
    topic_name: str
    status: str = "not_scraped"  # "scraped" or "not_scraped"
    created_at: str
    updated_at: Optional[str] = None

# Data model for topic preference response
class TopicPreferenceResponse(BaseModel):
    id: str
    user_id: str
    topic_name: str
    status: str
    created_at: str
    updated_at: Optional[str] = None

# Data model for research paper metadata
class ResearchPaperMetadata(BaseModel):
    document_id: str
    title: str
    authors: List[str]
    published_date: str
    source: str
    pdf_url: Optional[str] = None
    abstract: str
    summary: Optional[str] = None
    labels: Optional[List[str]] = None  # New field for labels

# Data model for adding research papers metadata
class AddResearchPapersMetadata(BaseModel):
    research_papers_metadata: List[ResearchPaperMetadata]

# Data model for research paper metadata stored in database
class ResearchPaperMetadataDB(BaseModel):
    id: str
    document_id: str
    title: str
    authors: List[str]
    published_date: str
    source: str
    pdf_url: Optional[str] = None
    fetched_on: str
    abstract: str
    summary: Optional[str] = None
    created_at: str
    updated_at: Optional[str] = None

# Data model for research paper metadata response
class ResearchPaperMetadataResponse(BaseModel):
    id: str
    document_id: str
    title: str
    authors: List[str]
    published_date: str
    source: str
    pdf_url: Optional[str] = None
    abstract: str
    summary: Optional[str] = None
    labels: Optional[List[str]] = None  # New field for labels
    created_at: str
    updated_at: str

# Data model for getting research papers metadata request
class GetResearchPapersMetadata(BaseModel):
    document_ids: List[str]

# Data model for comment
class Comment(BaseModel):
    document_id: str
    user_id: str
    comment_text: str

# Data model for adding comments
class AddComment(BaseModel):
    document_id: str
    user_id: str
    comment_text: str

# Data model for comment stored in database
class CommentDB(BaseModel):
    id: str
    comment_id: str
    document_id: str
    user_id: str
    comment_text: str
    created_at: str
    updated_at: str

# Data model for comment response
class CommentResponse(BaseModel):
    id: str
    comment_id: str
    document_id: str
    user_id: str
    comment_text: str
    created_at: str
    updated_at: str

# Data model for getting comments request
class GetComments(BaseModel):
    user_id: str
    document_id: str

# Data model for getting comments response
class GetCommentsResponse(BaseModel):
    success: bool
    document_id: str
    comments: List[CommentResponse]
    total_comments: int

# Data model for simplified comment response (for get-comments endpoint)
class SimpleCommentResponse(BaseModel):
    comment_id: str
    user_id: str
    document_id: str
    comment_text: str

# Data model for updating comment
class UpdateComment(BaseModel):
    user_id: str
    document_id: str
    comment_id: str
    comment_text: str