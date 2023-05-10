

import sys,os
sys.path.append('../')

from core.stochastic_process import Stochastic_Process
from post_process import post_process as pp

# Define which input files should be considered and run. 
# Files are specified as numbers in a list (e.g. [1,2] will consider input_file_1.py and input_file_2.py)
input_files_to_run = [1]

'''
1 -> Kategori 1
2 -> Kategori 2
3 -> Kategori 3
4 -> Kategori 4
'''

#Calls the stochastic process and saves the result in a list of stochastic profiles
for j in input_files_to_run:
    Profiles_list = Stochastic_Process(j)
    
    
    #Post-processes the results and generates plots
    Profiles_avg, Profiles_list_kW, Profiles_series = pp.Profile_formatting(Profiles_list)
    pp.Profile_series_plot(Profiles_series) #by default, profiles are plotted as a series
    
    
    pp.export_series(Profiles_series,j)
   

    #Gjennomsnittseffekt iløpet av en dag
    if len(Profiles_list) > 1: 
        pp.Profile_cloud_plot(Profiles_list, Profiles_avg)


'''
5 simuleringer; simulerer man-tirs-ons-tors-fre

7 simuleringer; simulerer man-tirs-ons-tors-fre-lør-søn. Noen komponenter har innlagt helgevariabel. Disse vil
spille inn om simuleringen strekker seg over en helg

365 simuleringer; simulere for et helt år        
'''

