import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { StartComponent } from './start/start.component';
import { RunnerComponent } from './runner/runner.component';

const routes: Routes = [
  {path: '', component: StartComponent},
  {path: 'runner', component: RunnerComponent},

];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule { }
