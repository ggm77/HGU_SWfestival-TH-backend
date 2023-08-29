from ..dao.dao import getUserInfo

async def getUsername(username):

    #get user info from dao
    user = await getUserInfo(username)

    try:
        result = user["username"]
    except:
        return False
    
    return result

async def getInfoForToken(username):
    #get user info from dao
    user = await getUserInfo(username)
    
    try:
        result = {"username":user["username"], "userType":user["userType"], "disabled":user["disabled"]}
    except:
        return False
    
    return result