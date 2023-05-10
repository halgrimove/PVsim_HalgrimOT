# -*- coding: utf-8 -*-
"""
Created on Tue Jan 31 16:59:03 2023

@author: halgr

INFORMASJON OM HVA SOM FINNES I DE ULIKE MAPPENE


Offgrid_PVgis:
    
    Her ligger times-data input fra pvgis. Pvgis_processing prosesserer timesdataene og gjør dem 
    til riktig format til bruk i "offgrid_pvlib". Fjerner uviktige kolonner og setter korrekt index
    

Offgrid_PVlib:
    
    Her ligger de prosseserte dataene fra PV-gis. I filen "PV_production" spesifiseres lokasjon av anlegg
    type solcellepaneler og konfigurasjon av paneler. Det legges også inn verdier til PV-lib sin temperatur
    modell. Filen bruker innebygde funskjoner i PV-lib til å estimere solproduksjon gjennom et år. Estimert sol.
    produksjon er i timsverdier.
    
    Resultatet lagres i "input_files" mappen i Offgrid_PVsyst mappen
    
    
RAMP:
    
    Input_files:
        
        Her "lages" hver kategorihytte.
        
     Test -> "ramp_run":
         
         I denne funksjonen lages de årlige effektprofilene for kategorihyttene. Effektprofilene produseres
         i tur. I filen spesifiseres det hvilken hytte det simuleres for. Når filen kjøres kommer det et 
         sprøsmål i kontrollvinduet om hvor mange dager det skal simuleres for. Siden vi er ute etter en årlig profil
         skrives det her inn 365. Dette gir en forbruksprofil på 365 dager. Hver dag er lik (men fortsatt noe ulike grunnet
         tilfeldighetsfaktorer som ramp bruker). Forbruket som er estimert er for en "vinterdag"
         
         Resultatet lagres i "input_files" mappen i Offgrid_PVsyst mappen
         
         
 Offgrid_PVsyst (Local energy community 2):

     
    Input_files:

        Her ligger inputdataene fra RAMP og Pvlib. Dette er timesverdier.

    LEC_input_files:

        Her prosesseres input-filene videre. De interpoleres til kvarter-verdier og gjør dem om til kW (fra W)      
        
    LEC_offgrid_analysis:
        
        Filen som simulerer for hvert tidssteg gjennom et helt år. Filen klaler også på plotte-funksjonen 
        
    Model_builder_per_timestep:
        
        Filen beregner energiflytsverdier for et spesifikt tidssteg (med energideling)
        
    LEC_offgrid_plot:
        
        Plotter energiflytsverdiene
        
    trade_XXXX:
        
        Setter kjøps/salgs-andelene i tidssteget
        
    season_generator:
        
        Tilpasser forbruksprofilene et spesifikt bruksmønster
        
    sf_rate:
        
        Beregner self sufficient ratio
        
    offgrid_model_builder:
        
        Beregner energiflytsverdier uten energideling
        
    offgrid_plot:
        
        Plotter energiflytsverdeir uten energideling
        
        
HVORDAN KJØRE SIMULERING:
    
    - I filen LEC_offgrid_analysis.py -> Trykk "run". I kodelinjen:
        
        demand, pv = lecif.LEC_input_files(deltakere10, bruksmønster10)
        
        Endres inputverdiene ettersom hvilke forbruksprofiler og bruksmønsterprofiler som tas inn. I LEC_offgrid
        analysis ligger det lagt inn ulike profiler, demand1/2/3.... og bruksmønster1/2/3. Tallene i deltaker filene 
        står i stil til hvilken inputfil den kaller på, bruksmønsteret står i stil til bruksmønsterne spesifisert
        i season generator.
        
     - Plotting av energiflytsvariabler skjer nederst i filen LEC_offgrid_analysis. I kkodelinjen:
         
         for week in range(20,25):

             for i in range(n):
             
                 ofg_plot.LEC_offgrid_plot(dict_list, demand[i], pv[i], week, i)
                 
        Her plottes ukene 20, 21, 22, 23 og 24. Ukenummerene kan endres etter ønske.


      - Dersom det skal endres på forbruksprofiler, må man endre på input-filene i RAMP. MEd de nye inputfilene må
        man kjøre "ramp_run" på nytt (for 365 dager).

      - Dersom det skal endres på PV-anlegg, må endringene gjøres i "PV_production". Etter at endringene er gjort må 
        filen kjøres på nytt. 
        
      - Ved å endre på verdiene:
          
          battery_share_activate = 1 #Inkludere batteriutveksling når de er tomme/fulle
          flex_activate = 1 #Inkludere fleksibel batteriutveksling

          flex_limit = 0.2
          
          
        I model_builder_per_timestep endrer man på tillatelser for utveksling av energi på batteri. Flex limit endrer
        på betingelsene for hvordan et flex batteri deltar i markedet.
        
        
       - Variabelen: "time_analysis" = (month-1)*2880 + (day-1)*96 + hour*4 + minute/15, settes for å studere energihandelen
         i et spesifikt tidssteg. Dette vises i kontrollvinduet.
         
         
         
 
             


























'''

