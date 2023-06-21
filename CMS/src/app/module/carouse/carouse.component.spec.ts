import { ComponentFixture, TestBed } from '@angular/core/testing';

import { CarouseComponent } from './carouse.component';

describe('CarouseComponent', () => {
  let component: CarouseComponent;
  let fixture: ComponentFixture<CarouseComponent>;

  beforeEach(() => {
    TestBed.configureTestingModule({
      declarations: [CarouseComponent]
    });
    fixture = TestBed.createComponent(CarouseComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
