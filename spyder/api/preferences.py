# -*- coding: utf-8 -*-
#
# Copyright © Spyder Project Contributors
# Licensed under the terms of the MIT License
# (see spyder/__init__.py for details)

"""
API to create an entry in Spyder Preferences associated to a given plugin.
"""

# Standard library imports
import types
from typing import Tuple, Union, Set

# Third party imports
from qtpy.QtWidgets import QWidget

# Local imports
from spyder.plugins.preferences.api import SpyderConfigPage, BaseConfigTab


OptionSet = Set[Union[str, Tuple[str, ...]]]


class SpyderPreferencesTab(BaseConfigTab):
    """
    Widget that represents a tab on a preference page.

    All calls to :class:`SpyderConfigPage` attributes are resolved
    via delegation.
    """

    # Name of the tab to display on the configuration page.
    TITLE = None

    def __init__(self, parent: SpyderConfigPage):
        super().__init__(parent)
        self.parent = parent

        if self.TITLE is None or not isinstance(self.TITLE, str):
            raise ValueError("TITLE must be a str")

    def apply_settings(self) -> OptionSet:
        """
        Hook called to manually apply settings that cannot be automatically
        applied.

        Reimplement this if the configuration tab has complex widgets that
        cannot be created with any of the `self.create_*` calls.
        """
        return set({})

    def is_valid(self) -> bool:
        """
        Return True if the tab contents are valid.

        This method can be overriden to perform complex checks.
        """
        return True

    def __getattr__(self, attr):
        this_class_dir = dir(self)
        if attr not in this_class_dir:
            return getattr(self.parent, attr)
        else:
            return super().__getattr__(attr)


class PluginConfigPage(SpyderConfigPage):
    """
    Widget to expose the options a plugin offers for configuration as
    an entry in Spyder's Preferences dialog.
    """

    # TODO: Temporal attribute to handle which appy_settings method to use
    # the one of the conf page or the one in the plugin, while the config
    # dialog system is updated.
    APPLY_CONF_PAGE_SETTINGS = False

    def __init__(self, plugin, parent):
        self.plugin = plugin
        self.CONF_SECTION = plugin.CONF_SECTION
        self.main = parent.main
        self.get_font = plugin.get_font

        if not self.APPLY_CONF_PAGE_SETTINGS:
            self._patch_apply_settings(plugin)

        SpyderConfigPage.__init__(self, parent)

    def _wrap_apply_settings(self, func):
        """
        Wrap apply_settings call to ensure that a user-defined custom call
        is called alongside the Spyder Plugin API configuration propagation
        call.
        """
        def wrapper(self, options):
            opts = self.previous_apply_settings()
            func(options | opts)
        return types.MethodType(wrapper, self)

    def _patch_apply_settings(self, plugin):
        self.previous_apply_settings = self.apply_settings
        try:
            # New API
            self.apply_settings = self._wrap_apply_settings(plugin.apply_conf)
            self.get_option = plugin.get_conf_option
            self.set_option = plugin.set_conf_option
            self.remove_option = plugin.remove_conf_option
        except AttributeError:
            # Old API
            self.apply_settings = self._wrap_apply_settings(
                plugin.apply_plugin_settings)
            self.get_option = plugin.get_option
            self.set_option = plugin.set_option
            self.remove_option = plugin.remove_option

    def get_name(self):
        """
        Return plugin name to use in preferences page title, and
        message boxes.

        Normally you do not have to reimplement it, as soon as the
        plugin name in preferences page will be the same as the plugin
        title.
        """
        try:
            # New API
            name = self.plugin.get_name()
        except AttributeError:
            # Old API
            name = self.plugin.get_plugin_title()

        return name

    def get_icon(self):
        """
        Return plugin icon to use in preferences page.

        Normally you do not have to reimplement it, as soon as the
        plugin icon in preferences page will be the same as the plugin
        icon.
        """
        try:
            # New API
            icon = self.plugin.get_icon()
        except AttributeError:
            # Old API
            icon = self.plugin.get_plugin_icon()

        return icon

    def setup_page(self):
        """
        Setup configuration page widget

        You should implement this method and set the layout of the
        preferences page.

        layout = QVBoxLayout()
        layout.addWidget(...)
        ...
        self.setLayout(layout)
        """
        raise NotImplementedError

    def apply_settings(self) -> OptionSet:
        """
        Hook called to manually apply settings that cannot be automatically
        applied.

        Reimplement this if the configuration page has complex widgets that
        cannot be created with any of the `self.create_*` calls.

        This call should return a set containing the configuration options that
        changed.
        """
        return set({})
