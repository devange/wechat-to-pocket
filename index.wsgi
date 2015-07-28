import sae
from pocket import wsgi


application = sae.create_wsgi_app(wsgi.application)