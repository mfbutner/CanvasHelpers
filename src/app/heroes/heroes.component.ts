import { Component, OnInit } from '@angular/core';
import { Hero } from 'src/app/hero'
import { HeroService } from '../hero.service';

@Component({
  selector: 'app-heroes',
  templateUrl: './heroes.component.html',
  styleUrls: ['./heroes.component.css']
})
export class HeroesComponent implements OnInit {

  /* set heroes list to elements from HEROES */
  heroes: Hero[];
  /* selected hero */
  selectedHero: Hero;

  constructor() { 
  }

  ngOnInit(): void {
  }

  /* each hero element has an id and name */
  hero: Hero = {
    id: 1,
    name: 'Windstorm'
  };

  /* on select assigns the clicked hero from the template to selectedHero */
  onSelect(hero: Hero): void {
    this.selectedHero = hero;
  }
}
