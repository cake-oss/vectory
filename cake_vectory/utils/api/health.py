# SPDX-FileCopyrightText: 2025 Cake AI Technologies, Inc.
#
# SPDX-License-Identifier: Apache-2.0

"""Health check functionality for the Weaviate API."""

from typing import Dict

from cake_vectory.utils.api.client import WeaviateClient


class HealthClient(WeaviateClient):
    """Client for health check operations."""

    def check_health(self) -> Dict[str, bool]:
        """Check if Weaviate is live and ready.

        Returns:
            Dict: Health status with 'live' and 'ready' keys
        """
        health = {"live": False, "ready": False}

        try:
            live_response = self.get(".well-known/live")
            health["live"] = True
        except Exception:
            pass

        try:
            ready_response = self.get(".well-known/ready")
            health["ready"] = True
        except Exception:
            pass

        return health
