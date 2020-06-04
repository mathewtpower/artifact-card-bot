#!/usr/bin/env python3

import discord
import re
import json
import requests
import config

CARDS = 'https://kollieflower.github.io/Artifact2/json/Cards.json'
ABILITIES = 'https://kollieflower.github.io/Artifact2/json/Abilities.json'

client = discord.Client()

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('[') and message.content.endswith(']'):
        cardQuery = re.search(r"\[(.+)\]", message.content).group(1)
        cardsRequest = requests.get(CARDS).text
        abilitiesRequest = requests.get(ABILITIES).text
        cardList = json.loads(cardsRequest)
        abilityList = json.loads(abilitiesRequest)
        for card in cardList:
            if card['versions'][-1]['card_name']['english'].lower() == cardQuery.lower():
                card = card['versions'][-1]
                name = card['card_name']['english']
                cardType = card['card_type']
                cardSet = card['set']
                rarity = card['rarity']
                if cardType != 'Item':
                    colour = card['colour']
                else:
                    colour = 'O'
                #thumbnailUrl = 'https://kollieflower.github.io/Artifact2/Images/Cards/MiniImage/' + card['miniimage'] + '.jpg'
                cardArtUrl = 'https://kollieflower.github.io/Artifact2/Images/Cards/CardArt/' + card['image'] + '.jpg'

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
                    colour = 'Gold'
                    colourCode = 0xccac00

                embed = discord.Embed(title=name, colour=colourCode)
                embed.add_field(name='Type', value=colour + ' ' + cardType, inline=False)

                if cardType == 'Hero':
                    abilityName = ''
                    abilityType = ''
                    abilityTrigger = ''
                    abilityEffect = ''
                    abilityText = ''
                    signatureName = ''
                    signatureText = ''
                    attack = card['attack']
                    armour = card['armour']
                    hp = card['hp']

                    for ability in card['abilities']:
                        abilityBase = int(ability.split('_')[0])
                        abilityVersion = int(ability.split('_')[1])
                        for ability in abilityList:
                            if ability['card_id'] == abilityBase:
                                ability = ability['versions'][-1]
                                abilityName = ability['ability_name']['english']
                                abilityType = ability['ability_type']
                                #abilityTrigger = ability['text']['english']['TG']
                                #abilityEffect = ability['text']['english']['ET']
                                abilityText = ability['text']['english']
                                abilityText = re.sub(r'/n', '', abilityText)
                                abilityText = re.sub(r'\[\w+\]', '', abilityText)
                                embed.add_field(name='Ability: ' + abilityName, value=abilityText, inline=False)
                    for signature in card['signature']:
                        signatureBase = int(signature.split('_')[0])
                        signatureVersion = int(signature.split('_')[1])
                        for signature in cardList:
                            if signature['card_id'] == signatureBase:
                                signature = signature['versions'][-1]
                                signatureName = signature['card_name']['english']
                                signatureText = signature['text']['english']
                                signatureText = re.sub(r'/n', '', signatureText)
                                signatureText = re.sub(r'\[\w+\]', '', signatureText)
                                embed.add_field(name='Signature: ' + signatureName, value=signatureText, inline=False)
                    embed.add_field(name='Attack', value=str(attack), inline=True)
                    embed.add_field(name='Armour', value=str(armour), inline=True)
                    embed.add_field(name='HP', value=str(hp), inline=True)                
                else:
                    cardText = card['text']['english']
                    cardText = re.sub(r'/n', '', cardText)
                    cardText = re.sub(r'\[ATT\]', ' Attack', cardText)
                    cardText = re.sub(r'\[AR\]', ' Armour', cardText)
                    cardText = re.sub(r'\[HP\]', ' HP', cardText)
                    cardText = re.sub(r'\[\w+\]', '', cardText)                    
                    manaCost = card['cost']
                    crosslane = card['crosslane']
                    if crosslane == 'true':
                        crosslane = 'Yes'
                    else:
                        crosslane = 'No'
                    embed.add_field(name='Mana', value=manaCost, inline=True)
                    embed.add_field(name='Crosslane', value=crosslane, inline=True)
                    embed.add_field(name='Card Text', value=cardText, inline=False)
                    if cardType == 'Creep':
                        attack = card['attack']
                        armour = card['armour']
                        hp = card['hp']
                        embed.add_field(name='Attack', value=attack, inline=True)
                        embed.add_field(name='Armour', value=armour, inline=True)
                        embed.add_field(name='HP', value=hp, inline=True)
                    if cardType == 'Item':
                        cardSubType = card['card_subtype']
                        goldCost = card['gcost']
                        attack = card['attack']
                        armour = card['armour']
                        hp = card['hp']
                        embed.insert_field_at(2, name='Gold', value=goldCost, inline=True)
                        if cardSubType == 'Weapon' or cardSubType == 'Armor' or cardSubType =='Accessory':
                            embed.add_field(name='Attack', value=attack, inline=True)
                            embed.add_field(name='Armour', value=armour, inline=True)
                            embed.add_field(name='HP', value=hp, inline=True)
                #embed.set_thumbnail(url=thumbnailUrl)
                embed.set_thumbnail(url=cardArtUrl)
                #embed.set_image(url=cardArtUrl)
    elif message.content.startswith('|') and message.content.endswith('|'):
        abilityQuery = re.search(r"\|(.+)\|", message.content).group(1)
        abilitiesRequest = requests.get(ABILITIES).text
        abilityList = json.loads(abilitiesRequest)
        for ability in abilityList:
            if ability['versions'][-1]['ability_name']['english'].lower() == abilityQuery.lower():
                cardType = ability['card_type']
                ability = ability['versions'][-1]
                abilityName = ability['ability_name']['english']
                abilityType = ability['ability_type']
                manaCost = ability['cost']
                abilityCD = ability['cooldown']
                abilityImage = ability['image']
                abilityText = ability['text']['english']
                colourCode = 0x2f4f4f
                abilityArtUrl = 'https://kollieflower.github.io/Artifact2/Images/Abilities/' + abilityImage + '.jpg'

                embed = discord.Embed(title=abilityName, colour=colourCode)
                embed.add_field(name='Type', value=cardType, inline=False)
                embed.add_field(name='Card Text', value=abilityText, inline=False)
                embed.add_field(name='Ability Type', value=abilityType, inline=True)
                embed.add_field(name='Mana', value=manaCost, inline=True)
                embed.add_field(name='Cooldown', value=abilityCD, inline=True)
                embed.set_thumbnail(url=abilityArtUrl)
    
    await message.channel.send(embed=embed)

client.run(config.BOT_TOKEN)