import sys

sys.path.append("src/kedro_test")

from kedro.pipeline import Pipeline, node

from trainModel.train import prepare_data_for_modeling
from trainModel.train import split_data
from trainModel.train import train_model
from trainModel.train import evaluate_model

def train_pipeline(**kwargs):
    return Pipeline(
        [
            node(
                func= prepare_data_for_modeling,
                inputs=["primary_data", "params:primary_param"],
                outputs="prepare_data_for_modeling",
                name="prepare_data_for_modeling",
            ),
            node(
                func=split_data,
                inputs="prepare_data_for_modeling",
                outputs=["X_train", "X_test", "y_train", "y_test"],
                name="split_data",
            ),
            node(
                func=train_model,
                inputs=['X_train', 'y_train'],
                outputs="classifier",
                name="train_model",
            ),
            node(
                func=evaluate_model,
                inputs=['classifier', 'X_test', 'y_test'],
                outputs=None,
                name="evaluate_model",
            ),
        ]
    )