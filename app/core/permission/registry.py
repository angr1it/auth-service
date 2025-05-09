from enum import Enum

"""
Модуль для определения встроенных ресурсов и разрешений.

Classes:
    BuiltinResource: Перечисление встроенных ресурсов.
    OrganizationPermissions: Перечисление разрешений для ресурса 'organization'.

Variables:
    BUILTIN_PERMISSIONS (dict[str, list[str]]): Словарь встроенных разрешений для каждого ресурса.
"""

class BuiltinResource(str, Enum):
    organization = "organization"


class OrganizationPermissions(str, Enum):
    owner = "owner"


BUILTIN_PERMISSIONS: dict[str, list[str]] = {
    BuiltinResource.organization.value: [perm.value for perm in OrganizationPermissions],
}
