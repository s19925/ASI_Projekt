import sys

sys.path.append("src/pjatk_asi_project")

from kedro.pipeline import Pipeline, node

from processing.processing import load_and_truncate_data, drop_null_data


def processing_pipeline(**kwargs):
    return Pipeline(
        [
            node(
                func=load_and_truncate_data,
                inputs=["input_data", "params:input_param"],
                outputs="intermediate_data",
                name="load_and_truncate_data",
            ),
            node(
                func=drop_null_data,
                inputs="intermediate_data",
                outputs="primary_Data",
                name="drop_null_data",
            ),

        ]
    )