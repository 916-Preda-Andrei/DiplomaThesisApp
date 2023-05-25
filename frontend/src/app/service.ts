import {Injectable} from '@angular/core';
import {HttpClient, HttpHeaders} from '@angular/common/http';
import {Observable} from 'rxjs';
import {map} from "rxjs/operators";
import { Street } from './start/street';
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

    startSumo(): Observable<String> {
        return this.http.get<String>(this.backendUrl + "start");
    }

    startSumoOptimized(): Observable<String> {
        return this.http.get<String>(this.backendUrl + "startOptimized");
    }

    editStreets(streets: Street[]): Observable<Response> {
        const url = `${this.backendUrl}edit/streets`;
        return this.http.post<Response>(url, streets);
    }
    editLoads(loads: LoadFactor[]): Observable<Response> {
        const url = `${this.backendUrl}edit/loads`;
        return this.http.post<Response>(url, loads);
    }
}