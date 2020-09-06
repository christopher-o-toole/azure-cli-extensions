# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

from azext_thoth_experimental._util import safe_repr


# pylint: disable=too-few-public-methods
class Link():
    def __init__(self, url: str, context: str):
        super().__init__()
        self.url = url
        self.context = context

    def __repr__(self):
        attrs = {
            'url': self.url,
            'context': self.context
        }
        return safe_repr(self, attrs)
