# ---------------------------------------------------
# Codoctopus — a provider-neutral agent orchestration framework.
#
# See docs/ARCHITECTURE_V2.md for the layering. The rule that keeps this
# reusable: nothing under codoctopus/ may import a web framework or a task
# queue. Those live in the runtime backends and the web app.
# ---------------------------------------------------

from codoctopus.config import Settings, get_settings

__version__ = "2.0.0.dev0"

__all__ = ["Settings", "get_settings", "__version__"]
