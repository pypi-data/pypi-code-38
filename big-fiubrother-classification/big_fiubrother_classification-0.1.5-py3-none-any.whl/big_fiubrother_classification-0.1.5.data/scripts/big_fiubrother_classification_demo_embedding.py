#!python

from big_fiubrother_classification.face_embedder_factory import FaceEmbedderFactory
import sys
import os

if __name__ == '__main__':

    if len(sys.argv) < 3:

        print("--------------------------------")
        print("This script receives a pretrained model and a list of prealigned images and calculates embeddings for each")
        print("")
        print("Usage: ")
        print("python big_fiubrother_classification_demo_embedding.py ['mvds_facenet' | 'tf_facenet'] 'image_path1' 'image_path2' ... ")
        print("--------------------------------")

    else:

        # Create Face embedder
        face_embedder_type = sys.argv[1]
        if face_embedder_type == "mvds_facenet":
            face_embedder_object = FaceEmbedderFactory.build_mvds_facenet()
        elif face_embedder_type == "tf_facenet":
            face_embedder_object = FaceEmbedderFactory.build_tensorflow_facenet()
        else:
            print("ERROR: Invalid face detector type")

        output_folder_base = "output"
        if not os.path.exists(output_folder_base):
            os.mkdir(output_folder_base)
        output_folder = output_folder_base + "/" + face_embedder_type
        if not os.path.exists(output_folder):
            os.mkdir(output_folder)

        # Get Face Embeddings
        image_paths = sys.argv[2:]
        output_csv = open("output/" + face_embedder_type + "/embeddings.txt", "w")
        print("Length: " + str(len(image_paths)))
        for i in range(len(image_paths)):
            image_path = image_paths[i]
            emb = face_embedder_object.get_embedding(image_path)

            # Save embeddings to csv file in output folder
            filename = os.path.basename(image_path)
            emb_csv = ','.join(['%.8f' % num for num in emb])
            line = filename + "," + emb_csv + "\n"
            output_csv.write(line)
        output_csv.close()

        # Close face embedder
        face_embedder_object.close()
