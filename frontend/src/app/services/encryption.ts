// src/app/services/encryption.service.ts
import { Injectable } from '@angular/core';
import * as CryptoJS from 'crypto-js';
import { environment } from '../../environments/environment';

@Injectable({
  providedIn: 'root'
})
export class EncryptionService {

  private key = CryptoJS.enc.Utf8.parse(
    environment.aesKey.substring(0, 32)
  );
  
  private isEncryption = environment.enableEncryption;

  encrypt(data: object): string {
    // Flag OFF hai → plain JSON return karo
    if (!this.isEncryption) {
      console.log('%c[DEV] Request Payload (plain):',
        'color: #4CAF50; font-weight: bold', data);
      return JSON.stringify(data);
    }

    // Flag ON hai → encrypt karo
    const jsonStr = JSON.stringify(data);
    const iv = CryptoJS.lib.WordArray.random(16);
    const encrypted = CryptoJS.AES.encrypt(jsonStr, this.key, {
      iv: iv,
      mode: CryptoJS.mode.CBC,
      padding: CryptoJS.pad.Pkcs7
    });
    const combined = iv.concat(encrypted.ciphertext);
    const result = CryptoJS.enc.Base64.stringify(combined);

    console.log('%c[PROD] Request Encrypted:',
      'color: #FF9800; font-weight: bold', result);
    return result;
  }

  decrypt(encryptedStr: string): any {
    // Flag OFF hai → already plain JSON hai
    if (!this.isEncryption) {
      const parsed = JSON.parse(encryptedStr);
      console.log('%c[DEV] Response Payload (plain):',
        'color: #2196F3; font-weight: bold', parsed);
      return parsed;
    }

    // Flag ON hai → decrypt karo
    const combined = CryptoJS.enc.Base64.parse(encryptedStr);
    const iv = CryptoJS.lib.WordArray.create(
      (combined as any).words.slice(0, 4)
    );
    const ciphertext = CryptoJS.lib.WordArray.create(
      (combined as any).words.slice(4)
    );
    const decrypted = CryptoJS.AES.decrypt(
      { ciphertext } as any,
      this.key,
      { iv, mode: CryptoJS.mode.CBC, padding: CryptoJS.pad.Pkcs7 }
    );
    const result = JSON.parse(
      decrypted.toString(CryptoJS.enc.Utf8)
    );

    console.log('%c[PROD] Response Decrypted:',
      'color: #9C27B0; font-weight: bold', result);
    return result;
  }
}