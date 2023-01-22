import gi
gi.require_version('WebKit2', '4.0')
gi.require_version('Gtk', '3.0')
from gi.repository import WebKit2, Gtk
import json, re, os

from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive
# Constants
CLIENT_ID = "12218029133-ida16vij2qn6pukq4jm3tl0qjcs1ma9m.apps.googleusercontent.com"
CLIENT_SECRET = "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"
SCOPE = "https://www.googleapis.com/auth/drive"
REDIRECT_URI = "https://thn22yt.blogspot.com"

def on_decide_policy(webview, decision, decision_type):
    # Check if the URL is the redirect URI

    if not os.path.exists("tmp"):
        if re.search(f"{REDIRECT_URI}.*", decision.get_request().get_uri()):
        #if decision.get_request().get_uri() == REDIRECT_URI:
            # Get the code from the URL
            code = decision.get_request().get_uri().split("code=")
            # Authorize the code
            print(code[1])
            gauth.Authorize(code[1])
            # Save the credentials
            gauth.SaveCredentialsFile("mycreds.txt")
            # Get the Google Drive client
            drive = GoogleDrive(gauth)
            open("tmp","x")


# Get the authorization URL
gauth = GoogleAuth()
gauth.client_id = CLIENT_ID
gauth.client_secret = CLIENT_SECRET
gauth.redirect_uri = REDIRECT_URI
gauth.scope = SCOPE
auth_url = gauth.GetAuthUrl()

# Create a WebView window to display the auth URL
webview = WebKit2.WebView()
webview.load_uri(auth_url)

# Add a signal handler to detect when the auth URL redirects
webview.connect("decide-policy", on_decide_policy)
# Show the window
win = Gtk.Window()
win.add(webview)
win.connect("delete-event",Gtk.main_quit)
win.show_all()

# Run the GTK main loop
Gtk.main()
