# -*- coding: utf-8 -*-
from django.utils import six
from django.utils.crypto import constant_time_compare, salted_hmac
from django.utils.http import base36_to_int, int_to_base36
import time


class AliToken(object):

    key_salt = "django.contrib.auth.tokens.PasswordResetTokenGenerator"

    def make_token(self, user):

        return self._make_token_with_timestamp(user, self._num_days())

    def check_token(self, user, token):
        """
        Check that a password reset token is correct for a given user.
        """
        # Parse the token
        try:
            ts_b36, hash = token.split("-")
        except ValueError:
            return False

        try:
            ts = base36_to_int(ts_b36)
        except ValueError:
            return False

        if not constant_time_compare(self._make_token_with_timestamp(user, ts),
                                     token):
            return False

        return True

    def _make_token_with_timestamp(self, user, timestamp):
        ts_b36 = int_to_base36(timestamp)
        hash = salted_hmac(
            self.key_salt,
            self._make_hash_value(user, timestamp),
        ).hexdigest()[::2]
        return "%s-%s" % (ts_b36, hash)

    def _make_hash_value(self, user, timestamp):
        # Ensure results are consistent across DB backends
        login_timestamp = '' if user.last_login is None else user.last_login.\
            replace(microsecond=0, tzinfo=None)
        return (
            six.text_type(user.pk) + user.password +
            six.text_type(login_timestamp) + six.text_type(timestamp)
        )

    def _num_days(self):
        # current_milli_time = lambda: int(round(time.time() * 1000))
        # return current_milli_time()
        return int(round(time.time() * 1000))

    def token_life_time(self, creation_time):
        current_time = time.time()
        if int(current_time - float(creation_time)) >= 30:
            return False
        else:
            return True
