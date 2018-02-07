import os
from google.appengine.ext.webapp import template
from google.appengine.ext import ndb
import webapp2
import json
import httpcodes

# For generating random state variable.
import string
import random

# USE THE GOOGLE FETCH LIBRARY TO MAKE HTTP REQUESTS TO GOOGLE OAUTH

class MainPage(webapp2.RequestHandler):
    def get(self):
        # Method to generate a random string is from
        # https://stackoverflow.com/questions/2257441/random
        #   -string-generation-with-upper-case-letters-and-digits-in-python
        length = 10
        state = ''.join(random.choice(
            string.ascii + string.digits) for _ in length)
        # Ensure state can be verified when auth code comes back
        AccessHandler.state = state

        # From google documentation
        base_oauth_url = "https://accounts.google.com/o/oauth2/v2/auth?"
        scope = "email"

        template_values = {
            'url': oauth_url,
            'state': state
        }
        path = os.path.join(os.path.dirname(__file__), 'index.html')
        self.response.out.write(template.render(path, template_values))
        httpcodes.write_created(self)

# Handles exchanging the authorization code for an access token
class AccessHandler(webapp2.RequestHandler):
    state = "default"
    def get(self):
        # Confirm that the state is correct.

        # Swap the auth token for an access token
        base = "https://www.googleapis.com/oauth2/v4/token"
            

class AppHandler(webapp2.RequestHandler):
    state = "default"
    def get(self):



# [START app]
app = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/authorized', AppHandler),
    ('/partial', AccessHandler),
], debug=True)
# [END app]
