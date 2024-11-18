package main

import (
	"encoding/json"
	"io"
	"log"
	"net/http"
)

type ServerState struct {
	clients []Client
	data    []Data
}

func (state *ServerState) Registration(w http.ResponseWriter, r *http.Request) {
	decoder := json.NewDecoder(r.Body)
	var client Client
	err := decoder.Decode(&client)
	if err != nil {
		log.Fatal(err)
	}
	for i := range state.clients {
		if state.clients[i].Name == client.Name {
			log.Println("Client registered: ", client.Name)
			io.WriteString(w, "Client already registered")
			w.WriteHeader(http.StatusConflict)
			return
		}
	}
	state.clients = append(state.clients, client)
	log.Println("Client registered: ", client.Name)
	io.WriteString(w, "Client registered")
}

func (state *ServerState) SendData(w http.ResponseWriter, r *http.Request) {
	decoder := json.NewDecoder(r.Body)
	var data Data
	err := decoder.Decode(&data)
	if err != nil {
		log.Fatal(err)
	}
	log.Println("Data received: ", data)
	state.data = append(state.data, data)
}

func (state *ServerState) Clients(w http.ResponseWriter, r *http.Request) {
	json.NewEncoder(w).Encode(state.clients)
	w.Header().Set("Content-Type", "application/json")
}

func (state *ServerState) Updates(w http.ResponseWriter, r *http.Request) {
	updatesForUser := []Data{}
	user := r.Header["User"]
	for _, data := range state.data {
		if data.Target == user[0] {
			updatesForUser = append(updatesForUser, data)
		}
	}

	json.NewEncoder(w).Encode(updatesForUser)
	w.Header().Set("Content-Type", "application/json")
}
