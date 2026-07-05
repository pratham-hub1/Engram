import urllib.request, urllib.parse, json

url = 'http://127.0.0.1:8000/api/query?q=' + urllib.parse.quote('Provide a high-level summary of the project architecture and recent state.') + '&intent=general'
try:
    resp = urllib.request.urlopen(url)
    body = resp.read().decode('utf-8')
    with open("api_response.json", "w", encoding="utf-8") as f:
        f.write(body)
except Exception as e:
    with open("api_error.txt", "w", encoding="utf-8") as f:
        f.write(str(e))
