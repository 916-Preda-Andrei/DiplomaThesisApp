import { ComponentFixture, TestBed } from '@angular/core/testing';

import { AppErrorDialogComponent } from './app-error-dialog.component';

describe('AppErrorDialogComponent', () => {
  let component: AppErrorDialogComponent;
  let fixture: ComponentFixture<AppErrorDialogComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ AppErrorDialogComponent ]
    })
    .compileComponents();

    fixture = TestBed.createComponent(AppErrorDialogComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
