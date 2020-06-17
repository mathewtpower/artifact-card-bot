#!/usr/bin/env python3

import discord
import re
import json
import requests
import config
import logger
from keywords import keywords
from util import colour_lookup

CARDS = 'https://kollieflower.github.io/Artifact2/json/Cards.json'
ABILITIES = 'https://kollieflower.github.io/Artifact2/json/Abilities.json'

client = discord.Client()

def getCardColour(card):
    logger.debug('Getting card colour')
    if(card['card_type'] != 'Item'):
        return 'O'
    return card['colour']

def findCard(cardQuery, cards, cardType, partialMatch=False):
    logger.debug('Finding cards')
    if partialMatch == False:
        if cardType == 'card':
            logger.info('Searching for card with exact match of query: ' + cardQuery)
            for card in cards[0]:
                if isinstance(cardQuery, str):
                    if card['versions'][-1]['card_name']['english'].lower() == cardQuery:
                        logger.info(card['versions'][-1]['card_name']['english'].lower() + ' matches query: ' + cardQuery + '. Returning card')
                        return card
                    else:
                        logger.debug((card['versions'][-1]['card_name']['english'].lower() + ' does not match query: ' + cardQuery))
                else:
                    if card['card_id'] == cardQuery:
                        logger.info(card['card_id'] + ' matches query: ' + cardQuery + '. Returning card')
                        return card
                    else:
                        logger.debug(card['card_id'] + ' does not match query: ' + str(cardQuery))
        elif cardType == 'ability':
            logger.info('Searching for ability with exact match of query: ' + cardQuery)
            for card in cards[1]:
                if isinstance(cardQuery, int):
                    if card['card_id'] == cardQuery:
                        logger.info(card['card_id'] + ' matches query: ' + cardQuery + '. Returning card')
                        return card
                    else:
                        logger.debug(card['card_id'] + ' does not match query: ' + str(cardQuery))
        elif cardType == 'keyword':
            logger.info('Searching for keyword with exact match of query: ' + cardQuery)
            for keyword in keywords:
                if keyword.lower() == cardQuery:
                    return [keyword, keywords[keyword]]
        logger.info('No entry found for query: ' + cardQuery + '. Searching for partial matches')
        card = findCard(cardQuery, cards, cardType, True)
        return card
    elif partialMatch == True:
        if cardType == 'card':
            logger.info('Searching for card with partial match of query: ' + cardQuery)
            for card in cards[0]:
                if cardQuery in card['versions'][-1]['card_name']['english'].lower():
                    logger.info('Partial match found for query: ' + cardQuery + '. Returning card: ' + card['versions'][-1]['card_name']['english'].lower())
                    return card
                else:
                    logger.debug('No partial match found for card query: ' + cardQuery + ' in ' + card['versions'][-1]['card_name']['english'].lower())
        elif cardType == 'ability':
            logger.info('Searching for ability with exact partial of query: ' + cardQuery)
            for card in cards[1]:
                if cardQuery in card['versions'][-1]['ability_name']['english'].lower():
                    logger.info('Partial match found for ability query: ' + cardQuery + '. Returning ability: ' + card['versions'][-1]['ability_name']['english'].lower())
                    return card
                else:
                    logger.debug('No partial match found for ability query: ' + cardQuery + ' in ' + card['versions'][-1]['ability_name']['english'].lower())
        elif cardType == 'keyword':
            logger.info('Searching for keyword with partial match of query: ' + cardQuery)
            for keyword in keywords:
                if cardQuery in keyword.lower():
                    logger.info('Partial match found for keyword query: ' + cardQuery + '. Returning keyword: ' + keyword.lower())
                    return [keyword, keywords[keyword]]
                else:
                    logger.debug('No partial match found for keyword query: ' + cardQuery)

