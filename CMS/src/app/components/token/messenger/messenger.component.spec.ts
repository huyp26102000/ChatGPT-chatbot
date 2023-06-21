import { ComponentFixture, TestBed } from '@angular/core/testing';

import { MessengerComponent } from './messenger.component';

describe('MessengerComponent', () => {
  let component: MessengerComponent;
  let fixture: ComponentFixture<MessengerComponent>;

  beforeEach(() => {
    TestBed.configureTestingModule({
      declarations: [MessengerComponent]
    });
    fixture = TestBed.createComponent(MessengerComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
