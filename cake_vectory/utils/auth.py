# SPDX-FileCopyrightText: 2025 Cake AI Technologies, Inc.
#
# SPDX-License-Identifier: Apache-2.0

"""Authentication utilities for the Cake Vectory CLI."""

import os
from typing import Dict, Optional


def get_auth_headers(api_key: Optional[str] = None) -> Dict[str, str]:
    """Get authentication headers based on the provided API key.
    
    If an API key is provided, it will be used for Bearer token authentication.
    If no API key is provided, the default "NONE" authentication will be used.
    
    Args:
        api_key: API key for authentication
        
    Returns:
        Dict: Authentication headers
    """
    if api_key:
        return {"Authorization": f"Bearer {api_key}"}
    else:
        return {"Authorization": "NONE"}
