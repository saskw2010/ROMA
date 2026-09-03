from src.datasets.synthetic_generator import SyntheticDataGenerator
from src.models.hybrid import HybridRecommendationModel


def run() -> dict:
    generator = SyntheticDataGenerator(random_state=3)
    matrix = generator.generate_user_audit_matrix(12, 8)
    features = generator.generate_item_features(8, 4)
    targets = matrix.mean(axis=0)
    model = HybridRecommendationModel()
    model.train({"collaborative": matrix, "content": features}, {"collaborative": matrix, "content": targets})
    return {"scores_shape": list(model.predict({"collaborative": matrix, "content": features}).shape)}


if __name__ == "__main__":
    print(run())
