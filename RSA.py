import random

class RSAHelper():

    def __init__(self, prime1, prime2):
        self.a = prime1
        self.b = prime2 

    # This method calculates GCD of 2 numbers.
    def gcd(self, a, b):
        while b != 0:
            a, b = b, a % b
        return a

    # This method calculates multiplicative inverse of 2 numbers using euclid's extended algorithm.
    def multiplicative_inverse(self, e, phi):
        d = 0
        x1 = 0
        x2 = 1
        y1 = 1
        temp_phi = phi
        
        while e > 0:
            temp1 = temp_phi//e
            temp2 = temp_phi - temp1 * e
            temp_phi = e
            e = temp2
            
            x = x2- temp1* x1
            y = d - temp1 * y1
            
            x2 = x1
            x1 = x
            d = y1
            y1 = y
        
        if temp_phi == 1:
            return d + phi

    # This method checks if the number is prime or not.
    def is_prime(self, num):
        if num == 2:
            return True
        if num < 2 or num % 2 == 0:
            return False
        for n in range(3, int(num**0.5)+2, 2):
            if num % n == 0:
                return False
        return True

    def generate_keypair(self, p, q):
        if not (self.is_prime(p) and self.is_prime(q)):
            raise ValueError('Both numbers must be prime.')
        elif p == q:
            raise ValueError('p and q cannot be equal')
        #n = pq
        n = p * q

        #Phi is the totient of n
        phi = (p-1) * (q-1)

        #Choose an integer e such that e and phi(n) are coprime
        e = random.randrange(1, phi)

        #Use Euclid's Algorithm to verify that e and phi(n) are comprime
        g = self.gcd(e, phi)
        while g != 1:
            e = random.randrange(1, phi)
            g = self.gcd(e, phi)

        print("Value of e is : ", e)
        print("Value of phi is : ", phi)

        #Use Extended Euclid's Algorithm to generate the private key
        d = self.multiplicative_inverse(e, phi)
        
        #Return public and private keypair
        #Public key is (e, n) and private key is (d, n)
        return ((e, n), (d, n))

    def encrypt(self, pk, plaintext):
        #Unpack the key into it's components
        key, n = pk
        #Convert each letter in the plaintext to numbers based on the character using a^b mod m
        cipher = [(ord(char) ** key) % n for char in plaintext]
        #Return the array of bytes
        return cipher

    def decrypt(self, pk, ciphertext):
        #Unpack the key into its components
        key, n = pk
        #Generate the plaintext based on the ciphertext and key using a^b mod m
        plain = [chr((char ** key) % n) for char in ciphertext]
        print("Decrypted message is : ", plain)
        #Return the array of bytes as a string
        return ''.join(plain)