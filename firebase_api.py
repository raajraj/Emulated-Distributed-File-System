from flask import Blueprint, render_template, jsonify, request
from importlib.resources import path
import requests
import re
import json
import pandas as pd

from multiprocessing import Pool
from itertools import repeat


FIREBASE_API_BASE = "/firebase"
firebase_api = Blueprint('firebase', __name__,
                        template_folder='templates')


base_url = 'https://dsci-project-28e72-default-rtdb.firebaseio.com'
dir_base_url = 'https://dsci-project-28e72-default-rtdb.firebaseio.com/Dir'
files_base_url = 'https://dsci-project-28e72-default-rtdb.firebaseio.com/Files'
store_base_url = 'https://dsci-project-28e72-default-rtdb.firebaseio.com/Store'
base_end = '/.json'
store_file_end = '.json'
base_prefix = '/root/children/'


placeholder = dict()
placeholder["content"] = ['.']
placeholder["children"] = {}



filestore = dict()
filestore['sars'] = "/admin/protected/sarsdata"
filestore['ebola'] = "/admin/protected/eboladata"
filestore['covid'] = "/admin/protected/coviddata"



def strip_punc(item):
    result = re.sub(r'''[!"#$%&'()*+, -./:;<=>?@[\]^_`{|}~]+\ *''', " ", item)
    return result


def path_to_json_string(path: str):
    pass


def verify_mkdir(url: str):
    get_req = requests.get(url)
    data = None
    if (get_req.status_code == 200):
        data = get_req.json()
        # print(data)
    else:
        print('Conn error!!')
    # print(data)
    if data == None:
        print('No preexisting repo here')
        return True
    else:
        print('Existing Data here')
        return False
    # return False if data == None else True


def path_preprocess(path: str):
    path = path[1:]
    path = path.replace('/', '/children/')
    return path


def fetch_files(path_parts, filename: str):
    #print("Path Parts before ::~~")
    # print(path_parts)
    if filename in path_parts:
        path_parts = path_parts[:path_parts.index(filename)]
        # remove the last 'children' from the path
        path_parts = path_parts[:-10]
    # make a get requerst to get a list of files
    #print("Path Parts final ::~~")
    # print(path_parts)
    path_parts_url = dir_base_url + base_prefix+path_parts+base_end
    req = requests.get(path_parts_url)
    data = None
    if (req.status_code == 200):
        data = req.json()
        # print(data)
    return data, path_parts_url


def delete(url):
    print(url)
    req = requests.delete(url)
    if (req.status_code == 200):
        print(req.json())
        return req.json()
    else:
        print('Error~!!')
        return None


def patch(url, filename, data):
    req = requests.patch(url, data=json.dumps(data))
    if (req.status_code == 200):
        # print(req.json())
        return req.json()
    else:
        print('Error~!!')
        return None


def read(filepath: str):
    # TODO reading from form logic
    data = pd.read_csv(filepath)
    records = []
    for i in data.index:
        records.append(data.iloc[i].to_json())
    return records


def insert_file_name_in_dir(file, path: str):
    path_parts = path_preprocess(path)
    filename = file
    # print(path_parts)
    # print(filename)
    data, url_update = fetch_files(path_parts, filename)
    #print("INSIDE INSERT FN func::")
    # print(data)
    if 'content' in data.keys():
        print('Content found in file')
        # print(data['content'])
        # TODO handle case of '.'
        # add our filename
        if filename in data['content']:
            print("FILE ALREADY EXISTS!!")
            return
        data['content'].append(filename)
    else:
        print('No content child found')
        # create child node
        data['content'] = [filename]
    patch(url_update, filename, data)


def insert_file_partition_names_in_meta(file_parts: list, dirpath: str, filename: str):
    parts = []
    for idx in range(len(file_parts)):
        name = filename.split('.')[0]+'_'+str(idx+1)
        parts.append(name)
    # print(parts)
    files_parts_url = files_base_url+base_end
    payload = dict()
    # verify if it exists or not
    # print(dirpath)
    payload[dirpath] = parts
    # print(files_parts_url)
    res = patch(files_parts_url, "test", data=payload)
    if res != None:
        return parts


