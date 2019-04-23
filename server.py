from RSA import RSAHelper

if __name__ == '__main__':
    '''
    Detect if the script is being run directly by the user
    '''
    print("RSA Encrypter/ Decrypter")
    
    p = int(input("Enter a prime number (17, 19, 23, etc): "))
    q = int(input("Enter another prime number (Not one you entered above): "))
    
    rsaHelper = RSAHelper(p, q)

    print("Generating your public/private keypairs now . . .")
    public, private = rsaHelper.generate_keypair(p, q)

    print("Your public key is ", public ," and your private key is ", private) 

    message = input("Enter a message to encrypt with your private key: ")
    encrypted_msg = rsaHelper.encrypt(private, message)

    print("Your encrypted message is: ")
    print(''.join(map(lambda x: str(x), encrypted_msg)))
    print("Decrypting message with public key ", public ," . . .")
    print("Your message is:")
    print(rsaHelper.decrypt(public, encrypted_msg))