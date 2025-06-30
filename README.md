# blog-api
A simple backend API of a blog-style application.

# Features
- Basic login functionality (token-based authentication)
- Post viewing, creation, modification, and deletion
    - Pagination and filtering
- Comment viewing, creation, modification, and deletion
- CORS protection

# Instructions
1) Clone the repository or use the project folder
```
git clone https://github.com/zenpa1/blog-api
cd <project-folder>
```

2) Set up virtual environment
```
python -m venv blogvenv
source blogvenv/bin/activate  # Linux/Mac
blogvenv\Scripts\activate  # Windows
```

3) Install dependencies
```
pip install -r requirements.txt
```

4) Open VSCode while in blogvenv AND project directory
```
code
```

5) Open a PowerShell terminal in VSCode and paste the following command
```
uvicorn app.main:app --reload
```

6) Open a Git Bash terminal for cURL

7) Open cURL.txt and insert the commands into a Bash terminal (easiest on Visual Studio Code)

## Tech Stack

### Core
- **Language**: Python 3.10+
- **Web Framework**: [FastAPI](https://fastapi.tiangolo.com/) 
- **Database ORM**: [SQLAlchemy 2.0](https://www.sqlalchemy.org/)
- **Authentication**: BCrypt + JWT (via python-jose)

### Key Dependencies
- Password Hashing: `bcrypt`
- Data Validation: `pydantic`
- ASGI Server: `uvicorn`