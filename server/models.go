package main

type Client struct {
	Name      string `json:"name"`
	PublicKey string `json:"publicKey"`
}

type Data struct {
	Target        string `json:"target"`
	Source        string `json:"source"`
	EncryptedData string `json:"encryptedData"`
}
