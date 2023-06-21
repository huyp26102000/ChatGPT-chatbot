import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';

import { AppRoutingModule } from './app-routing.module';
import { AppComponent } from './app.component';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { HomeComponent } from './components/home/home.component';
import { MenuComponent } from './components/menu/menu.component';
import { TokenComponent } from './components/token/token.component';
import { ZaloComponent } from './components/token/zalo/zalo.component';
import { ApikeyComponent } from './components/token/apikey/apikey.component';
import { MessengerComponent } from './components/token/messenger/messenger.component';
import { LoginComponent } from './components/login/login.component';
import { SignupComponent } from './components/login/signup/signup.component';
import { CarouseComponent } from './module/carouse/carouse.component';

@NgModule({
	declarations: [
		AppComponent,
		HomeComponent,
		MenuComponent,
		TokenComponent,
		ZaloComponent,
		ApikeyComponent,
		MessengerComponent,
		LoginComponent,
		SignupComponent,
		CarouseComponent,
	],
	imports: [
		BrowserModule,
		AppRoutingModule,
		FormsModule,
		ReactiveFormsModule
	],
	providers: [],
	bootstrap: [AppComponent]
})
export class AppModule { }
