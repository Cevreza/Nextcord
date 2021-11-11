from __future__ import annotations
import asyncio
from inspect import signature, Parameter
from typing import Any, Callable, Dict, List, Optional, Set, TYPE_CHECKING, Tuple, Union

from . import utils
from .abc import GuildChannel
from .enums import ApplicationCommandType, ApplicationCommandOptionType, ChannelType
from .interactions import Interaction
from .member import Member
from .message import Message
from .mixins import Hashable
from .role import Role
from .user import User

if TYPE_CHECKING:
    from .guild import Guild
    from .state import ConnectionState


__all__ = (
    'ApplicationCommandResponseOptionChoice',
    'ApplicationCommandResponseOption',
    'ApplicationCommandResponse',
    'SlashOption',
    'ApplicationCommand',
    'ApplicationSubcommand',
    'CommandOption',
    'ClientCog',
    'InvalidCommandType',
    'slash_command',
    'message_command',
    'user_command'
)


class InvalidCommandType(Exception):
    """Raised when an unhandled Application Command type is encountered."""
    pass


class ApplicationCommandResponse(Hashable):
    """Represents the response that Discord sends back when queried for Application Commands.

    Attributes
    ----------
    id: :class:`int`
        Discord ID of the Application Command.
    type: :class:`nextcord.ApplicationCommandType`
        Enum corresponding to the Application Command type. (slash, message, user)
    guild_id: Optional[:class:`int`]
        The Guild ID associated with the Application Command. If None, it's a global command.
    name: :class:`str`
        Name of the Application Command.
    description: :class:`str`
        Description of the Application Command.
    options: List[:class:`nextcord.ApplicationCommandResponseOption`]
        A list of options or subcommands that the Application Command has.
    default_permission: :class:`bool`
        If the command is enabled for users by default.
    """

    def __init__(self, state: ConnectionState, payload: dict):
        self._state: ConnectionState = state
        self.id: int = int(payload["id"])
        self.type: ApplicationCommandType = ApplicationCommandType(payload["type"])
        self.guild_id: Optional[int] = utils._get_as_snowflake(payload, "guild_id")
        self.name: str = payload["name"]
        self.description: str = payload["description"]
        self.options: List[
            ApplicationCommandResponseOption
        ] = ApplicationCommandResponseOption._create_options(payload.get("options", []))
        self.default_permission: Optional[bool] = payload.get(
            "default_permission", True
        )

    @property
    def guild(self) -> Optional[Guild]:
        """Optional[:class:`Guild`]: Returns the :class:`Guild` associated with this Response, if any."""
        return self._state._get_guild(self.guild_id)

    @property
    def signature(self) -> Tuple[str, int, Optional[int]]:
        """Returns a simple high level signature of the command. No commands registered in the bot at the same time
        should have identical signatures.

        Returns
        -------
        name: :class:`str`
            Name of the Application Command.
        type: :class:`int`
            Discord's integer value of the Application Command type
        guild_id: Optional[:class:`int`]
            The Guild ID associated with the Application Command. If None, it's a global command.
        """
        return self.name, self.type.value, self.guild_id


class ApplicationCommandResponseOptionChoice:
    """Represents a single choice in a list of options.

    Attributes
    ----------
    name: :class:`str`
        Name of the choice, this is what users see in Discord.
    value: Union[:class:`str`, :class:`int`, :class:`float`]
        Value of the choice, this is what Discord sends back to us.
    """

    def __init__(self, payload: Optional[dict] = None):
        if not payload:
            payload = {}
        self.name: str = payload.get('name')
        self.value: Union[str, int, float] = payload.get('value')


