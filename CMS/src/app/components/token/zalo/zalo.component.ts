import { Component } from '@angular/core';
import { FormControl, FormGroup, NgForm, Validators } from '@angular/forms';

@Component({
	selector: 'app-zalo',
	templateUrl: './zalo.component.html',
	styleUrls: ['./zalo.component.css']
})
export class ZaloComponent {
	checks = true;
	yunaforms = new FormGroup({
		token: new FormControl('', [Validators.required])
 	});

	// name = this.yunaforms.get('name');
	// token = this.yunaforms.get('token');

	onSubmit(){
		console.log(this.yunaforms.dirty);
	}
}