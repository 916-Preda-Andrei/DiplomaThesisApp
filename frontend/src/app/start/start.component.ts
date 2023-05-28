import { Component } from '@angular/core';
import { Router } from '@angular/router';
import { Service } from '../service';
import { MatDialog } from '@angular/material/dialog';
import { AppErrorDialogComponent } from '../app-error-dialog/app-error-dialog.component';
import { Street } from './street';


@Component({
  selector: 'app-start',
  templateUrl: './start.component.html',
  styleUrls: ['./start.component.css']
})
export class StartComponent {

  trainedValues = [
    {value: ['W','3', 'E', '3', 'S', '3', 'N', '3'], viewValue: 'W:3, E:3, S:3, N:3'}
  ];

  lanesOutValues = [
    {value: '3', viewValue: '3'},
    {value: '4', viewValue: '4'},
    {value: '5', viewValue: '5'},
    {value: '6', viewValue: '6'},
  ];

  lanesInValues = [
    {value: '1', viewValue: '1'},
    {value: '2', viewValue: '2'},
    {value: '3', viewValue: '3'},
    {value: '4', viewValue: '4'},
    {value: '5', viewValue: '5'},
    {value: '6', viewValue: '6'},
  ];
  westLanesOut: string = '3';
  westLanesIn: string = '1';

  eastLanesOut: string = '3';
  eastLanesIn: string = '1';

  southLanesOut: string = '3';
  southLanesIn: string = '1';

  northLanesOut: string = '3';
  northLanesIn: string = '1';

  trainedList: string[] = [];

  streets: Street[] = [];

  constructor(private service: Service, private router: Router, private dialog: MatDialog) { 
  }

  ngOnInit(): void {
  }

  go_next(): void {
    if(!this.checkExistingTraining()){
      this.openErrorDialog("There is no training made for this intersection configuration!");
      return;
    }
    
    var total_exit_lanes = Number(this.westLanesIn) + Number(this.eastLanesIn) + Number(this.southLanesIn) + Number(this.northLanesIn);

    if(Number(this.westLanesOut) > total_exit_lanes - Number(this.westLanesIn)){
      this.openErrorDialog("The number of approach lanes for the West Street is greater than the total number of exit lanes!");
      return;
    }

    if(Number(this.eastLanesOut) > total_exit_lanes - Number(this.eastLanesIn)){
      this.openErrorDialog("The number of approach lanes for the East Street is greater than the total number of exit lanes!");
      return;
    }

    if(Number(this.southLanesOut) > total_exit_lanes - Number(this.southLanesIn)){
      this.openErrorDialog("The number of approach lanes for the South Street is greater than the total number of exit lanes!");
      return;
    }

    if(Number(this.northLanesOut) > total_exit_lanes - Number(this.northLanesIn)){
      this.openErrorDialog("The number of approach lanes for the North Street is greater than the total number of exit lanes!");
      return;
    }

    this.streets = [
      { street: 'west', lanesIn: this.westLanesIn, lanesOut: this.westLanesOut },
      { street: 'east', lanesIn: this.eastLanesIn, lanesOut: this.eastLanesOut },
      { street: 'south', lanesIn: this.southLanesIn, lanesOut: this.southLanesOut },
      { street: 'north', lanesIn: this.northLanesIn, lanesOut: this.northLanesOut }
    ];
    this.service.editStreets(this.streets).subscribe( response => {
        if(response.status === 200){
          this.router.navigate(['/runner']).then(_ => {});
        }
        else{
          this.openErrorDialog("There was a problem in creating the intersection");
        }
    });
  }

  checkExistingTraining(): Boolean {
      for (const trainedIntersection of this.trainedValues) {
        let ok: Boolean = true;
        if (trainedIntersection.value[1] != this.westLanesOut)
          ok = false;
        if (trainedIntersection.value[3] != this.eastLanesOut)
          ok = false;
        if (trainedIntersection.value[5] != this.southLanesOut)
          ok = false;
        if (trainedIntersection.value[7] != this.northLanesOut)
          ok = false;
        if (ok)
          return true;
      }
      return false;
  }

  refreshApproachLanes(): void {
    this.westLanesOut = this.trainedList[1];
    this.eastLanesOut = this.trainedList[3];
    this.southLanesOut = this.trainedList[5];
    this.northLanesOut = this.trainedList[7];
  }

  openErrorDialog(message: string) {
    const dialogRef = this.dialog.open(AppErrorDialogComponent, {
      data: { message: message }
    });
  }
}
