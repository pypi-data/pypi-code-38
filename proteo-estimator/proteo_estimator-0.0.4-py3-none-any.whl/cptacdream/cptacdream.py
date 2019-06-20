import docker


def predict_protein_abundances(
        rna,
        cna,
        output_dir,
        tumor='breast',
        logging=True,
        ):

    image_name = 'proteo_estimator/sub2:{}'.format(tumor)
    print(image_name)
    client = docker.from_env()

    if logging:
        print("Pulling image. This may take a few minutes...")

    client.images.pull(image_name)

    running_container = client.containers.run(
        image_name,
        detach=True,
        volumes={
            rna: {
                'bind': '/rna.txt',
                'mode': 'rw'
            },
            cna: {
                'bind': '/cna.txt',
                'mode': 'rw'
            },
            output_dir: {
                'bind': '/output',
                'mode': 'rw'
            }
        }
    )

    if logging:
        for line in running_container.logs(stream=True):
            print(line.strip())

    prediction_output_f = '{}/prediction.tsv'.format(output_dir)
    confidence_output_f = '{}/confidence.tsv'.format(output_dir)

    return prediction_output_f, confidence_output_f


if __name__ == '__main__':
    _container = predict_protein_abundances(
        tumor='breast',
        rna='/Users/anna/Documents/DREAM_Challenge/hongyang_image_files/sub2_breast_CPTAC_breast/evaluation_data/prospective_breast_RNA_sort_common_gene_15107.txt',
        cna='/Users/anna/Documents/DREAM_Challenge/hongyang_image_files/sub2_breast_CPTAC_breast/evaluation_data/prospective_breast_CNA_sort_common_gene_16884.txt',
        output_dir='/Users/anna/PycharmProjects/proteo_estimator/tests/output',
        logging=True
        )
    print(_container)
