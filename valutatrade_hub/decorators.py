import functools
import logging
from .logging_config import setup_logging

def log_action(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        currency = kwargs.get("currency", args[0] if len(args) > 0 else None)
        amount = kwargs.get("amount", args[1] if len(args) > 1 else None)
        username = func.__globals__.get("current_user")
        try:
            result = func(*args, **kwargs)
            user_id = result["user_id"]
            rate = result["rate"]
            base = result["base"]
            old_balance = result["old_balance"]
            new_balance = result["new_balance"]
            logger = setup_logging()
            logger.info(
                f"Action: {func.__name__.upper()}, "
                f"Currency: {currency}, "
                f"Amount: {amount}, "
                f"Result: OK, "
                f"Username: {username}, "
                f"User ID: {user_id}, "
                f"Rate: {rate}, "
                f"Base: {base}, "
                f"Balance: {old_balance} -> {new_balance}"
                )
            return result
        except Exception as e:
            logger = setup_logging()
            logger.error(
                f"Action: {func.__name__.upper()}, "
                f"Currency: {currency}, "
                f"Amount: {amount}, "
                f"Result: ERROR, "
                f"Exception: {type(e).__name__}, "
                f"Message: {e}, "
                f"Username: {username}"
            )
            raise
    return wrapper