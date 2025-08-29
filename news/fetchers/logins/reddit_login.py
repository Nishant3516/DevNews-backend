import requests
from decouple import config


CLIENT_ID = config("REDDIT_CLIENT_ID")
CLIENT_SECRET = ""
REDIRECT_URI = "http://localhost:8080"
CODE = "LiRI1K2yF3PJI07IluhwrG29v1f_Dw"

auth = requests.auth.HTTPBasicAuth(CLIENT_ID, CLIENT_SECRET)

data = {
    "grant_type": "authorization_code",
    "code": CODE,
    "redirect_uri": REDIRECT_URI,
}

headers = {"User-Agent": "newsfetcher by yourusername"}

response = requests.post(
    "https://www.reddit.com/api/v1/access_token",
    auth=auth,
    data=data,
    headers=headers,
)

print(response.json())
