# ThreatByte

ThreatByte is a vulnerable web application designed to demonstrate some Web Application and API Security risks. It provides a platform to explore and understand common security vulnerabilities in web applications and APIs.

## Requirements

 - Python 3.x (where x is your specific Python version)
 - SQLite

## Run

To run ThreatByte application locally, you can follow these steps:

1. **Clone the repository:**

   ```
   git clone https://github.com/anotherik/ThreatByte.git
   ```

2. **Navigate to the project directory:**

   ```
   cd threatbyte
   ```

3. **Create a Virtual Environment**:
    ```bash
    python -m venv venv_threatbyte
    ```

4. **Activate the Virtual Environment**:
    - On Windows:
        ```bash
        venv_threatbyte\Scripts\activate
        ```
    - On macOS and Linux:
        ```bash
        source venv_threatbyte/bin/activate
        ```
        
5. **Install dependencies:**

   ```
   pip install -r requirements.txt
   ```

6. **Initialize the database:**

   ```
   python db/create_db_tables.py
   ```

7. **Run the application:**

   ```
   python run.py
   ```

8. **Access the application in your web browser at `http://localhost:5000`.**

9. **Deactivate the Virtual Environment**:
    At the end of testing, deactivate the virtual environment:
    ```bash
    deactivate
    ```

## Docker

Alternatively, you can use Docker to run ThreatByteLand. Ensure you have Docker installed on your system.

1. **Build the Docker image:**

   ```
   docker build -t threatbyteland .
   ```

2. **Run the Docker container:**

   ```
   docker run -p 5000:5000 threatbyteland
   ```

3. **Access the application in your web browser at `http://localhost:5000`.**

## Features

The ThreatByteLand application aims to represent a simple online sharing platform. Currently it has the following features:

- **User Authentication:** Users can sign up, log in, and log out.
- **Dashboard:** Users have a personalized dashboard to view and manage their uploaded files.
- **File Upload:** Users can upload files to the application.
- **Profile Management:** Users can view and edit their profile information.

## Vulnerabilities

- **Broken Authentication**
  - Brute-force attacks
  - Session Management issues
  - Insufficiently Protected Credentials
- **Cryptographic Failures**
- **Injections:**
  - **SQL Injection**
  - **Cross-Site Scripting (XSS):**
    - Reflected
    - DOM
    - Stored 
- **Cross-Site Request Forgery**
- **Server-Side Request Forgery**
- **Unrestricted File Upload**
- **Broken Access Control**
  - Broken Object Level Authorization - BOLA
  - Broken Object Property Level Authorization - BOPA
  - Broken Function Level Authorization - BFLA
- **Insecure configurations**

