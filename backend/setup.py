from setuptools import setup, find_packages

setup(
    name="autograding-system",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "fastapi",
        "uvicorn",
        "python-dotenv",
        "python-jose[cryptography]",
        "passlib[bcrypt]",
        "python-multipart",
        "sqlalchemy",
        "supabase",
        "pinecone",
        "mistralai",
        "openai",
        "anthropic",
        "langchain-text-splitters",
        "pydantic",
        "pydantic-settings",
        "email-validator",
        "PyMuPDF",
    ],
) 