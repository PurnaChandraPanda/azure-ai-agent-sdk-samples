#!/bin/bash

set -e

total_requests=5
sleep_duration=5

# Run the Python script in a loop N times with a delay of x seconds each time
for i in $(seq 1 "$total_requests");
do
    echo "Running iteration $i"
    start_ms=$(date +%s%3N)

    python -m tests.client_langchain_orchestrate
    
    end_ms=$(date +%s%3N)
    echo "\nTime taken: $((end_ms - start_ms)) ms"
    echo ""

    sleep $sleep_duration
done

echo "All iterations completed."
