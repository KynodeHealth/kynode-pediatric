# Copyright 2026 KYNODE
# Licensed under the Apache License, Version 2.0.

from __future__ import annotations

import os
from pathlib import Path

import uvicorn


def main() -> None:
    """Run the local clinic node."""
    db_path = os.environ.get("KYNODE_LOCAL_NODE_DB")
    if not db_path:
        default_path = Path.cwd() / "kynode_pediatric_local_node.sqlite3"
        os.environ["KYNODE_LOCAL_NODE_DB"] = str(default_path)

    host = os.environ.get("KYNODE_LOCAL_NODE_HOST", "127.0.0.1")
    port = int(os.environ.get("KYNODE_LOCAL_NODE_PORT", "8080"))
    uvicorn.run(
        "kynode_pediatric_local_node.app:create_app",
        factory=True,
        host=host,
        port=port,
        log_level="info",
    )


if __name__ == "__main__":
    main()
