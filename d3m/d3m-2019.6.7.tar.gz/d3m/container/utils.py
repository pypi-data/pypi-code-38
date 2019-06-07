import os
import json
import typing

from d3m import container as container_module, exceptions, utils


def save_container(container: typing.Any, output_dir: str) -> None:
    # Saving data.
    if isinstance(container, container_module.Dataset):
        # Dataset saver creates any missing directories.
        dataset_uri = 'file://{dataset_path}'.format(dataset_path=os.path.join(output_dir, 'datasetDoc.json'))
        container.save(dataset_uri)
    else:
        # We do not want to override anything.
        os.makedirs(output_dir, exist_ok=False)
        dataframe_path = os.path.join(output_dir, 'data.csv')

        if isinstance(container, container_module.DataFrame):
            container.to_csv(dataframe_path)
        elif isinstance(container, (container_module.List, container_module.ndarray)):
            container = container_module.DataFrame(container)
            container.to_csv(dataframe_path)
        else:
            raise exceptions.NotSupportedError("Value with type '{value_type}' cannot be saved as a container type.".format(value_type=type(container)))

    # Saving metadata.
    input_metadata = container.metadata.to_json_structure()
    metadata_path = os.path.join(output_dir, 'metadata.json')

    with open(metadata_path, 'w') as outfile:
        json.dump(input_metadata, outfile, indent=2, sort_keys=True, allow_nan=False)
