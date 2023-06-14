import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { RunnerComponent } from './runner/runner.component';

const routes: Routes = [
  {path: '', component: RunnerComponent},

];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule { }
