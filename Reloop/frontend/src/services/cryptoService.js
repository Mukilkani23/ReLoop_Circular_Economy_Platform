import nacl from 'tweetnacl';
import { decodeBase64, encodeBase64, decodeUTF8, encodeUTF8 } from 'tweetnacl-util';

class CryptoService {
  /**
   * Generates a new Box key pair.
   */
  static generateKeyPair() {
    return nacl.box.keyPair();
  }

  /**
   * Encrypts a message for a specific receiver.
   * @param {string} msg Plaintext message
   * @param {Uint8Array} mySecretKey Sender's private key
   * @param {Uint8Array} theirPublicKey Receiver's public key
   */
  static encrypt(msg, mySecretKey, theirPublicKey) {
    const nonce = nacl.randomBytes(nacl.box.nonceLength);
    const messageUint8 = decodeUTF8(msg);
    const encrypted = nacl.box(messageUint8, nonce, theirPublicKey, mySecretKey);
    
    // Return nonce + encrypted message as a single base64 string
    const fullMessage = new Uint8Array(nonce.length + encrypted.length);
    fullMessage.set(nonce);
    fullMessage.set(encrypted, nonce.length);
    
    return encodeBase64(fullMessage);
  }

  /**
   * Decrypts a message from a specific sender.
   * @param {string} encryptedBase64 The base64 full message (nonce + ciphertext)
   * @param {Uint8Array} mySecretKey Receiver's private key
   * @param {Uint8Array} theirPublicKey Sender's public key
   */
  static decrypt(encryptedBase64, mySecretKey, theirPublicKey) {
    const fullMessage = decodeBase64(encryptedBase64);
    const nonce = fullMessage.slice(0, nacl.box.nonceLength);
    const ciphertext = fullMessage.slice(nacl.box.nonceLength);
    
    const decrypted = nacl.box.open(ciphertext, nonce, theirPublicKey, mySecretKey);
    if (!decrypted) {
      throw new Error("Could not decrypt message. Key mismatch or compromised data.");
    }
    
    return encodeUTF8(decrypted);
  }

  /**
   * Key conversion helpers (Uint8Array <-> Base64)
   */
  static keyToBase64(keyUint8) {
    return encodeBase64(keyUint8);
  }

  static base64ToKey(keyBase64) {
    return decodeBase64(keyBase64);
  }
}

export default CryptoService;
