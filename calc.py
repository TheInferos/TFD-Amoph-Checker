import json
players = [ "Sini", "Hex"]
file_path = "output.txt"
patternFile = "Amorph.json"
itemsWanted = "itemsWanted.json"
focus = ["Executor", "Secret Gar"]

def main():
    patterns, wants, locations = mapInputs()
    output = ""
    if focus:
        output = calcFocused(patterns, wants)
    else: 
        output = calcAll(patterns, wants)
    writeFile(output)

def calcAll(patterns, wants):
    playerMap = {}
    for player in players:
        playerMap[player] = {"wants":mapWants(wants[player]) }
        playerMap[player]["value"] = findWantedAmorphs(patterns, playerMap[player]["wants"])
    mapOpenings(playerMap, "value", "allLocations")
    orderPlayerOpenings(playerMap, "value", "allLocations" )
    common_items = list(set(list(playerMap["Sini"]["locations"].keys())) & set(list(playerMap["Hex"]["locations"].keys())))
    nice_message = prettyPrint(playerMap, common_items, "", "value", "allLocations")
    nice_message += soloItemPrint(playerMap, common_items, "value", "allLocations")
    return nice_message

def calcFocused(patterns, wants):
    playerMap = {}
    for player in players:
        playerMap[player] = {"wants":mapWants(wants[player]) }
        playerMap[player]["value"] = findWantedAmorphs(patterns, playerMap[player]["wants"])
        playerMap[player]["focused"] = {}
        for material in playerMap[player]["value"]:
            if any(focusedItem in valuedItems for focusedItem in focus for valuedItems in playerMap[player]["value"][material]["items"]):
                playerMap[player]["focused"][material] = playerMap[player]["value"][material]
    mapOpenings(playerMap,"focused", "focusedLocations")
    mapOpenings(playerMap,"value", "allLocations")
    common_focus_items = list(set(list(playerMap["Sini"]["focusedLocations"].keys())) & set(list(playerMap["Hex"]["focusedLocations"].keys())))
    common_sini_focus_items_unfiltered = list(set(playerMap["Sini"]["focusedLocations"].keys()) & set(playerMap["Hex"]["allLocations"].keys()))
    common_sini_focus_items = [item for item in common_sini_focus_items_unfiltered if item not in common_focus_items]
    common_hex_focus_items_unfiltered = list(set(list(playerMap["Sini"]["allLocations"].keys())) & set(list(playerMap["Hex"]["focusedLocations"].keys())))
    common_hex_focus_items = [item for item in common_hex_focus_items_unfiltered if item not in common_focus_items]

    orderPlayerOpenings(playerMap, "focused", "focusedLocations")
    orderPlayerOpenings(playerMap, "value", "allLocations")
    output = f"{prettyPrint(playerMap,common_focus_items, "Both Focus\n\n","focused", "focusedLocations")}\n\n"
    output += f"{prettyPrintSingleFocus(playerMap, "Sini", common_sini_focus_items, "Sini Focus\n", "focused", "focusedLocations", "value", "allLocations")}\n\n"
    output += f"{prettyPrintSingleFocus(playerMap, "Hex", common_hex_focus_items, "Hex Focus\n", "focused", "focusedLocations", "value", "allLocations")}\n\n"
    output += soloItemPrint(playerMap, common_focus_items + common_sini_focus_items + common_hex_focus_items, "value", "allLocations" )
    return output


def mapInputs():
    patterns = read_json_file(patternFile)
    wants = read_json_file(itemsWanted)
    locations = mapOpenerToAmorph(patterns)
    return patterns, wants, locations

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
            message += f"\t\t{item["name"]}  at  {str(int(item["chance"]*100))}% chance\n"
    return {"items": items, "worth":wanted, "message": message, "amorph": amorph}

