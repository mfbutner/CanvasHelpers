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

  getHeroes(): Observable<Hero[]> {
    this.MessageService.add('HeroService: fetched heroes');
    return of(HEROES);
  }

  getHero(id: number): Observable<Hero> {
    // TODO: send the message_after_ fetching the hero
    this.MessageService.add('HeroService: fetched hero id=${id}');
    return of(HEROES.find(hero => hero.id === id));
  }

}
