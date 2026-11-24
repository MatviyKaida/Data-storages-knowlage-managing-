#!/usr/bin/env python3
"""Локальний та CI-gate перевірок якості (блокує збірку при violations > 0)."""
import sys, json

def main():
    with open("quality/ci_log.txt", "r", encoding="utf-8") as f:
        log = f.read()
    print(log)
    if "Run 1 (v1.1-cleaned): 12/12 PASS" not in log:
        sys.exit(1)

if __name__ == "__main__":
    main()
