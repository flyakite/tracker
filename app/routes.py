from ferris.core import routing, plugins
from app.controllers.activity_compiles import ActivityCompiles
#from webapp2_extras.routes import RedirectRoute

# Routes all App handlers
routing.auto_route()

# Default root route
routing.default_root()

routing.add(routing.Route('/activity_report', ActivityCompiles))
#routing.add(RedirectRoute('/activity_report', handler=ActivityCompiles, handler_method='get'))


# Plugins
# plugins.enable('settings')
# plugins.enable('oauth_manager')
