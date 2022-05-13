"""
The MIT License (MIT)
Copyright (c) 2021-present tag-epic
Permission is hereby granted, free of charge, to any person obtaining a
copy of this software and associated documentation files (the "Software"),
to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense,
and/or sell copies of the Software, and to permit persons to whom the
Software is furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.

Module to allow for backwards compatibility for existing code and extensions
"""

from nextcord import (ActionRow, Activity, ActivityType, AllowedMentions,
                      AppInfo, ApplicationCheckFailure, ApplicationCommand,
                      ApplicationCommandOptionType, ApplicationCommandType,
                      ApplicationError, ApplicationFlags,
                      ApplicationInvokeError, ApplicationSubcommand, Asset,
                      Attachment, AudioSource, AuditLogAction,
                      AuditLogActionCategory, AuditLogChanges, AuditLogDiff,
                      AuditLogEntry, AutoShardedClient, BanEntry, BaseActivity,
                      BotIntegration, Button, ButtonStyle, CategoryChannel,
                      ChannelType, Client, ClientCog, ClientException,
                      ClientUser, Color, Colour, CommandOption, Component,
                      ComponentType, ConnectionClosed, ContentFilter,
                      CustomActivity, DefaultAvatar, DeletedReferencedMessage,
                      DiscordException, DiscordServerError, DMChannel, Embed,
                      Emoji, EntityMetadata, Enum, ExpireBehavior,
                      ExpireBehaviour, FFmpegAudio, FFmpegOpusAudio,
                      FFmpegPCMAudio, File, Forbidden, Game, GatewayNotFound,
                      GroupChannel, Guild, GuildSticker, HTTPException,
                      Integration, IntegrationAccount, IntegrationApplication,
                      Intents, Interaction, InteractionMessage,
                      InteractionResponded, InteractionResponse,
                      InteractionResponseType, InteractionType,
                      InvalidArgument, InvalidCommandType, InvalidData, Invite,
                      InviteTarget, LoginFailure, Member, MemberCacheFlags,
                      Message, MessageFlags, MessageReference, MessageType,
                      NoMoreItems, NotFound, NotificationLevel, NSFWLevel,
                      Object, PartialAppInfo, PartialEmoji,
                      PartialInteractionMessage, PartialInviteChannel,
                      PartialInviteGuild, PartialMessage, PartialMessageable,
                      PartialWebhookChannel, PartialWebhookGuild, PCMAudio,
                      PCMVolumeTransformer, PermissionOverwrite, Permissions,
                      PrivilegedIntentsRequired, PublicUserFlags,
                      RawBulkMessageDeleteEvent, RawIntegrationDeleteEvent,
                      RawMemberRemoveEvent, RawMessageDeleteEvent,
                      RawMessageUpdateEvent, RawReactionActionEvent,
                      RawReactionClearEmojiEvent, RawReactionClearEvent,
                      RawTypingEvent, Reaction, Role, RoleTags, ScheduledEvent,
                      ScheduledEventEntityType, ScheduledEventPrivacyLevel,
                      ScheduledEventStatus, ScheduledEventUser, SelectMenu,
                      SelectOption, ShardInfo, SlashOption, SpeakingState,
                      Spotify, StageChannel, StageInstance, StagePrivacyLevel,
                      StandardSticker, Status, Sticker, StickerFormatType,
                      StickerItem, StickerPack, StickerType, Streaming,
                      StreamIntegration, SyncWebhook, SyncWebhookMessage,
                      SystemChannelFlags, Team, TeamMember,
                      TeamMembershipState, Template, TextChannel, TextInput,
                      TextInputStyle, Thread, ThreadMember, User, UserFlags,
                      VerificationLevel, VersionInfo, VideoQualityMode,
                      VoiceChannel, VoiceClient, VoiceProtocol, VoiceRegion,
                      VoiceState, Webhook, WebhookMessage, WebhookType, Widget,
                      WidgetChannel, WidgetMember, __path__, abc,
                      incompatible_libraries, message_command, opus,
                      slash_command, ui, user_command, utils, version_info)

__title__ = "nextcord"
__author__ = "tag-epic & Rapptz"
__license__ = "MIT"
__copyright__ = "Copyright 2015-present Rapptz & tag-epic"
__version__ = "2.0.0a10"

__path__ = __import__("pkgutil").extend_path(__path__, __name__)
