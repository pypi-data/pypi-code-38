import cv2
import boto3

def get_matches(method, img1, img2):
    # Default CV Algo, if none is passed
    cv_algo = cv2.BRISK_create()

    # Initiate detector
    if method == 'ORB':
        cv_algo = cv2.ORB_create()
    elif method == 'BRISK':
        cv_algo = cv2.BRISK_create()
    elif method == 'AKAZE':
        cv_algo = cv2.AKAZE_create()

    # find the keypoints and descriptors with SIFT
    kp1, des1 = cv_algo.detectAndCompute(img1,None)
    kp2, des2 = cv_algo.detectAndCompute(img2,None)

    # create BFMatcher object
    bf = cv2.BFMatcher()

    # Match descriptors.
    #matches = bf.match(des1,des2)
    matches = bf.knnMatch(des1,des2, k=2)

    return matches, kp1, kp2

def find_good_matches_ratio(matches, lowe_ratio, method, img1, img2, kp1, kp2):
    # Apply ratio test
    good = []

    for m,n in matches:
        if m.distance < lowe_ratio * n.distance:
            good.append([m])

    msg1 = 'using %s with lowe_ratio %.2f' % (method, lowe_ratio)
    msg2 = 'there are %d good matches' % (len(good))

    return msg1, msg2

def apply_cv_algo(method, lowe_ratio, img1, img2):
    matches, kp1, kp2 = get_matches(method, img1, img2)
    msg1, msg2 = find_good_matches_ratio(matches, lowe_ratio, method, img1, img2, kp1, kp2)
    return msg1, msg2

def calculate_match_ratio(first_file_name, second_file_name):
    lowe_ratio = 0.89
    method = 'ORB'
    bucket_name = "fake-invoices-hackathon-jun12"

    s3_resource = boto3.resource('s3')
    first_file = s3_resource.Object(bucket_name, first_file_name).download_file(f'/tmp/{first_file_name}')
    second_file = s3_resource.Object(bucket_name, second_file_name).download_file(f'/tmp/{second_file_name}')

    decoded_document_image = cv2.imread(first_file)
    decoded_bad_invoice_image = cv2.imread(second_file)
    return apply_cv_algo(method, lowe_ratio, decoded_document_image, decoded_bad_invoice_image)

def lambda_handler():
    response = calculate_match_ratio('invoicegenerator.png', 'chinese.jpg')
    return {
        'statusCode': 200,
        'body': response
    }