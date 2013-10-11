# annex

### Summary
Annex provides assistance with developing plugin-based tools.

With Annex you can load and reload plugins from various python modules without
the requirement that they exist on the PYTHONPATH.


### Example Usage

In your project you would define a base class from which all plugins for
project would subclass.


_base\_plugin.py_

```python
class BaseTestPlugin(object):
    def run(self, *args, **kwargs):
        raise NotImplementedError()
```


_example\_plugin.py_

```python
from base\_plugin import BaseTestPlugin

class PrinterPlugin(BaseTestPlugin):
    def run(self, *args, **kwargs):
        print args, kwargs
```

_foo.py_

```Python
from base\_plugin import BaseTestPlugin
from annex import Annex

plugins = Annex(BaseTestPlugin, "/path/to/plugins")

for plugin in plugins:
    plugin.run("foo", bar="baz")
```


