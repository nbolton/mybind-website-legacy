from django.contrib.auth.models import User, check_password
from django.contrib.auth.backends import ModelBackend

class AuthBackend(ModelBackend):
    def authenticate(self, username=None, password=None, customer=None):
        
        if customer:
            # in some cases, we need to just set the authenticated user, rather
            # then checking the username and password.
            return customer
        
        # nothing special going on here - just auth as django normaly would
        return super(AuthBackend, self).authenticate(
            username=username, password=password)
