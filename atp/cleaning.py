import pandas as pd
import numpy as np


def clean_df(df, country):
    
    #Selecting only for the country selected
    df_c = df[df['Location'].str.contains(country, case=False)]

    #Droping id
    df_c.drop("_id", inplace=True, axis=1)

    #Droping Born 
    df_c.drop("Born", axis=1, inplace=True)

    #Droping Link of the Player
    df_c.drop("LinkPlayer", axis=1, inplace=True)

    #Drop Hand
    df_c.drop("Hand", axis=1, inplace=True)

    #Clean Hight
    index_to_fill = df_c[df_c["Height"] == "NA"]["Height"].index
    mean_of_height = round(df_c[df_c["Height"] != "NA"]["Height"].astype(int).mean(),0)
    df_c["Height"].loc[index_to_fill] = mean_of_height

    # Converting Hight to int
    df_c['Height'] = df_c['Height'].astype(int)

    #Cleaning Prize
    df_c['Prize'] = df_c['Prize'].replace(regex=[r'�'],value='')
    df_c['Prize'] = df_c['Prize'].replace(regex=[r'$'],value='')
    df_c['Prize'] = df_c['Prize'].str.replace('$', '')
    df_c['Prize'] = df_c['Prize'].str.replace(',', '')

    # Cleaning missing prize for the mean
    index_to_fill = df_c[df_c['Prize'] == ""].index
    mean_prize = np.round(np.mean(df_c[df_c['Prize']!=""]['Prize'].astype(float)), 0)
    df_c["Prize"].loc[index_to_fill] = mean_prize


    # Converting to float
    df_c['Prize'] = df_c['Prize'].astype(float)

    
    # Droping null values to score
    indices_to_drop = df_c[df_c["Score"] == 'null'].index
    df_c.drop(index=indices_to_drop, axis=0, inplace=True)


    # aplicar a função à coluna 'Score' e criar uma nova coluna 'Score_sem_espacos_virgulas'
    df_c['Score_1'] = df_c['Score'].apply(retirar_espacos_virgulas)

    #Count to create target variable
    df_c['Numero_sets'] = df_c['Score_1'].apply(contar_sets)

    #Drop Columns with RET (Player didn't finished)
    index_to_drop = df_c[df_c['Score'].str.contains('(RET)')].index
    df_c.drop(index_to_drop, axis=0, inplace=True)

    #Drop Columns with WO
    index_to_drop = df_c[df_c['Score'].str.contains('(W/O)')].index
    df_c.drop(index_to_drop, axis=0, inplace=True)

    #Droping rows with Nan for number of sets
    df_c.dropna(subset=['Numero_sets'], inplace=True, axis=0)

    #The player that does not have rank will be attributed the rank of 1001
    index_to_fill = df_c[df_c['GameRank'] == "-"].index
    df_c["GameRank"].loc[index_to_fill] = "1001"

    #Game rank to int
    df_c["GameRank"] = df_c["GameRank"].astype(int)

    #Calculating the score 
    df_c["TotalPoints"] = df_c["Score_1"].apply(num_of_points)

    #Droping unecessary columns 
    df_c.drop(["Score", "Score_1"], axis=1, inplace=True)

    # Converting number of setting to integer
    df_c['Numero_sets'] = df_c['Numero_sets'].astype(int)

    #Dropping rows that does not contain dates
    indices_to_drop = df_c[~df_c['Date'].str.contains('-', case=False)].index
    df_c.drop(index=indices_to_drop, axis=0, inplace=True)

    # Split date in start date and end date
    df_c["start_date"] = df_c["Date"].apply(lambda x: x.split("-")[0])
    df_c["end_date"] = df_c["Date"].apply(lambda x: x.split("-")[1])

    #Converting date in date type
    df_c["start_date"] = pd.to_datetime(df_c["start_date"])
    df_c["end_date"] = pd.to_datetime(df_c["end_date"])

    #Creating new variable len of tornament
    df_c["tornament_days"] = (df_c["end_date"] - df_c["start_date"]).dt.days

    #Drop original date that we're not going to use
    df_c.drop("Date", inplace=True, axis=1)

    #Selecting only updated data before 2000
    df_c = df_c[df_c["start_date"].dt.year >2000] 

    #Joining the winning and losing
    switzerland_sw_winner = df_c[df_c['WL'] == 'W']
    switzerland_sw_losser = df_c[df_c['WL'] == 'L']

    switzerland_sw_winner['GameId'] = switzerland_sw_winner['Tournament'] + '_' + switzerland_sw_winner['Location'] + '_' + switzerland_sw_winner['Ground'] + '_' + \
               switzerland_sw_winner['Prize'].astype(str) + '_' + switzerland_sw_winner['GameRound'] + '_' + switzerland_sw_winner['Numero_sets'].astype(str) + \
               '_' + switzerland_sw_winner['tornament_days'].astype(str) + '_' + switzerland_sw_winner['start_date'].astype(str) + '_' + switzerland_sw_winner['PlayerName']  + '_' + switzerland_sw_winner['Oponent']

    switzerland_sw_losser['GameId'] = switzerland_sw_losser['Tournament'] + '_' + switzerland_sw_losser['Location'] + '_' + switzerland_sw_losser['Ground'] + '_' + \
               switzerland_sw_losser['Prize'].astype(str) + '_' + switzerland_sw_losser['GameRound'] + '_' + switzerland_sw_losser['Numero_sets'].astype(str) + \
               '_' + switzerland_sw_losser['tornament_days'].astype(str) + '_' + switzerland_sw_losser['start_date'].astype(str) +'_' + switzerland_sw_losser['Oponent'] + '_' + switzerland_sw_losser['PlayerName']


    player_1 = ['PlayerName', 'Height','Tournament', 'Location', 'Ground', 'Prize', 'GameRound','GameRank', 'Numero_sets',
        'TotalPoints', 'start_date', 'end_date', 'tornament_days','GameId']
    player_2 = ['PlayerName', 'Height','GameRank','GameId']
    df_f = pd.merge(switzerland_sw_winner[player_1], switzerland_sw_losser[player_2], on='GameId', how='inner')

    # Renaming column 
    reanme_columns_name = ["Player1_Name", "Player1_Height", "Tournament", "Location", "Ground", "Prize", "GameRound", "Player2_Rank", "Num_Sets", "TotalPoints", "Start_Date", "End_Date", "Tornament_Days", "GameId", "Player2_Name", "Player2_Height", "Player1_Rank"] 
    df_f.columns = reanme_columns_name

    #Creating the diff of the rank between two players 
    df_f["Rank_Diff"] = abs(df_f["Player1_Rank"] - df_f["Player2_Rank"])

    return df_f

def retirar_espacos_virgulas(score):
    return score.replace(' ', '').replace(',', '').replace('-','')


def contar_sets(score_1):
    num_digitos = len(score_1)
    resultado = score_1
    if '(RET)' in score_1:

        ret_pos = score_1.find('(RET)')
        num_digitos = sum(c.isdigit() for c in score_1[:ret_pos])
        
    else:
        num_digitos = sum(c.isdigit() for c in score_1)

    if num_digitos == 10:
        return 5
    elif num_digitos == 8:
        return 4
    elif num_digitos == 6:
        return 3
    elif num_digitos == 4:
        return 2
    elif num_digitos == 2:
        return 1
    elif resultado == '(W/O)':
        return 0
    else:
        return None


def num_of_points(Score_1):
    total_points = 0
    for i in range(len(Score_1)):
        total_points += int(Score_1[i])
    return total_points