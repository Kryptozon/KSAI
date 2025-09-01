from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from db import get_all_reports
import secrets, bcrypt

security = HTTPBasic()

# Credentials
ADMIN_USER = "khaled.d4rensics@gmail.com"
ADMIN_PASS_HASH = bcrypt.hashpw("KSAai137".encode(), bcrypt.gensalt())

def verify_admin(credentials: HTTPBasicCredentials = Depends(security)):
    correct_user = secrets.compare_digest(credentials.username, ADMIN_USER)
    correct_pass = bcrypt.checkpw(credentials.password.encode(), ADMIN_PASS_HASH)
    if not (correct_user and correct_pass):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Unauthorized",
                            headers={"WWW-Authenticate": "Basic"})
    return credentials.username

def get_admin_dashboard():
    rows = get_all_reports()
    html = """
    <html>
    <head>
      <title>KS-AI Admin</title>
      <style>
        body { font-family: Arial; margin:20px; background:#f4f4f9; }
        h1 { color:#004aad; }
        table { border-collapse:collapse; width:100%; }
        th, td { border:1px solid #ddd; padding:8px; }
        th { background:#004aad; color:white; }
        tr:nth-child(even){background-color:#f9f9f9;}
      </style>
    </head>
    <body>
      <h1>KS-AI Crypto Report Logs</h1>
      <table>
        <tr><th>ID</th><th>Session</th><th>Query</th><th>PDF</th><th>Created At</th></tr>
    """
    for row in rows:
        html += f"<tr><td>{row[0]}</td><td>{row[1]}</td><td>{row[2]}</td><td><a href='/download/{row[3]}' target='_blank'>PDF</a></td><td>{row[4]}</td></tr>"
    html += "</table></body></html>"
    return html
