# -*- coding: utf-8 -*-

#%% Import required libraries
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

#%% Post-processing
'''
Just some additional code lines to calculate useful indicators and generate plots
'''
def Profile_formatting(stoch_profiles):
    #stoch_profiles vil være antall simuleringer av uavhengige dager vi velger å simulere, skrevet inn av bruker
    #stoch_profiles vil inneholde så mange daglige simuleringer som brukeren har skrevet inn
    
    Profile_avg = np.zeros(1440)
    for pr in stoch_profiles:
        Profile_avg = Profile_avg + pr
        #for løkken slutter etter innhopp
        #Plusser sammen flere simuleringer. Stoch_profiles er en "array med daglige lastflyt simuleringer"
        
    Profile_avg = Profile_avg/len(stoch_profiles)
    #Gjennomsnittsverdier for minutt-verdiene gjennom dagen. Inneholder stoch_profiles kun en simulering vil, denne være lik 
    #Profile_series
    
    Profile_kW = []
    for kW in stoch_profiles:
        Profile_kW.append(kW/1000)
        #Gjør om effekt minutt-verdiene i watt i stoch_profiles til kW. Deler atl på 1000 
    
    Profile_series = np.array([])
    for iii in stoch_profiles:
        Profile_series = np.append(Profile_series,iii)
        #legger element iii til på slutten av array Profile_series
        #Fyller Profile_series med elementene i stoch_profiles
        
        #Denne vil legge simuleringer etterhverandre i en liste, derfor økende timeantall langs x-aksen
    
    return (Profile_avg, Profile_kW, Profile_series)

def Profile_cloud_plot(stoch_profiles,stoch_profiles_avg):
    #tar inn ALLE daglige lastflytsimuleringene i stoch profiles og den ene gjennomsnitts lastflytprofilen som ble definert
    #over som Profile_avg
    
    #x = np.arange(0,1440,5)
    plt.figure(figsize=(10,5))
    for n in stoch_profiles:
        #Plotter de daglige simuleringene i egen farge
        plt.title("Cloud Plot")
        plt.plot(np.arange(1440),n,'#b0c4de')
        plt.xlabel('Time (hours)')
        plt.ylabel('Power (W)')
        plt.ylim(ymin=0)
        #plt.ylim(ymax=5000)
        plt.margins(x=0)
        plt.margins(y=0)
    plt.plot(np.arange(1440),stoch_profiles_avg,'#4169e1')
    plt.xticks([0,240,480,(60*12),(60*16),(60*20),(60*24)],[0,4,8,12,16,20,24])
    #plt.savefig('profiles.eps', format='eps', dpi=1000)
    plt.show()


def Profile_series_plot(stoch_profiles_series):
    #x = np.arange(0,1440,5)
    plt.figure(figsize=(10,5))
    plt.plot(np.arange(len(stoch_profiles_series)),stoch_profiles_series,'#4169e1')
    #plt.xlabel('Time (hours)')
    plt.title("Serie plot")
    plt.ylabel('Power (W)')
    plt.ylim(ymin=0)
    #plt.ylim(ymax=5000)
    plt.margins(x=0)
    plt.margins(y=0)
    #plt.xticks([0,240,480,(60*12),(60*16),(60*20),(60*24)],[0,4,8,12,16,20,24])
    #plt.savefig('profiles.eps', format='eps', dpi=1000)
    plt.show()

#%% Export individual profiles
'''
for i in range (len(Profile)):
    np.save('p0%d.npy' % (i), Profile[i])
'''

# Export Profiles

def export_series(stoch_profiles_series, j):
    series_frame = pd.DataFrame(stoch_profiles_series)
    series_frame.to_csv("C:/Users\halgr/OneDrive - NTNU/Masteroppgave/Python/Modellering_PvOffgrid/offgrid_PVsyst/input_files/demand_%d.csv" % (j))