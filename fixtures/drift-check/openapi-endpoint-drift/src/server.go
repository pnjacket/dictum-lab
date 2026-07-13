package main

import "net/http"

// DICT: API-LIST-NOTES
func handleList(w http.ResponseWriter, r *http.Request) {}

// DICT: API-CREATE-NOTE
func handleCreate(w http.ResponseWriter, r *http.Request) {}

func main() {
	http.HandleFunc("/notes", handleList)
	http.ListenAndServe(":8080", nil)
}