def getCardDetails(cardQuery, cards, cardType, forUnit=False):
    logger.debug('Getting card details')
    card = findCard(cardQuery, cards, cardType)

    if cardType == 'keyword':
        embed = discord.Embed(title=card[0], colour=0xf8f8ff)
        embed.add_field(name='Definition', value=card[1])
        return embed
    elif cardType == 'card':
        try:
            card = card['versions'][-1]
        except TypeError as e:
            logger.warning(e)
            return
        if forUnit == False:
            cardSet = card['set']
            rarity = card['rarity']
            name = card['card_name']['english']
            cardType = card['card_type']
            cardArtURL = 'https://kollieflower.github.io/Artifact2/Images/Cards/CardArt/' + card['image'] + '.jpg'
            if cardType != 'Hero':
                cardText = card['text']['english']
                cardText = cleanUpText(cardText)

            # colour_short = getCardColour(card)
            # colour = colour_lookup[colour_short]['name']
            # colourCode = colour_lookup[colour_short]['colourCode']

            if cardType != 'Item':
                colour = card['colour']
            else:
                colour = 'O'

            if colour == 'B':
                colour = 'Black'
                colourCode = 0x000000
            if colour == 'U':
                colour = 'Blue'
                colourCode = 0x00008b
            if colour == 'G':
                colour = 'Green'
                colourCode = 0x006400
            if colour == 'R':
                colour = 'Red'
                colourCode = 0xa50000
            if colour == 'O':
                colour = ''
                colourCode = 0xccac00
            if colour == 'C':
                colour = 'Colourless'
                colourCode = 0x808080
            
            embed = discord.Embed(title=name, colour=colourCode)
            embed.add_field(name='Type', value=colour + ' ' + cardType, inline=False)

            if cardType == 'Hero':
                ability = {}
                signature = {}
                attack = card['attack']
                armour = card['armour']
                hp = card['hp']
                for heroAbility in card['abilities']:
                    heroAbilityBase = int(heroAbility.split('_')[0])
                    heroAbilityVersion = int(heroAbility.split('_')[1])
                    ability = getCardDetails(heroAbilityBase, cards, 'ability', True)
                    if ability:
                        embed.add_field(name='Ability: ' + ability['name'], value=ability['cardText'], inline=False)
                for signature in card['signature']:
                    signatureBase = int(signature.split('_')[0])
                    signatureVersion = int(signature.split('_')[1])
                    signature = getCardDetails(signatureBase, cards, 'card', True)
                    if signature:
                        embed.add_field(name='Signature: ' + signature['name'], value=signature['cardText'], inline=False)
                embed.add_field(name='Attack', value=attack, inline=True)
                embed.add_field(name='Armour', value=armour, inline=True)
                embed.add_field(name='HP', value=hp, inline=True)
            if cardType == 'Creep':
                attack = card['attack']
                armour = card['armour']
                hp = card['hp']
                mana = card['cost']
                crosslane = card['crosslane']
                if crosslane:
                    crosslane = 'Yes'
                else:
                    crosslane = 'No'
                embed.add_field(name='Mana', value=mana, inline=True)
                embed.add_field(name='Crosslane', value=crosslane, inline=True)
                embed.add_field(name='Card Text', value=cardText, inline=False)
                embed.add_field(name='Attack', value=attack, inline=True)
                embed.add_field(name='Armour', value=armour, inline=True)
                embed.add_field(name='HP', value=hp, inline=True)
            if cardType == 'Item':
                cardSubType = card['card_subtype']
                goldCost = card['gcost']
                attack = card['attack']
                armour = card['armour']
                hp = card['hp']
                mana = card['cost']
                crosslane = card['crosslane']
                if crosslane:
                    crosslane = 'Yes'
                else:
                    crosslane = 'No'
                embed.add_field(name='Mana', value=mana, inline=True)
                embed.add_field(name='Gold', value=goldCost, inline=True)
                embed.add_field(name='Crosslane', value=crosslane, inline=True)
                embed.add_field(name='Card Text', value=cardText, inline=False)
                if cardSubType == 'Weapon' or cardSubType == 'Armor' or cardSubType =='Accessory':
                    embed.add_field(name='Attack', value=attack, inline=True)
                    embed.add_field(name='Armour', value=armour, inline=True)
                    embed.add_field(name='HP', value=hp, inline=True)
            if cardType == 'Spell':
                mana = card['cost']
                crosslane = card['crosslane']
                if crosslane:
                    crosslane = 'Yes'
                else:
                    crosslane = 'No'
                embed.add_field(name='Mana', value=mana, inline=True)
                embed.add_field(name='Crosslane', value=crosslane, inline=True)
                embed.add_field(name='Card Text', value=cardText, inline=False)
            if cardType == 'Improvement':
                mana = card['cost']
                crosslane = card['crosslane']
                if crosslane:
                    crosslane = 'Yes'
                else:
                    crosslane = 'No'
                embed.add_field(name='Mana', value=mana, inline=True)
                embed.add_field(name='Crosslane', value=crosslane, inline=True)
                embed.add_field(name='Card Text', value=cardText, inline=False)
            if cardType == 'Summon':
                attack = card['attack']
                armour = card['armour']
                hp = card['hp']
                mana = card['cost']
                crosslane = card['crosslane']
                for summonAbility in card['abilities']:
                    summonAbilityBase = int(summonAbility.split('_')[0])
                    summonAbilityVersion = int(summonAbility.split('_')[1])
                    ability = getCardDetails(summonAbilityBase, cards, 'ability', True)
                    if ability:
                        embed.add_field(name='Ability ' + ability['name'], value=ability['cardText'], inline=False)
                if crosslane:
                    crosslane = 'Yes'
                else:
                    crosslane = 'No'
                embed.add_field(name='Mana', value=mana, inline=True)
                embed.add_field(name='Crosslane', value=crosslane, inline=True)
                embed.add_field(name='Card Text', value=cardText, inline=False)
                embed.add_field(name='Attack', value=attack, inline=True)
                embed.add_field(name='Armour', value=armour, inline=True)
                embed.add_field(name='HP', value=hp, inline=True)
            embed.set_thumbnail(url=cardArtURL)
            return embed
        elif forUnit == True:
                name = card['card_name']['english']
                cardText = card['text']['english']
                cardText = cleanUpText(cardText)
                return {'name': name, 'cardText': cardText}                
    elif cardType == 'ability':
        card = card['versions'][-1]
        if forUnit == False:
            cardType = 'Ability'
            name = card['ability_name']['english']
            cardText = card['text']['english']
            cardText = cleanUpText(cardText)
            cardArtURL = 'https://kollieflower.github.io/Artifact2/Images/Abilities/' + card['image'] + '.jpg'
            colourCode = 0x663399
            abilityType = card['ability_type'] 
            mana = card['cost']
            cooldown = card['cooldown']

            embed = discord.Embed(title=name, colour=colourCode)
            embed.add_field(name='Type', value=cardType, inline=False)
            embed.add_field(name='Card Text', value=cardText, inline=False)
            embed.add_field(name='Ability Type', value=abilityType, inline=True)
            embed.add_field(name='Mana', value=mana, inline=True)
            embed.add_field(name='Cooldown', value=cooldown, inline=True)

            embed.set_thumbnail(url=cardArtURL)
            return embed
        elif forUnit == True:
            name = card['ability_name']['english']
            cardText = card['text']['english']
            cardText = cleanUpText(cardText)
            return {'name': name, 'cardText': cardText}