def store_parts(file_parts: list, dirpath: str, filename: str):
    parts = []
    dirpath = dirpath.replace('/', '_-_')
    path = store_base_url + '/' + base_end
    for index, file in enumerate(file_parts):
        # verify if it exists or not first
        name = filename.split('.')[0]+'_'+str(index+1)
        name = dirpath+'_-_'+name
        data = dict()
        data[name] = file_parts[index]
        res = patch(path, dirpath, data=data)


def getParts(filename, dirpath):
    files_parts_url = files_base_url+dirpath + \
        '/'+stripFileName(filename)+base_end
    # print(files_parts_url)
    get_req = requests.get(files_parts_url)
    #print("PRINTING FROM GET PARTS")
    # print(get_req.json())
    return get_req.json()


def generateLocs(dirPath, partNames):
    result = dict()
    for name in partNames:
        result[name] = 'Store' + dirPath + '/' + name
    # print(result)
    return result


def stripFileName(file):
    return file.split('/')[-1].split('.')[0]


@firebase_api.route(f"{FIREBASE_API_BASE}/mkdir")
def mkdir():
    path = request.args.get('path')
    # expect input /user/pappu/dhundho
    path = path_preprocess(path)
    url = dir_base_url + base_prefix + path + base_end
    # must first check if the path already exists or not
    print(url)
    print(placeholder)
    if (verify_mkdir(url)):
        req = requests.patch(url, data=json.dumps(placeholder))
        if (req.status_code == 200):
            print(req.json())
            return json.dumps({"status": "directory created successfully!"})
            # return req.json()
        else:
            return req.json()
    else:
        print("mkdir: cannot create directory: File exists")
        return json.dumps({"status": "error: directory already exists"})


@firebase_api.route(f"{FIREBASE_API_BASE}/ls")
# def ls(path):
def ls():
    path = request.args.get('path')
    path = path_preprocess(path)
    url = dir_base_url + base_prefix + path + base_end
    data = None
    get_req = requests.get(url)
    result = dict()
    # print(url)
    if (get_req.status_code == 200):
        data = get_req.json()
        if "children" in data:
            # print(data['children'])
            result['directories'] = list(data['children'].keys())
        if 'content' in data:
            result['files'] = data['content']
        else:
            print('No children found for directory::'+path)
    else:
        print('No such directory exists')
        return json.dumps({"status": "error: directory doesn't exist"})
    # print(result)
    if result == None:
        return json.dumps({"status": "error: No Such file or part"})
    return json.dumps(result)


def lslocal(path):
    path = path_preprocess(path)
    url = dir_base_url + base_prefix + path + base_end
    data = None
    get_req = requests.get(url)
    result = dict()
    #print(url)
    if(get_req.status_code == 200):
        data = get_req.json()
        if "children" in data:
            #print(data['children'])
            result['directories'] = list(data['children'].keys())
        if 'content' in data:
                result['files'] = data['content']
        else:
            print('No children found for directory::'+path)
    else:
        print('No such directory exists')
    #print(result)
    return result


@firebase_api.route(f"{FIREBASE_API_BASE}/put", methods=["POST"])
# def put(filepath, dirpath,numpart):
def put():
    filedata = request.files.get('file')
    filepath = filedata.filename
    dirpath = request.form.get('dirpath')
    numpart = request.form.get('numpart')
    numpart = int(numpart)
    # assuming i get file from filepath
    data = read(filedata)
    #print('TOTAL FILE SIZE ::'+str(len(data)))
    part_size = int(len(data)/int(numpart))
    #print('PART SIZE::'+str(part_size))
    files = []
    for idx in range(numpart):
        # print(idx)
        start = idx * part_size
        stop = start + part_size
        if idx == numpart-1:
            stop = len(data)
        #print('START IDX ::'+str(start))
        #print('STOP IDX ::'+str(stop))
        files.append(json.dumps(data[start: stop]))
    # print(len(files))
    # first update the file .i.e add the filename to the directory
    #   3 places
    #   1. Dir structure for full filename
    #   2. Files Struct for part names and path
    #   3. Actual store
    #   1. Dir structure for full filename
    try:
        insert_file_name_in_dir(filepath, dirpath)
        #   2. Files Struct for part names and path
        parts = insert_file_partition_names_in_meta(
            files, dirpath+'/'+stripFileName(filepath), filepath)
        #   3. Actual store
        store_parts(files, dirpath, filepath)
        return json.dumps({"status": "OK"})
    except:
        return json.dumps({"status": "error occurred!"})


