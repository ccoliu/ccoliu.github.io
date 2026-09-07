# ---------------------------------------------------
# Codoctopus — Runtime
#
# Import from here, not from the individual backend modules.
# ---------------------------------------------------

from codoctopus.runtime.base import Executor, PlanResult
from codoctopus.runtime.local import LocalExecutor

__all__ = ["Executor", "LocalExecutor", "PlanResult"]
