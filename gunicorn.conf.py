# ---------------------------------------------------
# Gunicorn configuration for Render
# ---------------------------------------------------

import os

# Bind to the PORT env var that Render provides
bind = f"0.0.0.0:{os.environ.get('PORT', '10000')}"

# Workers — Render starter instances have limited memory,
# so keep this low.  2 workers is a safe default.
workers = 2

# Timeout — GPT calls can take a while, so set a generous timeout.
timeout = 300

# Logging
accesslog = "-"
errorlog = "-"
loglevel = "info"
