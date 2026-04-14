#!/usr/bin/env python3
# Copyright (c) 2017-2026 Wesley Peng
#
# Licensed under the GNU Lesser General Public License v3.0 (LGPL-3.0).
# You may obtain a copy of the License at
#
# https://www.gnu.org/licenses/lgpl-3.0.html
#
# This software is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Lesser General Public License for more details.

"""Push JUnit XML test results to OpenSearch.

Usage:
    python push_results.py \\
        --reports-dir reports/ \\
        --opensearch-url http://opensearch:9200 \\
        --index test-results

Parses all JUnit XML files in the reports directory, extracts test cases,
and bulk-indexes them into OpenSearch for visualization in the QA Dashboard.
"""

import argparse
import datetime
import json
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False


def parse_junit_xml(xml_path):
    """Parse a JUnit XML file and return a list of test result dicts."""
    results = []
    tree = ET.parse(xml_path)
    root = tree.getroot()

    # Handle both <testsuites><testsuite>... and <testsuite>... formats
    suites = root.findall('.//testsuite')
    if not suites and root.tag == 'testsuite':
        suites = [root]

    for suite in suites:
        suite_name = suite.get('name', 'unknown')
        suite_time = float(suite.get('time', 0))

        for tc in suite.findall('testcase'):
            name = tc.get('name', 'unknown')
            classname = tc.get('classname', suite_name)
            time_taken = float(tc.get('time', 0))

            status = 'passed'
            message = None
            if tc.find('failure') is not None:
                status = 'failed'
                message = tc.find('failure').get('message', '')
            elif tc.find('error') is not None:
                status = 'error'
                message = tc.find('error').get('message', '')
            elif tc.find('skipped') is not None:
                status = 'skipped'
                message = tc.find('skipped').get('message', '')

            results.append({
                'suite': suite_name,
                'classname': classname,
                'name': name,
                'status': status,
                'duration_seconds': time_taken,
                'message': message,
                'source_file': str(xml_path),
                'timestamp': datetime.datetime.utcnow().isoformat() + 'Z',
                'framework': 'agentic-taf',
                'suite_duration': suite_time,
            })

    return results


def push_to_opensearch(results, opensearch_url, index_name):
    """Bulk-index test results into OpenSearch."""
    if not HAS_REQUESTS:
        print('ERROR: requests library not installed, cannot push to OpenSearch')
        return False

    bulk_body = ''
    for doc in results:
        action = json.dumps({'index': {'_index': index_name}})
        body = json.dumps(doc)
        bulk_body += f'{action}\n{body}\n'

    if not bulk_body:
        print('No results to push')
        return True

    url = f'{opensearch_url.rstrip("/")}/_bulk'
    headers = {'Content-Type': 'application/x-ndjson'}

    try:
        resp = requests.post(url, data=bulk_body, headers=headers, timeout=30)
        resp.raise_for_status()
        result = resp.json()
        errors = result.get('errors', False)
        items = result.get('items', [])
        print(f'Indexed {len(items)} results to {index_name} '
              f'(errors={errors})')
        return not errors
    except Exception as exc:
        print(f'Failed to push to OpenSearch: {exc}')
        return False


def push_to_agent_api(results, agent_url):
    """Push test results via agent reporting API."""
    if not HAS_REQUESTS:
        print('ERROR: requests library not installed')
        return False

    url = f'{agent_url.rstrip("/")}/api/v1/reporting/test-results'
    headers = {
        'Content-Type': 'application/json',
        'X-User': 'ci-bot',
        'X-Role': 'ci-service',
        'X-Team': 'platform-team',
    }

    summary = {
        'total': len(results),
        'passed': sum(1 for r in results if r['status'] == 'passed'),
        'failed': sum(1 for r in results if r['status'] == 'failed'),
        'skipped': sum(1 for r in results if r['status'] == 'skipped'),
        'error': sum(1 for r in results if r['status'] == 'error'),
        'framework': 'agentic-taf',
        'timestamp': datetime.datetime.utcnow().isoformat() + 'Z',
    }

    try:
        resp = requests.post(url, json=summary, headers=headers, timeout=30)
        print(f'Agent API response: {resp.status_code}')
        return resp.status_code < 500
    except Exception as exc:
        print(f'Failed to push to agent API: {exc}')
        return False


def main():
    parser = argparse.ArgumentParser(description='Push JUnit results to OpenSearch')
    parser.add_argument('--reports-dir', required=True, help='Directory containing JUnit XML files')
    parser.add_argument('--opensearch-url', help='OpenSearch URL (e.g. http://opensearch:9200)')
    parser.add_argument('--agent-url', help='Agent API URL (e.g. http://agent:8000)')
    parser.add_argument('--index', default='test-results', help='OpenSearch index name')
    args = parser.parse_args()

    reports_dir = Path(args.reports_dir)
    if not reports_dir.exists():
        print(f'Reports directory not found: {reports_dir}')
        sys.exit(1)

    xml_files = list(reports_dir.glob('*.xml'))
    if not xml_files:
        print(f'No XML files found in {reports_dir}')
        sys.exit(0)

    all_results = []
    for xml_file in xml_files:
        try:
            results = parse_junit_xml(xml_file)
            all_results.extend(results)
            print(f'Parsed {len(results)} results from {xml_file.name}')
        except Exception as exc:
            print(f'Failed to parse {xml_file.name}: {exc}')

    print(f'\nTotal: {len(all_results)} test results')
    passed = sum(1 for r in all_results if r['status'] == 'passed')
    failed = sum(1 for r in all_results if r['status'] == 'failed')
    skipped = sum(1 for r in all_results if r['status'] == 'skipped')
    print(f'  Passed: {passed}, Failed: {failed}, Skipped: {skipped}')

    ok = True
    if args.opensearch_url:
        ok = push_to_opensearch(all_results, args.opensearch_url, args.index) and ok
    if args.agent_url:
        ok = push_to_agent_api(all_results, args.agent_url) and ok

    if not args.opensearch_url and not args.agent_url:
        print('\nNo destination specified (use --opensearch-url or --agent-url)')

    sys.exit(0 if ok else 1)


if __name__ == '__main__':
    main()
