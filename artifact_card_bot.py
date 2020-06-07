#!/usr/bin/env python3

import discord
import re
import json
import requests
import config
from keywords import keywords
from util import colour_lookup

CARDS = 'https://kollieflower.github.io/Artifact2/json/Cards.json'
ABILITIES = 'https://kollieflower.github.io/Artifact2/json/Abilities.json'

client = discord.Client()

def getCardColour(card):
    if(card['card_type'] != 'Item'):
        return 'O'
    return card['colour']

def findCard(cardQuery, cards, partialMatch=False):
    if partialMatch == False:
        for card in cards[0]:
            if isinstance(cardQuery, str):
                if card['versions'][-1]['card_name']['english'].lower() == cardQuery:
                    return card
                # else:
                #     print(card['versions'][-1]['card_name']['english'].lower() + "does not match: " + cardQuery)
            else:
                if card['card_id'] == cardQuery:
                    return card
                # else:
                #     print(card['card_id'] + " does not match: " + str(cardQuery))
        for card in cards[1]:
            if isinstance(cardQuery, int):
                if card['card_id'] == cardQuery:
                    return card
                # else:
                #     print("No card found with ID: " + str(cardQuery))
        card = findCard(cardQuery, cards, True)
        return card
    elif partialMatch == True:
        for card in cards[0]:
            if cardQuery in card['versions'][-1]['card_name']['english'].lower():
                return card
            # else:
            #     print(cardQuery + " not in " + card['versions'][-1]['card_name']['english'].lower())
        for card in cards[1]:
            if cardQuery in card['versions'][-1]['ability_name']['english'].lower():
                return card
            # else:
            #     print(cardQuery + " not in " + card['versions'][-1]['ability_name']['english'].lower())

def getCardDetails(cardQuery, cards, cardType, forUnit=False):
    if cardType == 'keyword':
        if isinstance(cardQuery, str):
            for keyword in keywords:
                if keyword.lower() == cardQuery:
                    embed = discord.Embed(title=keyword, colour=0xf8f8ff)
                    embed.add_field(name='Definition', value=keywords[keyword])
                    return embed
        return None
    card = findCard(cardQuery, cards)

    if cardType == 'card':
        card = card['versions'][-1]
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
    cardsRequest = requests.get(CARDS).text
    cardList = json.loads(cardsRequest)
    abilitiesRequest = requests.get(ABILITIES).text
    abilityList = json.loads(abilitiesRequest)

    return [cardList, abilityList]

def cleanUpText(cardText):
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
    print('We have logged in as {0.user}'.format(client))

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('[') and message.content.endswith(']'):
        cardQuery = re.search(r"\[(.+)\]", message.content).group(1).lower()
        cards = fetchCards()
        embed = getCardDetails(cardQuery, cards, 'card')

        try:
            await message.channel.send(embed=embed)
        except Exception as e:
            print(e)
    if message.content.startswith('|') and message.content.endswith('|'):
        cardQuery = re.search(r"\|(.+)\|", message.content).group(1).lower()
        cards = fetchCards()
        embed = getCardDetails(cardQuery, keywords, 'keyword')
        if not embed:
            embed = getCardDetails(cardQuery, cards, 'ability')

        try:
            await message.channel.send(embed=embed)
        except Exception as e:
            print(e)


if __name__ == '__main__':
    client.run(config.BOT_TOKEN)