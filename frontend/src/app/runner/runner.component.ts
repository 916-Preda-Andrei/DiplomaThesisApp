import { Component } from '@angular/core';
import { Service } from '../service';
import { MatDialog } from '@angular/material/dialog';
import { AppErrorDialogComponent } from '../app-error-dialog/app-error-dialog.component';

@Component({
  selector: 'app-runner',
  templateUrl: './runner.component.html',
  styleUrls: ['./runner.component.css']
})
export class RunnerComponent {
  simulatorStarted: boolean = false;

  constructor(private service: Service, private dialog: MatDialog) { 
  }

  ngOnInit(): void {
  }

  start_normal(): void {
    if (this.simulatorStarted) {
      this.openErrorDialog("A simulator is already running! Close that one in order to start another one!");
      return;
    }

    this.simulatorStarted = true;
    this.service.startSumo().subscribe( response => {
      this.simulatorStarted = false;
    });
  }

  start_optimized(): void {
    if (this.simulatorStarted) {
      this.openErrorDialog("A simulator is already running! Close that one in order to start another one!");
      return;
    }

    this.simulatorStarted = true;
    this.service.startSumoOptimized().subscribe( response => {
      this.simulatorStarted = false;
    });
  }

  openErrorDialog(message: string) {
    const dialogRef = this.dialog.open(AppErrorDialogComponent, {
      data: { message: message }
    });
  }
}
