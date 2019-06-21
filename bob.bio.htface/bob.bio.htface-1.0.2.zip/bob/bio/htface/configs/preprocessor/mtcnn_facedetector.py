from bob.bio.htface.preprocessor import FaceDetectMTCNN

# Detects the face amd crops it without eye detection
preprocessor_no_eyes = FaceDetectMTCNN(image_size=(128, 128))
