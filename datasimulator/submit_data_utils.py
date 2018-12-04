
import os
from os.path import join
import requests
import json


def submit_test_data(host, project,  dir, access_token_file, max_chunk_size=1):

    api_endpoint = host + '/api/v0/submission/' + project

    token = ''
    if os.path.isfile(access_token_file):
        with open(access_token_file, 'r') as reader:
            token = reader.read()
        token = token[:-1]
    else:
        print('There is no input token text file. Continue anyway!')

    submission_order = ''
    if(os.path.isfile(join(dir, 'DataImportOrder.txt'))):
        with open(join(dir, 'DataImportOrder.txt'), 'r') as reader:
            submission_order = reader.read()
    else:
        print('There is no DataImportOrder.txt file!')
        return

    submission_order = submission_order.split('\n')

    for fname in (submission_order):
        chunk_size = max_chunk_size
        if fname is None or fname == '':
            print('There is no {} in input directory'.format(fname))
            continue
        with open(join(dir, fname+".json"), 'r') as rfile:
            data = json.loads(rfile.read())
            index = 0
            while index < len(data):
                response = requests.put(api_endpoint, data=json.dumps(list(data[index:min(index+chunk_size, len(data))])), headers={
                                        'content-type': 'application/json', 'Authorization': 'bearer ' + token})
                if response.status_code == 504:
                    chunk_size = chunk_size/2
                    print("Reduce the chunk size by half. {}".format(chunk_size))
                    if chunk_size == 0:
                        break
                    continue

                elif response.status_code != 200:
                    print(
                        "\n\n==============================={}=================================".format(fname))
                    print('Failed at chunk {}'.format(index/chunk_size))
                    if index == 0:
                        print response.content
                    print response.status_code

                index = index + chunk_size
            print('Done submitting {}'.format(fname))
