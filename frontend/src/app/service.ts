import {Injectable} from '@angular/core';
import {HttpClient, HttpHeaders} from '@angular/common/http';
import {Observable} from 'rxjs';
import {map} from "rxjs/operators";
import { Semaphore } from './runner/semaphore';
import { LoadFactor } from './runner/loadFactor';


@Injectable({
    providedIn: 'root'
})
export class Service {
    httpOptions = {
        headers: new HttpHeaders({
            'Content-Type': 'application/json'
          })
    };
    private backendUrl = 'http://localhost:5000/';

    constructor(private http: HttpClient){
    }

    startSumo(mode: string): Observable<Response> {
        return this.http.get<Response>(this.backendUrl + "start/" + mode);
    }

    startSumoOptimized(mode: string): Observable<Response> {
        return this.http.get<Response>(this.backendUrl + "startOptimized/" + mode);
    }

    editSemaphores(semaphores: Semaphore[]): Observable<Response> {
        const url = `${this.backendUrl}edit/semaphores`;
        console.log(semaphores);
        return this.http.post<Response>(url, semaphores);
    }
    editLoads(loads: LoadFactor[]): Observable<Response> {
        const url = `${this.backendUrl}edit/loads`;
        return this.http.post<Response>(url, loads);
    }
}