import pandas as pd
import numpy as np
import os
import time
import ast
import pickle
import requests
import json
import matplotlib.pyplot as plt
import seaborn as sns

############################################################################################################################################

def get_arena_tournaments(club='sc-weisse-dame-ev', no_tournaments = 500):
    
    '''
    This Function retrieves tournament information of specific lichess team via Lichess API
    
    Arguments:
        a: name of lichess team 
        b: number maximal tournaments
        
    Returns:
        The sum of the two integer arguments
    '''
    
    website_url = 'https://lichess.org/api/team/'+ club + '/arena?max=' + str(no_tournaments)
    response = requests.get(website_url)
    list_resp = response.text.splitlines()
    json_resp = list(map(lambda x: json.loads(x), list_resp))
    
    T_id=[]
    T_Name = []
    T_Date =[]
    T_Clock =[]
    
    for i in range(len(json_resp)):
        
        if 'jeffforever' == json_resp[i]['createdBy']:
            
            T_Date.append(time.strftime('%Y-%m-%d',
                                        time.gmtime(json_resp[i]['startsAt']/1000)))
            T_Name.append(json_resp[i]['fullName'][:-12])   
            T_Clock.append(str(int(json_resp[i]['clock']['limit']/60))+ ' + '
                           +str(json_resp[i]['clock']['increment']))            
            T_id.append('https://lichess.org/tournament/' + json_resp[i]['id'])
     
    
    # create dictionary for Dataframe
    dict = {'Datum':T_Date, 'Turnier': T_Name,'Bedenkzeit':T_Clock,'Link': T_id }
    # create DataFrame
    df = pd.DataFrame(dict)
        
    return df

############################################################################################################################################
def save_arena_tournament_json_files(df, club='sc-weisse-dame-ev'):
    
    '''
    This Function retrieves player results for differnt tournaments via Lichess API
    
    Arguments:
        a: df containaning id of tournaments
        b: club name
        
    Returns:
        None
    '''
 
    # Directory
    directory =  os.path.join('json_data',club)

    try:
        os.makedirs('.\\' + directory, exist_ok = True)
        print("Directory '%s' created successfully" % directory)
    except OSError as error:
        print("Directory '%s' can not be created" % directory)
    
    
    url = 'https://lichess.org/api/tournament/'
    
    
    for row in range (df.shape[0]):
        
        filepath = os.path.join('json_data',
                                         club,
                                        'date_' + df.iloc[row, 0] + '_T_id_'+ df.iloc[row,-1][-8:] + '.json')
            
        if not os.path.exists(filepath):
            
            response = requests.get(url + df.iloc[row, 3][-8:]+'/results')
            list_resp = response.text.splitlines()
            json_resp = list(map(lambda x: json.loads(x), list_resp))
            with open(filepath, 'w') as f:
                json.dump(json_resp, f)
                
############################################################################################################################################                
                
def get_player_results (df, club='sc-weisse-dame-ev'):

    '''
    This Function transfers player data from json file to dataframe
    
    Arguments:
        a: df containaning id of tournaments
        b: club name
        
    Returns:
        df
    '''
    
    
    df['Ergebnisse_Spieler'] = ''
    df['Anzahl_Spieler'] = ''
    
    # creates List with actual players and score values
    
    for row in range(df.shape[0]):
            list_players=[[],[]]
            
            filepath = os.path.join('json_data',
                                     club,
                                     'date_' + df.iloc[row, 0] + '_T_id_'+ df.iloc[row,-3][-8:] + '.json')

            with open(filepath) as f:
                list_T= json.load(f)
    
    
            for k in range(len(list_T)):
                if club == list_T[k]['team']:
                    list_players[0].append(list_T[k]['username'])
                    list_players[1].append(list_T[k]['score'])
            df.loc[row,'Ergebnisse_Spieler'] = str(list_players)   
            df.loc[row,'Anzahl_Spieler'] = len(list_players[0])  
            
    return df

############################################################################################################################################


def get_club_df(club='sc-weisse-dame-ev', no_tournaments = 500):
    
    '''
    Combination of functions for more details, see description of functions.
    
    Arguments:
        a: name of lichess team 
        b: number maximal tournaments 
        
    Returns:
        df
    '''
    
    df = get_arena_tournaments(club='sc-weisse-dame-ev', no_tournaments = 500)
    
    save_arena_tournament_json_files(df, club)
    
    df = get_player_results (df, club)
    
    return df

############################################################################################################################################

def change_names(df, dict_names_replace):
    
    '''
    Replaces names in case player used two accounts
    
    Arguments:
        a: df
        b: dictionary with name to be replaced and new name
        
    Returns:
        df
    '''
  
    for name in dict_names_replace:
        for row in range(df.shape[0]):
            if name in df.iloc[row,-2]:
                df.iloc[row,-2] = df.iloc[row,-2].replace(name, dict_names_replace[name])
            
            
    return df

############################################################################################################################################

