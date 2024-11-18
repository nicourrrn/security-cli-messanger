package main

import (
	"encoding/json"
	"io"
	"log"
	"net/http"
)

type ServerState struct {
	clients []Client
}

func (state *ServerState) Registration(w http.ResponseWriter, r *http.Request) {
	decoder := json.NewDecoder(r.Body)
	var client Client
	err := decoder.Decode(&client)
	if err != nil {
		log.Fatal(err)
	}
	state.clients = append(state.clients, client)
	log.Println("Client registered: ", client.Name)
	io.WriteString(w, "Client registered")
}

func (state *ServerState) SendData(w http.ResponseWriter, r *http.Request) {
}

func (state *ServerState) Clients(w http.ResponseWriter, r *http.Request) {
	json.NewEncoder(w).Encode(state.clients)
}

func (state *ServerState) Updates(w http.ResponseWriter, r *http.Request) {
}
