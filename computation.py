import math
import pandas as pd
import numpy as np
from scipy.stats import spearmanr
# calculated spearman rank coefficient for two given 1D data arrays
def my_spearman(dataA, dataB):

    linear_dataA = []
    linear_dataB = []

    for aDay in range(len(dataA)):   # there are 6 days
        for aSlot in range(len(dataA[aDay])):   # aDay may have # of slots or window
            if dataA[aDay][aSlot] and dataB[aDay][aSlot]:
                linear_dataA.append(dataA[aDay][aSlot])
                linear_dataB.append(dataB[aDay][aSlot])
            elif dataA[aDay][aSlot] and not dataB[aDay][aSlot]:
                linear_dataA.append(dataA[aDay][aSlot])
                linear_dataB.append(0.0001)
            elif not dataA[aDay][aSlot] and dataB[aDay][aSlot]:
                linear_dataA.append(0.0001)
                linear_dataB.append(dataB[aDay][aSlot])
            # else: # in case when both windows of a and b are empty then don't include them
            #     linear_dataA.append(0.0001)
            #     linear_dataB.append(0.0001)

    # calculate spearman rank correlation coef using numpy function
    coef = (pd.Series(linear_dataA)).corr(pd.Series(linear_dataB), method='spearman')
    # coef, p = spearmanr(linear_dataA,linear_dataB)

    # 3 assumption are added here,  if value is NaN then return 0
    if np.isnan(coef):
        coef = 0.0001
    if coef == 0.0:
        coef = 0.0001
    if coef == 1.0:
        coef = 0.99999
    if coef == -1.0:
        coef = -0.9999
    # print(f"coef: {coef}")
    return coef

# performs calculation of Z for given N, R1a2a, R1a2b,R2a2b spearman correlation coefficient
def ZFormula(N,r1a2a,r1a2b,r2a2b):
    rm_square = (pow(r1a2a,2) + pow(r1a2b,2))/2
    f = (1-r2a2b)/(2*(1-rm_square))
    h = (1- (f*rm_square))/(1-rm_square)
    Z1a2a = (math.log((1+r1a2a)/(1-r1a2a)))/2
    Z1a2b = (math.log((1+r1a2b)/(1-r1a2b)))/2
    z = (Z1a2a - Z1a2b) * ((math.sqrt(N-3))/(2*(1-r2a2b)*h))
    return z

# perform P value calculation for a given Z value
def PFunction(z):
    p = 0.3275911
    a1 = 0.254829592
    a2 = -0.284496736
    a3 = 1.421413741
    a4 = -1.453152027
    a5 = 1.061405429
    sign = None
    if z < 0.0:
        sign = -1
    else:
        sign = 1
    x = abs(z)/math.sqrt(2.0)
    t = 1.0/ (1.0 + (p*x))
    erf = 1.0 - (((((a5 * t + a4) * t) + a3) * t + a2) * t + a1) * t * math.exp(-x * x)
    return 0.5 * (1.0 + sign * erf)

