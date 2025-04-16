import hashlib
import os
from cryptography.fernet import Fernet

class BlockchainVideoEncryptor:
    def __init__(self):
        # In a real application, you would load a pre-existing chain or initialize a proper database.
        # Here, we'll use a simple list for demonstration.  This is NOT secure for production.
        self.chain = []
        self.create_genesis_block()

    def create_genesis_block(self):
        # The first block in the blockchain
        genesis_block = {
            'index': 0,
            'timestamp': '2023-10-27 10:00:00',  # Replace with actual timestamp
            'data': 'Genesis Block',
            'previous_hash': '0'  # Special case for the first block
        }
        genesis_block['hash'] = self.hash_block(genesis_block)
        self.chain.append(genesis_block)

    def hash_block(self, block):
        # Creates a SHA-256 hash of a block
        block_string = f"{block['index']}{block['timestamp']}{block['data']}{block['previous_hash']}"
        return hashlib.sha256(block_string.encode()).hexdigest()

    def get_previous_block(self):
        # Returns the last block in the chain
        return self.chain[-1]

    def create_new_block(self, data):
        # Creates a new block and adds it to the chain
        previous_block = self.get_previous_block()
        new_index = previous_block['index'] + 1
        new_timestamp = '2023-10-27 10:05:00'  # Replace with actual timestamp
        new_block = {
            'index': new_index,
            'timestamp': new_timestamp,
            'data': data,
            'previous_hash': previous_block['hash']
        }
        new_block['hash'] = self.hash_block(new_block)
        self.chain.append(new_block)
        return new_block

    def encrypt_video(self, video_path):
        # Generates a key for encryption.  The key itself is NOT stored on the blockchain.
        key = Fernet.generate_key()  # THIS KEY IS CRUCIAL AND SHOULD BE SECURELY STORED.
        f = Fernet(key)

        try:
            with open(video_path, "rb") as video_file:
                video_data = video_file.read()
        except FileNotFoundError:
            print(f"Error: Video file not found at {video_path}")
            return None, None

        encrypted_data = f.encrypt(video_data)

        # Create a block on the blockchain to record the encryption.
        # IMPORTANT: We are NOT storing the key on the blockchain. This is a HUGE security risk.
        encryption_info = {
            'video_file': os.path.basename(video_path), #Store video name
            'encryption_method': 'Fernet' # Store the method
        }
        self.create_new_block(encryption_info)

        return encrypted_data, key

    def decrypt_video(self, encrypted_data, key):
        # Decrypts the video data using the provided key.
        f = Fernet(key)  # Re-use the SAME key used for encryption.
        decrypted_data = f.decrypt(encrypted_data)
        return decrypted_data

# Example Usage:
if __name__ == "__main__":
    encryptor = BlockchainVideoEncryptor()

    video_file_path = "/Users/kushagraagarwal/Library/Group Containers/group.net.whatsapp.WhatsApp.shared/Message/Media/120363046924507024@g.us/c/1/c12f1f6a-8e07-45e5-864e-a0269619889a.mp4"  # Replace with your video file
    encrypted_data, encryption_key = encryptor.encrypt_video(video_file_path)  # Get data and the KEY
    if encrypted_data:
        print("Video encrypted successfully!")

        # Store encrypted_data to a file (e.g., "encrypted_video.enc")
        # IMPORTANT: Securely store the encryption_key separately.  Do NOT store it in the code.
        with open("encrypted_video.enc", "wb") as encrypted_file:
            encrypted_file.write(encrypted_data)

        # Load encrypted data (for decryption example):
        with open("encrypted_video.enc", "rb") as encrypted_file:
            loaded_encrypted_data = encrypted_file.read()


        # Decryption (example) - assuming you've retrieved the key securely:
        decrypted_data = encryptor.decrypt_video(loaded_encrypted_data, encryption_key)

        # Save the decrypted data to a new file
        with open("decrypted_video.mp4", "wb") as decrypted_file:
            decrypted_file.write(decrypted_data)

        print("Video decrypted successfully!")

        # Print the blockchain:
        print("Blockchain:")
        for block in encryptor.chain:
            print(block)