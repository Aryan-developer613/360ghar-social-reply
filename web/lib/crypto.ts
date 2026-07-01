/**
 * Web Crypto API utilities for client-side payload encryption.
 */

export async function generateEncryptionKey(): Promise<CryptoKey> {
  return await window.crypto.subtle.generateKey(
    {
      name: "AES-GCM",
      length: 256,
    },
    true,
    ["encrypt", "decrypt"]
  );
}

export async function exportKey(key: CryptoKey): Promise<string> {
  const exported = await window.crypto.subtle.exportKey("raw", key);
  const exportedKeyBuffer = new Uint8Array(exported);
  const exportedKeyBase64 = btoa(String.fromCharCode(...exportedKeyBuffer));
  return exportedKeyBase64;
}

export async function importKey(base64Key: string): Promise<CryptoKey> {
  const binaryString = atob(base64Key);
  const bytes = new Uint8Array(binaryString.length);
  for (let i = 0; i < binaryString.length; i++) {
    bytes[i] = binaryString.charCodeAt(i);
  }
  return await window.crypto.subtle.importKey(
    "raw",
    bytes,
    { name: "AES-GCM" },
    true,
    ["encrypt", "decrypt"]
  );
}

export async function encryptPayload(data: string, key: CryptoKey): Promise<{ ciphertext: string; iv: string }> {
  const encoder = new TextEncoder();
  const iv = window.crypto.getRandomValues(new Uint8Array(12));
  const ciphertextBuffer = await window.crypto.subtle.encrypt(
    {
      name: "AES-GCM",
      iv: iv,
    },
    key,
    encoder.encode(data)
  );

  const ciphertextBytes = new Uint8Array(ciphertextBuffer);
  return {
    ciphertext: btoa(String.fromCharCode(...ciphertextBytes)),
    iv: btoa(String.fromCharCode(...iv)),
  };
}

export async function decryptPayload(ciphertextBase64: string, ivBase64: string, key: CryptoKey): Promise<string> {
  const decoder = new TextDecoder();
  
  const cipherStr = atob(ciphertextBase64);
  const cipherBytes = new Uint8Array(cipherStr.length);
  for (let i = 0; i < cipherStr.length; i++) cipherBytes[i] = cipherStr.charCodeAt(i);
  
  const ivStr = atob(ivBase64);
  const ivBytes = new Uint8Array(ivStr.length);
  for (let i = 0; i < ivStr.length; i++) ivBytes[i] = ivStr.charCodeAt(i);

  const decryptedBuffer = await window.crypto.subtle.decrypt(
    {
      name: "AES-GCM",
      iv: ivBytes,
    },
    key,
    cipherBytes
  );

  return decoder.decode(decryptedBuffer);
}
