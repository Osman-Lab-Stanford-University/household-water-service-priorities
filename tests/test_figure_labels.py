import json,re,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'code'))
from generate_synthetic_demo import build
def test_figure_label_register_matches_current_manuscript_count():
    d=json.loads((ROOT/'config/figure_label_contract.json').read_text())
    assert len(d['figure_captions'])==13
    assert all('salien' not in value.lower() for value in d['figure_captions'].values())
    assert len([x for x in d['figure_captions'] if x.startswith('Figure S')])==7
def test_current_publication_label_docs_no_legacy_salience():
    for f in [ROOT/'README.md',ROOT/'docs/NUMERICAL_VERIFICATION.md']:
        assert 'salien' not in f.read_text().lower()
def test_synthetic_generator_is_deterministic_and_labeled():
    d1=build();d2=build()
    assert d1.equals(d2)
    assert d1.household_id.str.startswith('SYNTHETIC_').all()
    assert len(d1)==120
