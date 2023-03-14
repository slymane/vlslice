# VLSLICE

```bash
# Update repository
git pull

# Build client
cd vlslice/client
npm run build

# Run server
cd ../server
gunicorn --bind 0.0.0.0:5000 server:app \
    --workers=1 \
    --timeout=300 \
    --graceful-timeout=300 \
    --reload
```

## Client

Made with Svelte

## Server

Made with Flask
