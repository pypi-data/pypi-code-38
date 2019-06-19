from pys3 import PyS3

if __name__ == '__main__':
    test_url = 's3://drebble-training-output/test.txt'

    file = PyS3(test_url, 'w')

    file.write('Hello!')
    file.close()