package main

import (
	"net/http"
)

func main() {
	http.HandleFunc("/registration", Registration)
	http.HandleFunc("/send_data", SendData)
	http.HandleFunc("/clients", Clients)
	http.HandleFunc("/updates", Updates)

	http.ListenAndServe(":8080", nil)
}
