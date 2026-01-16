#!/usr/bin/env python3
"""
Deduplicate SARIF findings between Semgrep and Gitleaks.
Removes secrets findings from Semgrep that are already detected by Gitleaks.
"""

import json
import re
import sys
import os


def load_sarif(filepath):
    """Load a SARIF file and return its contents."""
    with open(filepath, 'r') as f:
        return json.load(f)


def save_sarif(filepath, data):
    """Save SARIF data to a file."""
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=2)


def extract_locations(sarif_data):
    """Extract all file:line locations from a SARIF file."""
    locations = set()
    for run in sarif_data.get('runs', []):
        for result in run.get('results', []):
            for loc in result.get('locations', []):
                phys = loc.get('physicalLocation', {})
                uri = phys.get('artifactLocation', {}).get('uri', '')
                line = phys.get('region', {}).get('startLine', 0)
                if uri and line:
                    locations.add(f'{uri}:{line}')
    return locations


def is_secret_finding(rule_id, message):
    """Check if a finding is related to secrets/credentials."""
    pattern = re.compile(
        r'(key|token|secret|password|credential|api.key|private|auth)',
        re.IGNORECASE
    )
    return bool(pattern.search(rule_id) or pattern.search(message))


def deduplicate(semgrep_file, gitleaks_file):
    """Remove duplicate secrets from Semgrep SARIF that exist in Gitleaks."""
    # Load SARIF files
    semgrep = load_sarif(semgrep_file)
    gitleaks = load_sarif(gitleaks_file)

    # Extract Gitleaks locations
    gitleaks_locations = extract_locations(gitleaks)
    print(f'Gitleaks locations found: {len(gitleaks_locations)}')

    # Filter Semgrep results
    removed_count = 0
    for run in semgrep.get('runs', []):
        filtered_results = []
        for result in run.get('results', []):
            rule_id = result.get('ruleId', '')
            message = result.get('message', {}).get('text', '')

            # Check if it's a secrets-related finding
            if is_secret_finding(rule_id, message):
                # Check if same location exists in Gitleaks
                dominated = False
                for loc in result.get('locations', []):
                    phys = loc.get('physicalLocation', {})
                    uri = phys.get('artifactLocation', {}).get('uri', '')
                    line = phys.get('region', {}).get('startLine', 0)
                    if f'{uri}:{line}' in gitleaks_locations:
                        dominated = True
                        break

                if dominated:
                    removed_count += 1
                    continue

            filtered_results.append(result)

        run['results'] = filtered_results

    # Save filtered SARIF
    save_sarif(semgrep_file, semgrep)
    print(f'Removed {removed_count} duplicate secret(s) from Semgrep SARIF')
    return removed_count


def main():
    semgrep_file = 'sarif-results/semgrep-sarif/semgrep.sarif'

    # Find Gitleaks file (can be results.sarif or gitleaks-report.sarif)
    gitleaks_file = ''
    if os.path.exists('sarif-results/gitleaks-sarif/results.sarif'):
        gitleaks_file = 'sarif-results/gitleaks-sarif/results.sarif'
    elif os.path.exists('sarif-results/gitleaks-sarif/gitleaks-report.sarif'):
        gitleaks_file = 'sarif-results/gitleaks-sarif/gitleaks-report.sarif'

    # Check if files exist
    if not os.path.exists(semgrep_file):
        print(f'Semgrep SARIF not found: {semgrep_file}')
        sys.exit(0)

    if not gitleaks_file:
        print('Gitleaks SARIF not found')
        sys.exit(0)

    print(f'Semgrep SARIF: {semgrep_file}')
    print(f'Gitleaks SARIF: {gitleaks_file}')

    deduplicate(semgrep_file, gitleaks_file)


if __name__ == '__main__':
    main()
