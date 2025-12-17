#!/bin/bash
# Import all CSV chunks to Neon database

if [ -z "$DATABASE_URL" ]; then
    echo "ERROR: DATABASE_URL environment variable is not set"
    echo "Please set it with: export DATABASE_URL='your-neon-connection-string'"
    exit 1
fi

CHUNKS_DIR="../chunks"

if [ ! -d "$CHUNKS_DIR" ]; then
    echo "ERROR: Chunks directory not found at $CHUNKS_DIR"
    exit 1
fi

echo "Starting import of all CSV chunks..."
echo "This may take 1-2 hours depending on your connection speed."
echo ""

for file in "$CHUNKS_DIR"/shopify-storeleads-part*.csv; do
    if [ -f "$file" ]; then
        echo "================================================"
        echo "Importing: $(basename "$file")"
        echo "================================================"
        python3 import-to-neon.py "$file"
        if [ $? -eq 0 ]; then
            echo "✓ Successfully imported $(basename "$file")"
        else
            echo "✗ Failed to import $(basename "$file")"
            exit 1
        fi
        echo ""
    fi
done

echo "================================================"
echo "✓ All chunks imported successfully!"
echo "================================================"