class ApplicationCommandResponseOption:
    """Represents an argument/parameter/option or subcommand of an Application Command.

    Attributes
    ----------
    type: :class:`ApplicationCommandOptionType`
        Enum corresponding to the Application Command Option type. (subcommand, string, integer, etc.)
    name: :class:`str`
        Name of the option or subcommand.
    description: :class:`str`
        Description of the option or subcommand.
    required: :class:`bool`
        If this option is required for users or not.
    """

    def __init__(self, payload: dict):
        self.type = ApplicationCommandOptionType(int(payload["type"]))
        self.name: str = payload['name']
        self.description: str = payload['description']
        self.required: Optional[bool] = payload.get('required')
        self.choices: List[ApplicationCommandResponseOptionChoice] = self._create_choices(payload.get('choices', []))
        self.options: List[ApplicationCommandResponseOption] = self._create_options(payload.get('options', []))

    @staticmethod
    def _create_choices(data: List[dict]) -> List[ApplicationCommandResponseOptionChoice]:
        return [ApplicationCommandResponseOptionChoice(raw_choice) for raw_choice in data]

    @staticmethod
    def _create_options(data: List[dict]) -> List[ApplicationCommandResponseOption]:
        return [ApplicationCommandResponseOption(raw_option) for raw_option in data]


class ClientCog:
    # TODO: I get it's a terrible name, I just don't want it to duplicate current Cog right now.
    __cog_application_commands__: Dict[int, ApplicationCommand]
    __cog_to_register__: List[ApplicationCommand]

    def __new__(cls, *args, **kwargs):
        new_cls = super(ClientCog, cls).__new__(cls)
        new_cls._read_methods()
        return new_cls

    def _read_methods(self):
        self.__cog_to_register__ = []
        for base in reversed(self.__class__.__mro__):
            for elem, value in base.__dict__.items():
                is_static_method = isinstance(value, staticmethod)
                if is_static_method:
                    value = value.__func__
                if isinstance(value, ApplicationCommand):
                    if isinstance(value, staticmethod):
                        raise TypeError(f"Command {self.__name__}.{elem} can not be a staticmethod.")
                    value.cog_parent = self
                    self.__cog_to_register__.append(value)
                elif isinstance(value, ApplicationSubcommand):
                    value.cog_parent = self

    @property
    def to_register(self) -> List[ApplicationCommand]:
        return self.__cog_to_register__


class SlashOption:
    def __init__(self, name: str = None, description: str = None, required: bool = None, choices: dict = None,
                 default: Any = None, channel_types: List[ChannelType, ...] = None):
        """Provides Discord with information about an option in a command.

        When this class is set as the default argument of a parameter in an Application Command, additional information
        about the parameter is sent to Discord for the user to see.

        Parameters
        ----------
        name: Optional[:class:`str`]
            The name of the Option on Discords side. If left as None, it defaults to the parameter name.
        description: Optional[:class:'str']
            The description of the Option on Discords side. If left as None, it defaults to "".
        required: Optional[:class:'bool']
            If a user is required to provide this argument before sending the command. Defaults to Discords choice. (False at this time)
        choices: Optional[:class:`bool`]
            Dictionary of choices. The keys are what the user sees, the values correspond to what is sent to us.
        default: Optional[Any]
            When required is not True and the user doesn't provide a value for this Option, this value is given instead.
        channel_types: Optional[List[:class:`enums.ChannelType`]]
            The list of valid channel types for the user to choose from. Used only by channel Options.
        """
        if not choices:
            choices = []
        self.name: Optional[str] = name
        self.description: Optional[str] = description
        self.required: Optional[bool] = required
        self.choices: Optional[dict] = choices
        self.default: Optional[Any] = default
        self.channel_types: Optional[List[ChannelType, ...]] = channel_types


