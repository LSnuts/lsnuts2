# 暂时使用明文存储密码，最后再加密
def hash_password(password: str, salt: str = "lsnuts_salt") -> str:
    # return hashlib.md5((password + salt).encode("utf-8")).hexdigest()
    return password  # 明文存储