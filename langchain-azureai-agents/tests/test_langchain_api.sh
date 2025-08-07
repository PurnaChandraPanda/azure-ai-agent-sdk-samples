#!/bin/bash

set -e

total_requests=5
sleep_duration=5



# Run the curl test script in a loop N times with a delay of x seconds each time
for i in $(seq 1 "$total_requests");
do
    echo "Running iteration $i"
    response=$(curl --silent --show-error --no-keepalive \
            -H "Connection: close" \
            -H "Content-Type: application/json" \
            -X POST http://0.0.0.0:4000/ask \
            -d '{"query":"5 supply chain news for reliance"}' \
            -w '\n%{time_total}\n')
    
    time_taken=$(printf '%s\n' "$response" | tail -n1)
    body=$(printf '%s\n' "$response" | sed '$d')

    echo "Response: $body"
    echo "Time taken: ${time_taken}s"
    echo ""
    sleep $sleep_duration
done


echo "All iterations completed."
