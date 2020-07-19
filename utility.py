from datetime import datetime
import os
import pickle
import glob
import pandas as pd

# store temporary intermediary file.. there will be 3 folder in file_processed folder 10,227,300 and each will have 54 file
def store_pickle(anObj):
    actual_name = os.path.basename(anObj.file_path)
    only_name = os.path.splitext(actual_name)[0]
    processed_file_name = "./file_processed/"
    if anObj.interval == 10:
        processed_file_name += '10'
    if anObj.interval == 227:
        processed_file_name += '227'
    if anObj.interval == 300:
        processed_file_name += '300'

    processed_file_name += '/'
    final_processed_name = processed_file_name + only_name
    f = open(final_processed_name, 'wb')
    pickle.dump(anObj, f)
    f.flush()
    f.close()

# get file names from a given file path for eg ./file_processed/d39bjs.xlsx the function returns 'd39bjs'
def get_file_names(files_paths):
    file_names = []
    for aPath in files_paths:
        actual_name = os.path.basename(aPath)
        name = os.path.splitext(actual_name)[0]
        file_names.append(name)
    return file_names.copy()

# get file name from a given path
def get_name_from_path(aPath):
    actual_name = os.path.basename(aPath)
    name = os.path.splitext(actual_name)[0]
    return name

# in case to generate tables in html page
def generate_html_tables(table_data, interval, PAverage):
    path = './tables/table_'+str(interval)+'.html'
    windows = '<h2>Time Window: '+ str(interval)+'</h2>'
    weeks1 = '<h3>Week 1: 2/4/2013 - 2/8/2013</h3>'
    weeks2 = '<h3>Week 2: 2/11/2013 - 2/15/2013</h3>'
    PAvg = '<h3> Average of P-Value > 0.05 ::  '+str(PAverage)
    f = open(path,'w')
    table_data = windows + weeks1 + weeks2 + PAvg+ table_data
    f.write(table_data)
    f.flush()
    f.close()
    print(f"File {path} successfully created.")

# generates a csv file from a datafram
def generate_final_csv(df,interval,PAverage = 0):
    path = './tables/table_' + str(interval) + '.csv'
    df.to_csv(path)

# generates a csv file :
# Params:: Table: 2D data table, index: rows names list, column: column name list, file_name: name of csv file, interval: current window(eg 10,227,500)
def generate_csv(table, index, column, location, file_name, interval):
    file_path = location + str(interval) +'/'
    if not os.path.exists(file_path):
        os.makedirs(file_path)
    final_path = file_path + file_name
    df = pd.DataFrame(table, index=index, columns=column)
    df.to_csv(final_path)
    print(f"file {final_path} created successfully at {datetime.now()} ")

# Used to get a user a week data in a 1D list
def get_data_column(week_data):
    lst = []
    for aDay in range(len(week_data)):  # there are 6 days
        for aSlot in range(len(week_data[aDay])):  # aDay may have # of slots or window
            if week_data[aDay][aSlot]:
                lst.append(week_data[aDay][aSlot])
            else:
                lst.append(0.0001)
    return lst.copy()

def get_pickle(file_name):
    f = open(file_name,'rb')
    anObj = pickle.load(f)
    f.close()
    return anObj

def cleanup_folders(path):
    files10 = glob.glob(path+'/10/*')
    for f in files10:
        os.remove(f)
    files227 = glob.glob(path + '/227/*')
    for f in files227:
        os.remove(f)
    files300 = glob.glob(path + '/300/*')
    for f in files300:
        os.remove(f)

def write_temp_csv(lst,filename):
    temp = []
    for a in lst:
        temp.append([a])
    df = pd.DataFrame(temp)
    df.to_csv('./temp/'+filename+'.csv')