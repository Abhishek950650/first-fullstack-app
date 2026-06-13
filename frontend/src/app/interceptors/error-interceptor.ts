// src/app/interceptors/error.interceptor.ts
import {
  HttpInterceptorFn,
  HttpRequest,
  HttpHandlerFn,
  HttpEvent,
  HttpErrorResponse
} from '@angular/common/http';
import { inject } from '@angular/core';
import { Observable, throwError } from 'rxjs';
import { catchError } from 'rxjs/operators';
import { Router } from '@angular/router';
import { Auth } from '../services/auth';

export const errorInterceptor: HttpInterceptorFn = (
  req: HttpRequest<any>,
  next: HttpHandlerFn
): Observable<HttpEvent<any>> => {

  const router      = inject(Router);
  const authService = inject(Auth);

  return next(req).pipe(
    catchError((error: HttpErrorResponse) => {

      switch (error.status) {

        case 401:
          // Token expire ho gaya → logout karke login pe bhejo
          authService.clearSession();
          router.navigate(['/login']);
          break;

        case 403:
          // Access nahi hai → home pe bhejo
          router.navigate(['/home']);
          break;

        case 500:
          // Server error
          console.error('Server error — backend check karo');
          break;

        case 0:
          // Network error — backend band hai
          console.error('Backend server se connect nahi ho pa raha');
          break;
      }

      // Error aage throw karo — component bhi handle kar sake
      return throwError(() => error);
    })
  );
};