import { Component } from '@angular/core';
import { Service } from '../service';
import { MatDialog } from '@angular/material/dialog';
import { AppErrorDialogComponent } from '../app-error-dialog/app-error-dialog.component';
import { LoadFactor } from './loadFactor';

@Component({
  selector: 'app-runner',
  templateUrl: './runner.component.html',
  styleUrls: ['./runner.component.css']
})
export class RunnerComponent {
  simulatorStarted: boolean = false;
  north_left_load: number = 5;
  north_front_load: number = 5;
  north_right_load: number = 5;
  west_left_load: number = 5;
  west_front_load: number = 5;
  west_right_load: number = 5;
  east_left_load: number = 5;
  east_front_load: number = 5;
  east_right_load: number = 5;
  south_left_load: number = 5;
  south_front_load: number = 5;
  south_right_load: number = 5;
  loadFactors: LoadFactor[] = [] 

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

  edit_load_factor(): void {
    this.loadFactors = [
      {from: 'north', to: 'east', loadFactor: this.north_left_load},
      {from: 'north', to: 'south', loadFactor: this.north_front_load},
      {from: 'north', to: 'west', loadFactor: this.north_right_load},
      {from: 'west', to: 'north', loadFactor: this.west_left_load},
      {from: 'west', to: 'east', loadFactor: this.west_front_load},
      {from: 'west', to: 'south', loadFactor: this.west_right_load},
      {from: 'east', to: 'south', loadFactor: this.east_left_load},
      {from: 'east', to: 'west', loadFactor: this.east_front_load},
      {from: 'east', to: 'north', loadFactor: this.east_right_load},
      {from: 'south', to: 'west', loadFactor: this.south_left_load},
      {from: 'south', to: 'north', loadFactor: this.south_front_load},
      {from: 'south', to: 'east', loadFactor: this.south_right_load}

    ]
  }

  openErrorDialog(message: string) {
    const dialogRef = this.dialog.open(AppErrorDialogComponent, {
      data: { message: message }
    });
  }
}
