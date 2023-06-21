import { Component } from '@angular/core';

@Component({
	selector: 'app-menu',
	templateUrl: './menu.component.html',
	styleUrls: ['./menu.component.css']
})
export class MenuComponent {
	activeMenu: number | null = null;

	ToggleMenu(index: number) {
		if (this.activeMenu === index) {
			this.activeMenu = null;
		} else {
			this.activeMenu = index;
		}
  	}
}
