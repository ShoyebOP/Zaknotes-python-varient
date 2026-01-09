#!/usr/bin/env python3
"""
Extract Vimeo iframe URL from a webpage using Playwright with cookie authentication.
"""

import argparse
import sys
import os
from urllib.parse import urlparse
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup


def parse_netscape_cookies(cookie_file_path, target_domain):
    """
    Parse Netscape-formatted cookie file and return cookies for Playwright.
    """
    cookies = []
    
    try:
        with open(cookie_file_path, 'r') as f:
            for line in f:
                line = line.strip()
                
                # Skip empty lines and comments
                if not line or (line.startswith('#') and not line.startswith('#HttpOnly_')):
                    continue
                
                # Handle HttpOnly prefix
                if line.startswith('#HttpOnly_'):
                    line = line[len('#HttpOnly_'):]
                
                # Split by tab
                parts = line.split('\t')
                if len(parts) < 7:
                    continue
                
                domain = parts[0]
                domain_flag = parts[1].upper() == 'TRUE' # TRUE means include subdomains (domain cookie)
                path = parts[2]
                secure = parts[3].upper() == 'TRUE'
                expiration = parts[4]
                name = parts[5]
                value = ' '.join(parts[6:])
                
                # Check if cookie belongs to target domain
                if target_domain.endswith(domain.lstrip('.')) or domain.lstrip('.').endswith(target_domain):
                    expires = int(expiration) if expiration.isdigit() else -1
                    # Treat 0 as session cookie (-1)
                    if expires == 0:
                        expires = -1
                    
                    # Handle domain based on flag
                    # If domain_flag is TRUE, it's a domain cookie (should start with .)
                    # If FALSE, it's a host-only cookie (should NOT start with .)
                    final_domain = domain
                    if domain_flag:
                        if not final_domain.startswith('.'):
                            final_domain = '.' + final_domain
                    else:
                        if final_domain.startswith('.'):
                            final_domain = final_domain.lstrip('.')

                    # Special handling for __Host- cookies (must be secure, path=/, no domain attribute/host-only)
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
                        'expires': expires
                    }
                    cookies.append(cookie)
                    print(f"DEBUG: Parsed cookie: {name} (expires={expires}, domain={cookie['domain']}, secure={secure})", file=sys.stderr)
    
    except FileNotFoundError:
        print(f"ERROR: Cookie file not found: {cookie_file_path}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"ERROR: Failed to parse cookie file: {e}", file=sys.stderr)
        sys.exit(1)
    
    return cookies


def extract_vimeo_url(url, cookie_file):
    """
    Extract Vimeo iframe URL using Playwright.
    """
    try:
        parsed_url = urlparse(url)
        target_domain = parsed_url.netloc
        
        print(f"INFO: Target URL: {url}", file=sys.stderr)
        
        cookies = parse_netscape_cookies(cookie_file, target_domain)
        if not cookies:
            print(f"ERROR: No valid cookies found for domain: {target_domain}", file=sys.stderr)
            sys.exit(1)
        
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            )
            
            # Add cookies to context
            try:
                context.add_cookies(cookies)
            except Exception as e:
                print(f"ERROR: Failed to add cookies: {e}", file=sys.stderr)
                # Try adding one by one to find the culprit
                for cookie in cookies:
                    try:
                        context.add_cookies([cookie])
                    except Exception as inner_e:
                        print(f"ERROR: Bad cookie: {cookie['name']} - {inner_e}", file=sys.stderr)
                browser.close()
                sys.exit(1)
            
            page = context.new_page()
            
            print(f"INFO: Navigating to target page...", file=sys.stderr)
            page.goto(url, wait_until="networkidle")
            
            # Wait for iframe to be present
            try:
                page.wait_for_selector("iframe", timeout=30000)
            except Exception:
                print("ERROR: Timeout waiting for iframe to load", file=sys.stderr)
                browser.close()
                sys.exit(1)
            
            # Get page content and parse with BeautifulSoup
            content = page.content()
            soup = BeautifulSoup(content, 'html.parser')
            
            iframes = soup.find_all('iframe')
            for iframe in iframes:
                src = iframe.get('src', '')
                if 'player.vimeo.com' in src:
                    print("INFO: Successfully found Vimeo iframe", file=sys.stderr)
                    browser.close()
                    return src
            
            print("ERROR: No Vimeo iframe found on page", file=sys.stderr)
            browser.close()
            sys.exit(1)
            
    except Exception as e:
        print(f"ERROR: Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Extract Vimeo iframe URL from a webpage using Playwright'
    )
    parser.add_argument('--url', required=True, help='Target webpage URL')
    parser.add_argument('--cookies', required=True, help='Path to Netscape cookie file')
    
    args = parser.parse_args()
    
    if not os.path.isfile(args.cookies):
        print(f"ERROR: Cookie file does not exist: {args.cookies}", file=sys.stderr)
        sys.exit(1)
    
    vimeo_url = extract_vimeo_url(args.url, args.cookies)
    
    if vimeo_url:
        print(vimeo_url)
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == '__main__':
    main()
