from src.datasets.synthetic_generator import SyntheticDataGenerator
from src.models.collaborative_filtering import CollaborativeFilteringModel


def run() -> dict:
    generator = SyntheticDataGenerator(random_state=11)
    matrix = generator.generate_user_audit_matrix(16, 10)
    model = CollaborativeFilteringModel(n_components=3)
    model.train(matrix, matrix)
    return model.evaluate(matrix, matrix)


if __name__ == "__main__":
    print(run())
