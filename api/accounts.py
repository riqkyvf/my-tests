from playwright.sync_api import APIRequestContext, APIResponse, Error

from config import ACCOUNTS_URL, REQUEST_TIMEOUT_MS


def create_account(
    api_context: APIRequestContext,
    user: dict[str, str],
) -> APIResponse:
    return api_context.post(
        ACCOUNTS_URL,
        data=user,
        timeout=REQUEST_TIMEOUT_MS,
    )


def delete_account(api_context: APIRequestContext) -> APIResponse:
    try:
        return api_context.delete(
            ACCOUNTS_URL,
            timeout=REQUEST_TIMEOUT_MS,
        )
    except Error as error:
        # Журнал HTTP-запроса может содержать Cookie и Authorization.
        message = error.message.partition("Call log:")[0].strip()
        raise type(error)(message) from None