def fetchCards():
    logger.debug('Fetching cards')
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

    if message.content.startswith('[') and message.content.endswith(']'):
        cardQuery = re.search(r"\[(.+)\]", message.content).group(1).lower()
        if cardQuery == 'help':
            logger.debug('Displaying usage')
            await message.channel.send('```To lookup a card: [cardname], [cardname|c] or [cardname|card]\nTo lookup an ability: [abilityname|a] or [abilityname|ability]\nTo lookup a keyword: [keywordname|k] or [keywordname|keyword]\nTo display this help page: [help]```')
            return
        logger.info('Message Content contains cardQuery: ' + cardQuery)
        cardQuery = cardQuery.split('|')
        cards = fetchCards()
        if len(cardQuery) > 1:
            cardType = cardQuery[1]
            logger.debug('Set card type to: ' + cardType)
            cardQuery = cardQuery[0]
            logger.debug('Set card query to: ' + cardQuery)
        else:
            cardQuery = cardQuery[0]
            logger.debug('Set card query to: ' + cardQuery)
            cardType = 'card'
            logger.debug('Set card type to: ' + cardType)
        logger.info('Getting card details')
        embed = getCardDetails(cardQuery, cards, cardType)

        try:
            await message.channel.send(embed=embed)
        except Exception as e:
            logger.error(e)

if __name__ == '__main__':
    logger = logger.get_logger(__name__, 'bot.log', 'INFO')
    logger.info('Starting Bot')
    client.run(config.BOT_TOKEN)