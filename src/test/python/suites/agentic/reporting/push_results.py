#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2026 Wesley Peng
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

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
import os
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

# Canonical test-type taxonomy (mirrors agent's TEST_TYPES in
# src/api/routes/reporting.py). Producers MUST emit one of these as
# `test_suite` so the Reports drill-down can group by type.
TEST_TYPES = ('unit', 'integration', 'ui', 'smoke', 'e2e', 'perf', 'chaos')


def _derive_test_type(source_file: str, suite_name: str, override: str | None) -> str:
    """Pick a canonical test type from CLI override, then filename, then suite."""
    if override:
        return override
    haystack = f'{source_file} {suite_name}'.lower()
    for t in TEST_TYPES:
        if re.search(rf'\b{t}\b', haystack):
            return t
    return 'unit'

try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False


def parse_junit_xml(xml_path, test_type_override: str | None = None):
    """Parse a JUnit XML file and return a list of test result dicts.

    Enriches each doc with CI correlation fields (repo, pipeline_id,
    build_number, branch, commit_sha) from the Jenkins env so the
    Dashboard Reports drill-down can join against test-coverage-*.
    """
    results = []
    tree = ET.parse(xml_path)
    root = tree.getroot()

    # Handle both <testsuites><testsuite>... and <testsuite>... formats
    suites = root.findall('.//testsuite')
    if not suites and root.tag == 'testsuite':
        suites = [root]

    # Jenkins env correlation (no-op outside Jenkins). repo defaults to
    # the agentic-taf repo when JOB_NAME is unset.
    job = os.environ.get('JOB_NAME', '') or ''
    repo = job.split('/')[0] if job else 'agentic-taf'
    branch = os.environ.get('BRANCH_NAME') or os.environ.get('GIT_BRANCH') or 'main'
    commit_sha = os.environ.get('GIT_COMMIT', '')
    pipeline_id = os.environ.get('BUILD_TAG', '')
    build_number_raw = os.environ.get('BUILD_NUMBER', '0')
    try:
        build_number = int(build_number_raw)
    except ValueError:
        build_number = 0
    team = os.environ.get('TEAM', 'platform-team')

    for suite in suites:
        suite_name = suite.get('name', 'unknown')
        suite_time = float(suite.get('time', 0))
        test_type = _derive_test_type(str(xml_path), suite_name, test_type_override)

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
                # JUnit-derived fields (kept for backward compatibility)
                'suite': suite_name,
                'classname': classname,
                'name': name,
                'status': status,
                'duration_seconds': time_taken,
                'duration_ms': int(time_taken * 1000),
                'message': message,
                'source_file': str(xml_path),
                'timestamp': datetime.datetime.utcnow().isoformat() + 'Z',
                'framework': 'agentic-taf',
                'suite_duration': suite_time,
                # Canonical fields the agent reads for joining + grouping
                'test_suite': test_type,        # canonical type taxonomy
                'test_name': name,              # mirror of `name`
                'test_type': test_type,         # explicit alias
                'repo': repo,
                'branch': branch,
                'commit_sha': commit_sha,
                'pipeline_id': pipeline_id,
                'build_number': build_number,
                'team': team,
                'is_flaky': False,
                'retry_count': 0,
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
    parser.add_argument(
        '--test-type',
        choices=TEST_TYPES,
        help='Override the canonical test type. If omitted, derived from the '
             'XML filename / suite name (regex against the TEST_TYPES list); '
             'falls back to "unit".',
    )
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
            results = parse_junit_xml(xml_file, test_type_override=args.test_type)
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