@firebase_api.route(f"{FIREBASE_API_BASE}/getpartitionLocations")
def getPartitionLocations():
    file = request.args.get('file')
    filename = file.split('/')[-1].split('.')[0]
    dirPath = file.removesuffix('/'+filename+'.csv')
    # print(dirPath)
    data = lslocal(dirPath)
    # print(data)
    locs = None
    if "files" in data and filename+'.csv' in data['files']:
        # now return the partitions
        partsNames = getParts(filename, dirPath)
        locs = generateLocs(dirPath, partsNames)
    return jsonify(locs)


@firebase_api.route(f"{FIREBASE_API_BASE}/readPartition")
def readPartition():
    file = request.args.get('file')
    partNumber = request.args.get('partNumber')
    locs = getPartitionLocationsLocal(file)
    print(locs)
    filename = file.split('/')[-1].split('.')[0]
    dirPath = file.removesuffix(filename+'.csv')
    dirPath = dirPath.replace('/', '_-_')
    path = store_base_url + '/'+dirPath + \
        filename + '_' + str(partNumber) + base_end
    # print(dirPath)
    print(path)
    get_req = requests.get(path)
    print(get_req.json())
    return get_req.json()


def readPartitionLocal(file, partNumber):
    locs = getPartitionLocationsLocal(file)
    print(locs)
    filename = file.split('/')[-1].split('.')[0]
    dirPath = file.removesuffix(filename+'.csv')
    dirPath = dirPath.replace('/', '_-_')
    path = store_base_url + '/'+dirPath + \
        filename + '_' + str(partNumber) + base_end
    # print(dirPath)
    print(path)
    get_req = requests.get(path)
    print(get_req.json())
    return get_req.json()


@firebase_api.route(f"{FIREBASE_API_BASE}/cat")
def cat():
    file = request.args.get('file')
    filename = file.split('/')[-1].split('.')[0]
    dirPath = file.removesuffix(filename+'.csv')
    locs = getPartitionLocationsLocal(file)
    res = []
    for idx in range(len(locs)):
        res.append(json.loads(readPartitionLocal(file, idx+1)))
    flat_list = [item for sublist in res for item in sublist]
    print(''.join(flat_list))
    if flat_list == None or len(flat_list) == 0:
        return json.dumps({"status": "error reading file"})
    return flat_list


def getPartitionLocationsLocal(file):
    filename = file.split('/')[-1].split('.')[0]
    dirPath = file.removesuffix('/'+filename+'.csv')
    # print(dirPath)
    data = lslocal(dirPath)
    # print(data)
    locs = None
    if "files" in data and filename+'.csv' in data['files']:
        # now return the partitions
        partsNames = getParts(filename, dirPath)
        locs = generateLocs(dirPath, partsNames)
    return locs


