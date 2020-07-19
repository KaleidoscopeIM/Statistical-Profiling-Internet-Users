from computation import *
from storage import *
from utility import *
import glob
import time

files_lst = glob.glob('./files/*.xlsx')
intervals = [10, 227, 300]  # interval of 10 second, 227 second and 5 minute
# this step is basically to create intermediary files for 3 windows
def execute_step1(clean_processed_files = True):
    if clean_processed_files:  # if yes then all intermediary files will be deleted if previously created
        cleanup_folders('./file_processed')
    print(files_lst)
    for aFile in files_lst:
        df = pd.read_excel(aFile, usecols=['doctets', 'Real First Packet', 'Duration'])   # r1 r2 r3
        df = df[df['Duration'] > 0]
        interval_objs = []  # 3 objects for 3 intervals
        for i in range(3):
            interval_objs.append(Storage(intervals[i], aFile))
        for aIntervalObj in interval_objs:
            for r in df.itertuples():
                doctets = r[1]
                duration = r[3]/1000 # to convert milli second into seconds
                real_first_packet = datetime.fromtimestamp(r[2]/1000)  # convert in milli second and then in datetime string
                aIntervalObj.store_in_slot(real_first_packet, doctets, duration)
            # aIntervalObj.print_windows()
            average_oct_per_duration(aIntervalObj, perform_slicing=True) # slicing will carry forward doctets value if it duration is larger then current window size
            # aIntervalObj.print_windows()
            store_pickle(aIntervalObj) # create intermediary files
        print(f"_______  file: {aFile}  complete at {datetime.now()}_______ processing: {files_lst.index(aFile)+1} out of {len(files_lst)}")
        
# this is calculation function to perform all type of data calculation
def execute_step2(save_weeks=False, save_spearman=False, save_z=False, save_p=True):
    for aInterval in intervals:
        interval_files = glob.glob('./file_processed/' + str(aInterval) + '/*') # location where intermediary files stored

        N = 162000 / aInterval  # windows in a week.. total seconds = 9(hrs in a day) * 60 * 60 * 5(days) N = number of window in a week
        PSum = 0
        PCount = 0
        P_table = []  # it wil be a 2d array to store complete PValue tables
        spearman_R1a2a_table = []
        spearman_R1a2b_table = []
        spearman_R2a2a_table = []
        Z_table = []
        Week1_table = []
        Week2_table = []

        for aRow_file in interval_files:
            userA_Obj = get_pickle(aRow_file)
            P_row = []
            R1a2a_row = []
            R1a2b_row = []
            R2a2a_row = []
            Z_row = []

            for aColumn_File in interval_files:
                userB_Obj = get_pickle(aColumn_File)

                userA_week1 = userA_Obj.windows_week1
                userA_week2 = userA_Obj.windows_week2
                # userB_week1 = userB_Obj.windows_week1 # this is not required for any calculation
                userB_week2 = userB_Obj.windows_week2

                R1a2a = my_spearman(userA_week1, userA_week2)
                R1a2b = my_spearman(userA_week1, userB_week2)
                R2a2b = my_spearman(userA_week2, userB_week2)

                ZValue = ZFormula(N, R1a2a, R1a2b, R2a2b)
                PValue = PFunction(ZValue)
                if PValue > 0.05:  # calculating average of the p values grater then 0.05
                    PSum += PValue
                    PCount += 1

                if save_spearman:
                    R1a2a_row.append(R1a2a)
                    R1a2b_row.append(R1a2b)
                    R2a2a_row.append(R2a2b)

                if save_z:
                    ZValue = format(ZValue, 'f')  # remove scientific notation
                    Z_row.append(ZValue)

                if save_p:
                    PValue = format(PValue, 'f')  # remove scientific notation
                    P_row.append(PValue)

            if save_spearman:
                spearman_R1a2a_table.append(R1a2a_row)
                spearman_R1a2b_table.append(R1a2b_row)
                spearman_R2a2a_table.append(R2a2a_row)

            if save_z:
                Z_table.append(Z_row)

            if save_p:
                P_table.append(P_row)

            if save_weeks:
                week1_row = get_data_column(userA_Obj.windows_week1)
                week2_row = get_data_column(userA_Obj.windows_week2)
                Week1_table.append(week1_row)
                Week2_table.append(week2_row)

        # save respective files if required
        user_names = get_file_names(interval_files)
        if save_spearman:
            generate_csv(table=spearman_R1a2a_table, index= user_names, column= user_names, location='./spearman/', file_name='R1a2a.csv', interval=aInterval)
            generate_csv(table=spearman_R1a2b_table, index= user_names, column= user_names, location='./spearman/', file_name='R1a2b.csv', interval=aInterval)
            generate_csv(table=spearman_R2a2a_table, index= user_names, column= user_names, location='./spearman/', file_name='R2a2a.csv', interval=aInterval)

        if save_z:
            generate_csv(table=Z_table, index= user_names, column= user_names, location='./ZValues/', file_name='ZValues.csv', interval=aInterval)

        if save_p:
            generate_csv(table=P_table, index= user_names, column= user_names, location='./PValues/', file_name='PValues.csv', interval=aInterval)

        if save_weeks:
            generate_csv(table=Week1_table, index= user_names, column= None, location='./Weeks/', file_name='Week1_windows.csv',
                         interval=aInterval)
            generate_csv(table=Week2_table, index= user_names, column= None, location='./Weeks/', file_name='Week2_windows.csv',
                         interval=aInterval)
        # html = df.to_html() # in case to store file as html to view in browser
        # generate_html_tables(html,aInterval,PAverage)
        PAverage = PSum/PCount
        print(f"P-value average for interval {aInterval} is :{PAverage}")


if __name__ == '__main__':
    tic = start = time.process_time()
    print(f"Execution step 1 started at: {datetime.now()}")
    execute_step1(clean_processed_files=True)
    print(f"Total time taken in step 1 is:   {(time.process_time()-tic)/60} minutes")
    tic = time.process_time()
    print(f"Execution step 2 started at: {datetime.now()}")
    execute_step2(save_weeks=False, save_spearman=False, save_z=False, save_p=True)
    print(f"Total time taken in step 2 is:   {(time.process_time()-tic)/60} minutes")
    print(f"Execution step 2 completed at: {datetime.now()}")
    print(f"Total execution time of program:     {(time.process_time()-start)/60} minutes")








