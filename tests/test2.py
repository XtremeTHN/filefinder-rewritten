import gi
gi.require_version('WebKit2', '4.0')
gi.require_version('Gtk', '3.0')
from gi.repository import WebKit2, Gtk
from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive
from google.oauth2.credentials import Credentials
import json
import requests

CLIENT_ID = "12218029133-rs0cbfd88jnebhb74qahvqjtkjm8jpo7.apps.googleusercontent.com"
CLIENT_SECRET = "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"
SCOPE = "https://www.googleapis.com/auth/drive"
REDIRECT_URI = "https://thn22yt.blogspot.com"

def authenticate():
    # Generar la URL de autorización
    auth_url = f"https://accounts.google.com/o/oauth2/auth?client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI}&scope={SCOPE}&response_type=code"

    # Crear la ventana personalizada con webkit2 de gtk
    webview = WebKit2.WebView()
    webview.load_uri(auth_url)

    # Add a signal handler to detect when the auth URL redirects
    webview.connect("decide-policy", decide_policy_cb)
    # Show the window
    win = Gtk.Window()
    win.add(webview)
    win.connect("delete-event",Gtk.main_quit)
    win.show_all()
    # Run the GTK main loop
    Gtk.main()

    

def decide_policy_cb(webview, decision, decision_type):
    if decision_type != WebKit2.PolicyDecisionType.NAVIGATION_ACTION:
        return

    uri = decision.get_navigation_action().get_request().get_uri()
    if "code=" in uri:
        code = uri.split("code=")[1]
        get_token(code)

def get_token(code):
    client_id = "your_client_id"
    client_secret = "your_client_secret"
    redirect_uri = "http://localhost"
    # Solicitar el token de acceso y actualización
    data = {
        "code": code,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "redirect_uri": SCOPE,
        "grant_type": "authorization_code"
    }
    resp = requests.post("https://oauth2.googleapis.com/token", data=data)
    tokens = json.loads(resp.text)
    access_token = tokens["access_token"]
    refresh_token = tokens["refresh_token"]
    # Utilizar los tokens para acceder a los recursos de Google Drive
    gauth = GoogleAuth()
    gauth.credentials = creds = Credentials.from_authorized_user_info(info=tokens)
    drive = GoogleDrive(gauth)

authenticate()
