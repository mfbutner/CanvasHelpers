import { Component, OnInit } from '@angular/core';

import { Hero } from 'src/app/hero'
import { HeroService } from '../hero.service';
import { MessageService } from '../message.service';

@Component({
  selector: 'app-heroes',
  templateUrl: './heroes.component.html',
  styleUrls: ['./heroes.component.css']
})
export class HeroesComponent implements OnInit {

  /* set heroes list to elements from HEROES */
  heroes: Hero[];
  
  /* will construct herocomponent with data from heroService */
  /* private messageService component for herocomponet */
  constructor(private heroService: HeroService, private messageService:MessageService) { 
  }

  /* get heros on init */
  ngOnInit(): void {
    this.getHeroes();
  }

  getHeroes(): void {
    this.heroService.getHeroes()
      .subscribe(heroes => this.heroes = heroes);
  }

 
}
