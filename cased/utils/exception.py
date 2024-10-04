from typing import Any, Optional


class CasedAPIError(Exception):
    def __init__(
        self, message: str, status_code: Optional[int] = None, response_body: Any = None
    ):
        """
        Initialize the CasedAPIError.

        Args:
            message (str): The error message.
            status_code (Optional[int]): The HTTP status code of the failed request.
            response_body (Any): The response body from the failed request.
        """
        self.message = message
        self.status_code = status_code
        self.response_body = response_body
        super().__init__(self.message)

    # TODO: make this specific based on status codes returned from our API,
    # right now it is too generic.
    def __str__(self):
        """Return a string representation of the error."""
        error_msg = self.message
        if self.status_code:
            error_msg += f" (Status code: {self.status_code})"
        if self.response_body:
            error_msg += f"\nResponse body: {self.response_body}"
        return error_msg
