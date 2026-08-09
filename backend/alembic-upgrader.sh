#!/bin/bash
set -e 
echo "Applying migrations"
uv run alembic upgrade head
echo "Done"
exec "$@"  
