from .admin import admin_handlers
from .profile import get_profile_handlers  # <- функция, а не переменная
from .gameplay import gameplay_handlers
from .economy import economy_handlers
from .combat import combat_handlers

all_commands = (
    *admin_handlers,
    *get_profile_handlers(),  # <- вызываем функцию
    *gameplay_handlers,
    *economy_handlers,
    *combat_handlers
)