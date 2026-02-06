#!/usr/bin/env python3
"""
Extract media links (Vimeo, Vidinfra) from a webpage using Playwright.
"""

import argparse
import sys
import os
import threading
import queue
import re
from urllib.parse import urlparse, urljoin
from playwright.sync_api import sync_playwright


def parse_netscape_cookies(cookie_file_path):
    """
    Parse Netscape-formatted cookie file and return cookies for Playwright.
    Returns all cookies in the file.
    """
    cookies = []
    
    try:
        with open(cookie_file_path, 'r') as f:
            for line in f:
                line = line.strip()
                
                # Skip empty lines and comments
                if not line or (line.startswith('#') and not line.startswith('#HttpOnly_')):
                    continue
                
                is_http_only = False
                # Handle HttpOnly prefix
                if line.startswith('#HttpOnly_'):
                    line = line[len('#HttpOnly_'):]
                    is_http_only = True
                
                # Split by tab
                parts = line.split('\t')
                if len(parts) < 7:
                    continue
                
                domain = parts[0]
                domain_flag = parts[1].upper() == 'TRUE'
                path = parts[2]
                secure = parts[3].upper() == 'TRUE'
                expiration = parts[4]
                name = parts[5]
                value = ' '.join(parts[6:])
                
                expires = int(expiration) if expiration.isdigit() else -1
                if expires == 0:
                    expires = -1
                
                final_domain = domain
                if domain_flag:
                    if not final_domain.startswith('.'):
                        final_domain = '.' + final_domain
                else:
                    if final_domain.startswith('.'):
                        final_domain = final_domain.lstrip('.')

                if name.startswith('__Host-'):
                    secure = True
                    path = '/'
                    if final_domain.startswith('.'):
                        final_domain = final_domain.lstrip('.')
                    
                cookie = {
                    'name': name,
                    'value': value,
                    'domain': final_domain,
                    'path': path,
                    'secure': secure,
                    'expires': expires,
                    'httpOnly': is_http_only
                }
                cookies.append(cookie)
    
    except FileNotFoundError:
        print(f"ERROR: Cookie file not found: {cookie_file_path}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"ERROR: Failed to parse cookie file: {e}", file=sys.stderr)
        sys.exit(1)
    
    return cookies


def select_with_timeout(options, timeout=30):
    """
    Prompt user to select an option with a timeout.
    """
    print(f"\nMultiple links found. Please select one (1-{len(options)}) [Timeout {timeout}s]:", file=sys.stderr)
    for i, opt in enumerate(options, 1):
        print(f"{i}. {opt}", file=sys.stderr)
    
    res_queue = queue.Queue()

    def get_input():
        try:
            choice = input(f"Select (1-{len(options)}, default 1): ")
            res_queue.put(choice)
        except EOFError:
            res_queue.put("")
        except Exception:
            res_queue.put("")

    thread = threading.Thread(target=get_input)
    thread.daemon = True
    thread.start()

    try:
        choice = res_queue.get(timeout=timeout)
        if not choice or not choice.isdigit():
            return options[0]
        idx = int(choice) - 1
        if 0 <= idx < len(options):
            return options[idx]
        return options[0]
    except queue.Empty:
        print(f"\nTimeout reached. Defaulting to option 1.", file=sys.stderr)
        return options[0]


def extract_link(url, cookie_file, user_agent=None):
    """
    Extract Vimeo/Vidinfra media link.
    """
    if not user_agent:
        user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        
    try:
        cookies = parse_netscape_cookies(cookie_file)
        
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(
                user_agent=user_agent
            )
            
            try:
                context.add_cookies(cookies)
            except Exception as e:
                print(f"ERROR: Failed to add cookies: {e}", file=sys.stderr)
                browser.close()
                return None
            
            page = context.new_page()
            print(f"INFO: Navigating to {url}...", file=sys.stderr)
            
            # Use longer timeouts and wait for commit
            page.goto(url, wait_until="commit", timeout=60000)
            
            # Wait for content to settle
            print(f"INFO: Waiting for content to settle...", file=sys.stderr)
            page.wait_for_timeout(15000)
            
            print(f"DEBUG: Final URL: {page.url}", file=sys.stderr)
            
            found_links = set()

            # Iterate through ALL frames
            all_frames = page.frames
            for frame in all_frames:
                try:
                    f_url = frame.url
                    if not f_url or f_url == "about:blank":
                        continue
                        
                    if 'player.vimeo.com' in f_url or 'player.vidinfra.com' in f_url:
                        found_links.add(f_url.split('?')[0])
                            
                except:
                    continue

            browser.close()

            if not found_links:
                print(f"ERROR: No links found", file=sys.stderr)
                return None

            sorted_links = sorted(list(found_links))
            if len(sorted_links) > 1:
                selected = select_with_timeout(sorted_links)
                return selected if selected else sorted_links[0]
            return sorted_links[0]
            
    except Exception as e:
        print(f"ERROR: Unexpected error in extract_link: {e}", file=sys.stderr)
        return None


def main():
    parser = argparse.ArgumentParser(description='Vimeo/Vidinfra Media Link Extractor')
    parser.add_argument('--url', required=True, help='Target webpage URL')
    parser.add_argument('--cookies', required=True, help='Path to Netscape cookie file')
    parser.add_argument('--user-agent', help='Custom Browser User-Agent')
    
    args = parser.parse_args()
    
    if not os.path.isfile(args.cookies):
        print(f"ERROR: Cookie file does not exist: {args.cookies}", file=sys.stderr)
        sys.exit(1)
    
    link = extract_link(args.url, args.cookies, args.user_agent)
    
    if link:
        print(link)
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == '__main__':
    main()
