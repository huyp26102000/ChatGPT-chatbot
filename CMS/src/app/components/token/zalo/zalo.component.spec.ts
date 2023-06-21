import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ZaloComponent } from './zalo.component';

describe('ZaloComponent', () => {
  let component: ZaloComponent;
  let fixture: ComponentFixture<ZaloComponent>;

  beforeEach(() => {
    TestBed.configureTestingModule({
      declarations: [ZaloComponent]
    });
    fixture = TestBed.createComponent(ZaloComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
