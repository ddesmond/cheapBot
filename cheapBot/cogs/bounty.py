import datetime
from typing import Dict, List
import discord
from discord.ext import commands
from .. import config
from secrets import choice
import os
import pickle
import json

cooldown_time = 1

class Bounty(commands.Cog):
  bot: commands.Bot
  allowed_channels: List[str]
  cooldowns: Dict[str, datetime.datetime]


  def __init__(self, bot: commands.Bot):
    super().__init__()
    self.bot = bot
    self.allowed_channels = config.allowed_party_channels
    self.cooldowns = {}

  def not_on_cooldown(self, addr: str) -> bool:
    if addr in self.cooldowns:
      if datetime.datetime.now() > self.cooldowns[addr]:
        self.cooldowns.pop(addr)
        return True
      else:
        return False
    return True

  # Get all bounties
  def get_bounties(self):
    # Load data (deserialize)
    with open('cheapBot/cogs/bounty_data/bounties.json') as json_file:
      return json.load(json_file)

  # Get bounty by position or name
  def get_bounty_by_id(self, id_position: str):
    # Load data (deserialize)
    for i, bounty in enumerate(self.get_bounties()["bounty_data"]):
      if str(i+1) == str(id_position):
        return(bounty)
      elif bounty["bounty_name"] == str(id_position):
        return(bounty)
      else:
        pass

  # write bounties to json
  def bounty_write_json(self, data): 
    with open('cheapBot/cogs/bounty_data/bounties.json','w') as f: 
      json.dump(data, f, indent=4)


  # append bounty data to current bounty dataset
  def append_bounty(self, new_data):
  # function to add to JSON 
    with open('cheapBot/cogs/bounty_data/bounties.json') as f: 
      data = json.load(f) 
        
      temp = data['bounty_data'] 
      # appending data to temp
      temp.append(new_data) 
          
    self.bounty_write_json(data)


  def pop_bounty(self, new_data):
  # function to add to JSON 
    with open('cheapBot/cogs/bounty_data/bounties.json') as f: 
      data = json.load(f) 
      # del, but remove -1 for order
      del data['bounty_data'][int(new_data)-1]
          
    self.bounty_write_json(data)


  # delete bounty, only a who made it can delete it
  def remove_from_bounty(self, id_position: str):
    # Load data (deserialize)
    for i, bounty in enumerate(self.get_bounties()["bounty_data"]):
      if str(i+1) == str(id_position):
        self.pop_bounty(str(i+1))
        return True

      elif bounty["bounty_name"] == str(id_position):
        self.pop_bounty(str(i+1))
        return True
      else:
        pass

  # update key value of a bounty
  def bounty_update_key_value(self, bounty_id, bkey, bvalue):
    data_to_update = self.get_bounty_by_id(bounty_id)
    data_to_update[bkey] = bvalue
    self.pop_bounty(bounty_id)
    self.append_bounty(data_to_update)


  # count total nums of bounties
  def count_bounties(self):
    length = len(self.get_bounties()['bounty_data'])
    return length


  # bounties have to be unique in name. So, we check if there is already one with same name
  def check_if_bounty_exists(self, name: str):
    # Load data (deserialize)
    for i, bounty in enumerate(self.get_bounties()["bounty_data"]):
      
      if bounty["bounty_name"] == name:
        return True




  # IMPORTANT: this was the on_message event, has been renamed to run to comply with repo's
  # program flow

  # BOUNTIES CODE BELOW!!

  @commands.command()
  async def bounty(self, ctx: commands.Context):
    """
    List bounties!
    """
    get_userid = ctx.message.author
    #print(get_userid)
    #print(self.count_bounties())
    if ctx.author.bot:
      return

    # Check if the address is on message
    if not ctx.message.content:
      return

    if ctx.channel.name in self.allowed_channels:
      message: discord.Message = ctx.message
      num_open = self.count_bounties()
      if num_open != 0:
      
        s = f'\n **{message.author.name}** asked for bounties. '
        s += f'\n **The Bounty** list:'
        s += f'\n There are {num_open} bounties!'
        for i, bounty in enumerate(self.get_bounties()["bounty_data"]):
          #print(bounty["bounty_name"])
          s += f'\n {i+1} - {bounty["bounty_name"]} - from {bounty["bounty_creator"]} - Value {bounty["bounty_value"]} cTH - Info: {bounty["bounty_description"]} - Status: {bounty["bounty_status"]}'

      else:
        s = f'\n There are 0 bounties! Try again later!'
      await message.channel.send(s)


  @commands.command()
  async def create_bounty(self, ctx: commands.Context):
    """
    Create a bounty! Format: Bounty name, Value in cTH, Description
    $cheap create_bounty Billiard-CTH, 199, little billiard in cth
    """
    get_userid = ctx.message.author
    bounty_creator = get_userid.name
    bounty_creator_id = get_userid.id

    if ctx.author.bot:
      return

    # Check if the address is on message
    if not ctx.message.content:
      return

    if ctx.channel.name in self.allowed_channels:
      message: discord.Message = ctx.message
      create_bounty_parse = ctx.message.content.replace("$cheap create_bounty ","").split(",")
      bounty_name = str(create_bounty_parse[0])
      bounty_value = str(create_bounty_parse[1])
      bounty_description = str(create_bounty_parse[2])
      grab_last_bounty = 0 #self.count_bounties()
      bounty_status = "started"
      bounty_assigne = ""
      bounty_payload = {"bounty_name": bounty_name,
                        "bounty_creator" : bounty_creator, 
                        "bounty_value" : bounty_value,
                        "bounty_description" : bounty_description,
                        "bounty_creator_id" : bounty_creator_id,
                        "bounty_status" : bounty_status, 
                        "bounty_assigne" : bounty_assigne}
      s = ""
      try:
        if self.check_if_bounty_exists(bounty_name) != True:
          self.append_bounty(bounty_payload)
          s += f'\n Your Bounty has been added to Bounty list, try $cheap bounty to see if all is OK.'
        else:
          s += f'\n Bounty with this name exists. Bounty not added. Check for unique bounty name.'
      except:
        s += f'\n Failed to enter bounty. Ask bot devs for help.'
      await message.channel.send(s)

  @commands.command()
  async def update_bounty(self, ctx: commands.Context):
    """
    Update your bounties status! Dont forget to pay you are due when youre Done!

    """

    get_userid = ctx.message.author
    #print(get_userid)
    if ctx.author.bot:
      return

    # Check if the address is on message
    if not ctx.message.content:
      return

    if ctx.channel.name in self.allowed_channels:
      message: discord.Message = ctx.message
      who_asks = get_userid.id
      bounty_parse = ctx.message.content.replace("$cheap update_bounty ","").split(" ")
      bounty_id = str(bounty_parse[0])
      bounty_status = str(bounty_parse[1])

      if bounty_id != None:
        bounty_from_data = self.get_bounty_by_id(str(bounty_id))
        #print(str(bounty_id))
        s = ''
        #print(bounty_from_data["bounty_creator_id"])

        if bounty_from_data["bounty_creator_id"] == who_asks:
          print("removing data")
          self.bounty_update_key_value(bounty_id,"bounty_status", bounty_status)
          print("done the bounty")
          s += f'\n Bounty updated! Thanks Robin.'
        else:
          s += f'\n You cannot update this bounty, since you have not created it. Sorry Boris. Bad day.'

        
        await message.channel.send(s)


  @commands.command()
  async def remove_bounty(self, ctx: commands.Context):
    """
    Remove your submitted bounty!
    Please enter ID or Bounty name:
    $cheap remove_bounty 1
    $cheap remove_bounty Cans
    """
    #print("remove bounty")
    get_userid = ctx.message.author
    #print(get_userid)
    if ctx.author.bot:
      return

    # Check if the address is on message
    if not ctx.message.content:
      return

    if ctx.channel.name in self.allowed_channels:
      message: discord.Message = ctx.message
      who_asks = get_userid.id
      bounty_parse = ctx.message.content.replace("$cheap remove_bounty ","").split(",")
      bounty_to_remove = bounty_parse[0]

      if str(bounty_to_remove) is None:
        await message.channel.send("Please enter ID or Bounty name. Thanks.")


      if bounty_to_remove != None:
        bounty_from_data = self.get_bounty_by_id(str(bounty_to_remove))
        print(str(bounty_from_data))
        s = ''
        #print(bounty_from_data["bounty_creator_id"])

        if bounty_from_data["bounty_creator_id"] == who_asks:
          print("removing data")
          
          self.remove_from_bounty(str(bounty_to_remove))
          s += f'\n You can remove this bounty, since you created it. Good job Lorrie.'
          s += f'\n Bounty removed.'
        else:
          s += f'\n You cannot remove this bounty, since you have not created it. Sorry Lorrie.'

        await message.channel.send(s)



  @commands.command()
  async def add_me_to_bounty(self, ctx: commands.Context):
    """
    Add yourself to a bounty and start working!
    """
    print("remove bounty")


  @commands.command()
  async def get_bounty(self, ctx: commands.Context):
    """
    Get bounty detail either by ID or name
    """
    get_userid = ctx.message.author
    #print(get_userid)
    if ctx.author.bot:
      return

    # Check if the address is on message
    if not ctx.message.content:
      return

    if ctx.channel.name in self.allowed_channels:
      message: discord.Message = ctx.message
      bounty_parse = ctx.message.content.replace("$cheap get_bounty ","").split(",")
      #print("PARSED User input:", bounty_parse[0])
      s = ''
      try:
        bounty = self.get_bounty_by_id(bounty_parse[0])
      #   #print("detail bounty")
        s = f"\n **{message.author.name}**, here is the Bounty you've asked for."
        s += f'\n {bounty["bounty_name"]} - from {bounty["bounty_creator"]} - Value {bounty["bounty_value"]} cTH - Info: {bounty["bounty_description"]} - Status: {bounty["bounty_status"]}'

      except:
        s += f'\n No bounty found. Sorry Lorrie.'

      await message.channel.send(s)