class CommandOption(SlashOption):
    option_types = {
        str: ApplicationCommandOptionType.string,
        int: ApplicationCommandOptionType.integer,
        bool: ApplicationCommandOptionType.boolean,
        User: ApplicationCommandOptionType.user,
        Member: ApplicationCommandOptionType.user,
        GuildChannel: ApplicationCommandOptionType.channel,
        Role: ApplicationCommandOptionType.role,
        # TODO: Is this in the library at all currently? This includes Users and Roles.
        # Mentionable: CommandOptionType.mentionable
        float: ApplicationCommandOptionType.number,
        Message: ApplicationCommandOptionType.integer  # TODO: This is janky, the user provides an ID or something? Ugh.
    }
    """Maps Python typings to Discord Application Command typings."""
    def __init__(self, parameter: Parameter):
        """Represents a Python function parameter that corresponds to a Discord Option.

        This must set and/or handle all variables from CmdArg, hence the subclass.
        This shouldn't be created by the user, only by other Application Command-related classes.

        Parameters
        ----------
        parameter: :class:`inspect.Parameter`
            The Application Command Parameter object to read and make usable by Discord.
        """
        super().__init__()
        self.parameter = parameter
        cmd_arg_given = False
        cmd_arg = SlashOption()
        if isinstance(parameter.default, SlashOption):
            cmd_arg = parameter.default
            cmd_arg_given = True
        self.functional_name = parameter.name

        # TODO: Cleanup logic for this.
        # All optional variables need to default to None for functions down the line to understand that they were never
        # set. If Discord demands a value, it should be the minimum value required.
        self.name = cmd_arg.name if cmd_arg.name is not None else parameter.name
        self.description = cmd_arg.description if cmd_arg.description is not None else " "
        self.required = cmd_arg.required if cmd_arg.required is not None else None
        self.choices = cmd_arg.choices if cmd_arg.choices is not None else {}
        if not cmd_arg_given and parameter.default is not parameter.empty:
            self.default = parameter.default
        else:
            self.default = cmd_arg.default
        if self.default is None and cmd_arg.required in (None, True):
            self.required = True
        self.channel_types = cmd_arg.channel_types if cmd_arg.channel_types is not None else []
        self.type: ApplicationCommandOptionType = self.get_type(parameter.annotation)
        self.verify()

    def get_type(self, typing: type) -> ApplicationCommandOptionType:

        if typing is self.parameter.empty:
            return ApplicationCommandOptionType.string
        elif valid_type := self.option_types.get(typing, None):
            return valid_type
        else:
            raise NotImplementedError(f"Type \"{typing}\" isn't a supported typing for Application Commands.")

    def verify(self):
        """This should run through CmdArg variables and raise errors when conflicting data is given."""
        if self.channel_types and self.type is not ApplicationCommandOptionType.channel:
            raise ValueError("channel_types can only be given when the var is typed as nextcord.abc.GuildChannel")

    def handle_slash_argument(self, state: ConnectionState, argument: Any, interaction: Interaction) -> Any:
        """Handles arguments, specifically for Slash Commands."""
        if self.type is ApplicationCommandOptionType.channel:
            return state.get_channel(int(argument))
        elif self.type is ApplicationCommandOptionType.user:
            if interaction.guild:
                return interaction.guild.get_member(int(argument))
            else:
                return state.get_user(int(argument))
        elif self.type is ApplicationCommandOptionType.role:
            return interaction.guild.get_role(int(argument))
        elif self.type is ApplicationCommandOptionType.integer:
            return int(argument)
        elif self.type is ApplicationCommandOptionType.number:
            return float(argument)
        elif self.type is Message:  # TODO: This is mostly a workaround for Message commands, switch to handles below.
            return state._get_message(int(argument))
        return argument

    def handle_message_argument(self, *args):
        """For possible future use, will handle arguments specific to Message Commands (Context Menu type.)"""
        raise NotImplementedError  # TODO: Even worth doing? We pass in what we know already.

    def handle_user_argument(self, *args):
        """For possible future use, will handle arguments specific to User Commands (Context Menu type.)"""
        raise NotImplementedError  # TODO: Even worth doing? We pass in what we know already.

    @property
    def payload(self) -> dict:
        """Returns a payload meant for Discord for this specific Option.

        Options that are not specified AND not required won't be in the returned payload.

        Returns
        -------
        payload: :class:`dict`
            The Discord payload for this specific Option.
        """
        # TODO: Figure out why pycharm is being a dingus about self.type.value being an unsolved attribute.
        # noinspection PyUnresolvedReferences
        ret = {"type": self.type.value, "name": self.name, "description": self.description}
        if self.required is not None:
            ret["required"] = self.required
        if self.choices:
            ret["choices"] = [{"name": key, "value": value} for key, value in self.choices.items()]
        if self.channel_types:
            # noinspection PyUnresolvedReferences
            ret["channel_types"] = [channel_type.value for channel_type in self.channel_types]
        # We don't ask for the payload if we have options, so no point in checking for options.
        return ret


