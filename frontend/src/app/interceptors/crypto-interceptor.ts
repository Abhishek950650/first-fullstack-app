// src/app/interceptors/crypto.interceptor.ts
import { HttpInterceptorFn, HttpRequest, HttpHandlerFn } from '@angular/common/http';
import { inject } from '@angular/core';
import { map } from 'rxjs/operators';
import { EncryptionService } from '../services/encryption';

export const cryptoInterceptor: HttpInterceptorFn = (
  req: HttpRequest<any>,
  next: HttpHandlerFn
) => {
  const encService = inject(EncryptionService);

  // ── Step 1: Request body encrypt karo ──────────────
  let encryptedReq = req;

  if (req.body && req.method !== 'GET') {
    const encryptedBody = encService.encrypt(req.body);

    encryptedReq = req.clone({
      body: { data: encryptedBody }   // { data: "encrypted..." }
    });
  }

  // ── Step 2: Response decrypt karo ──────────────────
  return next(encryptedReq).pipe(
    map((event: any) => {

      // HTTP Response aaya hai
      if (event?.body?.data) {
        const decryptedBody = encService.decrypt(event.body.data);

        // Response body replace karo decrypted data se
        return event.clone({ body: decryptedBody });
      }

      return event;
    })
  );
};