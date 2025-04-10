from auth.schemas.users import UserInfo


def is_superadmin(userInfo: UserInfo):

    return userInfo.get("role") == "super_admin"


def is_manager(userInfo: UserInfo):
    return userInfo.get("role") == "artist_manager"


def is_artist(userInfo: UserInfo):
    return userInfo.get("role") == "artist"