@firebase_api.route(f"{FIREBASE_API_BASE}/rm")
# def rm(path:str):
def rm():
    path = request.args.get('path')
    # 2 parts
    # 1st remove file from list in directory
    path_parts = path_preprocess(path)
    filename = path_parts.split('/')[-1]
    # print(filename)
    data, url_update = fetch_files(path_parts, filename)
    if 'content' in data.keys():
        print('Content found in file')
        print(data['content'])
        # preexisting list just remove the current data
        data['content'].remove(filename)
        print(data['content'])
        # now push the updated list to the db
        # call delete func to remove actual file parts as well!!!!
        locs = getPartitionLocationsLocal(path)
        patch(url_update,filename,data)
        print(locs)
        filename = path.split('/')[-1].split('.')[0]

        delete(files_base_url+path.removesuffix('.csv')+store_file_end)
        # removed from files list
        # now remove from store
        #dirPath = dirPath.replace('/', '_-_')
        # print(dirPath)
        for item in locs:
            p = locs[item].split('/')[1:]
            p = "/".join(p)
            p = p.replace('/', '_-_')
            p = "_-_"+p
            print(p)
            delete(store_base_url+"/"+p+store_file_end)
    else:
        print('No content child found')
        return json.dumps({"status": "error: no record found"})
    return json.dumps({"status": "OK"})


def catLocal(file):
    filename = file.split('/')[-1].split('.')[0]
    dirPath = file.removesuffix(filename+'.csv')
    locs = getPartitionLocationsLocal(file)
    res = []
    for idx in range(len(locs)):
        res.append(json.loads(readPartitionLocal(file, idx+1)))
    flat_list = [item for sublist in res for item in sublist]
    # print(''.join(flat_list))
    if flat_list == None or len(flat_list) == 0:
        return json.dumps({"status": "error reading file"})
    return flat_list


def mkdirLocal(path):
    # expect input /user/pappu/dhundho
    path = path_preprocess(path)
    url = dir_base_url + base_prefix + path + base_end
    # must first check if the path already exists or not
    # print(url)
    # print(placeholder)
    if (verify_mkdir(url)):
        req = requests.patch(url, data=json.dumps(placeholder))
        if (req.status_code == 200):
            print(req.json())
            return req.json()
        else:
            return req.json()
    else:
        print("mkdir: cannot create directory: File exists")
        return json.dumps({"status": "error: directory already exists"})


def putLocal(filepath, dirpath, numpart):
    numpart = int(numpart)
    # assuming i get file from filepath
    data = read(filepath)
    #print('TOTAL FILE SIZE ::'+str(len(data)))
    part_size = int(len(data)/int(numpart))
    #print('PART SIZE::'+str(part_size))
    files = []
    for idx in range(numpart):
        # print(idx)
        start = idx * part_size
        stop = start + part_size
        if idx == numpart-1:
            stop = len(data)
        # print('START IDX ::'+str(start))
        # print('STOP IDX ::'+str(stop))
        files.append(json.dumps(data[start: stop]))
    # print(len(files))
    # first update the file .i.e add the filename to the directory
    #   3 places
    #   1. Dir structure for full filename
    #   2. Files Struct for part names and path
    #   3. Actual store
    #   1. Dir structure for full filename
    try:
        insert_file_name_in_dir(filepath, dirpath)
        #   2. Files Struct for part names and path
        parts = insert_file_partition_names_in_meta(
            files, dirpath+'/'+stripFileName(filepath), filepath)
        #   3. Actual store
        store_parts(files, dirpath, filepath)
        return json.dumps({"status": "OK"})
    except:
        return json.dumps({"status": "error occurred!"})


@firebase_api.route(f'{FIREBASE_API_BASE}/countrydeathcount')
def numDeathsbyCountry():
    file = request.args.get('dataset')
    country = request.args.get('country')
    path = filestore[file]
    # prepare datasets
    mkdirLocal(path)
    putLocal(file+'.csv', path, 4)
    locs = getPartitionLocationsLocal(path+"/"+file+'.csv')
    res = []
    params1 = []
    params2 = []
    for idx in range(len(locs)):
        params1.append(file+"#3#"+str(idx+1))
        params2.append("process#"+str(idx+1))
    # now multithread the application
    # print(params1)
    with Pool() as pool:
        mapper_results = pool.starmap(mapperQ1, zip(params1, repeat(country)))

    reducer_res = reducerQ1(mapper_results)
    # print("!@@@@@@@@@@@@@@@@@@@@@@@@@!!!!!")
    # print("Here are the results")
    # print(len(mapper_results))
    # print(type(mapper_results))
    final_result = dict()
    mapper_results = [
        x.to_json() if not x.empty else "{}" for x in mapper_results]
    final_result["mapper"] = mapper_results
    final_result["reducer"] = reducer_res.to_json()
    final_result = json.dumps(final_result)
    # print(final_result)
    return final_result


