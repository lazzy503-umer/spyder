# -*- coding: utf-8 -*-

# Copyright © Spyder Project Contributors
# Licensed under the terms of the MIT License
# (see spyder/__init__.py for details)

import pytest

from qtpy.QtCore import QObject, Signal

from spyder.plugins.completion.providers.snippets.provider import (
    SnippetsProvider)
from spyder.plugins.completion.tests.conftest import qtbot_module


class CompletionManagerMock(QObject):
    sig_recv_snippets = Signal(list)

    def handle_response(self, client, req_id, response):
        snippets = list(response['params'])
        self.sig_recv_snippets.emit(list(snippets))


@pytest.fixture(scope='module')
def snippets_completions(qtbot_module, request):
    snippets = SnippetsProvider(None, dict(SnippetsProvider.CONF_DEFAULTS))
    completions = CompletionManagerMock(None)
    qtbot_module.addWidget(snippets)
    qtbot_module.addWidget(completions)

    with qtbot_module.waitSignal(snippets.sig_provider_ready, timeout=30000):
        snippets.start()

    def teardown():
        snippets.shutdown()

    request.addfinalizer(teardown)

    snippets.sig_response_ready.connect(completions.handle_response)
    return snippets, completions
