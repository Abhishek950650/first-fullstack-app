// src/app/interceptors/crypto.interceptor.ts
import {
  HttpInterceptorFn,
  HttpRequest,
  HttpHandlerFn,
  HttpEvent,
  HttpResponse
} from '@angular/common/http';
import { inject } from '@angular/core';
import { Observable } from 'rxjs';
import { map } from 'rxjs/operators';
import { EncryptionService } from '../services/encryption';
import { environment } from '../../environments/environment';

export const cryptoInterceptor: HttpInterceptorFn = (
  req: HttpRequest<any>,
  next: HttpHandlerFn
): Observable<HttpEvent<any>> => {

  const encService = inject(EncryptionService);
  const isEncryption = environment.enableEncryption;

  // ── Request ────────────────────────────────────────
  let outgoingReq = req;

  if (req.body && req.method !== 'GET') {

    if (isEncryption) {
      // Production → encrypted body bhejo
      const encryptedBody = encService.encrypt(req.body);
      outgoingReq = req.clone({
        body: { data: encryptedBody }
      });
    } else {
      // Development → plain body bhejo as-is
      outgoingReq = req.clone({ body: req.body });
    }
  }

  // ── Response ───────────────────────────────────────
  return next(outgoingReq).pipe(
    map((event: HttpEvent<any>) => {

      if (event instanceof HttpResponse) {

        if (isEncryption && event.body?.data) {
          // Production → decrypt karo
          const decrypted = encService.decrypt(event.body.data);
          return event.clone({ body: decrypted });
        }

        // Development → body as-is return karo
        return event;
      }

      return event;
    })
  );
};