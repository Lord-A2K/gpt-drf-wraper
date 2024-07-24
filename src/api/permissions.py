from rest_framework.permissions import BasePermission
from rest_framework.exceptions import APIException


class NotEnoughTokensException(APIException):
    status_code = 403
    default_detail = "You do not have enough tokens to send a message."
    default_code = "not_enough_tokens"


class HasEnoughTokens(BasePermission):

    def has_permission(self, request, view):
        if request.user.tokens <= 10:
            raise NotEnoughTokensException(
                detail={
                    "message": "You do not have enough tokens to send a message.",
                    "minimum_tokens_required": 11,
                    "current_tokens": request.user.tokens,
                }
            )
        return True
