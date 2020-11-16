import { Injectable } from '@angular/core';
import { Observable, of } from 'rxjs';
import { MessageService } from './message.service';

import { Hero } from './hero';
import { HEROES } from './mock-heroes';

@Injectable({
  /* we declare that this service should be  created 
  by the root application injector. */
  providedIn: 'root'
})
export class HeroService {
  
  constructor(private MessageService: MessageService) {}

  getHeros(): Observable<Hero[]> {
    this.MessageService.add('HeroSErvice: fetched heroes');
    return of(HEROES);
  }

}
