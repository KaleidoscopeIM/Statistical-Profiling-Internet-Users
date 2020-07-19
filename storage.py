from datetime import datetime, date, time, timedelta

# this class stores intermediary data for a user file
# function - create windows for week 1 and week 2 for a given window interval,  stores octets,duration in appropriate window
# in case if week 3 and week 4 data is also required then uncomment commented lines
class Storage:
    def __init__(self, interval, path):
        self.interval = interval
        self.file_path = path
        self.windows_week1 = [[], [], [], [], []]  # 5 days  windows for mon, tue, wed, thu, fri
        self.windows_week2 = [[], [], [], [], []]
        # self.windows_week3 = [[], [], [], [], []]
        # self.windows_week4 = [[], [], [], [], []]
        self.start_date = date(2013, 2, 4)  # starting for 4th feb because 1st feb has only one day of week
        # self.end_date = date(2013, 2, 28)
        self.end_date= date(2013,2,15) # second week ends on 15 th feb
        self.start_time = time(8, 00, 00)  # 8am
        self.end_time = time(17, 00, 00)  # 5pm
        self.create_windows()

    def create_windows(self): # create windows for a complete week
        start_date_time = datetime.combine(self.start_date, self.start_time)  # 8am
        end_date_time = datetime.combine(self.start_date, self.end_time)  # 5pm
        cur_time = start_date_time
        slot_count = 0
        while cur_time < end_date_time:
            # print(datetime.strftime(cur_time, '%H:%M:%S%p'))
            aDay = 0
            while aDay < len(self.windows_week1):  # create slots inside each day
                self.windows_week1[aDay].append([])
                self.windows_week2[aDay].append([])
                # self.windows_week3[aDay].append([])
                # self.windows_week4[aDay].append([])
                aDay += 1
            cur_time = cur_time + timedelta(seconds=self.interval)
            slot_count += 1
        # print(f"Total slots : {slot_count}    Total a day slots {len(self.windows_week1[0])}")

    # stores (doctects,duration) for a given datetime in real_first_packet in appropriate slot
    def store_in_slot(self, real_first_packet, doctets, duration): # start from 8.00.00am to 4.59.59 pm
        if datetime.combine(self.start_date,self.start_time) <= real_first_packet < datetime.combine(self.end_date,self.end_time): # in between 4th feb to 28th feb
            if real_first_packet.time() < self.start_time or real_first_packet.time() > self.end_time: # only store if time is in between 8am to 5pm
                return
            day_num = real_first_packet.weekday()  # Monday is 0 , friday is 4 and Sunday is 6.
            if day_num > 4:  # not storing saturday and sunday
                return
            # octets_per_duration = doctets / duration
            aTuple = (doctets, duration)
            slot_num = self.get_slot_num(real_first_packet)
            week_num = self.get_week_num(real_first_packet)
            # print(f"day :{day_num}   slot_num: {slot_num}")
            if week_num == 1:
                self.windows_week1[day_num][slot_num].append(aTuple)
                return
            if week_num == 2:
                self.windows_week2[day_num][slot_num].append(aTuple)
                return
            # week 3 and week 4 not required - program optimization
            # if week_num == 3:
            #     self.windows_week3[day_num][slot_num].append(aTuple)
            #     return
            # if week_num == 4:
            #     self.windows_week4[day_num][slot_num].append(aTuple)

    def print_windows(self, day=None, week=None):
        if week == 1:
            print("___________________________________________________ week 1")
            day_num = 0
            for aDay in self.windows_week1:
                if aDay == day:
                    slot_num = 0
                    print(f"Day = {day_num}")
                    for aSlot in aDay:
                        if aSlot:
                            print(f"slot number {slot_num}  data = {aSlot}")
                        slot_num += 1
                    day_num += 1
                    print(f" >> Total slots: {slot_num}")
        if week is None and day is None:
            print("___________________________________________________ week 1")
            day_num = 0
            for aDay in self.windows_week1:
                slot_num = 0
                print(f"Day = {day_num}")
                for aSlot in aDay:
                    if aSlot:
                        print(f"slot number {slot_num}  data = {aSlot}")
                    slot_num += 1
                day_num += 1
                print(f" >> Total slots: {slot_num}")
            print("___________________________________________________ week 2")
            day_num = 0
            for aDay in self.windows_week2:
                slot_num = 0
                print(f"Day = {day_num} ")
                for aSlot in aDay:
                    if aSlot:
                        print(f"slot number {slot_num}  data = {aSlot}")
                    slot_num += 1
                day_num += 1
                print(f" >> Total slots: {slot_num}")

    # return week number from a date 4th feb 2013 return 1
    def get_week_num(self, aDateTime):
        if datetime.combine(self.start_date, self.start_time) <= aDateTime <= datetime.combine(date(2013, 2, 8), self.end_time):
            return 1
        if datetime.combine(date(2013, 2, 11), self.start_time) <= aDateTime <= datetime.combine(date(2013, 2, 15), self.end_time):
            return 2
        # if datetime.combine(date(2013, 2, 18), self.start_time) <= aDateTime <= datetime.combine(date(2013, 2, 22), self.end_time):
        #     return 3
        # if datetime.combine(date(2013, 2, 25), self.start_time) <= aDateTime <= datetime.combine(date(2013, 2, 28), self.end_time):
        #     return 4

    # return slot number from a given date. for window 10 intervals, a value will be returned in between 0 to 3239
    def get_slot_num(self, aDateTime): #slot num does not depend on date
        slot_start = None
        slot_end = None
        slot_num = 0
        while True:
            if slot_start is None:
                slot_start = datetime.combine(self.start_date, self.start_time)
                slot_end = slot_start + timedelta(seconds=self.interval)
            else:
                # if slot_start >= self.end_time:
                #     return None
                slot_start = slot_end
                slot_end = slot_end + timedelta(seconds=self.interval)
            if slot_start.time() <= aDateTime.time() <= slot_end.time():
                return slot_num
            slot_num += 1