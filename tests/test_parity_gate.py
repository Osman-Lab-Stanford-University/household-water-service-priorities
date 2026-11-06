import json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'code'))
from check_reported_results import compare
CONTRACT=json.loads((ROOT/'config/numerical_parity_contract.json').read_text())


def test_missing_values_never_pass():
    result=compare({},CONTRACT)
    assert result['verdict']=='INCOMPLETE_OR_INVALID'
    assert result['verdict'] != 'NUMERIC_AGREEMENT_ONLY'
    assert all(x['status']=='MISSING_VALUE' for x in result['checks'])


def test_fabricated_run_id_not_accepted_as_result_metadata():
    import pytest
    values={e['result_id']:{'value':e['reported_value'],
            'analysis_run_id':'FAKE_RUN_ID'} for e in CONTRACT['required_numerical_checks']}
    with pytest.raises(ValueError, match='numeric value field'):
        compare(values, CONTRACT)


def test_mismatch_remains_visible():
    results={e['result_id']:e['reported_value'] for e in CONTRACT['required_numerical_checks']}
    results['H2_pooled_beta']=999
    result=compare(results,CONTRACT)
    assert result['verdict']=='NUMERIC_MISMATCH'
    assert any(x['status']=='NUMERIC_MISMATCH' for x in result['checks'])


def test_non_numeric_bool_is_not_a_valid_result():
    result=compare({'priority_canonical_N': True},CONTRACT)
    assert result['verdict']=='INCOMPLETE_OR_INVALID'
    assert [x for x in result['checks'] if x['result_id']=='priority_canonical_N'][0]['status']=='INVALID_VALUE'


def test_whole_input_type_validated():
    import pytest
    with pytest.raises(ValueError):compare([1,2],CONTRACT)


def test_partial_example_is_incomplete_not_a_completed_disagreement():
    example=json.loads((ROOT/'tests/fixtures/partial_mismatch.json').read_text())
    result=compare(example, CONTRACT)
    assert result['verdict']=='INCOMPLETE_OR_INVALID'
    assert result['summary']['mismatching_values']==1
    assert result['summary']['missing_values']==12
    assert result['verdict'] != 'NUMERIC_AGREEMENT_ONLY'

def test_reported_precision_does_not_create_false_difference():
    inputs={e['result_id']:e['reported_value'] for e in CONTRACT['required_numerical_checks']}
    inputs['H2_pooled_beta']=-0.00447945
    inputs['H2_pooled_SE']=0.01168788
    result=compare(inputs, CONTRACT)
    assert result['verdict']=='NUMERIC_AGREEMENT_ONLY'
    assert result['summary']['mismatching_values']==0
    assert result['verdict'] == 'NUMERIC_AGREEMENT_ONLY'


def test_extra_numerical_ids_rejected():
    import pytest
    with pytest.raises(ValueError, match='Unknown result IDs'):
        compare({'unexpected_id': 12.0}, CONTRACT)


def test_extra_fields_in_value_object_rejected():
    import pytest
    with pytest.raises(ValueError, match='numeric value field'):
        compare({'H2_pooled_beta': {'value': -0.00448, 'comment': 'extra'}}, CONTRACT)


def test_complete_numerical_agreement_reports_matches():
    data = {e['result_id']: e['reported_value'] for e in CONTRACT['required_numerical_checks']}
    result=compare(data,CONTRACT)
    assert result['verdict']=='NUMERIC_AGREEMENT_ONLY'
    assert result['summary']['matching_values'] == len(CONTRACT['required_numerical_checks'])
