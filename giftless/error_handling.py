"""Handle errors according to the Git LFS spec

See https://github.com/git-lfs/git-lfs/blob/master/docs/api/batch.md#response-errors
"""
import logging

from werkzeug.exceptions import default_exceptions

from .representation import output_git_lfs_json
from .storage.exc import AccessDenied


class ApiErrorHandler:

    def __init__(self, app=None):
        if app:
            self.init_app(app)

    def init_app(self, app):
        for code in default_exceptions:
            app.errorhandler(code)(self.error_as_json)

        # Specifically handle AccessDenied with a JSON response and 403 status
        app.errorhandler(AccessDenied)(self.access_denied_as_json)

    @classmethod
    def error_as_json(cls, ex):
        """Handle errors by returning a JSON response
        only maps HTTP-based exceptions from werkzeug.exceptions (like NotFound or Forbidden)
        """
        log = logging.getLogger(__name__)
        code = ex.code if hasattr(ex, 'code') else 500
        data = {"message": str(ex)}
        log.debug(f"Returning error response: {data} with status {code}")

        return output_git_lfs_json(data=data, code=code)

    @classmethod
    def access_denied_as_json(cls, ex):
        """Handle AccessDenied by returning a JSON response with 403 status"""
        log = logging.getLogger(__name__)
        log.debug(f"Returning error response of AccessDenied with status 403")
        data = ex.as_dict()
        return output_git_lfs_json(data=data, code=403)
