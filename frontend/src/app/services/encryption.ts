// src/app/services/encryption.service.ts
import { Injectable } from '@angular/core';
import * as CryptoJS from 'crypto-js';
import { environment } from '../../environments/environment';

@Injectable({
  providedIn: 'root'
})
export class EncryptionService {

  private key = CryptoJS.enc.Utf8.parse(
    environment.aesKey.substring(0, 32)   // 32 chars = AES-256
  );

  /**
   * Data encrypt karo
   * Dict → JSON → AES Encrypt → base64
   * Random IV automatically generate hoga
   */
  encrypt(data: object): string {
    const jsonStr = JSON.stringify(data);
    // console.log('Encrypting data:', data);
    // Random IV banao (16 bytes)
    const iv = CryptoJS.lib.WordArray.random(16);

    const encrypted = CryptoJS.AES.encrypt(jsonStr, this.key, {
      iv: iv,
      mode: CryptoJS.mode.CBC,
      padding: CryptoJS.pad.Pkcs7
    });

    // IV + encrypted saath combine karo (backend jaisa)
    const combined = iv.concat(encrypted.ciphertext);
    return CryptoJS.enc.Base64.stringify(combined);
  }

  /**
   * Data decrypt karo
   * base64 → IV alag karo → AES Decrypt → JSON → Object
   */
  decrypt(encryptedStr: string): any {
    const combined = CryptoJS.enc.Base64.parse(encryptedStr);
    // console.log('Decrypting data:', encryptedStr);
    // Pehle 16 bytes = IV
    const iv = CryptoJS.lib.WordArray.create(
      (combined as any).words.slice(0, 4)
    );
    // Baaki = encrypted data
    const ciphertext = CryptoJS.lib.WordArray.create(
      (combined as any).words.slice(4)
    );

    const decrypted = CryptoJS.AES.decrypt(
      { ciphertext } as any,
      this.key,
      { iv, mode: CryptoJS.mode.CBC, padding: CryptoJS.pad.Pkcs7 }
    );

    return JSON.parse(decrypted.toString(CryptoJS.enc.Utf8));
  }
}