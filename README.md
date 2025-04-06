# artist-management-api

After cloning the repo, create a .env file and add your database URL like in .env.example, then run the following commands to set up the project:

1. python -m venv venv
2. venv\Scripts\activate for Windows, source venv/bin/activate for Linux
3. pip install -r requirements.txt
4. cd app
5. python create_database.py
6. uvicorn main:app --reload
