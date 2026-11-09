"""Run python3 server.py; set PORT and MYSPOT_DB for deployment."""
import base64, hashlib, hmac, json, os, secrets, sqlite3, time
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DB = os.environ.get("MYSPOT_DB", str(ROOT / "myspot.sqlite"))
def connect():
    db = sqlite3.connect(DB, timeout=10)
    db.row_factory = sqlite3.Row
    return db

with connect() as db:
    db.executescript("""
    CREATE TABLE IF NOT EXISTS users(name TEXT PRIMARY KEY,salt BLOB,digest BLOB);
    CREATE TABLE IF NOT EXISTS sessions(token TEXT PRIMARY KEY,name TEXT,expires INTEGER);
    CREATE TABLE IF NOT EXISTS posts(id INTEGER PRIMARY KEY,name TEXT,body TEXT,media TEXT);
    """)

class Handler(BaseHTTPRequestHandler):
    def reply(self, status, data, mime="application/json", cookie=None):
        raw = json.dumps(data).encode() if mime=="application/json" else data
        self.send_response(status)
        self.send_header("Content-Type",mime)
        self.send_header("X-Content-Type-Options","nosniff")
        self.send_header("Cache-Control","no-store")
        self.send_header("Content-Length",str(len(raw)))
        if cookie: self.send_header("Set-Cookie",cookie)
        self.end_headers()
        self.wfile.write(raw)

    def session(self,db):
        tokens = [v.strip()[3:] for v in self.headers.get("Cookie","").split(";") if v.strip().startswith("ms=")]
        token = tokens[0] if tokens else ""
        user = db.execute("SELECT name FROM sessions WHERE token=? AND expires>?",(token,time.time())).fetchone()
        return token, user["name"] if user else None

    def do_GET(self):
        path = self.path.split("?")[0]
        assets={"/":("index.html","text/html; charset=utf-8"),"/manifest.webmanifest":("manifest.webmanifest","application/manifest+json"),"/icon.png":("icon.png","image/png"),"/large.png":("large.png","image/png"),"/sw.js":("sw.js","text/javascript")}
        if path in assets:
            file,mime=assets[path]
            return self.reply(200,(ROOT/file).read_bytes(),mime)
        with connect() as db:
            _,user=self.session(db)
            if path=="/api/me": return self.reply(200,{"name":user})
            if not user: return self.reply(401,{"error":"Sign in first."})
            if path=="/api/feed":
                rows=db.execute("SELECT id,name,body, media != '' AS attached FROM posts ORDER BY id DESC LIMIT 40")
                return self.reply(200,[dict(r) for r in rows])
            if path.startswith("/media/") and path[7:].isdigit():
                row=db.execute("SELECT media FROM posts WHERE id=?",(path[7:],)).fetchone()
                if row and row[0]:
                    header,data=row[0].split(",",1)
                    return self.reply(200,base64.b64decode(data),header[5:-7])
        self.reply(404,{"error":"Not found."})

    def do_POST(self):
        if self.headers.get("Content-Type")!="application/json": return self.reply(415,{})
        try:
            length=int(self.headers.get("Content-Length","0"))
            if not 0<length<=6_000_000: return self.reply(413,{"error":"Upload limit is 4 MB."})
            data=json.loads(self.rfile.read(length))
            if not isinstance(data,dict): raise ValueError()
            with connect() as db:
                token,user=self.session(db)
                if self.path in ("/api/register","/api/login"):
                    name=str(data.get("name","")).strip().lower()
                    password=str(data.get("password",""))
                    if not 2<=len(name)<=32 or not name.replace("_","").isalnum() or not 8<=len(password)<=128:
                        return self.reply(400,{"error":"Use a 2–32 character handle and an 8–128 character password."})
                    row=db.execute("SELECT * FROM users WHERE name=?",(name,)).fetchone()
                    salt=row["salt"] if row else secrets.token_bytes(16)
                    digest=hashlib.scrypt(password.encode(),salt=salt,n=16384,r=8,p=1)
                    if self.path.endswith("register"):
                        try: db.execute("INSERT INTO users VALUES(?,?,?)",(name,salt,digest))
                        except sqlite3.IntegrityError: return self.reply(409,{"error":"Handle already taken."})
                    elif not row or not hmac.compare_digest(row["digest"],digest):
                        return self.reply(403,{"error":"Check your handle and password."})
                    token=secrets.token_hex(32)
                    db.execute("INSERT INTO sessions VALUES(?,?,?)",(token,name,int(time.time())+604800))
                    db.commit()
                    return self.reply(200,{"name":name},cookie="ms="+token+"; HttpOnly; SameSite=Strict; Path=/"+("; Secure" if os.getenv("HTTPS_ONLY")=="1" else ""))
                if not user: return self.reply(401,{"error":"Sign in first."})
                if self.path=="/api/logout":
                    db.execute("DELETE FROM sessions WHERE token=?",(token,));db.commit()
                    return self.reply(200,{},cookie="ms=; Max-Age=0; Path=/; SameSite=Strict")
                if self.path=="/api/post":
                    body=data.get("body","");media=data.get("media","")
                    if not isinstance(body,str) or not isinstance(media,str) or len(body)>2200 or not (body.strip() or media): raise ValueError()
                    if media:
                        header,encoded=media.split(",",1)
                        if header not in ["data:"+m+";base64" for m in ("image/jpeg","image/png","image/gif","image/webp","video/mp4","video/webm")]: raise ValueError()
                        if len(base64.b64decode(encoded,validate=True))>4_000_000: raise ValueError()
                    db.execute("INSERT INTO posts(name,body,media) VALUES(?,?,?)",(user,body,media));db.commit()
                    return self.reply(201,{})
        except (ValueError,TypeError): return self.reply(400,{"error":"Check the fields or choose a supported image or video under 4 MB."})
        self.reply(404,{})

if __name__=="__main__":
    ThreadingHTTPServer(("0.0.0.0",int(os.getenv("PORT",8000))),Handler).serve_forever()
