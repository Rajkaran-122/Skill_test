#!/bin/bash
# ============================================================
# Store Intelligence Platform — Kafka Topic Initialization
# ============================================================
# This script creates all required Kafka topics.
# Run inside the Kafka container: docker compose exec kafka bash /opt/kafka/create-topics.sh
# ============================================================

KAFKA_BIN="/opt/kafka/bin"
BOOTSTRAP="localhost:9092"

echo "============================================"
echo "  SIP — Creating Kafka Topics"
echo "============================================"

# Wait for Kafka to be ready
echo "Waiting for Kafka to be ready..."
while ! ${KAFKA_BIN}/kafka-broker-api-versions.sh --bootstrap-server ${BOOTSTRAP} > /dev/null 2>&1; do
    sleep 2
done
echo "Kafka is ready."

# Create topics
declare -A TOPICS=(
    ["visitor-events"]="12:168"      # 12 partitions, 7 days retention (168 hours)
    ["zone-events"]="12:168"
    ["queue-events"]="6:72"          # 6 partitions, 3 days retention
    ["conversion-events"]="6:720"    # 6 partitions, 30 days retention
    ["anomaly-events"]="3:720"       # 3 partitions, 30 days retention
    ["dashboard-events"]="3:24"      # 3 partitions, 1 day retention
    # Dead Letter Queues
    ["visitor-events-dlq"]="3:720"
    ["zone-events-dlq"]="3:720"
    ["queue-events-dlq"]="3:720"
    ["conversion-events-dlq"]="3:720"
)

for TOPIC in "${!TOPICS[@]}"; do
    IFS=':' read -r PARTITIONS RETENTION <<< "${TOPICS[$TOPIC]}"
    RETENTION_MS=$((RETENTION * 3600000))

    echo "Creating topic: ${TOPIC} (partitions=${PARTITIONS}, retention=${RETENTION}h)"

    ${KAFKA_BIN}/kafka-topics.sh \
        --bootstrap-server ${BOOTSTRAP} \
        --create \
        --topic ${TOPIC} \
        --partitions ${PARTITIONS} \
        --replication-factor 1 \
        --config retention.ms=${RETENTION_MS} \
        --config cleanup.policy=delete \
        --if-not-exists

    if [ $? -eq 0 ]; then
        echo "  ✓ ${TOPIC} created"
    else
        echo "  ✗ Failed to create ${TOPIC}"
    fi
done

echo ""
echo "============================================"
echo "  Topic creation complete"
echo "============================================"

# List all topics
echo ""
echo "Listing all topics:"
${KAFKA_BIN}/kafka-topics.sh --bootstrap-server ${BOOTSTRAP} --list
