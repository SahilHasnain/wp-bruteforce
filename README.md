# WordPress XMLRPC Brute Force

Brute force WordPress admin via XMLRPC `system.multicall` - packs 50+ login attempts per HTTP request.

## Target
- **URL:** `specialperson.dawateislami.net/xmlrpc.php`
- **Username:** `admin` (enumerated via `/wp-json/wp/v2/users`)
- **Method:** XMLRPC `wp.getUsersBlogs` via `system.multicall`

## Usage

### Local
```bash
pip install requests
python3 bruteforce.py -w wordlist.txt -u admin -b 50
```

### GitHub Actions
Go to Actions > WordPress Brute Force > Run workflow, select wordlist size.

## How it works
1. Loads password wordlist
2. Packs 50 passwords into a single XMLRPC `system.multicall` request
3. Sends to `xmlrpc.php`
4. Parses response for successful login
5. Repeats until found or wordlist exhausted

## Why XMLRPC
- No lockout mechanism
- No CAPTCHA
- No rate limiting
- 50 attempts per request = 75+ attempts/second
- Bypasses most IP-based rate limiters
