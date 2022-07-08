package main

import (
	"errors"
	"flag"
	"fmt"
	"log"
	"os"
	"path/filepath"
	"strings"
	"time"
)

const bufferDefaultSize = 10

func getFileExt(filename string) string {
	i := strings.LastIndexByte(filename, '.')

	if i == -1 {
		return ""
	}

	return filename[i:]
}

func isInner(toFind string, text []string) bool {
	for _, word := range text {
		if toFind == word {
			return true
		}
	}
	return false
}

func getFiles(dir string, exclude []string) (map[string][]string, error) {
	box := map[string][]string{}

	files, err := os.ReadDir(dir)
	if err != nil {
		return nil, err
	}

	for _, file := range files {
		if !file.IsDir() && !isInner(file.Name(), exclude) {
			ext := getFileExt(file.Name())
			if ext == "" {
				continue
			}

			if _, ok := box[ext]; !ok {
				box[ext] = make([]string, 0, bufferDefaultSize)
			}
			box[ext] = append(box[ext], file.Name())
		}
	}

	return box, nil
}

func createDirs(box map[string][]string) error {
	for k := range box {
		err := os.Mkdir(k, os.ModePerm)

		if !errors.Is(err, os.ErrExist) && err != nil {
			return err
		}
	}
	return nil
}

func moveFiles(src, dest string, filenames []string) error {
	var srcPath, destPath string

	for _, name := range filenames {
		destName := name

		srcPath = filepath.Join(src, name)
		destPath = filepath.Join(dest, destName)

		if _, err := os.Stat(destPath); err == nil {
			current := time.Now()
			destName = fmt.Sprintf("%d-%d-%d|%d:%d:%d-",
				current.Year(), current.Month(), current.Day(),
				current.Hour(), current.Minute(), current.Second()) + destName
		}

		destPath = filepath.Join(dest, destName)

		if err := os.Rename(srcPath, destPath); err != nil {
			return err
		}

	}
	return nil
}

func main() {
	flag.Parse()

	dir, err := os.Getwd()
	if err != nil {
		log.Fatalln(err)
	}

	box, err := getFiles(dir, flag.Args())
	if err != nil {
		log.Fatalln(err)
	}

	if err := createDirs(box); err != nil {
		log.Fatalln(err)
	}

	for k := range box {
		if err := moveFiles(dir, k, box[k]); err != nil {
			log.Fatalln(err)
		}
	}
}
