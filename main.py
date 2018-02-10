import os
from google.appengine.ext.webapp import template
from google.appengine.ext import ndb
import webapp2
import json
import httpcodes

# For generating random state variable.
import string
import random

# For making HTTP requests from the GAE server.
from google.appengine.api import urlfetch
import urllib

class MainPage(webapp2.RequestHandler):
    state = "default";
    def get(self):
        # Method to generate a random string is from
        # https://stackoverflow.com/questions/2257441/random
        #   -string-generation-with-upper-case-letters-and-digits-in-python
        length = 50
        MainPage.state = ''.join(random.choice(
            string.ascii_lowercase + string.ascii_uppercase + string.digits) for _ in range(length))

        # Read in the important data from the JSON file
        # From https://stackoverflow.com/questions/20199126/reading-json-from-a-file
        data = ''
        with open('client_secret.json') as json_data:
            data = json.load(json_data)
        json_string = json.dumps(data)

        # From google documentation, set up the url for the oauth2.0 endpoint
        base_oauth_url = data["web"]["auth_uri"]
        scope = "email"
        oauth_url = base_oauth_url + '?' \
            + 'client_id=' + data["web"]["client_id"] \
            + '&' + 'response_type=' + 'code' \
            + '&' + 'scope=' + scope \
            + '&' + 'redirect_uri=' + data["web"]["redirect_uris"][0] \
            + '&' + 'state=' + MainPage.state

        template_values = {
            'url': oauth_url,
            'state': MainPage.state,
            'json': json_string
        }
        path = os.path.join(os.path.dirname(__file__), 'index.html')
        self.response.out.write(template.render(path, template_values))
        httpcodes.write_created(self)

# Handles exchanging the authorization code for an access token
class AuthHandler(webapp2.RequestHandler):
    def get(self):
        # Confirm that the state is correct.
        if self.request.GET['state'] != MainPage.state:
            httpcodes.write_forbidden(self)
            self.response.write("FORBIDDEN")
            return
        try:
            self.request.GET['error']
            httpcodes.write_bad_request(self)
            self.response.write("ACCESS DENIED")
            return
        except:
            # Read in the important data from the JSON file
            # From https://stackoverflow.com/questions/20199126/reading-json-from-a-file
            data = ''
            with open('client_secret.json') as json_data:
                data = json.load(json_data)
            json_string = json.dumps(data)

            # Swap the auth token for an access token
            oauth_url = data["web"]['token_uri']
                
            # Prepare the POST request to get the new token
            payload = dict()
            payload['client_id'] = data["web"]["client_id"]
            payload["code"] = self.request.GET['code']
            payload['client_secret'] = data["web"]["client_secret"]
            payload["grant_type"] = "authorization_code"
            payload["redirect_uri"] = data["web"]["redirect_uris"][0]
            p = urllib.urlencode(payload)
            result = urlfetch.fetch(url=oauth_url, method=urlfetch.POST, \
                    payload=p, validate_certificate=True)

            content = json.loads(result.content)
            # print(result)
            # print(result.content)
            # print(result.status_code)
            # print(result.headers)

            # Take the results and use it to fetch the Google+ information
            headers = dict()
            headers["Authorization"] = "Bearer" + " " + \
                    content["access_token"]
            google_url = "https://www.googleapis.com/plus/v1/people/me"
            result_2 = urlfetch.fetch(url=google_url, method=urlfetch.GET, \
                    headers = headers, payload=None, validate_certificate=True)
            content_2 = json.loads(result_2.content)

            # print(result_2)
            # print(result_2.content)
            # print(result_2.status_code)
            # print(result_2.headers)

            # Show everyting that happened
            template_values = {
                'received_url': json.dumps(self.request.GET.dict_of_lists()),
                'received_state': self.request.GET['state'],
                'received_code': self.request.GET['code'],
                'swap_content': result.content,
                'url': oauth_url,
                'state': MainPage.state,
                'json': json_string,
                'first_name': content_2["name"]["givenName"],
                'last_name': content_2["name"]["familyName"],
                'google_link': content_2["url"]
            }
            path = os.path.join(os.path.dirname(__file__), 'authorized.html')
            self.response.out.write(template.render(path, template_values))
            httpcodes.write_created(self)



# [START app]
app = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/authorized', AuthHandler),
], debug=True)
# [END app]
