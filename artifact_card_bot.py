#!/usr/bin/env python3

import discord
import re
import json
import requests
import config
import logger
from util import colour_lookup

CARDS = 'https://kollieflower.github.io/Artifact2/json/Cards.json'
ABILITIES = 'https://kollieflower.github.io/Artifact2/json/Abilities.json'
KEYWORDS = 'https://kollieflower.github.io/Artifact2/json/Keywords.json'

client = discord.Client()

def getCardColour(card):
    logger.debug('Getting card colour')
    if(card['card_type'] != 'Item'):
        return 'O'
    return card['colour']

def findCard(cardQuery, cardType, partialMatch=False):
    logger.debug('Finding cards')
    if partialMatch == False:
        if cardType == 'card':
            cards = fetchCards(cardType)
            logger.info('Searching for card with exact match of query: ' + str(cardQuery))
            for card in cards[0]:
                if isinstance(cardQuery, int):
                    if card['card_id'] == cardQuery:
                        logger.info(str(card['card_id']) + ' matches query: ' + str(cardQuery) + '. Returning card')
                        return card
                    else:
                        logger.debug(str(card['card_id']) + ' does not match query: ' + str(cardQuery))
                else:
                    for version in card['versions']:
                        if 'card_name' in version:
                            if version['card_name']['english'].lower() == cardQuery:
                                logger.info(version['card_name']['english'].lower() + ' matches query: ' + str(cardQuery) + '. Returning card')
                                return getCardDetails(card, cardType)
                            else:
                                logger.debug(version['card_name']['english'].lower() + ' does not match query: ' + str(cardQuery))
        elif cardType == 'ability':
            cards = fetchCards(cardType)
            logger.info('Searching for ability with exact match of query: ' + str(cardQuery))
            for card in cards[1]:
                if isinstance(cardQuery, int):
                    if card['card_id'] == cardQuery:
                        logger.info(str(card['card_id']) + ' matches query: ' + str(cardQuery) + '. Returning card')
                        return card
                    else:
                        logger.debug(str(card['card_id']) + ' does not match query: ' + str(cardQuery))
                else:
                    for version in card['versions']:
                        if 'ability_name' in version:
                            if version['ability_name']['english'].lower() == cardQuery:
                                logger.info(str(version['ability_name']['english'].lower() + ' matches query: ' + str(cardQuery) + '. Returning card'))
                                return getCardDetails(card, cardType)
                            else:
                                logger.debug(str(version['ability_name']['english'].lower() + ' does not match query: ' + str(cardQuery)))
        elif cardType == 'keyword':
            cards = fetchCards(cardType)
            logger.info('Searching for keyword with exact match of query: ' + str(cardQuery))
            for card in cards:
                if card['keyword'].lower() == cardQuery:
                    return getCardDetails(card, cardType)
        logger.info('No entry found for query: ' + cardQuery + '. Searching for partial matches')
        card = findCard(cardQuery, cardType, True)
        return card
    elif partialMatch == True:
        if cardType == 'card':
            cards = fetchCards(cardType)
            logger.info('Searching for card with partial match of query: ' + str(cardQuery))
            for card in cards[0]:
                for version in card['versions']:
                    if 'card_name' in version:
                        if cardQuery in version['card_name']['english'].lower():
                            logger.info('Partial match found for query: ' + str(cardQuery) + '. Returning card: ' + version['card_name']['english'].lower())
                            return getCardDetails(card, cardType)
                        else:
                            logger.debug('No partial match found for card query: ' + str(cardQuery) + ' in ' + version['card_name']['english'].lower())
        elif cardType == 'ability':
            cards = fetchCards(cardType)
            logger.info('Searching for ability with exact partial of query: ' + str(cardQuery))
            for card in cards[1]:
                for version in card['versions']:
                    if 'ability_name' in version:
                        if cardQuery in version['ability_name']['english'].lower():
                            logger.info('Partial match found for ability query: ' + str(cardQuery) + '. Returning ability: ' + version['ability_name']['english'].lower())
                            return getCardDetails(card, cardType)
                        else:
                            logger.debug('No partial match found for ability query: ' + str(cardQuery) + ' in ' + version['ability_name']['english'].lower())
        elif cardType == 'keyword':
            cards = fetchCards(cardType)
            logger.info('Searching for keyword with partial match of query: ' + str(cardQuery))
            for card in cards:
                if cardQuery in card['keyword'].lower():
                    logger.info('Partial match found for keyword query: ' + str(cardQuery) + '. Returning keyword: ' + card['keyword'].lower())
                    return getCardDetails(card, cardType)
                else:
                    logger.debug('No partial match found for keyword query: ' + str(cardQuery))

