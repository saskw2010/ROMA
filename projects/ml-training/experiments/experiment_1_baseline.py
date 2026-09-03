from src.datasets.synthetic_generator import SyntheticDataGenerator
from src.models.risk_predictor import RiskPredictorModel


def run() -> dict:
    generator = SyntheticDataGenerator(random_state=7)
    features, scores = generator.generate_risk_dataset(24)
    model = RiskPredictorModel()
    model.train(features, scores)
    return model.evaluate(features, scores)


if __name__ == "__main__":
    print(run())