# this function calculates average of octects per duration if there are multiple data for a window
def average_oct_per_duration(aFileObj, perform_slicing = True):
    for i in range(len(aFileObj.windows_week1)):
        aDay = aFileObj.windows_week1[i]
        for j in range(len(aDay)):
            aSlot = aDay[j]
            if aSlot:
                sum_doctets_per_duration = 0
                for aTuple in aSlot:    # aTuple = (doctets, duration)
                    if perform_slicing:
                        if aTuple[1] <= aFileObj.interval:
                            doctets_per_duration = aTuple[0]/aTuple[1]
                            sum_doctets_per_duration += doctets_per_duration
                        else:                       # part of current slot = (doctets/Total duration) * current slot Duration
                            aSlice = (aTuple[0]/aTuple[1])*aFileObj.interval  # # of doctets falling in current slot
                            doctets_per_duration = aSlice / aFileObj.interval
                            sum_doctets_per_duration += doctets_per_duration
                            remaining_doctets =  aTuple[0] - aSlice
                            remaining_duration = aTuple[1] - aFileObj.interval
                            next_slot_tuple = (remaining_doctets, remaining_duration)
                            next_slot_index = j+1
                            if next_slot_index < len(aDay):
                                aDay[next_slot_index].append(next_slot_tuple)
                    else:
                        doctets_per_duration = aTuple[0] / aTuple[1]
                        sum_doctets_per_duration += doctets_per_duration
                avg = (sum_doctets_per_duration/len(aSlot))
                aFileObj.windows_week1[i][j] = avg

    for i in range(len(aFileObj.windows_week2)):
        aDay = aFileObj.windows_week2[i]
        for j in range(len(aDay)):
            aSlot = aDay[j]
            if aSlot:
                sum_doctets_per_duration = 0
                for aTuple in aSlot:  # aTuple = (doctets, duration)
                    if perform_slicing:
                        if aTuple[1] <= aFileObj.interval:
                            doctets_per_duration = aTuple[0] / aTuple[1]
                            sum_doctets_per_duration += doctets_per_duration
                        else:  # part of current slot = (doctets/Total duration) * current slot Duration
                            aSlice = (aTuple[0] / aTuple[1]) * aFileObj.interval  # # of doctets falling in current slot
                            doctets_per_duration = aSlice / aFileObj.interval
                            sum_doctets_per_duration += doctets_per_duration
                            remaining_doctets = aTuple[0] - aSlice
                            remaining_duration = aTuple[1] - aFileObj.interval
                            next_slot_tuple = (remaining_doctets, remaining_duration)
                            next_slot_index = j + 1
                            if next_slot_index < len(aDay):
                                aDay[next_slot_index].append(next_slot_tuple)
                    else:
                        doctets_per_duration = aTuple[0] / aTuple[1]
                        sum_doctets_per_duration += doctets_per_duration
                avg = (sum_doctets_per_duration / len(aSlot))
                aFileObj.windows_week2[i][j] = avg


    # >>>> not considering week 3 data <<<

    # for i in range(len(aFileObj.windows_week3)):
    #     aDay = aFileObj.windows_week3[i]
    #     for j in range(len(aDay)):
    #         aSlot = aDay[j]
    #         if aSlot:
    #             sum_doctets_per_duration = 0
    #             for aTuple in aSlot:  # aTuple = (doctets, duration)
    #                 if aTuple[1] <= aFileObj.interval:
    #                     doctets_per_duration = aTuple[0] / aTuple[1]
    #                     sum_doctets_per_duration += doctets_per_duration
    #                 else:  # part of current slot = (doctets/Total duration) * current slot Duration
    #                     aSlice = (aTuple[0] / aTuple[1]) * aFileObj.interval  # # of doctets falling in current slot
    #                     doctets_per_duration = aSlice / aFileObj.interval
    #                     sum_doctets_per_duration += doctets_per_duration
    #                     remaining_doctets = aTuple[0] - aSlice
    #                     remaining_duration = aTuple[1] - aFileObj.interval
    #                     next_slot_tuple = (remaining_doctets, remaining_duration)
    #                     next_slot_index = j + 1
    #                     if next_slot_index < len(aDay):
    #                         aDay[next_slot_index].append(next_slot_tuple)
    #             avg = (sum_doctets_per_duration / len(aSlot))
    #             aFileObj.windows_week3[i][j] = avg
    # not calculating week 4 data - optimazation
    # for i in range(len(aFileObj.windows_week4)):
    #     aDay = aFileObj.windows_week4[i]
    #     for j in range(len(aDay)):
    #         aSlot = aDay[j]
    #         if aSlot:
    #             sum_doctets_per_duration = 0
    #             for aTuple in aSlot:  # aTuple = (doctets, duration)
    #                 if aTuple[1] <= aFileObj.interval:
    #                     doctets_per_duration = aTuple[0] / aTuple[1]
    #                     sum_doctets_per_duration += doctets_per_duration
    #                 else:  # part of current slot = (doctets/Total duration) * current slot Duration
    #                     aSlice = (aTuple[0] / aTuple[1]) * aFileObj.interval  # # of doctets falling in current slot
    #                     doctets_per_duration = aSlice / aFileObj.interval
    #                     sum_doctets_per_duration += doctets_per_duration
    #                     remaining_doctets = aTuple[0] - aSlice
    #                     remaining_duration = aTuple[1] - aFileObj.interval
    #                     next_slot_tuple = (remaining_doctets, remaining_duration)
    #                     next_slot_index = j + 1
    #                     if next_slot_index < len(aDay):
    #                         aDay[next_slot_index].append(next_slot_tuple)
    #             avg = (sum_doctets_per_duration / len(aSlot))
    #             aFileObj.windows_week4[i][j] = avg
    # while i < len(obj.data):
    #     aobj = obj.data[i]
    #     j = 0
    #     while j < len(aobj):
    #         aslot = aobj[j]
    #         if aslot:
    #             total = 0
    #             k = 0
    #             while k < len(aslot):
    #                 total += aslot[k]
    #                 k += 1
    #             obj.data[i][j] = total/len(aslot)
    #         j += 1
    #     i += 1
