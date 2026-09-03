from __future__ import annotations

import numpy as np

from src.datasets.preprocessor import normalize_rows, train_validation_split
from src.datasets.synthetic_generator import SyntheticDataGenerator
from src.training.data_loader import DataLoader


def test_synthetic_generator_outputs_expected_shapes():
    generator = SyntheticDataGenerator(random_state=5)
    matrix = generator.generate_user_audit_matrix(7, 4)
    features, scores = generator.generate_risk_dataset(6, 3)
    assert matrix.shape == (7, 4)
    assert features.shape == (6, 3)
    assert scores.shape == (6,)


def test_preprocessor_normalizes_rows_and_splits_data():
    values = np.array([[1.0, 1.0], [2.0, 0.0], [3.0, 3.0]])
    normalized = normalize_rows(values)
    assert np.allclose(normalized.sum(axis=1), np.ones(3))
    train, validation = train_validation_split(values, validation_fraction=1 / 3)
    assert len(train) == 2
    assert len(validation) == 1


def test_data_loader_reads_saved_npz(tmp_path):
    path = tmp_path / "dataset.npz"
    np.savez(path, X=np.array([[1, 2]]), y=np.array([1]))
    dataset = DataLoader().load_npz(path)
    assert set(dataset) == {"X", "y"}
