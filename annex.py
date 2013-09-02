#!/usr/bin/env python

from __future__ import with_statement

import glob
import logging
import hashlib
import imp
import inspect
import os

logger = logging.getLogger("annex")

__author__ = "Gary M. Josack <gary@byoteki.com>"
__version__ = 0.1


def _md5sum(file_path):
    md5 = hashlib.md5()

    with open(file_path) as md5_file:
        while True:
            data = md5_file.read(1024 * 1024 * 4)
            if not data:
                break
            md5.update(data)

    return md5.digest()


class PluginModule(object):
    def __init__(self, plugin_file, plugins):
        self.plugin_file = plugin_file
        self.plugins = plugins
        self.md5 = _md5sum(plugin_file)


class Annex(object):
    def __init__(self, base_plugin, *plugin_dirs):
        """ Initializes plugins given paths to directories containing plugins.

            Args:
                base_class: Class from which your plugins subclass. This is
                            used to ensure only your modules can be loaded.
                plugin_dirs: Can be a string or a list containing an absolute path
                             to a directory containing plugins.
        """

        self.base_plugin = base_plugin
        self.plugin_dirs = set()
        self.loaded_modules = {}

        for plugin_dir in plugin_dirs:
            if isinstance(plugin_dir, basestring):
                self.plugin_dirs.add(plugin_dir)
            else:
                self.plugin_dirs.update(plugin_dir)

        for plugin_file in self._get_plugin_files(self.plugin_dirs):
            self._load_plugin(plugin_file)

    def __len__(self):
        return len(self.loaded_modules)

    def __iter__(self):
        for modules in self.loaded_modules.itervalues():
            for plugin in modules.plugins:
                yield plugin

    def __getattr__(self, name):
        for plugin in self:
            if plugin.__class__.__name__ == name:
                return plugin
        raise AttributeError

    def reload(self):
        logger.debug("Reloading Plugins...")

        deleted_modules = set(self.loaded_modules.keys())

        for plugin_file in self._get_plugin_files(self.plugin_dirs):
            if plugin_file not in self.loaded_modules:
                logger.debug("New Plugin Module found. Loading: %s", plugin_file)
                self._load_plugin(plugin_file)
            elif _md5sum(plugin_file) != self.loaded_modules[plugin_file].md5:
                deleted_modules.remove(plugin_file)
                logger.debug("Plugin Module changed. Reloading: %s", plugin_file)
                self._load_plugin(plugin_file)
            else:
                deleted_modules.remove(plugin_file)

        for plugin_file in deleted_modules:
            logger.debug("Plugin Module deleted. Removing: %s", plugin_file)
            del self.loaded_modules[plugin_file]

    def _load_plugin(self, plugin_file):
        logger.debug("Loading plugin from %s", plugin_file)
        try:
            plugin_module = self._import_plugin(plugin_file)
            if plugin_module is None:
                return

            plugins = []

            for name, obj in plugin_module.__dict__.iteritems():
                if (inspect.isclass(obj) and
                    issubclass(obj, self.base_plugin) and
                    name != self.base_plugin.__name__):
                    plugins.append(obj())

            if plugins:
                self.loaded_modules[plugin_file] = PluginModule(plugin_file, plugins)

        except Exception, err:
            logger.exception("Failed to load %s: %s", plugin_file, err)

    @staticmethod
    def _import_plugin(path):

        if not path.startswith("/"):
            logger.error("Annex plugins must be absolute path: %s", path)
            return

        module_path, module_file = os.path.split(path)
        module_file = os.path.splitext(module_file)[0]

        module_name = "annex_plugin_%s" % module_file

        fp, pathname, description = imp.find_module(module_file, [module_path])

        try:
            return imp.load_module(module_name, fp, pathname, description)
        finally:
            if fp:
                fp.close()

    @staticmethod
    def _get_plugin_files(plugin_dirs):
        files = []
        for plugin_dir in plugin_dirs:
            files.extend(glob.glob(os.path.abspath(os.path.join(plugin_dir, "*.py"))))
        return files

