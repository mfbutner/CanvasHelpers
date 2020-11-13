import { Injectable } from '@angular/core';
import { Hero } from './hero';
import { HEROES } from './mock-heroes';

@Injectable({
  /* we declare that this service should be  created 
  by the root application injector. */
  providedIn: 'root'
})
export class HeroService {
  
  constructor() {}

  getHeros(): Hero[] {
    return HEROES;
  }

}
