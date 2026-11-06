#!/usr/bin/env python3
"""Compare supplied numerical values against the manuscript reference contract."""
from __future__ import annotations
import argparse, json, math, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _number(value):
    return type(value) in (int, float) and math.isfinite(value)


def compare(computed, contract):
    """Compare values using the contract tolerances and report coverage."""
    if not isinstance(computed, dict):
        raise ValueError('Computed results must be a JSON object')
    allowed = {entry['result_id'] for entry in contract['required_numerical_checks']}
    extra = set(computed) - allowed
    if extra:
        raise ValueError(f'Unknown result IDs: {sorted(extra)}')
    for name, value in computed.items():
        if isinstance(value, dict) and set(value) != {'value'}:
            raise ValueError(f'{name} must contain only a numeric value field')
    checks = []
    for entry in contract['required_numerical_checks']:
        result_id = entry['result_id']
        supplied = computed.get(result_id)
        if isinstance(supplied, dict):
            observed = supplied.get('value')
        else:
            observed = supplied
        expected = entry['reported_value']
        tol = entry.get('absolute_tolerance', 1e-7)
        if not _number(expected) or not _number(tol) or tol < 0:
            raise ValueError(f'Invalid reference contract for {result_id}')
        if supplied is None:
            status = 'MISSING_VALUE'
            observed = None
        elif not _number(observed):
            status = 'INVALID_VALUE'
            observed = None
        else:
            status = ('NUMERIC_MATCH_UNVERIFIED' if abs(observed - expected) <= tol
                      else 'NUMERIC_MISMATCH')
        checks.append({'result_id': result_id, 'status': status,
                       'reported_value': expected, 'supplied_value': observed,
                       'absolute_tolerance': tol, 'manuscript_location': entry['location']})
    statuses = [c['status'] for c in checks]
    # Incomplete input takes precedence over overall numerical agreement.
    if any(s in ('MISSING_VALUE', 'INVALID_VALUE') for s in statuses):
        verdict = 'INCOMPLETE_OR_INVALID'
    elif any(s == 'NUMERIC_MISMATCH' for s in statuses):
        verdict = 'NUMERIC_MISMATCH'
    else:
        verdict = 'NUMERIC_AGREEMENT_ONLY'
    return {
        'verdict': verdict,
        'checks': checks,
        'summary': {
            'expected_targets': len(checks),
            'provided_numeric_values': sum(s in ('NUMERIC_MATCH_UNVERIFIED','NUMERIC_MISMATCH') for s in statuses),
            'matching_values': statuses.count('NUMERIC_MATCH_UNVERIFIED'),
            'mismatching_values': statuses.count('NUMERIC_MISMATCH'),
            'missing_values': statuses.count('MISSING_VALUE'),
            'invalid_values': statuses.count('INVALID_VALUE')}
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--computed', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    contract = json.loads((ROOT/'config/numerical_parity_contract.json').read_text())
    supplied = json.loads(args.computed.read_text())
    result = compare(supplied, contract)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2, allow_nan=False)+'\n')
    print(result['verdict'])
    return 0 if result['verdict'] == 'NUMERIC_AGREEMENT_ONLY' else 2


if __name__ == '__main__':
    sys.exit(main())
