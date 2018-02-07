import os
from google.appengine.ext.webapp import template
from google.appengine.ext import ndb
import webapp2
import json
import httpcodes

# [START main_page]
class MainPage(webapp2.RequestHandler):
    def get(self):
        template_values = {
                
        }
        path = os.path.join(os.path.dirname(__file__), 'index.html')
        self.response.out.write(template.render(path, template_values))
        httpcodes.write_created(self)
# [END main_page]

# [START app]
# Add the patch method to the allowed HTTP verbs
allowed_methods = webapp2.WSGIApplication.allowed_methods
new_allowed_methods = allowed_methods.union(('PATCH',))
webapp2.WSGIApplication.allowed_methods = new_allowed_methods

app = webapp2.WSGIApplication([
    ('/', MainPage),
], debug=True)
# [END app]
