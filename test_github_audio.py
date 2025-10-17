#!/usr/bin/env python3
"""
Test script to verify GitHub audio integration
"""
import sys

import requests

GITHUB_BASE = "https://raw.githubusercontent.com/saikesav-sai/rig_veda_audio_files/main"

def test_audio_file(mandala, hymn, stanza):
    """Test if an audio file exists on GitHub"""
    url = f"{GITHUB_BASE}/{mandala}/Hymn_{hymn}/Stanza_{stanza}.mp3"
    print(f"\n🔍 Testing: Mandala {mandala}, Hymn {hymn}, Stanza {stanza}")
    print(f"   URL: {url}")
    
    try:
        response = requests.head(url, timeout=5)
        if response.status_code == 200:
            size_mb = int(response.headers.get('content-length', 0)) / (1024 * 1024)
            print(f"   ✅ Found! Size: {size_mb:.2f} MB")
            return True
        else:
            print(f"   ❌ Not found (Status: {response.status_code})")
            return False
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def main():
    print("=" * 60)
    print("GitHub Audio Files Integration Test")
    print("=" * 60)
    
    # Test a few files
    test_cases = [
        (1, 1, 1),   # First stanza
        (1, 1, 2),   # Second stanza
        (2, 1, 1),   # Different mandala
        (1, 2, 1),   # Different hymn
    ]
    
    results = []
    for mandala, hymn, stanza in test_cases:
        result = test_audio_file(mandala, hymn, stanza)
        results.append(result)
    
    print("\n" + "=" * 60)
    print(f"Results: {sum(results)}/{len(results)} tests passed")
    print("=" * 60)
    
    if all(results):
        print("✅ All tests passed! GitHub integration is working.")
        return 0
    else:
        print("⚠️  Some tests failed. Check GitHub repository structure.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
