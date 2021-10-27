from fastapi_users import models

class DefaultUser(models.BaseUser):
    pass

class DefaultUserCreate(models.BaseUserCreate):
    pass

class DefaultUserUpdate(models.BaseUserUpdate):
    pass

class DefaultUserDB(User, models.BaseUserDB):
    pass

# models.BaseUser.__fields__