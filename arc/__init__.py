from jpype import JPackage
import sys

_arc = JPackage("arc")
util = _arc.util
sys.modules['arc'] = _arc