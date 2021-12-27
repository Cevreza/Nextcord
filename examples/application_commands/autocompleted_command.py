from nextcord import Interaction, SlashOption
from nextcord.ext import commands

bot = commands.Bot(command_prefix="$")  # won't let you do $my_slash_command

list_of_dog_breeds = [  # the list of dog breeds
    "German Shepard",
    "Poodle",
    "Pug",
    "Shiba Inu",
]


@bot.slash_command(guild_ids=[...])  # Limits guilds
async def your_favorite_dog(
    interaction: Interaction,
    dog: int = SlashOption(
        name="Your favorite dog",  # the name
        description="Choose the best dog from this autocompleted list!",  # our description
    ),
):  # our slash option.
    await interaction.response.send_message(
        f"your favorite dog is {dog}!"
    )  # sends the autocompleted result


@your_favorite_dog.on_autocomplete("dog")
async def favorite_dog(interaction: Interaction, dog):

    await interaction.response.send_autocomplete(list_of_dog_breeds)  
    # sending the list to discord.
