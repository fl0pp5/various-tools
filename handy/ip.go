package main

import (
	"encoding/json"
	"fmt"
	"log"
	"net/http"
)

const URL = "https://api.myip.com"

type API struct {
	IP      string
	Country string
}

func (api *API) show() {
	fmt.Printf("IP: %s\nCountry: %s\n", api.IP, api.Country)
}

func main() {
	resp, err := http.Get(URL)
	if err != nil {
		log.Fatalln(err)
	}

	var info API

	if err := json.NewDecoder(resp.Body).Decode(&info); err != nil {
		log.Fatalln(err)
	}

	info.show()
}
