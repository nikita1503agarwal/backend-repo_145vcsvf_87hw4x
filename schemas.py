"""
Database Schemas for DevShowcase Platform

Each Pydantic model represents a MongoDB collection (class name lowercased).

Collections:
- developer
- softwareapp
- review
"""
from typing import List, Optional
from pydantic import BaseModel, Field, HttpUrl, EmailStr


class Developer(BaseModel):
    """
    Developer profile
    Collection: developer
    """
    name: str = Field(..., description="Full name of the developer")
    email: EmailStr = Field(..., description="Contact email")
    bio: Optional[str] = Field(None, description="Short bio")
    website: Optional[HttpUrl] = Field(None, description="Personal website")
    github: Optional[str] = Field(None, description="GitHub username or URL")
    twitter: Optional[str] = Field(None, description="Twitter handle")
    avatar_url: Optional[HttpUrl] = Field(None, description="Avatar image URL")


class SoftwareApp(BaseModel):
    """
    Software application submitted by a developer
    Collection: softwareapp
    """
    title: str = Field(..., description="App title")
    description: str = Field(..., description="What it does and why it's useful")
    platform: str = Field(..., description="web | mobile | desktop | cli | library")
    category: Optional[str] = Field(None, description="Category e.g. productivity, devtools")
    tags: List[str] = Field(default_factory=list, description="Keywords/tags")
    repo_url: Optional[HttpUrl] = Field(None, description="Repository URL")
    website_url: Optional[HttpUrl] = Field(None, description="Landing page URL")
    image_url: Optional[HttpUrl] = Field(None, description="Hero/cover image URL")
    version: Optional[str] = Field(None, description="Current version string")
    license: Optional[str] = Field(None, description="License identifier")
    author_name: str = Field(..., description="Submitting developer name")
    author_email: EmailStr = Field(..., description="Submitting developer email")


class Review(BaseModel):
    """
    Structured review for an app
    Collection: review
    """
    app_id: str = Field(..., description="Referenced SoftwareApp _id as string")
    reviewer_name: str = Field(..., description="Name of the reviewer")
    rating: int = Field(..., ge=1, le=5, description="Star rating 1-5")
    pros: Optional[str] = Field(None, description="What works well")
    cons: Optional[str] = Field(None, description="What could be improved")
    suggestions: Optional[str] = Field(None, description="Actionable suggestions")
    comment: Optional[str] = Field(None, description="General comment")