def getCardDetails(card, cardType, forUnit=False):
    logger.debug('Getting card details')

    if cardType == 'keyword':
        embed = discord.Embed(title=card['keyword'], colour=0xf8f8ff)
        embed.add_field(name='Definition', value=card['desc'])
        return embed
    elif cardType == 'card':
        cardDetails = {}
        if forUnit == False:
            for version in card['versions']:
                if 'set' in version:
                    cardDetails['set'] = version['set']
                if 'rarity' in version:
                    cardDetails['rarity'] = version['rarity']
                if 'card_name' in version:
                    cardDetails['name'] = version['card_name']['english']
                if 'card_type' in version:
                    cardDetails['cardType'] = version['card_type']
                if 'image' in version:
                    cardDetails['image'] = 'https://kollieflower.github.io/Artifact2/Images/Cards/CardArt/' + version['image'] + '.jpg'
                # if cardType != 'Hero':
                if 'text' in version:
                    cardDetails['cardText'] = cleanUpText(version['text']['english'])

            # colour_short = getCardColour(card)
            # colour = colour_lookup[colour_short]['name']
            # colourCode = colour_lookup[colour_short]['colourCode']
                if cardDetails['cardType'] != 'Item':
                    if 'colour' in version:
                        cardDetails['colour'] = version['colour']
                else:
                    cardDetails['colour'] = 'O'

                if cardDetails['colour'] == 'B':
                    cardDetails['colour'] = 'Black'
                    cardDetails['colourCode'] = 0x000000
                if cardDetails['colour'] == 'U':
                    cardDetails['colour'] = 'Blue'
                    cardDetails['colourCode'] = 0x00008b
                if cardDetails['colour'] == 'G':
                    cardDetails['colour'] = 'Green'
                    cardDetails['colourCode'] = 0x006400
                if cardDetails['colour'] == 'R':
                    cardDetails['colour'] = 'Red'
                    cardDetails['colourCode'] = 0xa50000
                if cardDetails['colour'] == 'O':
                    cardDetails['colour'] = ''
                    cardDetails['colourCode'] = 0xccac00
                if cardDetails['colour'] == 'C':
                    cardDetails['colour'] = 'Colourless'
                    cardDetails['colourCode'] = 0x808080
                
                # embed = discord.Embed(title=name, colour=colourCode)
                # embed.add_field(name='Type', value=colour + ' ' + cardType, inline=False)

                # if cardType == 'Hero':
                
                    # ability = {}
                    # signature = {}
                if 'attack' in version:
                    cardDetails['attack'] = version['attack']
                if 'armour' in version:
                    cardDetails['armour'] = version['armour']
                if 'hp' in version:
                    cardDetails['hp'] = version['hp']
                if 'abilities' in version:
                    cardDetails['abilities'] = version['abilities']
                if 'signature' in version:
                    cardDetails['signature'] = version['signature']
                        # for heroAbility in version['abilities']:
                        #     heroAbilityBase = int(heroAbility.split('_')[0])
                        #     heroAbilityVersion = int(heroAbility.split('_')[1])
                        #     ability = getCardDetails(findCard(heroAbilityBase, 'ability'), 'ability', forUnit=True)
                        #     if ability:
                        #         embed.add_field(name='Ability: ' + ability['name'], value=ability['cardText'], inline=False)
                    # if 'signature' in version:
                    #     cardDetails['signature'] = version['signature']
                        # for signature in version['signature']:
                        #     signatureBase = int(signature.split('_')[0])
                        #     signatureVersion = int(signature.split('_')[1])
                        #     signature = getCardDetails(findCard(signatureBase, 'card'), 'card', forUnit=True)
                        #     if signature:
                        #         embed.add_field(name='Signature: ' + signature['name'], value=signature['cardText'], inline=False)
                    # embed.add_field(name='Attack', value=attack, inline=True)
                    # embed.add_field(name='Armour', value=armour, inline=True)
                    # embed.add_field(name='HP', value=hp, inline=True)
                # if cardType == 'Creep':
                    # if 'attack' in version:
                    #     attack = version['attack']
                    # if 'armour' in version:
                    #     armour = version['armour']
                    # if 'hp' in version:
                    #     hp = version['hp']
                if 'cost' in version:
                    cardDetails['mana'] = version['cost']
                if 'crosslane' in version:
                    cardDetails['crosslane'] = version['crosslane']
                if 'crosslane' in cardDetails:
                    cardDetails['crosslane'] = 'Yes'
                else:
                    cardDetails['crosslane'] = 'No'
                    # embed.add_field(name='Mana', value=mana, inline=True)
                    # embed.add_field(name='Crosslane', value=crosslane, inline=True)
                    # embed.add_field(name='Card Text', value=cardText, inline=False)
                    # embed.add_field(name='Attack', value=attack, inline=True)
                    # embed.add_field(name='Armour', value=armour, inline=True)
                    # embed.add_field(name='HP', value=hp, inline=True)
                # if cardType == 'Item':
                if 'card_subtype' in version:
                    cardDetails['cardSubType'] = version['card_subtype']
                if 'gcost' in version:
                    cardDetails['goldCost'] = version['gcost']
                    # if 'attack' in version:
                    #     attack = version['attack']
                    # if 'armour' in version:
                    #     armour = version['armour']
                    # if 'hp' in version:
                    #     hp = version['hp']
                    # if 'cost' in version:
                    #     mana = version['cost']
                    # if 'crosslane' in version:
                    #     crosslane = version['crosslane']
                    # if crosslane:
                    #     crosslane = 'Yes'
                    # else:
                    #     crosslane = 'No'
                    # embed.add_field(name='Mana', value=mana, inline=True)
                    # embed.add_field(name='Gold', value=goldCost, inline=True)
                    # embed.add_field(name='Crosslane', value=crosslane, inline=True)
                    # embed.add_field(name='Card Text', value=cardText, inline=False)
                    # if cardSubType == 'Weapon' or cardSubType == 'Armor' or cardSubType =='Accessory':
                    #     embed.add_field(name='Attack', value=attack, inline=True)
                    #     embed.add_field(name='Armour', value=armour, inline=True)
                    #     embed.add_field(name='HP', value=hp, inline=True)
                # if cardType == 'Spell':
                    # if 'cost' in version:
                    #     mana = version['cost']
                    # if 'crosslane' in version:
                    #     crosslane = version['crosslane']
                    # if crosslane:
                    #     crosslane = 'Yes'
                    # else:
                    #     crosslane = 'No'
                    # embed.add_field(name='Mana', value=mana, inline=True)
                    # embed.add_field(name='Crosslane', value=crosslane, inline=True)
                    # embed.add_field(name='Card Text', value=cardText, inline=False)
                # if cardType == 'Improvement':
                #     if 'cost' in version:
                #         mana = version['cost']
                #     if 'crosslane' in version:
                #         crosslane = version['crosslane']
                #     if crosslane:
                #         crosslane = 'Yes'
                #     else:
                #         crosslane = 'No'
                #     embed.add_field(name='Mana', value=mana, inline=True)
                #     embed.add_field(name='Crosslane', value=crosslane, inline=True)
                #     embed.add_field(name='Card Text', value=cardText, inline=False)
                # if cardType == 'Summon':
                #     if 'attack' in version:
                #         attack = version['attack']
                #     if 'armour' in version:
                #         armour = version['armour']
                #     if 'hp' in version:
                #         hp = version['hp']
                #     if 'cost' in version:
                #         mana = version['cost']
                #     if 'crosslane' in version:
                #         crosslane = version['crosslane']
                #     if 'abilities' in version:
                #         for summonAbility in version['abilities']:
                #             summonAbilityBase = int(summonAbility.split('_')[0])
                #             summonAbilityVersion = int(summonAbility.split('_')[1])
                #             ability = getCardDetails(findCard(summonAbilityBase, 'ability'), 'ability', forUnit=True)
                #             if ability:
                #                 embed.add_field(name='Ability ' + ability['name'], value=ability['cardText'], inline=False)
                #     if crosslane:
                #         crosslane = 'Yes'
                #     else:
                #         crosslane = 'No'
                #     embed.add_field(name='Mana', value=mana, inline=True)
                #     embed.add_field(name='Crosslane', value=crosslane, inline=True)
                #     embed.add_field(name='Card Text', value=cardText, inline=False)
                #     embed.add_field(name='Attack', value=attack, inline=True)
                #     embed.add_field(name='Armour', value=armour, inline=True)
                #     embed.add_field(name='HP', value=hp, inline=True)
                # embed.set_thumbnail(url=cardArtURL)
                # return embed
            embed = discord.Embed(title=cardDetails['name'], colour=cardDetails['colourCode'])
            embed.add_field(name='Type', value=cardDetails['colour'] + ' ' + cardDetails['cardType'], inline=False)
            if cardDetails['cardType'] == 'Hero' or cardDetails['cardType'] == 'Summon' or cardDetails['cardType'] == 'Creep':
                if cardDetails['abilities']:
                    for ability in cardDetails['abilities']:
                        abilityBase = int(ability.split('_')[0])
                        abilityVersion = int(ability.split('_')[1])
                        ability = getCardDetails(findCard(abilityBase, 'ability'), 'ability', forUnit=True)
                        embed.add_field(name='Ability: ' + ability['name'], value=ability['cardText'], inline=False)
            if cardDetails['cardType'] == 'Hero':
                if cardDetails['signature']:
                    for signature in cardDetails['signature']:
                        signatureBase = int(signature.split('_')[0])
                        signatureVersion = int(signature.split('_')[1])
                        signature = getCardDetails(findCard(signatureBase, 'card'), 'card', forUnit=True)
                        embed.add_field(name='Signature: ' + signature['name'], value=signature['cardText'], inline=False)
            if cardDetails['cardType'] != 'Hero':
                embed.add_field(name='Mana', value=cardDetails['mana'], inline=True)
                embed.add_field(name='Crosslane', value=cardDetails['crosslane'], inline=True)
                embed.add_field(name='Card Text', value=cardDetails['cardText'], inline=False)
            if cardDetails['cardType'] != 'Spell':
                embed.add_field(name='Attack', value=cardDetails['attack'], inline=True)
                embed.add_field(name='Armour', value=cardDetails['armour'], inline=True)
                embed.add_field(name='HP', value=cardDetails['hp'], inline=True)
            return embed
        elif forUnit == True:
            for version in card['versions']:
                if 'card_name' in version:
                    name = version['card_name']['english']
                if 'text' in version:
                    cardText = cleanUpText(version['text']['english'])
            return {'name': name, 'cardText': cardText}                
    elif cardType == 'ability':
        abilityDetails = {}
        if forUnit == False:
            for version in card['versions']:
                abilityDetails['cardType'] = 'Ability'
                if 'ability_name' in version:
                    abilityDetails['name'] = version['ability_name']['english']
                if 'text' in version:
                    abilityDetails['cardText'] = cleanUpText(version['text']['english'])
                if 'image' in version:
                    abilityDetails['cardArtURL'] = 'https://kollieflower.github.io/Artifact2/Images/Abilities/' + version['image'] + '.jpg'
                abilityDetails['colourCode'] = 0x663399
                if 'ability_type' in version:
                    abilityDetails['abilityType'] = version['ability_type'] 
                if 'cost' in version:
                    abilityDetails['mana'] = version['cost']
                if 'cooldown' in version:
                    abilityDetails['cooldown'] = version['cooldown']

            embed = discord.Embed(title=abilityDetails['name'], colour=abilityDetails['colourCode'])
            embed.add_field(name='Type', value=abilityDetails['cardType'], inline=False)
            embed.add_field(name='Card Text', value=abilityDetails['cardText'], inline=False)
            embed.add_field(name='Ability Type', value=abilityDetails['abilityType'], inline=True)
            embed.add_field(name='Mana', value=abilityDetails['mana'], inline=True)
            embed.add_field(name='Cooldown', value=abilityDetails['cooldown'], inline=True)

            embed.set_thumbnail(url=abilityDetails['cardArtURL'])
            return embed
        elif forUnit == True:
            for version in card['versions']:
                if 'ability_name' in version:
                    name = version['ability_name']['english']
                if 'text' in version:
                    cardText = version['text']['english']
                    cardText = cleanUpText(cardText)
            return {'name': name, 'cardText': cardText}