class ApplicationSubcommand:
    def __init__(self, callback: Callable, parent: Optional[Union[ApplicationCommand, ApplicationSubcommand]],
                 cmd_type: Union[ApplicationCommandType, ApplicationCommandOptionType],
                 cog_parent: Optional[ClientCog] = None, name: str = "", description: str = "",
                 choices: Optional[Dict[str, Any]] = None):
        """Represents a Python function that corresponds to a Discord Subcommand (Group). Turns a given function into
        a class able to feed Discord-given arguments to an async function.

        This contains the base methods that both regular application commands and subcommands need to have access to.
        This shouldn't be created by the user, only by other Application Command-related classes.

        Parameters
        ----------
        callback: Callable
            The function to call when the subcommand is triggered. Must be a coroutine.
        parent: Optional[Union[:class:`ApplicationCommand`, :class:`ApplicationSubcommand`]]
            Parent command or subcommand.
        cmd_type: Union[:class:`ApplicationCommandType`, :class:`ApplicationCommandOptionType`]
            Application Command type, or specific Application Command Option types.
        cog_parent: Optional[:class:`ClientCog`]
            Cog parent, supplied as the first argument to the callback if provided.
        name: :class:`str`
            Name of the command on Discord. Defaults to the name of the callback.
        description: :class:`str`
            Description of the command on Discord, if applicable. Defaults to an empty string.
        choices: Optional[Dict[:class:`str`, Any]]
            A dictionary of choices. Keys are the Discord-facing name of the choice, the values are what Discord sends
            back.
        """
        if not asyncio.iscoroutinefunction(callback):
            raise TypeError("Callback must be a coroutine.")

        self._parent: Union[ApplicationCommand, ApplicationSubcommand] = parent
        self._callback: Callable = callback

        self.type: Union[ApplicationCommandType, ApplicationCommandOptionType] = cmd_type
        self.name: str = name
        self.description: str = description
        self.choices: Dict[str, Any] = choices

        self.cog_parent: Optional[ClientCog] = cog_parent
        self.arguments: Dict[str, CommandOption] = {}
        self.children: Dict[str, ApplicationSubcommand] = {}
        self._analyze_content()
        self._analyze_callback()

    def _analyze_content(self):
        """This reads the content of itself and performs validation and changes to variables as needed."""
        if self._parent and self._parent.type is ApplicationCommandOptionType.sub_command_group and self.children:
            raise NotImplementedError("A subcommand can't have both subcommand parents and children! Discord does not"
                                      "support this.")
        if isinstance(self._parent, ApplicationCommand):
            if self.children:
                self.type = ApplicationCommandOptionType.sub_command_group
            else:
                self.type = ApplicationCommandOptionType.sub_command
        if self.type is ApplicationCommandType.user or self.type is ApplicationCommandType.message:
            self.description = ""
        else:
            if not self.description:
                self.description = " "

    def _analyze_callback(self):
        """This reads the callback, performs validation, and changes variables as needed."""
        if not self.name:
            self.name = self._callback.__name__
        first_arg = True

        for value in signature(self.callback).parameters.values():
            self_skip = value.name == "self"  # TODO: What kind of hardcoding is this, figure out a better way for self!
            if first_arg:
                # TODO: Is this even worth having?
                if value.annotation is not value.empty and value.annotation is not Interaction:
                    raise TypeError("The first argument in an Application Command should be typed as an Interaction")
                if not self_skip:
                    first_arg = False
            else:
                arg = CommandOption(value)
                self.arguments[arg.name] = arg

    @property
    def callback(self) -> Callable:
        return self._callback

    async def call(self, state: ConnectionState, interaction: Interaction, option_data: List[Dict[str, Any]]):
        """Calls the callback, gathering and inserting kwargs into the callback as needed.
        This must be able to call itself as subcommands may be subcommand groups, and thus have subcommands of their
        own.

        Parameters
        ----------
        state: :class:`ConnectionState`
            State object used to fetch Guild, Channel, etc from cache.
        interaction: :class:`Interaction`
            Interaction object to pass to callback.
        option_data: :class:`list`
            List of option data dictionaries from interaction data payload.
        """
        if self.children:
            # Discord currently does not allow commands that have subcommands to be ran. Therefore, if a command has
            # children, a subcommand must be being called.
            await self.children[option_data[0]["name"]].call(state, interaction, option_data[0].get("options", {}))
        elif self.type in (ApplicationCommandType.chat_input, ApplicationCommandOptionType.sub_command):
            # Slash commands are able to have subcommands, therefore that is handled here.
            await self.call_invoke_slash(state, interaction, option_data)
        else:
            # Anything that can't be handled in here should be raised for ApplicationCommand to handle.
            # TODO: Figure out how to hide this in exception trace log, devs don't need to see it.
            raise InvalidCommandType(f"{self.type} is not a handled Application Command type.")

    async def call_invoke_slash(self, state: ConnectionState, interaction: Interaction,
                                option_data: List[Dict[str, Any]]):
        """This invokes the slash command implementation with the given raw option data to turn into proper kwargs for
        the callback.

        Parameters
        ----------
        state: :class:`ConnectionState`
            State object used to fetch Guild, Channel, etc from cache.
        interaction: :class:`Interaction`
            Interaction object to pass to the callback.
        option_data: :class:`list`
            List of option data dictionaries from interaction data payload.
        """
        kwargs = {}
        uncalled_args = self.arguments.copy()
        for arg_data in option_data:
            if arg_data["name"] in uncalled_args:
                uncalled_args.pop(arg_data["name"])
                kwargs[self.arguments[arg_data["name"]].functional_name] = \
                    self.arguments[arg_data["name"]].handle_slash_argument(state, arg_data["value"], interaction)
            else:
                # TODO: Handle this better.
                raise NotImplementedError(f"An argument was provided that wasn't already in the function, did you"
                                          f"recently change it?\nRegistered Args: {self.arguments}, Discord-sent"
                                          f"args: {interaction.data['options']}, broke on {arg_data}")
        for uncalled_arg in uncalled_args.values():
            kwargs[uncalled_arg.functional_name] = uncalled_arg.default
        await self.invoke_slash(interaction, **kwargs)

    async def invoke_slash(self, interaction: Interaction, **kwargs):
        """Invokes the callback with the kwargs given."""
        if self.cog_parent:
            await self.callback(self.cog_parent, interaction, **kwargs)
        else:
            await self.callback(interaction, **kwargs)

    def error(self, coro):
        # TODO: Parity with legacy commands.
        raise NotImplementedError

    @property
    def payload(self) -> dict:
        """:class:`dict`: Outputs a Discord "Application Command Option Structure" payload."""
        self._analyze_content()
        ret = {"type": self.type.value, "name": self.name, "description": self.description}
        if self.choices:
            ret["choices"] = [{key: value} for key, value in self.choices.items()]
        if self.children:
            ret["options"] = [child.payload for child in self.children.values()]
        elif self.arguments:
            ret["options"] = [argument.payload for argument in self.arguments.values()]
        return ret

    def subcommand(self, **kwargs):
        """Creates a new subcommand off of this one."""
        def decorator(func: Callable):
            result = ApplicationSubcommand(func, self, ApplicationCommandOptionType.sub_command, **kwargs)
            self.children[result.name] = result
            return result
        return decorator


