# SPDX-FileCopyrightText: 2025 Cake AI Technologies, Inc.
#
# SPDX-License-Identifier: Apache-2.0

"""API interaction utilities for the Cake Vectory CLI.

This is a backward compatibility module. The actual implementation
has been moved to the cake_vectory.utils.api package.
"""

# Re-export the WeaviateAPI class from the api package
from cake_vectory.utils.api import WeaviateAPI
