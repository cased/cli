"""Constants used in the CLI"""

import os


class CasedConstants:

    ### Config files
    CONFIG_DIR = os.path.expanduser("~/.cased/config")
    ENV_FILE = os.path.join(CONFIG_DIR, "env")

    ### API Constants
    CASED_API_AUTH_KEY = "CASED_API_AUTH_KEY"
    CASED_ORG_ID = "CASED_ORG_ID"
    CASED_ORG_NAME = "CASED_ORG_NAME"

    BASE_URL = os.environ.get("CASED_BASE_URL", default="https://app.cased_cli.com")
    API_BASE_URL = BASE_URL + "/api/v1"

    # Project related constants
    CASED_WORKING_PROJECT_NAME = "CASED_WORKING_PROJECT_NAME"
    CASED_WORKING_PROJECT_ID = "CASED_WORKING_PROJECT_ID"