class ApplicationCommand(ApplicationSubcommand):
    def __init__(self, callback: Callable, cmd_type: ApplicationCommandType,
                 name: str = "", description: str = "", guild_ids: List[int] = None, force_global: bool = False,
                 default_permission: Optional[bool] = None):
        super().__init__(callback=callback, parent=None, cmd_type=cmd_type, name=name, description=description)
        # Basic input checking.
        if guild_ids is None:
            guild_ids = []
        self._state: Optional[ConnectionState] = None  # TODO: I thought there was a way around doing this, but *sigh*.
        self._is_global: Optional[bool] = True if (guild_ids and force_global) or (not guild_ids) else False
        self._is_guild: Optional[bool] = True if guild_ids else False

        self.default_permission: Optional[bool] = default_permission
        self.guild_ids: List[int] = guild_ids
        self.type = cmd_type
        self._global_id: Optional[int] = None
        self._guild_ids: Dict[int, int] = {}  # Guild ID is key, command ID is value.

    def parse_response(self, response: ApplicationCommandResponse):
        """Takes information from an :class:`ApplicationCommandResponse` and parses it for use."""
        self.raw_parse_result(response._state, response.guild_id, response.id)

    def raw_parse_result(self, state: ConnectionState, guild_id: Optional[int], command_id: int):
        """Takes direct information and uses it. Use when getting a :class:`ApplicationCommandResponse` is unreasonable.

        Parameters
        ----------
        state: :class:`ConnectionState`
            State object used to fetch cached data.
        guild_id: Optional[:class:`int`]
            Guild ID the Application Command corresponds to. If None, it's assumed to be Global.
        command_id: :class:`int`
            Command ID from Discord that corresponds to this object.
        """
        self._state = state
        if guild_id:
            self._guild_ids[guild_id] = command_id
        else:
            self._global_id = command_id

    async def call_from_interaction(self, interaction: Interaction):
        """Runs call using the held ConnectionState object and given interaction."""
        if not self._state:
            raise NotImplementedError("State hasn't been set yet, this isn't handled yet!")
        await self.call(self._state, interaction, interaction.data.get("options", {}))

    async def call(self, state: ConnectionState, interaction: Interaction, option_data: List[Dict[str, Any]]):
        """|coro|

            Calls the callback, gathering and inserting kwargs into the callback as needed.
            This handles CommandTypes that subcommands cannot handle, such as Message or User commands.

            state: :class:`ConnectionState`
                ConnectionState to fetch objects from cache.
            interaction: :class:`Interaction`
                Current Interaction object.
            option_data: List[Dict[:class:`str`, Any]]
                List of options, typically 'options' in the interaction data payload.
            """
        try:
            await super().call(state, interaction, option_data)
        except InvalidCommandType:
            if self.type is ApplicationCommandType.message:
                await self.call_invoke_message(interaction)
            elif self.type is ApplicationCommandType.user:
                await self.call_invoke_user(interaction)
            else:
                raise InvalidCommandType(f"{self.type} is not a handled Application Command type.")

    def _handle_resolved_message(self, message_data: dict) -> Message:
        """Adds found message data and adds it to the internal cache.

        Parameters
        ----------
        message_data: :class:`dict`
            The resolved message payload to add to the internal cache.

        Returns
        -------
        :class:`Message`
            The Python representation of a Discord message.
        """
        # TODO: This is garbage, find a better way to add a Message to the cache.
        #  It's not that I'm unhappy adding things to the cache, it's having to manually do it like this.
        # The interaction gives us message data, might as well use it and add it to the cache?
        channel, guild = self._state._get_guild_channel(message_data)
        message = Message(channel=channel, data=message_data, state=self._state)
        if not self._state._get_message(message.id) and self._state._messages is not None:
            self._state._messages.append(message)
        return message

    def _handle_resolved_user(self, user_data: dict) -> User:
        """

        Parameters
        ----------
        user_data: :class:`dict`
            The resolved user payload to add to the internal cache.

        Returns
        -------
        :class:`User`
            Represents a Discord user.
        """
        return self._state.store_user(user_data)

    async def call_invoke_message(self, interaction: Interaction):
        """Interprets the given interaction and invokes the callback as a Message Command."""
        # TODO: Look into function arguments being autoconverted and given? Arg typed "Channel" gets filled with the
        #  channel?
        # Is this kinda dumb? Yeah, but at this time it can only return one message.
        message = self._handle_resolved_message(list(interaction.data["resolved"]["messages"].values())[0])
        await self.invoke_message(interaction, message)

    async def call_invoke_user(self, interaction: Interaction):
        """Interprets the given interaction and invokes the callback as a User Command."""
        # TODO: Look into function arguments being autoconverted and given? Arg typed "Channel" gets filled with the
        #  channel?
        # Is this kinda dumb? Yeah, but at this time it can only return one user.
        user = self._handle_resolved_user(list(interaction.data["resolved"]["users"].values())[0])
        if interaction.guild and (member := interaction.guild.get_member(user.id)):
            await self.invoke_user(interaction, member)
        else:
            await self.invoke_user(interaction, user)

    async def invoke_message(self, interaction: Interaction, message: Message, **kwargs):
        """Invokes the callback with the given interaction, message, and kwargs as a Message Command."""
        if self.cog_parent:
            await self.callback(self.cog_parent, interaction, message, **kwargs)
        else:
            await self.callback(interaction, message, **kwargs)

    async def invoke_user(self, interaction: Interaction, member: Union[Member, User], **kwargs):
        """Invokes the callback with the given interaction, member/user, and kwargs as a User Command."""
        if self.cog_parent:
            await self.callback(self.cog_parent, interaction, member, **kwargs)
        else:
            await self.callback(interaction, member, **kwargs)

    def _get_basic_application_payload(self) -> dict:
        """Bare minimum payload that both Global and Guild commands can use."""
        payload = super().payload
        if self.type is not ApplicationCommandType.chat_input and "options" in payload:
            payload.pop("options")
        if self.default_permission is not None:
            payload["default_permission"] = self.default_permission
        return payload

    @property
    def payload(self) -> List[dict]:
        """Returns a list of Discord "Application Command Structure" payloads.

        Returns
        -------
        payloads: List[:class:`dict`]
            Returns a list containing the global command payload, if enabled, and payloads corresponding to every guild
            ID specified.
        """
        # TODO: This always returns a list, should it be "payloads"? Won't override subcommand payload though.
        partial_payload = self._get_basic_application_payload()

        ret = []
        if self.is_guild:
            for guild_id in self.guild_ids:
                temp = partial_payload.copy()  # This shouldn't need to be a deep copy as guild_id is on the top layer.
                temp["guild_id"] = guild_id
                ret.append(temp)
        if self.is_global:
            ret.append(partial_payload)
        return ret

    def get_guild_payload(self, guild_id: int) -> dict:
        """Creates a payload specific to a guild.

        Parameters
        ----------
        guild_id: :class:`int`
            Guild ID to create the payload for. Must be added to the ApplicationCommand.

        Returns
        -------
        :class:`dict`
            A Discord "Application Command Structure" payload specifically for a given Guild ID.
        """
        if not self.is_guild or guild_id not in self.guild_ids:
            raise NotImplementedError  # TODO: Make a proper error.
        partial_payload = self._get_basic_application_payload()
        partial_payload["guild_id"] = guild_id
        return partial_payload

    @property
    def global_payload(self) -> dict:
        """Creates a Discord "Application Command Structure" payload for a Global command."""
        if not self.is_global:
            raise NotImplementedError  # TODO: Make a proper error.
        return self._get_basic_application_payload()

    @property
    def is_guild(self) -> bool:
        return self._is_guild

    @property
    def is_global(self) -> bool:
        return self._is_global

    def get_signature(self, guild_id: Optional[int]) -> Optional[Tuple[str, int, Optional[int]]]:
        """Returns a basic signature for a given Guild ID. If None is given, then it is assumed Global."""
        if (guild_id is None and self.is_global) or (guild_id in self.guild_ids):
            return self.name, self.type.value, guild_id
        else:
            return None

    def get_signatures(self) -> Set[Tuple[str, int, Optional[int]]]:
        """Returns all basic signatures for this ApplicationCommand."""
        ret = set()
        if self.is_global:
            ret.add((self.name, self.type.value, None))
        if self.is_guild:
            for guild_id in self.guild_ids:
                ret.add((self.name, self.type.value, guild_id))
        return ret

    def check_against_raw_payload(self, raw_payload: dict, guild_id: Optional[int]) -> bool:
        """Checks if self.payload values match with what the given raw payload has.

        This doesn't make sure they are equal. Instead, this checks if all key:value pairs inside of any of our payloads
        also exist inside of the raw_payload. If there are extra keys inside of the raw_payload that aren't in our
        payloads, they will be ignored.


        Parameters
        ----------
        raw_payload: :class:`dict`
            Dictionary payload our payloads are compared against.
        guild_id: Optional[:class:`int`]
            Guild ID to compare against. If None, it's assumed to be a Global command.

        Returns
        -------
        :class:`bool`
            True if any of our payloads has every key:value pair corresponding with key:value's in the raw_payload,
            False otherwise.
        """
        our_payloads = self.payload
        for our_payload in our_payloads:
            if our_payload.get("guild_id", None) == guild_id:
                if self._recursive_item_check(our_payload, raw_payload):
                    return True
        return False

    def reverse_check_against_raw_payload(self, raw_payload: dict, guild_id: Optional[int]) -> bool:
        """Checks if the given raw payload values match with what self.payload has.

        This doesn't make sure they are equal, and works opposite of check_against_raw_payload. This checks if all
        key:value's inside of the raw_payload also exist inside one of our payloads.

        Parameters
        ----------
        raw_payload: :class:`dict`
            Dictionary payload to compare against our payloads.
        guild_id: :class:`int`
            Guild ID to compare against. If None, it's assumed to be a Global command.

        Returns
        -------
        :class:`bool`
            True if the raw_payload has every key:value pair corresponding to any of our payloads, False otherwise.
        """
        modded_payload = raw_payload.copy()
        modded_payload.pop("id")
        for our_payload in self.payload:
            if our_payload.get("guild_id", None) == guild_id:
                if self._recursive_item_check(modded_payload, our_payload):
                    return True
        return False

    def _recursive_item_check(self, item1, item2) -> bool:
        """Checks if item1 and item2 are equal.

        If both are lists, switches to list check. If dict, recurses. Else, checks equality.
        """
        if isinstance(item1, dict) and isinstance(item2, dict):
            for key, item in item1.items():
                if key == "value":
                    pass
                elif key not in item2:
                    return False
                elif not self._recursive_item_check(item, item2[key]):
                    return False
        elif isinstance(item1, list) and isinstance(item2, list):
            for our_item in item1:
                if not self._recursive_check_item_against_list(our_item, item2):
                    return False
        else:
            if isinstance(item1, str) and item1.isdigit():
                item1 = int(item1)
            if isinstance(item2, str) and item2.isdigit():
                item2 = int(item2)
            if item1 != item2:
                return False
        return True

    def _recursive_check_item_against_list(self, item1, list2: list) -> bool:
        if isinstance(item1, list):
            raise NotImplementedError
        elif isinstance(item1, dict):
            for item2 in list2:
                if isinstance(item2, list):
                    raise NotImplementedError
                elif isinstance(item2, dict):
                    if self._recursive_item_check(item1, item2):
                        return True
                else:
                    raise NotImplementedError
        else:
            raise NotImplementedError
        return False

    def subcommand(self, **kwargs):
        """Makes a function into a subcommand."""
        if self.type != ApplicationCommandType.chat_input:  # At this time, non-slash commands cannot have Subcommands.
            raise TypeError(f"{self.type} cannot have subcommands.")
        else:
            def decorator(func: Callable):
                result = ApplicationSubcommand(func, self, ApplicationCommandOptionType.sub_command, **kwargs)
                self.children[result.name] = result
                return result

            return decorator


def slash_command(*args, **kwargs):
    """Creates a Slash Application Command, used inside of a ClientCog."""
    def decorator(func: Callable):
        if isinstance(func, ApplicationCommand):
            raise TypeError("Callback is already an ApplicationCommandRequest.")
        return ApplicationCommand(func, cmd_type=ApplicationCommandType.chat_input, *args, **kwargs)
    return decorator


def message_command(*args, **kwargs):
    """Creates a Message Application Command, used inside of a ClientCog."""
    def decorator(func: Callable):
        if isinstance(func, ApplicationCommand):
            raise TypeError("Callback is already an ApplicationCommandRequest.")
        return ApplicationCommand(func, cmd_type=ApplicationCommandType.message, *args, **kwargs)
    return decorator


def user_command(*args, **kwargs):
    """Creates a User Application Command, used inside of a ClientCog."""
    def decorator(func: Callable):
        if isinstance(func, ApplicationCommand):
            raise TypeError("Callback is already an ApplicationCommandRequest.")
        return ApplicationCommand(func, cmd_type=ApplicationCommandType.user, *args, **kwargs)
    return decorator


def options_to_args(options: List[Dict[str, Any]]) -> Dict[str, Any]:
    return {option["name"]: option["value"] for option in options}