def mapOpenerToAmorph(amorphs):
    locations = {}
    for amorph in amorphs:
        mat = amorphs[amorph]
        if not (mat["useIn"] in locations):
            locations[mat["useIn"]] = []
        locations[mat["useIn"]].append(amorph)
    return locations

def mapOpenings(players, obKeyToMap, mapTo):
    for player in players:
        players[player][mapTo] = {}

        # Iterate over materials in the key specified by `obKeyToMap`
        for material in players[player][obKeyToMap]:
            amorph = players[player][obKeyToMap][material]["amorph"]
            location = amorph["useIn"]

            # Only process materials if their location is in `obKeyToMap`
            if location not in players[player][mapTo]:
                players[player][mapTo][location] = []

            # Add the material to the location map if it’s not already there
            if material not in players[player][mapTo][location]:
                players[player][mapTo][location].append(material)

            # Now, let's ensure all materials from the same location are included
            for value_material in players[player]["value"]:
                value_amorph = players[player]["value"][value_material]["amorph"]
                value_location = value_amorph["useIn"]

                if value_location == location and value_material not in players[player][mapTo][location]:
                    players[player][mapTo][location].append(value_material)

    # for player in players: 
    #     players[player][mapTo] = {}
    #     for material in  players[player][obKeyToMap]:
    #         amorph = players[player][obKeyToMap][material]["amorph"]
    #         if not (amorph["useIn"] in players[player][mapTo]):
    #             players[player][mapTo][amorph["useIn"]] = []
    #         players[player][mapTo][amorph["useIn"]].append(material)


def prettyPrint(players, common_list, startMessage, value, locations):
    output = startMessage
    for location in common_list:
        output += f"{location}:\n"
        for player in players:
            output += f"  {player}:\n"
            if location in players[player][locations]:
                for material in players[player][locations][location]:
                    amorph = players[player]["value"][material]
                    output += f"    {material} worth {int(amorph['worth'] * 100)}:\n{amorph['message']}"
            else:
                output += f"{player} has no items in {location} (Something went wrong :( ))\n"
        output += "\n"   
    return output

def prettyPrintSingleFocus(players, focusPlayer, common_list, startMessage, focusedValue, focusedLocation, value, locations):
    output = startMessage
    for location in common_list:
        output += f"{location}:\n"
        for player in players:
            output += f"\t{player}:\n"
            if player == focusPlayer:
                if location in players[player][focusedLocation]:
                    for material in players[player][focusedLocation][location]:
                        amorph = players[player]["value"][material]
                        output += f"\t\t{material} worth {int(amorph['worth'] * 100)}:\n{amorph['message']}"
                else:
                    output += f"{player} has no items in {location} (Something went wrong :( ))\n"
            else:
                if location in players[player][locations]:
                    for material in players[player][locations][location]:
                        amorph = players[player][value][material]
                        output += f"    {material} worth {int(amorph['worth'] * 100)}:\n{amorph['message']}"
                else:
                    output += f"{player} has no items in {location} (Something went wrong :( ))\n"

        output += "\n"   
    return output

def soloItemPrint(players, common_list, values, locations):
    output = ""
    for player in players:
        output += f"{player} only:\n"
        for location in players[player][locations]:
            if location not in common_list:
                output += f"\t{location}:\n"
                for material in players[player][locations][location]:
                    amorph = players[player][values][material]
                    output += f"\t\t{material} worth {int(amorph['worth'] * 100)}:\n{amorph['message']}"
        output += "\n"
    return output

def writeFile (output):
    with open(file_path, 'w+') as file:
        file.write(output)

def orderPlayerOpenings(playerMap, values, locationOb ):
    for player in playerMap:
        playerMap[player][locationOb+"Ordered"] = {}
        for location in playerMap[player][locationOb]:
            playerMap[player][locationOb+"Ordered"][location] =  sorted(playerMap[player][locationOb][location], key=lambda material: playerMap[player]["value"][material]["worth"], reverse=True ) 



main()