#!/usr/bin/env python

""" Annex provides assistance with developing plugin-based tools.

With Annex you can load and reload plugins from various python modules without
the requirement that they exist on the PYTHONPATH.

"""

from __future__ import with_statement

import glob
import logging
import hashlib
import imp
import inspect
import os

from .version import __version__

# Handle string detection without adding a dependency on any external modules.
try:
    basestring = basestring
except NameError:
    # basestring is undefined, must be Python 3.
    basestring = (str, bytes)

logger = logging.getLogger("annex")

__author__ = "Gary M. Josack <gary@byoteki.com>"


def _md5sum(file_path):
    """ Helper function that builds and md5sum from a file in chunks.

    Args:
        file_path: The path to the file you want an md5sum for.

    Returns:
        A string containing an md5sum.

    """
    md5 = hashlib.md5()

    with open(file_path, "rb") as md5_file:
        while True:
            data = md5_file.read(1024 * 1024 * 4)
            if not data:
                break
            md5.update(data)

    return md5.digest()


class PluginModule(object):
    """ Container for the plugins contained in a single module file.

    Attributes:
        plugin_file: Path to the file in which this plugin module was loaded.
        plugins: A list containing instances of plugins loaded from the plugin_file.
        md5: An md5 of the plugin_file's contents.

    """
    def __init__(self, plugin_file, plugins):
        self.plugin_file = plugin_file
        self.plugins = plugins
        self.md5 = _md5sum(plugin_file)


class Annex(object):
    """ Class for loading and retreiving various plugins.

    Attributes:
        base_plugin: Class from which your plugins subclass. This is used to
            decide which plugins will be loaded.
        plugin_dirs: A set of all directories where plugins can be loaded from.
        loaded_modules: A dictionary mapping plugin module filenames to
            PluginModule objects.

    """
    def __init__(self, base_plugin, plugin_dirs, instantiate=True, raise_exceptions=False,
            additional_plugin_callback=None):
        """ Initializes plugins given paths to directories containing plugins.

        Args:
            plugin_dirs: Can be a multilayered list of strings, which will be
                flattened, containing an absolute path to a directory
                containing plugins.
            instantiate: By default Annex will instantiate your plugins. Some
                times you need the control of instantiating them yourself.
            additional_plugin_callback: Function that's called after all
            `plugin_dirs` have loaded. This function should return a list of
            `base_plugin` derived 'additional' classes (which will be returned
            when iterating plugins).
        """

        self.base_plugin = base_plugin
        self.plugin_dirs = set()
        self.loaded_modules = {}
        self._instantiate = instantiate
        self._raise_exceptions = raise_exceptions
        self.additional_plugins = []

        for plugin_dir in plugin_dirs:
            if isinstance(plugin_dir, basestring):
                self.plugin_dirs.add(plugin_dir)
            else:
                self.plugin_dirs.update(plugin_dir)

        for plugin_file in self._get_plugin_files(self.plugin_dirs):
            self._load_plugin(plugin_file)

        if additional_plugin_callback:
            additional_plugins = additional_plugin_callback()
            for plugin in additional_plugins:
                if self._instantiate:
                    plugin = plugin()
                self.additional_plugins.append(plugin)

    def __len__(self):
        return len(self.loaded_modules)

    def __iter__(self):
        for modules in self.loaded_modules.values():
            for plugin in modules.plugins:
                yield plugin

        if self.additional_plugins:
            for plugin in self.additional_plugins:
                yield plugin

    def __getattr__(self, name):
        for plugin in self:
            if self._instantiate:
                obj_name = plugin.__class__.__name__
            else:
                obj_name = plugin.__name__
            if obj_name == name:
                return plugin
        raise AttributeError

    def reload(self):
        """ Reloads modules from the current plugin_dirs.

        This method will search the plugin_dirs attribute finding new plugin modules,
        updating plugin modules that have changed, and unloading plugin modules that
        no longer exist.

        """
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

            for name, obj in plugin_module.__dict__.items():
                if (inspect.isclass(obj) and
                    issubclass(obj, self.base_plugin) and
                    name != self.base_plugin.__name__):
                    if self._instantiate:
                        obj = obj()
                    plugins.append(obj)

            if plugins:
                self.loaded_modules[plugin_file] = PluginModule(plugin_file, plugins)

        except Exception as err:
            logger.exception("Failed to load %s: %s", plugin_file, err)
            if self._raise_exceptions:
                raise

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