def read_data_for_querying(file):
    filename = file.split("#3#")[0]
    part_number = file.split("#3#")[1]
    path = filestore[filename]
    data = readPartitionLocal(path+"/"+filename+".csv", part_number)
    # print("*****************DATALENS*************")
    data = json.loads(data)
    # print(len(data))
    # print(type(data[1]))
    df = pd.DataFrame()
    for item in data:
        curr = json.loads(item)
        # print(type(curr))
        # print(curr)
        curr = pd.DataFrame([curr])
        df = pd.concat([df, curr])
    return df


def mapperQ1(file, country):
    # Steps
    # 1. read partition info
    df = read_data_for_querying(file)
    # print(df.head())
    #   2. filter dataframe based on country
    res = df[df['Country'].str.lower() == country.lower(
    )][['Country', 'No. of deaths', 'Cumulative total cases']]
    # print(res)

    #   4. return value back
    #
    return res


def reducerQ1(result):
    res = pd.concat(result).groupby(['Country']).sum().reset_index()
    # print("!@#)(@!()#*!@()#*@!+#(@*!#+!@#")
    # print(res)
    # print("!PO@#U@!)(#*+@!#*@!(#+")
    return res


@firebase_api.route(f'{FIREBASE_API_BASE}/findcountriesbetween')
def findCountriesWithDeathCount():
    file = request.args.get('dataset')
    limit1 = request.args.get('limit1')
    limit1 = int(limit1)
    limit2 = request.args.get('limit2')
    limit2 = int(limit2)
    # file = "sars"
    path = filestore[file]
    # prepare datasets
    mkdirLocal(path)
    putLocal(file+'.csv', path, 4)
    locs = getPartitionLocationsLocal(path+"/"+file+'.csv')
    res = []
    params1 = []
    params2 = []
    for idx in range(len(locs)):
        params1.append(file+"#3#"+str(idx+1))
        params2.append("process#"+str(idx+1))
    # now multithread the application
    # print(params1)
    with Pool() as pool:
        mapper_results = pool.starmap(mapperQ2, zip(
            params1, repeat(limit1), repeat(limit2)))

    reducer_res = reducerQ2(mapper_results)
    # print("!@@@@@@@@@@@@@@@@@@@@@@@@@!!!!!")
    # print("Here are the results")
    # print(len(mapper_results))
    # print(type(mapper_results))
    final_result = dict()
    for item in mapper_results:
        item.reset_index(inplace=True)
    mapper_results = [
        x.to_json() if not x.empty else "{}" for x in mapper_results]
    final_result["mapper"] = mapper_results
    final_result["reducer"] = reducer_res.to_json()
    final_result = json.dumps(final_result)
    # print(final_result)
    return final_result


def mapperQ2(file, limit1, limit2):
    # Steps
    # 1. read partition info
    df = read_data_for_querying(file)
    # print(df.head())
    #   2. filter dataframe based on country
    res = df[(df['No. of deaths'] >= limit1) & (df['No. of deaths'] <= limit2)]
    if not res.empty:
        res = res[['Country', 'No. of deaths']]
    # print(res)

    #   4. return value back
    #
    return res


def reducerQ2(result):
    res = pd.concat(result).groupby(['Country']).sum().reset_index()
    # print("!@#)(@!()#*!@()#*@!+#(@*!#+!@#")
    # print(res)
    # print("!PO@#U@!)(#*+@!#*@!(#+")
    return res


