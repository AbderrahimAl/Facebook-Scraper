import maskpass

def login():
    email=str(input("Email : "))
    password=maskpass.advpass()
    login={
        'email':email,
        'pass':password
        }
    return login


