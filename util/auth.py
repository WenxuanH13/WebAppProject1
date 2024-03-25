def extract_credentials(request):
    bodyString = request.body.decode()
    usernamePair, passwordPair = bodyString.split('&',1)

    name = usernamePair.split('=')[1]
    username = name
    word = passwordPair.split('=')[1]
    password = word.replace('%21', '!').replace('%40', '@').replace('%23', '#').replace('%24', '$').replace('%5E', '^').replace('%26', '&').replace('%28', '(').replace('%29', ')').replace('%2D', '-').replace('%5F', '_').replace('%3D', '=').replace('%25', '%')

    return [username, password]


def validate_password(password):
    if len(password) < 8:
        return False
    
    lowerCase = {'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z'}
    upperCase = {'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z'}
    numbers = {'0', '1', '2', '3', '4', '5', '6', '7', '8', '9'}
    specialCharacters = {'!', '@', '#', '$', '%', '^', '&', '(', ')', '-', '_', '='}

    lowerCaseValid = False
    upperCaseValid = False
    numbersValid = False
    specialCharValid = False

    for char in password:
        if (char not in lowerCase) and (char not in upperCase) and (char not in numbers) and (char not in specialCharacters):
            return False
        elif char in lowerCase:   #lowercase
            lowerCaseValid = True
        elif char in upperCase:   #uppercase
            upperCaseValid = True
        elif char in numbers:     #numbers
            numbersValid = True
        elif char in specialCharacters:   #special characters
            specialCharValid = True

        if lowerCaseValid and upperCaseValid and numbersValid and specialCharValid:
            return True
        