@firebase_api.route(f'{FIREBASE_API_BASE}/analysisdeathpercountry')
def numdethpercountry():
    # file =  request.args.get('filename')
    files = ["sars", "ebola", "covid"]
    final_result = dict()
    final_result['mapper'] = {}
    final_result['reducer'] = {}
    for file in files:
        path = filestore[file]
        # prepare datasets
        mkdirLocal(path)
        putLocal(file+'.csv', path, 4)
        locs = getPartitionLocationsLocal(path+"/"+file+'.csv')
        res = []
        params1 = []
        params2 = []
        for idx in range(len(locs)):
            params1.append(file+"#3#"+str(idx+1))
            params2.append("process#"+str(idx+1))
        # now multithread the application
        # print(params1)
        with Pool() as pool:
            mapper_results = pool.starmap(mapperQ3, zip(params1))

        reducer_res = reducerQ3(mapper_results)
        # print("!@@@@@@@@@@@@@@@@@@@@@@@@@!!!!!")
        # print("Here are the results")
        # print(len(mapper_results))
        # print(type(mapper_results))

        for item in mapper_results:
            item.reset_index(inplace=True)
        mapper_results = [
            x.to_json() if not x.empty else "{}" for x in mapper_results]
        final_result["mapper"][file] = mapper_results
        final_result["reducer"][file] = reducer_res.to_json()

    final_result = json.dumps(final_result)
    # print(final_result)
    return final_result


def mapperQ3(file):
    # Steps
    # 1. read partition info
    df = read_data_for_querying(file)
    # print(df.head())
    #   2. filter dataframe based on country
    res = df
    if not res.empty:
        res = res.groupby(['Country']).sum().reset_index()[
            ['Country', 'No. of deaths']]
    # print(res)
    #   4. return value back
    #
    return res


def reducerQ3(result):
    res = pd.concat(result).groupby(['Country']).sum().reset_index()
    # print("!@#)(@!()#*!@()#*@!+#(@*!#+!@#")
    # print(res)
    # print("!PO@#U@!)(#*+@!#*@!(#+")
    return res


@firebase_api.route(f'{FIREBASE_API_BASE}/analysisrecovery')
def numpeoplerecovered():
    # file =  request.args.get('filename')
    files = ["sars", "ebola", "covid"]
    final_result = dict()
    final_result['mapper'] = {}
    final_result['reducer'] = {}
    final_fnal_result = dict()
    for file in files:
        path = filestore[file]
        # prepare datasets
        mkdirLocal(path)
        putLocal(file+'.csv', path, 4)
        locs = getPartitionLocationsLocal(path+"/"+file+'.csv')
        res = []
        params1 = []
        params2 = []
        for idx in range(len(locs)):
            params1.append(file+"#3#"+str(idx+1))
            params2.append("process#"+str(idx+1))
        # now multithread the application
        # print(params1)
        with Pool() as pool:
            mapper_results = pool.starmap(mapperQ4, zip(params1))

        reducer_res = reducerQ4(file, mapper_results)
        # print("!@@@@@@@@@@@@@@@@@@@@@@@@@!!!!!")
        # print("Here are the results")
        # print()
        # print(type(mapper_results))
        final_result["mapper"][file] = [x for x in mapper_results]
        final_result["reducer"][file] = reducer_res
    # print(final_result)
    final_result = json.dumps(final_result)
    # print(final_result)
    return final_result


def mapperQ4(file):
    # Steps
    # 1. read partition info
    df = read_data_for_querying(file)
    # print(df.head())
    #   2. filter dataframe based on country
    res = df
    if not res.empty:
        res['data'] = df['Cumulative total cases']-df['No. of deaths']

    total = res['data'].sum()
    totalcases = res['Cumulative total cases'].sum()
    # print(total)
    # print(totalcases)
    #   4. return value back
    #
    return (int(totalcases), int(total))


def reducerQ4(file, result):
    res = sum(i for i, j in result)
    totres = sum(j for i, j in result)
    # print("!@#)(@!()#*!@()#*@!+#(@*!#+!@#")
    # print(res)
    # print("!PO@#U@!)(#*+@!#*@!(#+")
    # print(totres)
    return (int(totres), int(res))
