import valkey
import valkey.exceptions


# The CacheService must be a singleton because the valkey client isn't :(
class CacheService:

    __shared_instance = None

    @staticmethod
    def getInstance(connectionString: str, isCacheDisabled: bool, expirationTime: int):
        """Static Access Method"""
        if isCacheDisabled:
            return None
        if CacheService.__shared_instance == None:
            cacheService = CacheService(connectionString, expirationTime)
            CacheService.__shared_instance = cacheService
            return cacheService
        return CacheService.__shared_instance

    def __init__(self, connectionString: str, expirationTime: int):
        """virtual private constructor"""
        try:
            valkey_client = valkey.from_url(connectionString)
            valkey_client.ping() ## Test if the connectionString works, throws an exception if the connection failed
            self.__client = valkey_client
            self.__expirationTime = expirationTime
        except valkey.exceptions.AuthenticationError:
            raise Exception("The connection failed due to invalid connection string, if you are not intending on using the cache service please set the CACHE_DISABLED env variable to true.")
    
    def get(self, key: str) -> str:
        """gets a key's value"""
        val = self.__client.get(key)
        if val != None:
            val = val.decode('utf-8')
        return val

    def set(self, key: str, val: str):
        """set a key-val pair with an expiration date"""
        self.__client.setex(key, self.__expirationTime, val)

    def exist(self, key: str) -> bool:
        """checks if a key exists"""
        return self.__client.exists(key) == 1
    
    def getExpirationTime(self) -> str:
        """returns the expiration time in a readable date format"""
        DAY_IN_SEC = 60*60*24
        HOUR_IN_SEC = 3600
        MINUTE_IN_SEC = 60

        days = self.__expirationTime // DAY_IN_SEC
        hours = (self.__expirationTime % DAY_IN_SEC) // HOUR_IN_SEC
        minutes = (self.__expirationTime % HOUR_IN_SEC) // MINUTE_IN_SEC
        seconds = self.__expirationTime % MINUTE_IN_SEC

        output = ""
        if days > 0 :
            output += f"{days} d "
        if hours > 0 :
            output += f"{hours} h "
        if minutes > 0 :
            output += f"{minutes} mn "
        if seconds > 0:
            output += f"{seconds} s"

        return output.strip()
        