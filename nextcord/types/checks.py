# SPDX-License-Identifier: MIT

from typing import TYPE_CHECKING, Any, Callable, Coroutine, TypeVar, Union

if TYPE_CHECKING:
    from nextcord.application_command import (
        BaseApplicationCommand,
        ClientCog,
        SlashApplicationSubcommand,
    )

    from ..ext.application_checks.core import CheckWrapper
    from ..interactions import Interaction

    T = TypeVar("T")

    Coro = Coroutine[Any, Any, T]
    MaybeCoro = Union[T, Coro[T]]
    CoroFunc = Callable[..., Coro[Any]]

    ApplicationCheck = Union[
        Callable[[ClientCog, Interaction], MaybeCoro[bool]],
        Callable[[Interaction], MaybeCoro[bool]],
        Callable[
            [
                Union[
                    CoroFunc,
                    Callable[[Interaction], bool],
                    BaseApplicationCommand,
                    SlashApplicationSubcommand,
                ]
            ],
            CheckWrapper,
        ],
    ]
    ApplicationHook = Union[
        Callable[[ClientCog, Interaction], Coro[Any]], Callable[[Interaction], Coro[Any]]
    ]
    ApplicationErrorCallback = Union[
        Callable[[ClientCog, Interaction, Exception], Coro[Any]],
        Callable[[Interaction, Exception], Coro[Any]],
    ]
