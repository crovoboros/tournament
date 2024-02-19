url_source = "https://www.pgstats.com/articles/introducing-spr-and-uf"

import keys # this is a python file which contains your start.gg API key, do NOT insert the string in the script itself for security reasons.

# project goal: take user input for API key, such that it needs not be a file.

import pysmashgg # https://pypi.org/project/pysmashgg/

def remaining_rounds(seed):
    """takes player seed as input, gives expected rounds from winning the tournament."""
    import math
    seed = int(seed)
    if seed == 1:
        return 0
    return math.floor(math.log2(seed - 1)) + math.ceil(math.log2(2 * seed / 3))

def upset_factor(seed_winner, seed_loser):
    """calculates upset factor between two given seed arguments."""
    winner_factor = remaining_rounds(seed_winner)
    loser_factor = remaining_rounds(seed_loser)
    return winner_factor - loser_factor

def find_entrant_pages(tournament_name, event_name):
    tournament_with_bracket = initial.tournament_show_with_brackets(tournament_name, event_name)
    total_entrants = tournament_with_bracket['entrants']
    return (total_entrants // 25) + 1

def findSets(tournament_name, event_name):
    total_sets = []
    i = 1
    sets = initial.tournament_show_sets(tournament_name,event_name, i)
    while sets != []:
        total_sets += sets
        i += 1
        sets = initial.tournament_show_sets(tournament_name,event_name, i)
    return total_sets

def findEntrants(tournament_name, event_name):
    try:
        entrant_pages = find_entrant_pages(tournament_name, event_name)
        entrants = []
        for i in range(1, entrant_pages + 1):
            entrant_page = initial.tournament_show_entrants(tournament_name, event_name, i)
            entrants += entrant_page
    except:
        raise
    return entrants

def findSeed(tag, seeding):
    return seeding[tag]

def findUpsets(sets, seeding, isCSV = False):
    upsets = ""
    if isCSV:
        upsets = "Winner;Seed;Loser;Seed;Upset Factor;Round\n"
    try:
        for set in sets:
            if set['entrant1Score'] != -1 and set['entrant2Score'] != -1: #can i turn the converse statement into isDQ()?
                winnerSeed = findSeed(set['winnerName'], seeding)
                loserSeed = findSeed(set['loserName'], seeding)
                upsetFactor = upset_factor(winnerSeed, loserSeed)
                winnerName = removeTeam(set['winnerName'])
                loserName = removeTeam(set['loserName'])
                if upsetFactor > 0:
                    if isCSV:
                        upsets += f"{winnerName};{winnerSeed};{loserName};{loserSeed};{upsetFactor};{set['bracketName']} - {set['fullRoundText']}\n"
                    else:
                        upsets += f"{winnerName:15s} [Seed {winnerSeed:3d}]   W - L   {loserName:15s} [Seed {loserSeed:3d}]   UF{upsetFactor:2d}    {set['bracketName']} {set['fullRoundText']}\n"
    except:
        raise
    return upsets

def removeTeam(tag):        
    if ' | ' in tag:
        team_entrant = tag.split(' | ')
        tag = team_entrant[1]
    return tag

def displaySets(sets):
    for set in sets:
        if set['entrant1Score'] != -1 and set['entrant2Score'] != -1:
            entrant1Name = removeTeam(set['entrant1Name'])
            entrant2Name = removeTeam(set['entrant2Name'])
            print(f"{entrant1Name:15} {set['entrant1Score']:1d} - {set['entrant2Score']:1d} {' ':4} {entrant2Name:15}", "   ", set['bracketName'], set['fullRoundText'])

def findResults(tournament_name, event_name):
    try:
        entrants = findEntrants(tournament_name, event_name)
        results = {}
        for entrant in entrants:
            results[entrant['tag']] = entrant['finalPlacement']
    except:
        print("Exception occurred in findPlacements")
    return results

def csvResults(entrants, countries = False):
    if countries:
        csv = "Seed;Tag;Placement;Seed Performance;Country\n"
    else:
        csv = "Seed;Tag;Placement;Seed Performance\n"
    for entrant in entrants:
        placement = entrant['finalPlacement']
        seed = entrant['seed']
        tag = entrant['tag']
        seed_performance = upset_factor(seed, placement)
        if countries:
            country = findCountry(tag, entrants)
            csv += f"{seed};{removeTeam(tag)};{placement};{seed_performance};{country}\n"
        else:
            csv += f"{seed};{removeTeam(tag)};{placement};{seed_performance}\n"
    return csv

def findCountry(tag, entrants):
    try:
        for entrant in entrants:
            if entrant['tag'] == tag:
                playerId = entrant['entrantPlayers'][0]['playerId']
                break
            else:
                continue
    except:
        raise
    try:
        player = initial.player_show_info(playerId)
        if player:
            country = player['country']
        else:
            country = None
    except:
        print(playerId)
        raise
    return country

if __name__ == "__main__":    

    initial = pysmashgg.SmashGG(keys.API, True)
    tournament_name = "valhalla-iv"
    event_name = "main-ultimate-singles"
    entrants = findEntrants(tournament_name, event_name)
    
    for entrant in entrants:
        if entrant['tag'] == "Dragon":
            entrant['seed'] = 41

    csv = csvResults(entrants, countries = True)
    print(csv)