def participants_and_league(df):
    
    '''
    Creates a figure with number of participants and league in dependence of the tournament round.
    
    Arguments:
        a: df
        b: dictionary with name to be replaced and new name
        
    Returns:
        df
    '''
    
    Liga_change = (df[::-1].loc[:,'Turnier'].str[-2])
    Liga_change[Liga_change == 's'] = 4
    Liga_change = Liga_change.astype(int)
    Liga_change = Liga_change.reset_index().drop('index', axis=1)
    Liga_change.index += 1 
    
    
    
    #plt.style.use(['science','notebook','grid'])
    
    fig,ax = plt.subplots(1,2, figsize=(24,7))
    
    
    #settings fontsize fs and lablepad lp
    fs = 24
    lp = 20
    # First Plot
    ax[0].plot(range(1,1+len(df)), df[::-1].loc[:,'Anzahl_Spieler'],'o--',color='g',ms=7)
    ax[0].set_title(label='WeDa Lichess-Teilnehmer', fontsize = 36, pad=lp, fontweight="bold")
    ax[0].set_ylabel('Spieleranzahl', fontsize = fs, labelpad=lp,fontweight="bold")
    ax[0].set_xlabel('Q-Liga Runde\n', fontsize = fs, labelpad=lp, fontweight="bold")
    ax[0].tick_params(axis='both', which='major', labelsize=18)
    ax[0].locator_params(axis='y', nbins=10)
    
    #Second PLot
    ax[1].plot(Liga_change,'o--',color='b',ms=7)
    ax[1].set_title(label='WeDa Q-Liga Verlauf ', fontsize = 36, pad=lp,fontweight="bold")
    ax[1].set_ylabel('Liga', fontsize = fs, labelpad=lp, fontweight="bold")
    ax[1].set_xlabel('Q-Liga Runde', fontsize = fs, labelpad=lp, fontweight="bold")
    ax[1].locator_params(axis='y', nbins=6)
    ax[1].tick_params(axis='both', which='major', labelsize=18)
    ax[1].set_ylim(8.2, 2.8)  # decreasing time
    
    plt.show()


############################################################################################################################################
    
def score_table(df):

        
    '''
    Extracts Score table from df
    
    Arguments:
        a: df
        
    Returns:
        df_score_table
    '''
    
    lst_players=[]
    
    for row in range(df.shape[0]):
        
            list_T = ast.literal_eval(df.loc[row,'Ergebnisse_Spieler'])  
            for j in range(len(list_T[0])):
                lst_players.append(list_T[0][j])
                 
    set_players = set(lst_players)
    df_score_table = pd.DataFrame(columns= ['1.Platz','2.Platz','3.Platz','Teilnahmen','Gesamtscore'],
                              index=set_players)
    df_score_table = df_score_table.fillna(0)
 
    
    ## determines number of participations for individual player
    for name in set_players:
        df_score_table.loc[name,'Teilnahmen'] = str(lst_players.count(name))
        
    for row in range(df.shape[0]):
        list_T = ast.literal_eval(df.loc[row,'Ergebnisse_Spieler'])   
        for name in set_players:
            
            ## Counts 1,2 und 3. place for individual player
            if name in list_T[0]:
                idx_name = list_T[0].index(name)
                
                if idx_name < 3:
                        df_score_table.loc[name,df_score_table.columns[list_T[0].index(name)]] =\
                        df_score_table.loc[name,df_score_table.columns[list_T[0].index(name)]]+1
                
            ## Zählen Gesamtscore
                df_score_table.loc[name,'Gesamtscore'] += list_T[1][idx_name]
       
    df_score_table = df_score_table.sort_values(['Gesamtscore'], ascending=False)            
    
    #df_score_table_Gesamt = df_score_table.rename(columns = {'Teilnahmen':'Teilnahmen'+'('+str(df.shape[0])+')'}) 
    
    return df_score_table


############################################################################################################################################

def save_pickle_score_table(df):   
    
    '''
    Save Score tables for differnt years
    
    Arguments:
        a: df
        
    Returns:
        None
    '''
    # score table for all years
    
    score_table(df).to_pickle('score_table_all.pkl')
    
    #score tavle for certain years
    
    lst_years=[2020,2021,2022]
    
    for year in lst_years:
        
        lst_players=[]
        
        mask = df.loc[:,'Datum'].str[0:4].astype(int) == year
        df_masked= df.loc[mask,:].reset_index()
                   
        score_table(df_masked).to_pickle('score_table_' + str(year) + '.pkl')
        

############################################################################################################################################    
    
def best_players(Zeitraum='score_table_all.pkl',Spieleranzahl=10):

    '''
    Creates figure with best players 
    
    Arguments:
        a: df
        
    Returns:
        None
    '''
    
    fig, ax = plt.subplots(figsize=(15,0.6*Spieleranzahl))

    df_Spieler = pd.read_pickle(Zeitraum)  
    
    df = df_Spieler.iloc[0:Spieleranzahl,:].astype(int)


    splot = sns.barplot(y=df.index, x="Gesamtscore", palette="Set2", data=df, ax=ax);

    ax.get_xaxis().set_visible(False)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.set_title('Bestenliste' + '\n', fontsize=25)

    plt.xticks(rotation = 90);
    
    max_rect = ax.patches[0].get_width()

    for rect in ax.patches :
        width = rect.get_width()
        plt.text(0.02*max_rect+rect.get_width(), rect.get_y()+0.5*rect.get_height(),
                     '%d' % int(width),
                     ha='center', va='center',weight='bold')
    plt.show();