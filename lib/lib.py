from data.dto.dto import getUsername, getInfoForToken



async def authenticate_user(username, password):

    user = await getUsername(username)

    if(user == False):
        return False
    
    #if password is correct
    return True


async def getAccessToken(username):

    try:
        user = await getInfoForToken(username)
    except Exception as e:
        print("[Error]",e,"in",__file__)
        return 

    print("create access token >>", user)
    
    return "ACCESSTOKEN"