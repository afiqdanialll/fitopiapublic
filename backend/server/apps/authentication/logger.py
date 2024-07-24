import logging
import datetime


auth_logger = logging.getLogger('auth_logger')
account_logger = logging.getLogger('account_logger')


def auth_log(user, request, success):
    # Authentication
    if success:
        tmp_success = "successfully"
    else:
        tmp_success = "unsuccessfully"

    auth_logger.info(f"User using {user} authenticated {tmp_success} using credentials from {request.META.get('REMOTE_ADDR')} on {datetime.datetime.now()}")


def two_fa_log(user, request, success):
    # Two Factor Authentication
    if success:
        tmp_success = "successfully"
    else:
        tmp_success = "unsuccessfully"

    auth_logger.info(f"User using {user} authenticated {tmp_success} using 2FA from {request.META.get('REMOTE_ADDR')} on {datetime.datetime.now()}")


def disable_account_log(user, request, enabled, admin, success):
    # Account disabled
    if success:
        if enabled:
            tmp_enable = "enabled"
        else:
            tmp_enable = "disabled"

        account_logger.info(f"Account {user} {tmp_enable} successfully by {admin} from {request.META.get('REMOTE_ADDR')} on {datetime.datetime.now()}")
    else:
        account_logger.info(f"Account {user} toggled unsuccessfully from {request.META.get('REMOTE_ADDR')} on {datetime.datetime.now()}")
    

def reset_password_log(user, request,admin, success):
    # Password reset
    if success:
        tmp_success = "successfully"
    else:
        tmp_success = "unsuccessfully"

    account_logger.info(f"Password reset for Account {user} {tmp_success} by {admin} from {request.META.get('REMOTE_ADDR')} on {datetime.datetime.now()}")
