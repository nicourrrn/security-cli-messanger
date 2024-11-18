package main

import (
	"log"
	"net/http"
)

func main() {
	state := ServerState{clients: []Client{}}

	http.HandleFunc("/registration", state.Registration)
	http.HandleFunc("/send_data", state.SendData)
	http.HandleFunc("/clients", state.Clients)
	http.HandleFunc("/updates", state.Updates)

	log.Println("Server started")
	http.ListenAndServe(":8080", nil)
}
