import { Component } from '@angular/core';

@Component({
    selector: 'app-token',
    templateUrl: './token.component.html',
    styleUrls: ['./token.component.css']
})
export class TokenComponent {
    title = 'zalo'
    list_menu = ['zalo']
    images = [
        {
            imageSrc: '../assets/graphic/Logo-vinendong.png',
            imageAlt: 'logo1'
        },
        {
            imageSrc: '../assets/graphic/Logo-vinendong.png',
            imageAlt: 'logo2'
        }
    ]
}
