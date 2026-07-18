from __future__ import annotations

from mangum import Mangum

from .api import app


handler = Mangum(app, lifespan="off")
