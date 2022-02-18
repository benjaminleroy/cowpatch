# read version from installed package
from importlib.metadata import version
__version__ = version(__name__)

from .layout import layout, area
from .base import patch
from .text import text
from .wrappers import wrapper_plotnine, wrapper_matplotlib, wrapper_seaborn
