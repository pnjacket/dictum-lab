package main

import (
	"net/http"
	"os"
)

// DICT: API-LIST-NOTES
func handleList(w http.ResponseWriter, r *http.Request) {}

/* DICT: API-CREATE-NOTE */
func handleCreate(w http.ResponseWriter, r *http.Request) {}

func main() {
	addr := os.Getenv("NOTES_ADDR")
	http.HandleFunc("/notes", handleList)
	http.ListenAndServe(addr, nil)
}
