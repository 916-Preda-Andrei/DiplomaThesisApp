import { Component, Inject } from '@angular/core';
import { MAT_DIALOG_DATA } from '@angular/material/dialog';

@Component({
  selector: 'app-error-dialog',
  template: '<h2 mat-dialog-title>Error</h2><div mat-dialog-content>{{ data.message }}</div><div mat-dialog-actions><button mat-button [mat-dialog-close]="true">Close</button></div>'
})
export class AppErrorDialogComponent {
  constructor(@Inject(MAT_DIALOG_DATA) public data: { message: string }) { }
}