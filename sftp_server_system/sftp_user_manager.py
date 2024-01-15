"""
Synopsis:
    This script holds an assortment of functions that allow you to create, modify and delete AWS Transfer Family SFTP server users.

Description:
    The following functions and their parameters populate the script below:

    1) check_user_store(user_name: str) -> dict
    2) create_user(user_name: str,
                    access_level: str,
                    ssh_key: str,
                    servicenow_request_number: str,
                    ip_range: str = None,
                    dr_ip_range: str = None
                    new_user_name: str = None) -> dict
    3) create_user_configs(user_name: str,
                    access_level: str,
                    ssh_key: str,
                    servicenow_request_number: str,
                    ip_range: str = None,
                    dr_ip_range: str = None
                    new_user_name: str = None) -> dict
    4) create_user_folder(user_name: str, access_level: str) -> None
    5) update_ssh_key(user_name: str, ssh_key: str, servicenow_request_number: str) -> dict
    6) delete_user(user_name: str, servicenow_request_number: str) -> dict

Reference Material:

Notes:

"""