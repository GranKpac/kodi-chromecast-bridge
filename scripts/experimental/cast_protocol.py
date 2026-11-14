#!/usr/bin/env python3
"""Experimental Cast V2 client. Configure CAST_HOST; no LAN IP or session ID is embedded."""
import json, os, socket, ssl, struct, time
from urllib.parse import urlsplit

APP="CC1AD845"
CONN="urn:x-cast:com.google.cast.tp.connection"
RECV="urn:x-cast:com.google.cast.receiver"
MEDIA="urn:x-cast:com.google.cast.media"
HEART="urn:x-cast:com.google.cast.tp.heartbeat"

def config():
    host=os.environ.get("CAST_HOST","").strip()
    if not host: raise SystemExit("Define CAST_HOST con la IP o nombre del Chromecast.")
    try: port=int(os.environ.get("CAST_PORT","8009")); timeout=float(os.environ.get("CAST_TIMEOUT","5"))
    except ValueError: raise SystemExit("CAST_PORT y CAST_TIMEOUT deben ser numéricos.")
    if not 1 <= port <= 65535 or timeout <= 0: raise SystemExit("Puerto o timeout no válido.")
    return host,port,timeout

def vi(n):
    b=bytearray()
    while n>127: b.append((n&127)|128); n >>= 7
    b.append(n); return bytes(b)

def fld(n,v): return vi((n<<3)|2)+vi(len(v))+v

def readvi(data,p):
    v=s=0
    while p<len(data):
        b=data[p]; p+=1; v|=(b&127)<<s
        if not b&128: return v,p
        s+=7
        if s>63: break
    raise ValueError("Varint protobuf incompleto")

def fields(data):
    out={}; p=0
    while p<len(data):
        tag,p=readvi(data,p); n,w=tag>>3,tag&7
        if w==0: v,p=readvi(data,p)
        elif w==2:
            size,p=readvi(data,p); end=p+size
            if end>len(data): raise ValueError("Campo protobuf truncado")
            v,p=data[p:end],end
        elif w==1: v,p=data[p:p+8],p+8
        elif w==5: v,p=data[p:p+4],p+4
        else: raise ValueError("Wire type no soportado: "+str(w))
        out[n]=v
    return out

class Cast:
    def __init__(self):
        self.host,self.port,timeout=config()
        raw=socket.create_connection((self.host,self.port),timeout)
        self.s=ssl._create_unverified_context().wrap_socket(raw,server_hostname=self.host)
        self.s.settimeout(timeout)
        self.send("receiver-0",CONN,{"type":"CONNECT","origin":{}})
    def close(self):
        try: self.s.close()
        except OSError: pass
    def send(self,dest,ns,msg):
        body=b"\x08\x00"+fld(2,b"sender-0")+fld(3,dest.encode())+fld(4,ns.encode())+b"\x28\x00"+fld(6,json.dumps(msg,separators=(",",":")).encode())
        self.s.sendall(struct.pack(">I",len(body))+body)
    def exact(self,n):
        b=bytearray()
        while len(b)<n:
            x=self.s.recv(n-len(b))
            if not x: raise ConnectionError("Chromecast cerró la conexión")
            b.extend(x)
        return bytes(b)
    def receive(self):
        n=struct.unpack(">I",self.exact(4))[0]
        if n>4*1024*1024: raise ValueError("Mensaje Cast demasiado grande")
        f=fields(self.exact(n)); ns=f.get(4,b"").decode("utf-8","replace")
        return ns,json.loads(f[6].decode("utf-8")) if f.get(6) else {}
    def pong(self,ns,msg):
        if ns.endswith(".heartbeat") and msg.get("type")=="PING":
            self.send("receiver-0",HEART,{"type":"PONG"}); return True
        return False
    def wait(self,predicate,seconds=20):
        end=time.monotonic()+seconds
        while time.monotonic()<end:
            try: ns,msg=self.receive()
            except socket.timeout: continue
            if self.pong(ns,msg): continue
            if predicate(ns,msg): return ns,msg
        raise TimeoutError("Tiempo de espera agotado")
    def launch(self):
        self.send("receiver-0",RECV,{"type":"LAUNCH","appId":APP,"requestId":1})
        def ready(ns,msg):
            if msg.get("type")=="LAUNCH_ERROR": raise RuntimeError("El receptor rechazó el lanzamiento")
            return msg.get("type")=="RECEIVER_STATUS"
        _,msg=self.wait(ready,25)
        for app in msg.get("status",{}).get("applications",[]):
            if app.get("appId")==APP and app.get("transportId"):
                t=app["transportId"]
                self.send(t,CONN,{"type":"CONNECT","origin":{}})
                return t
        raise RuntimeError("No se recibió transportId dinámico")
    def status(self):
        self.send("receiver-0",RECV,{"type":"GET_STATUS","requestId":2})
        return self.wait(lambda ns,m:ns.endswith(".receiver") and m.get("type")=="RECEIVER_STATUS",15)[1]
    def load(self,url,mime,title):
        t=self.launch()
        self.send(t,MEDIA,{"type":"LOAD","requestId":3,"autoplay":True,"currentTime":0,
          "media":{"contentId":url,"contentType":mime,"streamType":"BUFFERED","metadata":{"metadataType":0,"title":title}}})
        end=time.monotonic()+45
        while time.monotonic()<end:
            try: ns,msg=self.receive()
            except socket.timeout: continue
            if self.pong(ns,msg): continue
            if msg.get("type") in ("MEDIA_STATUS","LOAD_FAILED"):
                print(json.dumps(msg,indent=2,ensure_ascii=False))
                if msg["type"]=="LOAD_FAILED": raise RuntimeError("LOAD rechazado")
                return
        print("Sin MEDIA_STATUS tras 45 segundos")

def media(file,mime,title):
    url=os.environ.get("CAST_MEDIA_URL","").strip()
    if not url:
        path=os.path.join(os.path.abspath(os.environ.get("BRIDGE_DIR","/storage/kodi-chromecast-bridge")),file)
        try: url=open(path,encoding="utf-8").read().strip()
        except OSError as e: raise SystemExit("No se pudo leer el archivo URL local: "+str(e))
    u=urlsplit(url)
    if u.scheme not in ("http","https") or not u.hostname or u.username or u.password:
        raise SystemExit("Se requiere una URL HTTP(S) válida sin credenciales embebidas")
    c=Cast()
    try:
        print("Chromecast:",c.host,"| servidor multimedia:",u.hostname)
        print("TLS:",c.s.version())
        c.load(url,mime,title)
    finally: c.close()

def status():
    c=Cast()
    try: print(json.dumps(c.status(),indent=2,ensure_ascii=False))
    finally: c.close()

def launch():
    c=Cast()
    try: print("Default Media Receiver iniciado; transportId dinámico:",c.launch())
    finally: c.close()

def connect_test():
    c=Cast()
    try:
        print("TLS:",c.s.version(),"| CONNECT enviado")
        try:
            ns,msg=c.wait(lambda n,m:n.endswith(".heartbeat") or m.get("type") in ("RECEIVER_STATUS","LAUNCH_ERROR"),10)
            print(ns,json.dumps(msg,ensure_ascii=False))
        except TimeoutError: print("No llegó otro mensaje en 10 s; TLS/CONNECT completados")
    finally: c.close()