def fetchCards(cardType):
    logger.debug('Fetching cards')
    if cardType == 'keyword':
        keywordRequest = requests.get(KEYWORDS).text
        keywordList = json.loads(keywordRequest)
        return keywordList
    else:
        cardsRequest = requests.get(CARDS).text
        cardList = json.loads(cardsRequest)
        abilitiesRequest = requests.get(ABILITIES).text
        abilityList = json.loads(abilitiesRequest)
        return [cardList, abilityList]

def cleanUpText(cardText):
    logger.debug('Cleaning up card text')
    if cardText == '':
        cardText = 'This card has no text.'
    else:
        cardText = re.sub(r'/n', '', cardText)
        cardText = re.sub(r'\[ATT\]', ' Attack', cardText)
        cardText = re.sub(r'\[AR\]', ' Armour', cardText)
        cardText = re.sub(r'\[HP\]', ' HP', cardText)
        cardText = re.sub(r'\[\w+\]', '', cardText)   
    return cardText

@client.event
async def on_ready():
    logger.info('We have logged in as {0.user}'.format(client))

@client.event
async def on_message(message):
    logger.debug('Receiving message')
    if message.author == client.user:
        logger.debug('Reading our own message.')
        return

    cardQuery = re.search(r"\[(.+)\]", message.content).group(1).lower()
    if cardQuery == 'help':
        logger.debug('Displaying usage')
        await message.channel.send('```To lookup a card: [cardname]\nTo lookup an ability: [abilityname|a] or [abilityname|ability]\nTo lookup a keyword: [keywordname|k] or [keywordname|keyword]\nTo display this help page: [help]```')
        return
    logger.info('Message Content contains cardQuery: ' + cardQuery)

    cardQuery = cardQuery.split('|')
    logger.debug('Splitting query.')
    if len(cardQuery) > 1:
        cardType = cardQuery[1].lower()
        logger.debug('Set card type to: ' + cardType)
    else:
        cardType = 'c'
        logger.debug('Set card type to: ' + cardType)
        
    if cardType == 'keyword' or cardType == 'k':
        cardType = 'keyword'
    elif cardType == 'ability' or cardType == 'a':
        cardType = 'ability'
    else:
        cardType = 'card'
    logger.debug('Set card type to: ' + cardType)

    cardQuery = cardQuery[0].lower()
    logger.debug('Set card query to: ' + cardQuery)

    logger.info('Getting card details')
    embed = findCard(cardQuery, cardType)

    try:
        await message.channel.send(embed=embed)
    except Exception as e:
        logger.error(e)

if __name__ == '__main__':
    logger = logger.get_logger(__name__, 'bot.log', 'INFO')
    logger.info('Starting Bot')
    client.run(config.BOT_TOKEN)