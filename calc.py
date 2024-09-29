import json
players = [ "Sini", "Hex"]
file_path = "output.txt"
patternFile = "Amorph.json"
itemsWanted = "itemsWanted.json"
def main():
    patterns = read_json_file(patternFile)
    wants = read_json_file(itemsWanted)
    locations = mapOpenerToAmorph(patterns)
    playerMap = {}
    for player in players:
        playerMap[player] = {"wants":mapWants(wants[player]) }
        playerMap[player]["value"] = findWantedAmorphs(patterns, playerMap[player]["wants"])
    mapOpenings(playerMap)
    orderPlayerOpenings(playerMap)
    common_items = list(set(list(playerMap["Sini"]["locations"].keys())) & set(list(playerMap["Hex"]["locations"].keys())))

    nice_message = prettyPrint(playerMap, common_items)
    writeFile(nice_message)
    123

# Function to read and parse a JSON file
def read_json_file(file_path):
    with open(file_path, 'r') as file:
        data = json.load(file)
    return data

def mapWants(want):
    ob = {}
    for base in want:
        for part in want[base]:
            ob[base + " " + part] = want[base][part]
    return ob

def findWantedAmorphs(patterns, wants):
    amorphValues = {}
    for amorph in patterns:
        amorphMapped = checkAmorph(patterns[amorph], wants)
        if (amorphMapped["worth"] >0):
            amorphValues[amorph] = amorphMapped
    return amorphValues


def checkAmorph(amorph, wants):
    items = []
    wanted = 0
    message = ""
    for item in amorph["drops"]:
        if item["name"] in wants and wants[item["name"]]>0:
            items.append(item["name"])
            wanted += item["chance"]
            message += "\t\t" + item["name"] + " at  " + str(int(item["chance"]*100)) + "% chance\n"
    return {"items": items, "worth":wanted, "message": message, "amorph": amorph}

def mapOpenerToAmorph(amorphs):
    locations = {}
    for amorph in amorphs:
        mat = amorphs[amorph]
        if not (mat["useIn"] in locations):
            locations[mat["useIn"]] = []
        locations[mat["useIn"]].append(amorph)
    return locations

def mapOpenings(players):
    
    for player in players: 
        players[player]["locations"] = {}
        for material in  players[player]["value"]:
            amorph = players[player]["value"][material]["amorph"]
            if not (amorph["useIn"] in players[player]["locations"]):
                players[player]["locations"][amorph["useIn"]] = []
            players[player]["locations"][amorph["useIn"]].append(material)


def prettyPrint(players, common_list):
    output = ""
    
    # Print common locations and items
    for location in common_list:
        output += f"{location}:\n"  # Better formatting
        for player in players:
            output += f"  {player}:\n"
            # Check if the location exists in the ordered locations
            if location in players[player]["locationsOrdered"]:
                for material in players[player]["locationsOrdered"][location]:
                    amorph = players[player]["value"][material]
                    output += f"    {material} worth {int(amorph['worth'] * 100)}:\n{amorph['message']}"
            else:
                output += f"{player} has no items in {location}\n"
        output += "\n"
    
    # Print exclusive items for each player
    for player in players:
        output += f"{player} only:\n"
        for location in players[player]["locationsOrdered"]:
            if location not in common_list:  # Print only exclusive locations
                output += f"  {location}:\n"
                for material in players[player]["locationsOrdered"][location]:
                    amorph = players[player]["value"][material]
                    output += f"\t{material} worth {int(amorph['worth'] * 100)}:\n{amorph['message']}"
        output += "\n"
    
    return output

def writeFile (output):
    with open(file_path, 'w+') as file:
        file.write(output)

def orderPlayerOpenings(playerMap):
    for player in playerMap:
        playerMap[player]["locationsOrdered"] = {}
        for location in playerMap[player]["locations"]:
            playerMap[player]["locationsOrdered"][location] =  sorted(playerMap[player]["locations"][location], key=lambda material: playerMap[player]["value"][material]["worth"], reverse=True ) 



main()