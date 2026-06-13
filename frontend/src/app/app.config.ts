import { ApplicationConfig, provideBrowserGlobalErrorListeners, provideZonelessChangeDetection } from '@angular/core';
import { provideRouter, RouterLink } from '@angular/router';

import { routes } from './app.routes';
import { provideHttpClient, withInterceptors } from '@angular/common/http';
import { authInterceptor } from './interceptors/auth-interceptor';
import { cryptoInterceptor } from './interceptors/crypto-interceptor';
import { errorInterceptor } from './interceptors/error-interceptor';

export const appConfig: ApplicationConfig = {
  providers: [
    provideBrowserGlobalErrorListeners(),
    provideZonelessChangeDetection(),
    provideRouter(routes),
    provideHttpClient(),
    provideHttpClient(
      withInterceptors([
        cryptoInterceptor,   // 1st — encrypt req / decrypt res
        authInterceptor,     // 2nd — token attach
        errorInterceptor     // 3rd — errors handle
      ])
    ),
  ]
};
